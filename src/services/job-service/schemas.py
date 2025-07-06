from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from enum import Enum
import uuid

class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"

class EmploymentType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

# Job Schemas
class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: str = "USD"
    
    priority: Priority = Priority.MEDIUM
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    
    ahp_hierarchy_id: Optional[uuid.UUID] = None
    ideal_profiles: Optional[Dict[str, Any]] = None
    scoring_weights: Optional[Dict[str, Any]] = None
    
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    keywords: Optional[List[str]] = []

class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    salary_currency: Optional[str] = None
    
    status: Optional[JobStatus] = None
    priority: Optional[Priority] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    
    ahp_hierarchy_id: Optional[uuid.UUID] = None
    ideal_profiles: Optional[Dict[str, Any]] = None
    scoring_weights: Optional[Dict[str, Any]] = None
    
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    keywords: Optional[List[str]] = None

class JobResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    requirements: Optional[str]
    responsibilities: Optional[str]
    benefits: Optional[str]
    
    department: Optional[str]
    location: Optional[str]
    employment_type: Optional[str]
    experience_level: Optional[str]
    salary_min: Optional[Decimal]
    salary_max: Optional[Decimal]
    salary_currency: str
    
    status: str
    priority: str
    slug: Optional[str]
    
    required_skills: Optional[List[str]]
    preferred_skills: Optional[List[str]]
    certifications: Optional[List[str]]
    languages: Optional[List[str]]
    
    ahp_hierarchy_id: Optional[uuid.UUID]
    ideal_profiles: Optional[Dict[str, Any]]
    scoring_weights: Optional[Dict[str, Any]]
    
    seo_title: Optional[str]
    seo_description: Optional[str]
    keywords: Optional[List[str]]
    
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    posted_at: Optional[datetime]
    closed_at: Optional[datetime]
    
    applications_count: Optional[int] = 0
    views_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    id: uuid.UUID
    title: str
    department: Optional[str]
    location: Optional[str]
    employment_type: Optional[str]
    status: str
    priority: str
    applications_count: int = 0
    views_count: int = 0
    created_at: datetime
    posted_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Application Schemas
class JobApplicationCreate(BaseModel):
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    source: Optional[str] = None
    cover_letter: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    cover_letter: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    status: str
    source: Optional[str]
    cover_letter: Optional[str]
    ahp_score: Optional[Decimal]
    ahp_breakdown: Optional[Dict[str, Any]]
    applied_at: datetime
    last_updated: datetime
    
    class Config:
        from_attributes = True

# Template Schemas
class JobTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    template_data: Dict[str, Any]
    category: Optional[str] = None

class JobTemplateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    template_data: Dict[str, Any]
    category: Optional[str]
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Search and Filter Schemas
class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    experience_level: Optional[ExperienceLevel] = None
    status: Optional[JobStatus] = None
    skills: Optional[List[str]] = None
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None
    created_by: Optional[uuid.UUID] = None
    
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    sort_by: str = Field("created_at", regex="^(created_at|updated_at|title|applications_count)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")

# Response Wrappers
class PaginatedResponse(BaseModel):
    data: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

class JobStatsResponse(BaseModel):
    total_jobs: int
    active_jobs: int
    draft_jobs: int
    closed_jobs: int
    total_applications: int
    avg_applications_per_job: float
    top_departments: List[Dict[str, Any]]
    top_locations: List[Dict[str, Any]]
