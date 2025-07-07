from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db, init_db
from models import Candidate, Experience, Education, Skill, Resume, Application
from schemas import (
    CandidateCreate, CandidateUpdate, CandidateResponse,
    ExperienceCreate, ExperienceResponse,
    EducationCreate, EducationResponse,
    SkillCreate, SkillResponse,
    ResumeCreate, ResumeResponse,
    ApplicationCreate, ApplicationResponse,
    CandidateStats, SearchResponse
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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

candidate_service = CandidateService()

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "candidate-service"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "candidate-service"}

# Candidate endpoints
@app.post("/api/v1/candidates", response_model=CandidateResponse)
async def create_candidate(
    candidate: CandidateCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_candidate = await candidate_service.create_candidate(db, candidate)
        # Index in Elasticsearch in background
        background_tasks.add_task(candidate_service.index_candidate, db_candidate.id)
        return db_candidate
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    candidate = await candidate_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@app.put("/api/v1/candidates/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: str,
    candidate: CandidateUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_candidate = await candidate_service.update_candidate(db, candidate_id, candidate)
        if not db_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        # Re-index in Elasticsearch in background
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_candidate
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    success = await candidate_service.delete_candidate(db, candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # Remove from Elasticsearch in background
    background_tasks.add_task(candidate_service.remove_from_index, candidate_id)
    return {"message": "Candidate deleted successfully"}

@app.get("/api/v1/candidates", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    candidates = await candidate_service.list_candidates(db, skip, limit, status, source)
    return candidates

@app.post("/api/v1/candidates/search", response_model=SearchResponse)
async def search_candidates(
    query: str,
    skills: Optional[List[str]] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    location: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        results = await candidate_service.search_candidates(
            query=query,
            skills=skills,
            experience_min=experience_min,
            experience_max=experience_max,
            location=location,
            skip=skip,
            limit=limit
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/stats", response_model=CandidateStats)
async def get_candidate_stats(db: Session = Depends(get_db)):
    try:
        stats = await candidate_service.get_candidate_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Experience endpoints
@app.post("/api/v1/candidates/{candidate_id}/experiences", response_model=ExperienceResponse)
async def add_experience(
    candidate_id: str,
    experience: ExperienceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_experience = await candidate_service.add_experience(db, candidate_id, experience)
        # Re-index candidate in Elasticsearch
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_experience
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/{candidate_id}/experiences", response_model=List[ExperienceResponse])
async def get_candidate_experiences(candidate_id: str, db: Session = Depends(get_db)):
    experiences = await candidate_service.get_candidate_experiences(db, candidate_id)
    return experiences

@app.put("/api/v1/candidates/{candidate_id}/experiences/{experience_id}", response_model=ExperienceResponse)
async def update_experience(
    candidate_id: str,
    experience_id: str,
    experience: ExperienceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_experience = await candidate_service.update_experience(db, experience_id, experience)
        if not db_experience:
            raise HTTPException(status_code=404, detail="Experience not found")
        # Re-index candidate in Elasticsearch
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_experience
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/v1/candidates/{candidate_id}/experiences/{experience_id}")
async def delete_experience(
    candidate_id: str,
    experience_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    success = await candidate_service.delete_experience(db, experience_id)
    if not success:
        raise HTTPException(status_code=404, detail="Experience not found")
    # Re-index candidate in Elasticsearch
    background_tasks.add_task(candidate_service.index_candidate, candidate_id)
    return {"message": "Experience deleted successfully"}

# Education endpoints
@app.post("/api/v1/candidates/{candidate_id}/education", response_model=EducationResponse)
async def add_education(
    candidate_id: str,
    education: EducationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_education = await candidate_service.add_education(db, candidate_id, education)
        # Re-index candidate in Elasticsearch
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_education
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/{candidate_id}/education", response_model=List[EducationResponse])
async def get_candidate_education(candidate_id: str, db: Session = Depends(get_db)):
    education = await candidate_service.get_candidate_education(db, candidate_id)
    return education

# Skills endpoints
@app.post("/api/v1/candidates/{candidate_id}/skills", response_model=SkillResponse)
async def add_skill(
    candidate_id: str,
    skill: SkillCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_skill = await candidate_service.add_skill(db, candidate_id, skill)
        # Re-index candidate in Elasticsearch
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_skill
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/{candidate_id}/skills", response_model=List[SkillResponse])
async def get_candidate_skills(candidate_id: str, db: Session = Depends(get_db)):
    skills = await candidate_service.get_candidate_skills(db, candidate_id)
    return skills

# Resume endpoints
@app.post("/api/v1/candidates/{candidate_id}/resumes", response_model=ResumeResponse)
async def add_resume(
    candidate_id: str,
    resume: ResumeCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_resume = await candidate_service.add_resume(db, candidate_id, resume)
        # Re-index candidate in Elasticsearch
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_resume
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/{candidate_id}/resumes", response_model=List[ResumeResponse])
async def get_candidate_resumes(candidate_id: str, db: Session = Depends(get_db)):
    resumes = await candidate_service.get_candidate_resumes(db, candidate_id)
    return resumes

# Application endpoints
@app.post("/api/v1/candidates/{candidate_id}/applications", response_model=ApplicationResponse)
async def create_application(
    candidate_id: str,
    application: ApplicationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        db_application = await candidate_service.create_application(db, candidate_id, application)
        # Re-index candidate in Elasticsearch
        background_tasks.add_task(candidate_service.index_candidate, candidate_id)
        return db_application
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/candidates/{candidate_id}/applications", response_model=List[ApplicationResponse])
async def get_candidate_applications(candidate_id: str, db: Session = Depends(get_db)):
    applications = await candidate_service.get_candidate_applications(db, candidate_id)
    return applications

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
