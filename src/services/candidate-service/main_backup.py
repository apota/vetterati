from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db, init_db
from models import Candidate, CandidateExperience, CandidateEducation, CandidateSkill, CandidateResume, JobApplication
from schemas import (
    CandidateCreate, CandidateUpdate, CandidateResponse,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
