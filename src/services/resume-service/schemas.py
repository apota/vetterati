from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class CompanySize(str, Enum):
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"

class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None

class Experience(BaseModel):
    company: str
    position: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    skills: List[str] = []
    achievements: List[str] = []
    company_size: Optional[CompanySize] = None
    industry: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: str
    field: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    honors: List[str] = []
    prestige: Optional[float] = None

class TechnicalSkill(BaseModel):
    name: str
    level: ExperienceLevel
    years_of_experience: Optional[float] = None
    last_used: Optional[datetime] = None

class Certification(BaseModel):
    name: str
    issuer: str
    date_obtained: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    verification_url: Optional[str] = None

class Skills(BaseModel):
    technical: List[TechnicalSkill] = []
    soft: List[str] = []
    certifications: List[Certification] = []

class CandidateProfileBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[Location] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    experience: List[Experience] = []
    education: List[Education] = []
    skills: Optional[Skills] = None
    source: Optional[str] = None
    source_details: Optional[Dict[str, Any]] = None

class CandidateProfileCreate(CandidateProfileBase):
    pass

class CandidateProfileResponse(CandidateProfileBase):
    id: str
    total_years_experience: Optional[float] = None
    average_tenure: Optional[float] = None
    career_progression_score: Optional[float] = None
    parsing_confidence: Optional[float] = None
    parsing_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    id: str
    filename: str
    status: str
    message: str

class CandidateSearchRequest(BaseModel):
    query: Optional[str] = None
    skills: List[str] = []
    experience_years_min: Optional[int] = None
    experience_years_max: Optional[int] = None
    location: Optional[str] = None
    education_level: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

class CandidateSearchHit(BaseModel):
    id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    total_years_experience: Optional[float] = None
    skills: Optional[Skills] = None
    score: float

class CandidateSearchResponse(BaseModel):
    candidates: List[CandidateSearchHit]
    total: int
    page: int
    size: int
    pages: int
