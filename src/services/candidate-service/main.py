from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db, init_db
from models import Candidate, CandidateExperience, CandidateEducation, CandidateSkill, CandidateResume, JobApplication
from schemas import (
    CandidateCreate, CandidateUpdate, CandidateResponse, CandidateSearchParams,
    ExperienceCreate, ExperienceResponse,
    EducationCreate, EducationResponse,
    SkillCreate, SkillResponse,
    ResumeCreate, ResumeResponse,
    ApplicationCreate, ApplicationResponse,
    CandidateStats
)
from services.candidate_service import CandidateService
from config import get_settings

settings = get_settings()

app = FastAPI(
    title="Candidate Service",
    description="Vetterati Candidate Management Service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "candidate-service"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "candidate-service"}

@app.get("/api/v1/candidates/stats")
async def get_candidate_stats(db: Session = Depends(get_db)):
    """Get candidate statistics"""
    candidate_service = CandidateService(db)
    stats = candidate_service.get_candidate_stats()
    
    return {"success": True, "data": stats, "message": "Candidate statistics retrieved successfully"}

@app.get("/api/v1/candidates")
async def get_candidates(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    career_level: Optional[str] = Query(None),
    experience_min: Optional[int] = Query(None, ge=0),
    experience_max: Optional[int] = Query(None, ge=0),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    """Get paginated list of candidates"""
    candidate_service = CandidateService(db)
    
    # Create search params
    search_params = CandidateSearchParams(
        q=q,
        status=status,
        location=location,
        career_level=career_level,
        experience_min=experience_min,
        experience_max=experience_max,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    candidates, total, facets = candidate_service.search_candidates(search_params)
    
    # Format candidates for response
    formatted_candidates = []
    for candidate in candidates:
        # Build location string
        location_parts = []
        if candidate.location_city:
            location_parts.append(candidate.location_city)
        if candidate.location_state:
            location_parts.append(candidate.location_state)
        if candidate.location_country:
            location_parts.append(candidate.location_country)
        
        location_str = ", ".join(location_parts) if location_parts else None
        
        # Count applications (simplified for now)
        applications_count = 0  # TODO: Implement proper application counting when job_applications table is ready
        
        formatted_candidate = {
            "id": str(candidate.id),
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": location_str,
            "status": candidate.status,
            "career_level": candidate.career_level,
            "total_years_experience": candidate.total_years_experience,
            "created_at": candidate.created_at.isoformat(),
            "updated_at": candidate.updated_at.isoformat() if candidate.updated_at else None,
            "applications_count": applications_count,
            "latest_application_status": None  # TODO: Implement when needed
        }
        
        formatted_candidates.append(formatted_candidate)
    
    return {
        "success": True,
        "data": {
            "items": formatted_candidates,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "facets": facets
        },
        "message": "Candidates retrieved successfully"
    }

@app.get("/api/v1/candidates/{candidate_id}")
async def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Get candidate by ID"""
    try:
        candidate_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")
    
    candidate_service = CandidateService(db)
    candidate = candidate_service.get_candidate(candidate_uuid)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {"success": True, "data": candidate, "message": "Candidate retrieved successfully"}

@app.post("/api/v1/candidates")
async def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db)
):
    """Create a new candidate"""
    candidate_service = CandidateService(db)
    candidate = candidate_service.create_candidate(candidate_data)
    
    return {"success": True, "data": candidate, "message": "Candidate created successfully"}

@app.put("/api/v1/candidates/{candidate_id}")
async def update_candidate(
    candidate_id: str,
    candidate_data: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """Update a candidate"""
    try:
        candidate_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")
    
    candidate_service = CandidateService(db)
    candidate = candidate_service.update_candidate(candidate_uuid, candidate_data)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {"success": True, "data": candidate, "message": "Candidate updated successfully"}

@app.delete("/api/v1/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str, db: Session = Depends(get_db)):
    """Delete a candidate"""
    try:
        candidate_uuid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")
    
    candidate_service = CandidateService(db)
    success = candidate_service.delete_candidate(candidate_uuid)
    
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {"success": True, "message": "Candidate deleted successfully"}

@app.post("/api/v1/candidates/search")
async def search_candidates(
    search_params: CandidateSearchParams,
    db: Session = Depends(get_db)
):
    """Search candidates with advanced filters"""
    candidate_service = CandidateService(db)
    candidates, total, facets = candidate_service.search_candidates(search_params)
    
    return {
        "success": True,
        "data": {
            "items": candidates,
            "total": total,
            "facets": facets
        },
        "message": "Candidates search completed successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
