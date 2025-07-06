from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from database import get_db, init_db
from schemas import (
    HiringMetricsResponse,
    DiversityReportResponse,
    AhpPerformanceResponse,
    CustomReportRequest,
    CustomReportResponse,
    MetricsDashboardResponse,
    PredictiveAnalyticsResponse
)
from services.metrics_service import MetricsService
from services.reporting_service import ReportingService
from services.analytics_service import AnalyticsService
from services.predictive_service import PredictiveService
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Analytics Service...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Analytics Service...")

app = FastAPI(
    title="Analytics Service",
    description="Advanced analytics and reporting for ATS data",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
metrics_service = MetricsService()
reporting_service = ReportingService()
analytics_service = AnalyticsService()
predictive_service = PredictiveService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics"}

# Metrics endpoints
@app.get("/metrics/hiring", response_model=HiringMetricsResponse)
async def get_hiring_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    job_level: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get hiring metrics and KPIs"""
    try:
        metrics = await metrics_service.get_hiring_metrics(
            db, start_date, end_date, department, job_level
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting hiring metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get hiring metrics")

@app.get("/metrics/diversity", response_model=DiversityReportResponse)
async def get_diversity_metrics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get diversity and inclusion metrics"""
    try:
        metrics = await metrics_service.get_diversity_metrics(
            db, start_date, end_date, department
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting diversity metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get diversity metrics")

@app.get("/metrics/ahp-performance", response_model=AhpPerformanceResponse)
async def get_ahp_performance(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    job_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get AHP model performance metrics"""
    try:
        metrics = await metrics_service.get_ahp_performance_metrics(
            db, start_date, end_date, job_id
        )
        return metrics
    except Exception as e:
        logger.error(f"Error getting AHP performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get AHP performance metrics")

@app.get("/dashboard", response_model=MetricsDashboardResponse)
async def get_dashboard_data(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard data with key metrics"""
    try:
        dashboard_data = await analytics_service.get_dashboard_data(db, timeframe)
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

# Reporting endpoints
@app.post("/reports/custom", response_model=CustomReportResponse)
async def generate_custom_report(
    report_request: CustomReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate custom report based on parameters"""
    try:
        report = await reporting_service.generate_custom_report(db, report_request)
        return report
    except Exception as e:
        logger.error(f"Error generating custom report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate custom report")

@app.get("/reports/candidates/funnel")
async def get_candidate_funnel_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    job_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get candidate funnel analysis report"""
    try:
        report = await reporting_service.get_candidate_funnel_report(
            db, start_date, end_date, job_id
        )
        return report
    except Exception as e:
        logger.error(f"Error getting funnel report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get funnel report")

@app.get("/reports/time-to-hire")
async def get_time_to_hire_report(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Get time-to-hire analysis report"""
    try:
        report = await reporting_service.get_time_to_hire_report(
            db, start_date, end_date, department
        )
        return report
    except Exception as e:
        logger.error(f"Error getting time-to-hire report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get time-to-hire report")

# Predictive analytics endpoints
@app.get("/predictions/success-probability/{candidate_id}")
async def get_candidate_success_probability(
    candidate_id: str,
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get probability of candidate success for a job"""
    try:
        probability = await predictive_service.calculate_success_probability(
            db, candidate_id, job_id
        )
        return {"candidate_id": candidate_id, "job_id": job_id, "success_probability": probability}
    except Exception as e:
        logger.error(f"Error calculating success probability: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate success probability")

@app.get("/predictions/trends", response_model=PredictiveAnalyticsResponse)
async def get_hiring_trends(
    forecast_months: int = Query(3, ge=1, le=12),
    db: AsyncSession = Depends(get_db)
):
    """Get hiring trends and forecasts"""
    try:
        trends = await predictive_service.get_hiring_trends(db, forecast_months)
        return trends
    except Exception as e:
        logger.error(f"Error getting hiring trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get hiring trends")

# Export endpoints
@app.get("/export/metrics")
async def export_metrics(
    format: str = Query("csv", regex="^(csv|excel|pdf)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Export metrics data in various formats"""
    try:
        exported_data = await reporting_service.export_metrics_data(
            db, format, start_date, end_date
        )
        return exported_data
    except Exception as e:
        logger.error(f"Error exporting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export metrics")

# Real-time analytics endpoints
@app.get("/realtime/active-workflows")
async def get_active_workflows_count(db: AsyncSession = Depends(get_db)):
    """Get real-time count of active workflows"""
    try:
        count = await analytics_service.get_active_workflows_count(db)
        return {"active_workflows": count, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error getting active workflows count: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get active workflows count")

@app.get("/realtime/interviews-today")
async def get_todays_interviews(db: AsyncSession = Depends(get_db)):
    """Get interviews scheduled for today"""
    try:
        interviews = await analytics_service.get_todays_interviews(db)
        return interviews
    except Exception as e:
        logger.error(f"Error getting today's interviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get today's interviews")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
