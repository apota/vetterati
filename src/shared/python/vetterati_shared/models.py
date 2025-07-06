from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    EXPIRED = "expired"

class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    SCREENING = "screening"
    PHONE_INTERVIEW = "phone_interview"
    TECHNICAL_INTERVIEW = "technical_interview"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class InterviewType(str, Enum):
    PHONE = "phone"
    VIDEO = "video"
    IN_PERSON = "in_person"
    TECHNICAL = "technical"

class CandidateBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    current_company: Optional[str] = Field(None, max_length=200)
    current_position: Optional[str] = Field(None, max_length=200)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    education_level: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = Field(default_factory=list)
    source: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    salary_expectation: Optional[int] = Field(None, ge=0)
    availability: Optional[str] = Field(None, max_length=100)

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    current_company: Optional[str] = Field(None, max_length=200)
    current_position: Optional[str] = Field(None, max_length=200)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    education_level: Optional[str] = Field(None, max_length=100)
    skills: Optional[List[str]] = None
    source: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    salary_expectation: Optional[int] = Field(None, ge=0)
    availability: Optional[str] = Field(None, max_length=100)

class CandidateResponse(CandidateBase):
    id: str
    created_at: datetime
    updated_at: datetime

class JobPostingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    department: str = Field(..., min_length=1, max_length=100)
    location: str = Field(..., min_length=1, max_length=200)
    job_type: str = Field(..., max_length=50)  # full_time, part_time, contract
    job_level: str = Field(..., max_length=50)  # entry, mid, senior, executive
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    required_experience: Optional[int] = Field(None, ge=0, le=50)
    required_education: Optional[str] = Field(None, max_length=100)
    required_skills: Optional[List[str]] = Field(default_factory=list)
    nice_to_have_skills: Optional[List[str]] = Field(default_factory=list)
    benefits: Optional[List[str]] = Field(default_factory=list)
    remote_friendly: bool = Field(default=False)
    visa_sponsorship: bool = Field(default=False)

class JobPostingCreate(JobPostingBase):
    hiring_manager_id: str
    expires_at: Optional[datetime] = None

class JobPostingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    department: Optional[str] = Field(None, min_length=1, max_length=100)
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    job_type: Optional[str] = Field(None, max_length=50)
    job_level: Optional[str] = Field(None, max_length=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    required_experience: Optional[int] = Field(None, ge=0, le=50)
    required_education: Optional[str] = Field(None, max_length=100)
    required_skills: Optional[List[str]] = None
    nice_to_have_skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    remote_friendly: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    status: Optional[JobStatus] = None
    expires_at: Optional[datetime] = None

class JobPostingResponse(JobPostingBase):
    id: str
    hiring_manager_id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]

class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    additional_notes: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    candidate_id: str
    job_posting_id: str

class ApplicationUpdate(BaseModel):
    cover_letter: Optional[str] = None
    additional_notes: Optional[str] = None
    status: Optional[ApplicationStatus] = None

class ApplicationResponse(ApplicationBase):
    id: str
    candidate_id: str
    job_posting_id: str
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime

class InterviewBase(BaseModel):
    interview_type: InterviewType
    scheduled_at: datetime
    duration_minutes: int = Field(default=60, ge=15, le=480)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    interviewer_email: str

class InterviewCreate(InterviewBase):
    application_id: str

class InterviewUpdate(BaseModel):
    interview_type: Optional[InterviewType] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=480)
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None
    interviewer_email: Optional[str] = None
    status: Optional[str] = None

class InterviewResponse(InterviewBase):
    id: str
    application_id: str
    status: str
    created_at: datetime
    updated_at: datetime

# API Response wrappers
class ApiResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    details: Optional[Dict[str, Any]] = None
