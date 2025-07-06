from fastapi import FastAPI, HTTPException, Depends, Query, Path, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from config import settings
from database import get_db, Base, engine
from models import Job, JobApplication, JobTemplate
from schemas import (
    JobCreate, JobUpdate, JobResponse, JobListResponse,
    JobApplicationCreate, JobApplicationResponse,
    JobTemplateCreate, JobTemplateResponse,
    JobSearchRequest, PaginatedResponse, JobStatsResponse
)
from services.job_service import JobService, JobApplicationService, JobTemplateService

# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI app initialization
app = FastAPI(
    title="Vetterati Job Service",
    description="Job management service for the Vetterati ATS platform",
    version=settings.service_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.service_name, "version": settings.service_version}

@app.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service not ready")

# Dependency to get current user (simplified for now)
def get_current_user():
    # TODO: Implement actual JWT token validation
    return {"id": uuid.uuid4(), "email": "user@example.com"}

# Job Management Endpoints
@app.post(f"{settings.api_v1_prefix}/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job posting"""
    try:
        job_service = JobService(db)
        job = job_service.create_job(job_data, current_user["id"])
        
        # Add computed fields
        job.applications_count = 0
        job.views_count = 0
        
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"{settings.api_v1_prefix}/jobs/{{job_id}}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get job by ID"""
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Track job view
    if request:
        visitor_data = {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "referrer": request.headers.get("referer")
        }
        job_service.track_job_view(job_id, visitor_data)
    
    # Add computed fields
    job.applications_count = len(job.applications)
    job.views_count = 0  # TODO: Calculate from job_views table
    
    return job

@app.put(f"{settings.api_v1_prefix}/jobs/{{job_id}}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    job_data: JobUpdate = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update job"""
    job_service = JobService(db)
    job = job_service.update_job(job_id, job_data)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.applications_count = len(job.applications)
    job.views_count = 0
    
    return job

@app.delete(f"{settings.api_v1_prefix}/jobs/{{job_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete job (soft delete)"""
    job_service = JobService(db)
    success = job_service.delete_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get(f"{settings.api_v1_prefix}/jobs", response_model=PaginatedResponse)
async def search_jobs(
    query: Optional[str] = Query(None, description="Search query"),
    department: Optional[str] = Query(None, description="Department filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    employment_type: Optional[str] = Query(None, description="Employment type filter"),
    experience_level: Optional[str] = Query(None, description="Experience level filter"),
    status: Optional[str] = Query(None, description="Status filter"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    db: Session = Depends(get_db)
):
    """Search jobs with filters and pagination"""
    search_request = JobSearchRequest(
        query=query,
        department=department,
        location=location,
        employment_type=employment_type,
        experience_level=experience_level,
        status=status,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    job_service = JobService(db)
    jobs, total = job_service.search_jobs(search_request)
    
    # Convert to list response format
    job_list = []
    for job in jobs:
        job_dict = {
            "id": job.id,
            "title": job.title,
            "department": job.department,
            "location": job.location,
            "employment_type": job.employment_type,
            "status": job.status,
            "priority": job.priority,
            "applications_count": len(job.applications),
            "views_count": 0,  # TODO: Calculate from job_views
            "created_at": job.created_at,
            "posted_at": job.posted_at
        }
        job_list.append(job_dict)
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        data=job_list,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

@app.get(f"{settings.api_v1_prefix}/jobs/stats", response_model=JobStatsResponse)
async def get_job_stats(db: Session = Depends(get_db)):
    """Get job statistics"""
    job_service = JobService(db)
    stats = job_service.get_job_stats()
    return JobStatsResponse(**stats)

@app.post(f"{settings.api_v1_prefix}/jobs/{{job_id}}/publish", response_model=JobResponse)
async def publish_job(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Publish a job (change status from draft to active)"""
    job_service = JobService(db)
    job = job_service.publish_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or cannot be published")
    
    job.applications_count = len(job.applications)
    job.views_count = 0
    
    return job

@app.post(f"{settings.api_v1_prefix}/jobs/{{job_id}}/pause", response_model=JobResponse)
async def pause_job(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Pause an active job"""
    job_service = JobService(db)
    job = job_service.pause_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or cannot be paused")
    
    job.applications_count = len(job.applications)
    job.views_count = 0
    
    return job

# Job Application Endpoints
@app.post(f"{settings.api_v1_prefix}/jobs/{{job_id}}/applications", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    application_data: JobApplicationCreate = None,
    db: Session = Depends(get_db)
):
    """Create a new job application"""
    # Verify job exists
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create application
    application_service = JobApplicationService(db)
    application_dict = application_data.dict()
    application_dict["job_id"] = job_id
    
    application = application_service.create_application(application_dict)
    return application

@app.get(f"{settings.api_v1_prefix}/jobs/{{job_id}}/applications", response_model=PaginatedResponse)
async def get_job_applications(
    job_id: uuid.UUID = Path(..., description="Job ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get applications for a job"""
    application_service = JobApplicationService(db)
    applications, total = application_service.get_applications_for_job(job_id, page, per_page)
    
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        data=applications,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

# Job Template Endpoints
@app.post(f"{settings.api_v1_prefix}/job-templates", response_model=JobTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_job_template(
    template_data: JobTemplateCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job template"""
    template_service = JobTemplateService(db)
    template = template_service.create_template(template_data.dict(), current_user["id"])
    return template

@app.get(f"{settings.api_v1_prefix}/job-templates", response_model=List[JobTemplateResponse])
async def get_job_templates(
    category: Optional[str] = Query(None, description="Category filter"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get job templates"""
    template_service = JobTemplateService(db)
    templates = template_service.get_templates(current_user["id"], category)
    return templates

@app.post(f"{settings.api_v1_prefix}/job-templates/{{template_id}}/create-job", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job_from_template(
    template_id: uuid.UUID = Path(..., description="Template ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new job from a template"""
    template_service = JobTemplateService(db)
    job = template_service.create_job_from_template(template_id, current_user["id"])
    
    if not job:
        raise HTTPException(status_code=404, detail="Template not found")
    
    job.applications_count = 0
    job.views_count = 0
    
    return job

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
