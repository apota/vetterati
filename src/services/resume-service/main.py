from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from database import get_db, init_db
from models import CandidateProfile, ResumeFile
from schemas import (
    CandidateProfileResponse, 
    CandidateProfileCreate, 
    CandidateSearchRequest,
    CandidateSearchResponse,
    ResumeUploadResponse
)
from services.resume_parser import ResumeParserService
from services.candidate_service import CandidateService
from services.search_service import SearchService
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Resume Management Service...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Resume Management Service...")

app = FastAPI(
    title="Resume Management Service",
    description="AI-powered resume processing and candidate management system",
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
resume_parser = ResumeParserService()
candidate_service = CandidateService()
search_service = SearchService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "resume-management"}

@app.post("/resumes/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a resume file"""
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        # Save file and create resume record
        resume_file = await candidate_service.save_resume_file(db, file)
        
        # Process resume in background
        background_tasks.add_task(
            process_resume_background,
            resume_file.id,
            file
        )
        
        return ResumeUploadResponse(
            id=resume_file.id,
            filename=resume_file.filename,
            status="processing",
            message="Resume uploaded successfully and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload resume")

async def process_resume_background(resume_id: str, file: UploadFile):
    """Background task to process uploaded resume"""
    try:
        # Parse resume content
        parsed_data = await resume_parser.parse_resume(file)
        
        # Create candidate profile
        async with get_db() as db:
            candidate = await candidate_service.create_candidate_from_resume(
                db, resume_id, parsed_data
            )
            
            # Index in Elasticsearch
            await search_service.index_candidate(candidate)
            
        logger.info(f"Successfully processed resume {resume_id}")
        
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {str(e)}")

@app.post("/candidates", response_model=CandidateProfileResponse)
async def create_candidate(
    candidate_data: CandidateProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate profile manually"""
    try:
        candidate = await candidate_service.create_candidate(db, candidate_data)
        await search_service.index_candidate(candidate)
        return candidate
    except Exception as e:
        logger.error(f"Error creating candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create candidate")

@app.get("/candidates/{candidate_id}", response_model=CandidateProfileResponse)
async def get_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get candidate profile by ID"""
    candidate = await candidate_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@app.get("/candidates", response_model=List[CandidateProfileResponse])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all candidates with pagination"""
    candidates = await candidate_service.list_candidates(db, skip, limit)
    return candidates

@app.post("/candidates/search", response_model=CandidateSearchResponse)
async def search_candidates(search_request: CandidateSearchRequest):
    """Search candidates using Elasticsearch"""
    try:
        results = await search_service.search_candidates(search_request)
        return results
    except Exception as e:
        logger.error(f"Error searching candidates: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@app.put("/candidates/{candidate_id}", response_model=CandidateProfileResponse)
async def update_candidate(
    candidate_id: str,
    candidate_data: CandidateProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update candidate profile"""
    try:
        candidate = await candidate_service.update_candidate(db, candidate_id, candidate_data)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        await search_service.index_candidate(candidate)
        return candidate
    except Exception as e:
        logger.error(f"Error updating candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update candidate")

@app.delete("/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete candidate profile"""
    try:
        success = await candidate_service.delete_candidate(db, candidate_id)
        if not success:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        await search_service.remove_candidate(candidate_id)
        return {"message": "Candidate deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete candidate")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
