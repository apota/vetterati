from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging

from schemas import MetricsDashboardResponse

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Main analytics service for dashboard and real-time data"""
    
    async def get_dashboard_data(
        self,
        db: AsyncSession,
        timeframe: str = "30d"
    ) -> MetricsDashboardResponse:
        """Get comprehensive dashboard data"""
        
        try:
            # Calculate date range based on timeframe
            end_date = datetime.utcnow()
            if timeframe == "7d":
                start_date = end_date - timedelta(days=7)
            elif timeframe == "30d":
                start_date = end_date - timedelta(days=30)
            elif timeframe == "90d":
                start_date = end_date - timedelta(days=90)
            elif timeframe == "1y":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get active job postings
            active_jobs_query = text("""
                SELECT COUNT(*) as active_jobs
                FROM job_postings 
                WHERE status = 'active' AND expires_at > NOW()
            """)
            result = await db.execute(active_jobs_query)
            active_job_postings = result.scalar() or 0
            
            # Get total applications this period
            apps_query = text("""
                SELECT COUNT(*) as total_apps
                FROM applications 
                WHERE created_at BETWEEN :start_date AND :end_date
            """)
            result = await db.execute(apps_query, {"start_date": start_date, "end_date": end_date})
            total_applications_this_month = result.scalar() or 0
            
            # Get scheduled interviews
            interviews_query = text("""
                SELECT COUNT(*) as scheduled_interviews
                FROM interviews 
                WHERE scheduled_at > NOW() AND status = 'scheduled'
            """)
            result = await db.execute(interviews_query)
            interviews_scheduled = result.scalar() or 0
            
            # Get offers extended
            offers_query = text("""
                SELECT COUNT(*) as offers_extended
                FROM workflow_instances 
                WHERE current_stage = 'offer' 
                    AND updated_at BETWEEN :start_date AND :end_date
            """)
            result = await db.execute(offers_query, {"start_date": start_date, "end_date": end_date})
            offers_extended = result.scalar() or 0
            
            # Get hires this period
            hires_query = text("""
                SELECT COUNT(*) as hires_count
                FROM workflow_instances 
                WHERE current_stage = 'hired' 
                    AND updated_at BETWEEN :start_date AND :end_date
            """)
            result = await db.execute(hires_query, {"start_date": start_date, "end_date": end_date})
            hires_this_month = result.scalar() or 0
            
            # Get average time to hire
            time_to_hire_query = text("""
                SELECT AVG(EXTRACT(DAY FROM (wi.updated_at - a.created_at))) as avg_time
                FROM applications a
                JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE wi.current_stage = 'hired'
                    AND wi.updated_at BETWEEN :start_date AND :end_date
            """)
            result = await db.execute(time_to_hire_query, {"start_date": start_date, "end_date": end_date})
            avg_time_to_hire = float(result.scalar() or 0)
            
            # Get top performing sources
            sources_query = text("""
                SELECT 
                    c.source,
                    COUNT(a.id) as application_count,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hire_count
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
                GROUP BY c.source
                ORDER BY hire_count DESC, application_count DESC
                LIMIT 5
            """)
            result = await db.execute(sources_query, {"start_date": start_date, "end_date": end_date})
            
            top_performing_sources = []
            for row in result:
                conversion_rate = (row.hire_count / row.application_count * 100) if row.application_count > 0 else 0
                top_performing_sources.append({
                    "source": row.source,
                    "applications": row.application_count,
                    "hires": row.hire_count,
                    "conversion_rate": conversion_rate
                })
            
            # Get hiring velocity (weekly breakdown)
            velocity_query = text("""
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
            result = await db.execute(velocity_query, {"start_date": start_date, "end_date": end_date})
            
            hiring_velocity = []
            for row in result:
                hiring_velocity.append({
                    "week": row.week_start.strftime("%Y-%m-%d"),
                    "applications": row.applications,
                    "hires": row.hires
                })
            
            # Get diversity summary
            diversity_query = text("""
                SELECT 
                    c.gender,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hired_count
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
                GROUP BY c.gender
            """)
            result = await db.execute(diversity_query, {"start_date": start_date, "end_date": end_date})
            
            diversity_summary = {}
            total_hires = sum(row.hired_count for row in result)
            
            if total_hires > 0:
                for row in result:
                    if row.gender:
                        diversity_summary[row.gender] = {
                            "count": row.hired_count,
                            "percentage": (row.hired_count / total_hires * 100)
                        }
            
            # Get AHP performance summary
            ahp_query = text("""
                SELECT 
                    COUNT(*) as total_predictions,
                    AVG(score) as avg_score,
                    COUNT(CASE WHEN score > 0.8 THEN 1 END) as high_confidence_predictions
                FROM candidate_scores
                WHERE created_at BETWEEN :start_date AND :end_date
            """)
            result = await db.execute(ahp_query, {"start_date": start_date, "end_date": end_date})
            row = result.first()
            
            ahp_performance_summary = {
                "total_predictions": row.total_predictions if row else 0,
                "avg_confidence": float(row.avg_score or 0) if row else 0,
                "high_confidence_predictions": row.high_confidence_predictions if row else 0
            }
            
            return MetricsDashboardResponse(
                active_job_postings=active_job_postings,
                total_applications_this_month=total_applications_this_month,
                interviews_scheduled=interviews_scheduled,
                offers_extended=offers_extended,
                hires_this_month=hires_this_month,
                avg_time_to_hire=avg_time_to_hire,
                top_performing_sources=top_performing_sources,
                hiring_velocity=hiring_velocity,
                diversity_summary=diversity_summary,
                ahp_performance_summary=ahp_performance_summary
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise
    
    async def get_active_workflows_count(self, db: AsyncSession) -> int:
        """Get real-time count of active workflows"""
        
        try:
            query = text("""
                SELECT COUNT(*) as active_count
                FROM workflow_instances 
                WHERE current_stage NOT IN ('hired', 'rejected', 'withdrawn')
            """)
            result = await db.execute(query)
            return result.scalar() or 0
            
        except Exception as e:
            logger.error(f"Error getting active workflows count: {e}")
            raise
    
    async def get_todays_interviews(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get interviews scheduled for today"""
        
        try:
            today = datetime.utcnow().date()
            query = text("""
                SELECT 
                    i.id as interview_id,
                    c.first_name || ' ' || c.last_name as candidate_name,
                    jp.title as job_title,
                    i.interviewer_email,
                    i.scheduled_at,
                    i.interview_type,
                    i.status
                FROM interviews i
                JOIN applications a ON i.application_id = a.id
                JOIN candidates c ON a.candidate_id = c.id
                JOIN job_postings jp ON a.job_posting_id = jp.id
                WHERE DATE(i.scheduled_at) = :today
                ORDER BY i.scheduled_at
            """)
            
            result = await db.execute(query, {"today": today})
            
            interviews = []
            for row in result:
                interviews.append({
                    "interview_id": row.interview_id,
                    "candidate_name": row.candidate_name,
                    "job_title": row.job_title,
                    "interviewer": row.interviewer_email,
                    "scheduled_time": row.scheduled_at.isoformat(),
                    "type": row.interview_type,
                    "status": row.status
                })
            
            return interviews
            
        except Exception as e:
            logger.error(f"Error getting today's interviews: {e}")
            raise
