from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class CandidateStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    do_not_contact = "do_not_contact"

class CareerLevel(str, Enum):
    entry = "entry"
    mid = "mid"
    senior = "senior"
    executive = "executive"

class SkillLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"

class SkillCategory(str, Enum):
    technical = "technical"
    soft = "soft"
    language = "language"
    certification = "certification"

# Location schemas
class LocationCoordinates(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[LocationCoordinates] = None

# Experience schemas
class ExperienceCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    current: bool = False
    description: Optional[str] = None
    location: Optional[str] = None
    skills_used: Optional[List[str]] = []
    achievements: Optional[List[str]] = []

class ExperienceResponse(ExperienceCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    candidate_id: UUID
    created_at: datetime

# Education schemas
class EducationCreate(BaseModel):
    institution: str = Field(..., min_length=1, max_length=200)
    degree: Optional[str] = None
    field: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    honors: Optional[str] = None

class EducationResponse(EducationCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    candidate_id: UUID
    created_at: datetime

# Skill schemas
class SkillCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[SkillCategory] = SkillCategory.technical
    level: Optional[SkillLevel] = SkillLevel.intermediate
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    certified: bool = False
    certification_name: Optional[str] = None

class SkillResponse(SkillCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    candidate_id: UUID
    created_at: datetime

# Resume schemas
class ResumeCreate(BaseModel):
    filename: str
    file_size: int
    content_type: str
    upload_source: Optional[str] = "web"

class ResumeResponse(ResumeCreate):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    candidate_id: UUID
    original_filename: Optional[str]
    file_path: Optional[str]
    parsing_status: str
    parsing_confidence: Optional[float]
    is_primary: bool
    created_at: datetime

# Candidate schemas
class CandidateCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[Location] = None
    linkedin_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = None
    current_salary: Optional[int] = Field(None, ge=0)
    expected_salary: Optional[int] = Field(None, ge=0)
    source: Optional[str] = "web"
    experience: Optional[List[ExperienceCreate]] = []
    education: Optional[List[EducationCreate]] = []
    skills: Optional[List[SkillCreate]] = []

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    location: Optional[Location] = None
    linkedin_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = None
    current_salary: Optional[int] = Field(None, ge=0)
    expected_salary: Optional[int] = Field(None, ge=0)
    status: Optional[CandidateStatus] = None

class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    location: Optional[Location]
    linkedin_url: Optional[str]
    portfolio_url: Optional[str]
    github_url: Optional[str]
    total_years_experience: int
    career_level: Optional[str]
    current_salary: Optional[int]
    expected_salary: Optional[int]
    summary: Optional[str]
    status: str
    source: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    experiences: List[ExperienceResponse] = []
    educations: List[EducationResponse] = []
    skills: List[SkillResponse] = []
    resumes: List[ResumeResponse] = []

class CandidateSearchResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    location: Optional[Location]
    total_years_experience: int
    career_level: Optional[str]
    current_position: Optional[str]
    key_skills: List[str] = []
    match_score: Optional[float] = None
    highlight: Optional[Dict[str, List[str]]] = None

class CandidateListResponse(BaseModel):
    candidates: List[CandidateSearchResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    facets: Optional[Dict[str, Any]] = None

# Application schemas
class ApplicationCreate(BaseModel):
    job_id: UUID
    source: Optional[str] = "website"
    cover_letter: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    current_stage: Optional[str] = None
    overall_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    technical_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    cultural_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    experience_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    candidate_id: UUID
    job_id: UUID
    status: str
    source: Optional[str]
    cover_letter: Optional[str]
    overall_score: Optional[float]
    technical_score: Optional[float]
    cultural_score: Optional[float]
    experience_score: Optional[float]
    current_stage: Optional[str]
    stage_updated_at: Optional[datetime]
    applied_at: datetime
    updated_at: Optional[datetime]

# Search and filter schemas
class CandidateSearchParams(BaseModel):
    q: Optional[str] = None  # Full-text search
    skills: Optional[str] = None  # Comma-separated skills
    location: Optional[str] = None
    experience_min: Optional[int] = Field(None, ge=0)
    experience_max: Optional[int] = Field(None, ge=0)
    education_level: Optional[str] = None
    company: Optional[str] = None
    career_level: Optional[CareerLevel] = None
    status: Optional[CandidateStatus] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field("relevance", regex="^(relevance|created_at|name|experience)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")

# Statistics schemas
class CandidateStats(BaseModel):
    total_candidates: int
    active_candidates: int
    new_this_month: int
    by_career_level: Dict[str, int]
    by_location: Dict[str, int]
    top_skills: Dict[str, int]
    average_experience: float
