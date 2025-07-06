from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
import json
import logging

from models import GeneratedReport, ReportTemplate
from schemas import CustomReportRequest, CustomReportResponse

logger = logging.getLogger(__name__)

class ReportingService:
    """Service for generating and managing reports"""
    
    async def generate_custom_report(
        self,
        db: AsyncSession,
        report_request: CustomReportRequest
    ) -> CustomReportResponse:
        """Generate a custom report based on request parameters"""
        
        try:
            # Build dynamic query based on request
            data = await self._build_report_data(db, report_request)
            
            # Calculate summary statistics
            summary_stats = await self._calculate_summary_statistics(data)
            
            # Generate charts if requested
            charts = None
            if report_request.include_charts:
                charts = await self._generate_charts(data, report_request.metrics)
            
            # Save report metadata
            report_id = await self._save_report_metadata(db, report_request, len(data))
            
            return CustomReportResponse(
                report_id=report_id,
                report_name=report_request.report_name,
                data=data,
                summary_statistics=summary_stats,
                charts=charts
            )
            
        except Exception as e:
            logger.error(f"Error generating custom report: {e}")
            raise
    
    async def _build_report_data(
        self,
        db: AsyncSession,
        request: CustomReportRequest
    ) -> List[Dict[str, Any]]:
        """Build report data based on request parameters"""
        
        # Base query mapping
        base_queries = {
            "hiring_metrics": """
                SELECT 
                    jp.title as job_title,
                    jp.department,
                    jp.job_level,
                    COUNT(a.id) as total_applications,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as total_hires,
                    AVG(CASE WHEN wi.current_stage = 'hired' 
                        THEN EXTRACT(DAY FROM (wi.updated_at - a.created_at)) END) as avg_time_to_hire
                FROM applications a
                JOIN job_postings jp ON a.job_posting_id = jp.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
            """,
            "diversity_report": """
                SELECT 
                    c.gender,
                    c.ethnicity,
                    c.age_range,
                    jp.department,
                    COUNT(a.id) as total_candidates,
                    COUNT(CASE WHEN wi.current_stage = 'hired' THEN 1 END) as hired_count
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.id
                JOIN job_postings jp ON a.job_posting_id = jp.id
                LEFT JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE a.created_at BETWEEN :start_date AND :end_date
            """,
            "candidate_funnel": """
                SELECT 
                    jp.title as job_title,
                    wi.current_stage,
                    COUNT(*) as candidate_count,
                    AVG(EXTRACT(DAY FROM (wi.updated_at - wi.created_at))) as avg_days_in_stage
                FROM workflow_instances wi
                JOIN applications a ON wi.application_id = a.id
                JOIN job_postings jp ON a.job_posting_id = jp.id
                WHERE wi.created_at BETWEEN :start_date AND :end_date
            """
        }
        
        # Get base query
        base_query = base_queries.get(request.report_type.value, base_queries["hiring_metrics"])
        
        # Add filters
        filter_conditions = []
        params = {
            "start_date": request.date_range["start"],
            "end_date": request.date_range["end"]
        }
        
        for key, value in request.filters.items():
            if key == "department":
                filter_conditions.append("jp.department = :department")
                params["department"] = value
            elif key == "job_level":
                filter_conditions.append("jp.job_level = :job_level")
                params["job_level"] = value
            elif key == "job_id":
                filter_conditions.append("jp.id = :job_id")
                params["job_id"] = value
        
        if filter_conditions:
            base_query += " AND " + " AND ".join(filter_conditions)
        
        # Add GROUP BY
        if request.groupby_fields:
            group_fields = []
            for field in request.groupby_fields:
                if field == "department":
                    group_fields.append("jp.department")
                elif field == "job_level":
                    group_fields.append("jp.job_level")
                elif field == "job_title":
                    group_fields.append("jp.title")
                elif field == "stage":
                    group_fields.append("wi.current_stage")
            
            if group_fields:
                base_query += " GROUP BY " + ", ".join(group_fields)
        
        # Execute query
        result = await db.execute(text(base_query), params)
        
        # Convert to list of dictionaries
        data = []
        for row in result:
            row_dict = {}
            for key, value in row._mapping.items():
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
                else:
                    row_dict[key] = value
            data.append(row_dict)
        
        return data
    
    async def _calculate_summary_statistics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for the report data"""
        
        if not data:
            return {}
        
        # Convert to DataFrame for easier calculation
        df = pd.DataFrame(data)
        
        summary = {
            "total_records": len(data),
            "numeric_stats": {}
        }
        
        # Calculate stats for numeric columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_columns:
            summary["numeric_stats"][col] = {
                "mean": float(df[col].mean()) if not df[col].isna().all() else 0,
                "median": float(df[col].median()) if not df[col].isna().all() else 0,
                "min": float(df[col].min()) if not df[col].isna().all() else 0,
                "max": float(df[col].max()) if not df[col].isna().all() else 0,
                "sum": float(df[col].sum()) if not df[col].isna().all() else 0
            }
        
        return summary
    
    async def _generate_charts(self, data: List[Dict[str, Any]], metrics: List[str]) -> List[Dict[str, Any]]:
        """Generate chart configurations for the report"""
        
        if not data:
            return []
        
        charts = []
        df = pd.DataFrame(data)
        
        # Generate different chart types based on data
        for metric in metrics:
            if metric in df.columns:
                if df[metric].dtype in ['int64', 'float64']:
                    # Histogram for numeric data
                    charts.append({
                        "type": "histogram",
                        "title": f"Distribution of {metric}",
                        "data": {
                            "values": df[metric].dropna().tolist(),
                            "bins": 10
                        }
                    })
                else:
                    # Bar chart for categorical data
                    value_counts = df[metric].value_counts().head(10)
                    charts.append({
                        "type": "bar",
                        "title": f"Top 10 {metric}",
                        "data": {
                            "labels": value_counts.index.tolist(),
                            "values": value_counts.values.tolist()
                        }
                    })
        
        return charts
    
    async def _save_report_metadata(
        self,
        db: AsyncSession,
        request: CustomReportRequest,
        record_count: int
    ) -> str:
        """Save report metadata to database"""
        
        import uuid
        report_id = str(uuid.uuid4())
        
        # Create report record
        report = GeneratedReport(
            id=report_id,
            report_name=request.report_name,
            report_type=request.report_type.value,
            parameters=request.dict(),
            generated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)  # 30 day expiry
        )
        
        db.add(report)
        await db.commit()
        
        return report_id
    
    async def get_candidate_funnel_report(
        self,
        db: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get candidate funnel analysis report"""
        
        try:
            # Parse dates
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
            start_dt = datetime.fromisoformat(start_date) if start_date else end_dt - timedelta(days=30)
            
            # Funnel analysis query
            funnel_query = text("""
                WITH stage_counts AS (
                    SELECT 
                        wi.current_stage,
                        COUNT(*) as candidate_count,
                        AVG(EXTRACT(DAY FROM (wi.updated_at - wi.created_at))) as avg_days_in_stage
                    FROM workflow_instances wi
                    JOIN applications a ON wi.application_id = a.id
                    WHERE wi.created_at BETWEEN :start_date AND :end_date
                    """ + (f" AND a.job_posting_id = :job_id" if job_id else "") + """
                    GROUP BY wi.current_stage
                ),
                stage_order AS (
                    SELECT stage, ROW_NUMBER() OVER (ORDER BY 
                        CASE stage 
                            WHEN 'applied' THEN 1
                            WHEN 'screening' THEN 2
                            WHEN 'phone_interview' THEN 3
                            WHEN 'technical_interview' THEN 4
                            WHEN 'final_interview' THEN 5
                            WHEN 'offer' THEN 6
                            WHEN 'hired' THEN 7
                            ELSE 8
                        END
                    ) as stage_order
                    FROM (SELECT DISTINCT current_stage as stage FROM stage_counts) s
                )
                SELECT 
                    sc.current_stage,
                    sc.candidate_count,
                    sc.avg_days_in_stage,
                    so.stage_order,
                    LAG(sc.candidate_count) OVER (ORDER BY so.stage_order) as previous_stage_count
                FROM stage_counts sc
                JOIN stage_order so ON sc.current_stage = so.stage
                ORDER BY so.stage_order
            """)
            
            params = {"start_date": start_dt, "end_date": end_dt}
            if job_id:
                params["job_id"] = job_id
            
            result = await db.execute(funnel_query, params)
            
            funnel_data = []
            for row in result:
                conversion_rate = 0
                if row.previous_stage_count and row.previous_stage_count > 0:
                    conversion_rate = (row.candidate_count / row.previous_stage_count) * 100
                
                funnel_data.append({
                    "stage": row.current_stage,
                    "candidate_count": row.candidate_count,
                    "avg_days_in_stage": float(row.avg_days_in_stage or 0),
                    "conversion_rate": conversion_rate
                })
            
            return {
                "funnel_data": funnel_data,
                "total_candidates": sum(stage["candidate_count"] for stage in funnel_data),
                "overall_conversion_rate": (funnel_data[-1]["candidate_count"] / funnel_data[0]["candidate_count"] * 100) if funnel_data else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating funnel report: {e}")
            raise
    
    async def get_time_to_hire_report(
        self,
        db: AsyncSession,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        department: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get time-to-hire analysis report"""
        
        try:
            # Parse dates
            end_dt = datetime.fromisoformat(end_date) if end_date else datetime.utcnow()
            start_dt = datetime.fromisoformat(start_date) if start_date else end_dt - timedelta(days=30)
            
            # Time to hire query
            query = text("""
                SELECT 
                    jp.department,
                    jp.job_level,
                    jp.title as job_title,
                    EXTRACT(DAY FROM (wi.updated_at - a.created_at)) as time_to_hire_days
                FROM applications a
                JOIN job_postings jp ON a.job_posting_id = jp.id
                JOIN workflow_instances wi ON a.id = wi.application_id
                WHERE wi.current_stage = 'hired'
                    AND a.created_at BETWEEN :start_date AND :end_date
                """ + (f" AND jp.department = :department" if department else ""))
            
            params = {"start_date": start_dt, "end_date": end_dt}
            if department:
                params["department"] = department
            
            result = await db.execute(query, params)
            
            # Process results
            time_data = []
            department_stats = {}
            
            for row in result:
                time_data.append({
                    "department": row.department,
                    "job_level": row.job_level,
                    "job_title": row.job_title,
                    "time_to_hire_days": float(row.time_to_hire_days)
                })
                
                # Aggregate by department
                dept = row.department
                if dept not in department_stats:
                    department_stats[dept] = []
                department_stats[dept].append(float(row.time_to_hire_days))
            
            # Calculate statistics by department
            dept_summary = []
            for dept, times in department_stats.items():
                dept_summary.append({
                    "department": dept,
                    "avg_time_to_hire": sum(times) / len(times),
                    "median_time_to_hire": sorted(times)[len(times)//2],
                    "min_time_to_hire": min(times),
                    "max_time_to_hire": max(times),
                    "total_hires": len(times)
                })
            
            return {
                "time_to_hire_data": time_data,
                "department_summary": dept_summary,
                "overall_avg": sum(d["time_to_hire_days"] for d in time_data) / len(time_data) if time_data else 0
            }
            
        except Exception as e:
            logger.error(f"Error generating time-to-hire report: {e}")
            raise
    
    async def export_metrics_data(
        self,
        db: AsyncSession,
        format: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export metrics data in various formats"""
        
        try:
            # This would typically generate files and return download URLs
            # For now, return a mock response
            
            export_id = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            file_url = f"/exports/{export_id}.{format}"
            
            return {
                "export_id": export_id,
                "file_url": file_url,
                "format": format,
                "status": "completed",
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error exporting metrics data: {e}")
            raise
