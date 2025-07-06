from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, and_, or_
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging

from models import (
    AnalyticsMetric,
    HiringFunnel,
    DiversityMetric,
    AhpPerformanceMetric,
    TimeToHireMetric
)
from schemas import (
    HiringMetricsResponse,
    DiversityReportResponse,
    AhpPerformanceResponse,
    HiringMetric,
    DiversityMetric
)

logger = logging.getLogger(__name__)

class MetricsService:
    """Service for calculating and retrieving various metrics"""
    
    async def get_hiring_metrics(
        self,
        db: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        department: Optional[str] = None,
        job_level: Optional[str] = None
    ) -> HiringMetricsResponse:
        """Get comprehensive hiring metrics"""
        
        try:
            # Parse dates
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
            start_dt = datetime.fromisoformat(start_date) if start_date else end_dt - timedelta(days=30)
            
            # Base query filters
            filters = [
                text("created_at BETWEEN :start_date AND :end_date")
            ]
            params = {"start_date": start_dt, "end_date": end_dt}
            
            if department:
                filters.append(text("department = :department"))
                params["department"] = department
                
            if job_level:
                filters.append(text("job_level = :job_level"))
                params["job_level"] = job_level
            
            # Get total applications
            app_query = text("""
                SELECT COUNT(*) as total_applications
                FROM applications 
                WHERE """ + " AND ".join([f.text for f in filters]))
            
            result = await db.execute(app_query, params)
            total_applications = result.scalar() or 0
            
            # Get total hires
            hire_query = text("""
                SELECT COUNT(*) as total_hires
                FROM applications a
                JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE wi.current_stage = 'hired' AND """ + " AND ".join([f.text for f in filters]))
            
            result = await db.execute(hire_query, params)
            total_hires = result.scalar() or 0
            
            # Calculate hire rate
            hire_rate = (total_hires / total_applications * 100) if total_applications > 0 else 0
            
            # Get average time to hire
            time_query = text("""
                SELECT AVG(EXTRACT(DAY FROM (wi.updated_at - a.created_at))) as avg_time_to_hire
                FROM applications a
                JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE wi.current_stage = 'hired' AND """ + " AND ".join([f.text for f in filters]))
            
            result = await db.execute(time_query, params)
            avg_time_to_hire = float(result.scalar() or 0)
            
            # Get metrics by department
            dept_query = text("""
                SELECT 
                    jp.department,
                    COUNT(a.id) as applications,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hires,
                    AVG(CASE WHEN wi.current_stage = 'hired' 
                        THEN EXTRACT(DAY FROM (wi.updated_at - a.created_at)) END) as avg_days
                FROM applications a
                JOIN job_postings jp ON a.job_posting_id = jp.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
                GROUP BY jp.department
                ORDER BY applications DESC
            """)
            
            result = await db.execute(dept_query, {"start_date": start_dt, "end_date": end_dt})
            metrics_by_department = []
            for row in result:
                metrics_by_department.append({
                    "department": row.department,
                    "applications": row.applications,
                    "hires": row.hires or 0,
                    "hire_rate": (row.hires / row.applications * 100) if row.applications > 0 else 0,
                    "avg_time_to_hire": float(row.avg_days or 0)
                })
            
            # Get metrics by job level
            level_query = text("""
                SELECT 
                    jp.job_level,
                    COUNT(a.id) as applications,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hires
                FROM applications a
                JOIN job_postings jp ON a.job_posting_id = jp.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
                GROUP BY jp.job_level
                ORDER BY applications DESC
            """)
            
            result = await db.execute(level_query, {"start_date": start_dt, "end_date": end_dt})
            metrics_by_job_level = []
            for row in result:
                metrics_by_job_level.append({
                    "job_level": row.job_level,
                    "applications": row.applications,
                    "hires": row.hires or 0,
                    "hire_rate": (row.hires / row.applications * 100) if row.applications > 0 else 0
                })
            
            # Get time series data (weekly breakdown)
            time_series_query = text("""
                SELECT 
                    DATE_TRUNC('week', a.created_at) as week_start,
                    COUNT(a.id) as applications,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hires
                FROM applications a
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
                GROUP BY DATE_TRUNC('week', a.created_at)
                ORDER BY week_start
            """)
            
            result = await db.execute(time_series_query, {"start_date": start_dt, "end_date": end_dt})
            time_series_data = []
            for row in result:
                hire_rate_week = (row.hires / row.applications * 100) if row.applications > 0 else 0
                time_series_data.append(HiringMetric(
                    metric_name="weekly_hire_rate",
                    value=hire_rate_week,
                    period_start=row.week_start,
                    period_end=row.week_start + timedelta(days=6)
                ))
            
            return HiringMetricsResponse(
                total_applications=total_applications,
                total_hires=total_hires,
                hire_rate=hire_rate,
                avg_time_to_hire=avg_time_to_hire,
                metrics_by_department=metrics_by_department,
                metrics_by_job_level=metrics_by_job_level,
                time_series_data=time_series_data
            )
            
        except Exception as e:
            logger.error(f"Error calculating hiring metrics: {e}")
            raise
    
    async def get_diversity_metrics(
        self,
        db: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        department: Optional[str] = None
    ) -> DiversityReportResponse:
        """Get diversity and inclusion metrics"""
        
        try:
            # Parse dates
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
            start_dt = datetime.fromisoformat(start_date) if start_date else end_dt - timedelta(days=30)
            
            # Get diversity metrics by dimension
            diversity_query = text("""
                SELECT 
                    c.gender,
                    c.ethnicity,
                    jp.department,
                    COUNT(a.id) as total_candidates,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hired_count
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.id
                JOIN job_postings jp ON a.job_posting_id = jp.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
                """ + (f" AND jp.department = :department" if department else "") + """
                GROUP BY c.gender, c.ethnicity, jp.department
            """)
            
            params = {"start_date": start_dt, "end_date": end_dt}
            if department:
                params["department"] = department
            
            result = await db.execute(diversity_query, params)
            
            metrics = []
            diversity_by_department = {}
            
            for row in result:
                # Gender metrics
                if row.gender:
                    percentage = (row.hired_count / row.total_candidates * 100) if row.total_candidates > 0 else 0
                    metrics.append(DiversityMetric(
                        dimension="gender",
                        category=row.gender,
                        total_candidates=row.total_candidates,
                        hired_count=row.hired_count,
                        percentage=percentage
                    ))
                
                # Ethnicity metrics
                if row.ethnicity:
                    percentage = (row.hired_count / row.total_candidates * 100) if row.total_candidates > 0 else 0
                    metrics.append(DiversityMetric(
                        dimension="ethnicity",
                        category=row.ethnicity,
                        total_candidates=row.total_candidates,
                        hired_count=row.hired_count,
                        percentage=percentage
                    ))
                
                # Department aggregation
                dept = row.department
                if dept not in diversity_by_department:
                    diversity_by_department[dept] = {
                        "department": dept,
                        "total_candidates": 0,
                        "total_hires": 0,
                        "diversity_score": 0
                    }
                
                diversity_by_department[dept]["total_candidates"] += row.total_candidates
                diversity_by_department[dept]["total_hires"] += row.hired_count
            
            # Calculate overall diversity score (simplified)
            total_candidates = sum(m.total_candidates for m in metrics)
            diversity_score = len(set(m.category for m in metrics)) / len(metrics) * 100 if metrics else 0
            
            # Generate recommendations
            recommendations = []
            if diversity_score < 60:
                recommendations.append("Consider expanding recruitment channels to increase diversity")
            if any(m.percentage < 20 for m in metrics if m.dimension == "gender"):
                recommendations.append("Focus on gender balance in hiring process")
            
            return DiversityReportResponse(
                overall_diversity_score=diversity_score,
                diversity_by_department=list(diversity_by_department.values()),
                diversity_trends=[],  # TODO: Implement trending analysis
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error calculating diversity metrics: {e}")
            raise
    
    async def get_ahp_performance_metrics(
        self,
        db: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> AhpPerformanceResponse:
        """Get AHP model performance metrics"""
        
        try:
            # Parse dates
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
            start_dt = datetime.fromisoformat(start_date) if start_date else end_dt - timedelta(days=30)
            
            # Get AHP performance data
            perf_query = text("""
                SELECT 
                    cs.job_posting_id,
                    COUNT(*) as total_predictions,
                    COUNT(CASE WHEN wi.current_stage = 'hired' AND cs.score > 0.7 THEN 1 END) as successful_hires,
                    AVG(cs.score) as avg_prediction_confidence
                FROM candidate_scores cs
                JOIN applications a ON cs.candidate_id = a.candidate_id AND cs.job_posting_id = a.job_posting_id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE cs.created_at BETWEEN :start_date AND :end_date
                """ + (f" AND cs.job_posting_id = :job_id" if job_id else "") + """
                GROUP BY cs.job_posting_id
            """)
            
            params = {"start_date": start_dt, "end_date": end_dt}
            if job_id:
                params["job_id"] = job_id
            
            result = await db.execute(perf_query, params)
            
            total_predictions = 0
            successful_hires = 0
            avg_confidence = 0
            performance_by_job = []
            
            for row in result:
                total_predictions += row.total_predictions
                successful_hires += row.successful_hires or 0
                
                job_accuracy = (row.successful_hires / row.total_predictions * 100) if row.total_predictions > 0 else 0
                performance_by_job.append({
                    "job_id": row.job_posting_id,
                    "total_predictions": row.total_predictions,
                    "successful_hires": row.successful_hires or 0,
                    "accuracy_rate": job_accuracy,
                    "avg_confidence": float(row.avg_prediction_confidence or 0)
                })
            
            # Calculate overall metrics
            accuracy_rate = (successful_hires / total_predictions * 100) if total_predictions > 0 else 0
            
            # Simplified precision, recall, F1 calculation
            precision_score = accuracy_rate  # Simplified
            recall_score = accuracy_rate     # Simplified  
            f1_score = (2 * precision_score * recall_score / (precision_score + recall_score)) if (precision_score + recall_score) > 0 else 0
            
            avg_prediction_confidence = sum(p["avg_confidence"] for p in performance_by_job) / len(performance_by_job) if performance_by_job else 0
            
            return AhpPerformanceResponse(
                total_predictions=total_predictions,
                successful_hires=successful_hires,
                accuracy_rate=accuracy_rate,
                precision_score=precision_score,
                recall_score=recall_score,
                f1_score=f1_score,
                avg_prediction_confidence=avg_prediction_confidence,
                performance_by_job=performance_by_job,
                model_drift_indicators=[]  # TODO: Implement drift detection
            )
            
        except Exception as e:
            logger.error(f"Error calculating AHP performance metrics: {e}")
            raise
