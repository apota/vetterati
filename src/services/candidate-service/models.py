from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    
    # Location information
    location_city = Column(String(100))
    location_state = Column(String(50))
    location_country = Column(String(50))
    location_coordinates_lat = Column(Float)
    location_coordinates_lng = Column(Float)
    
    # Social profiles
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    github_url = Column(String(500))
    
    # Career summary
    total_years_experience = Column(Integer, default=0)
    career_level = Column(String(50))  # entry, mid, senior, executive
    current_salary = Column(Integer)
    expected_salary = Column(Integer)
    
    # Profile information
    summary = Column(Text)
    status = Column(String(50), default="active")  # active, inactive, do_not_contact
    source = Column(String(100))  # web, referral, linkedin, etc.
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    experiences = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    educations = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    resumes = relationship("CandidateResume", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="candidate")
    
    def __repr__(self):
        return f"<Candidate(id='{self.id}', email='{self.email}')>"

class CandidateExperience(Base):
    __tablename__ = "candidate_experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    
    company = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    current = Column(Boolean, default=False)
    description = Column(Text)
    location = Column(String(200))
    
    # Skills and achievements
    skills_used = Column(ARRAY(String))
    achievements = Column(ARRAY(Text))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="experiences")

class CandidateEducation(Base):
    __tablename__ = "candidate_educations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    
    institution = Column(String(200), nullable=False)
    degree = Column(String(100))
    field = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    gpa = Column(Float)
    honors = Column(String(200))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="educations")

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # technical, soft, language, certification
    level = Column(String(20))  # beginner, intermediate, advanced, expert
    years_experience = Column(Integer)
    certified = Column(Boolean, default=False)
    certification_name = Column(String(200))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="skills")

class CandidateResume(Base):
    __tablename__ = "candidate_resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    content_type = Column(String(100))
    
    # Parsing information
    parsing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    parsing_confidence = Column(Float)
    extracted_text = Column(Text)
    parsed_data = Column(JSON)
    
    # Metadata
    upload_source = Column(String(100))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), nullable=False)  # Reference to Job Service
    
    # Application details
    status = Column(String(50), default="submitted")  # submitted, screening, interviewing, offered, hired, rejected
    source = Column(String(100))  # website, referral, linkedin, etc.
    cover_letter = Column(Text)
    
    # Scoring and evaluation
    overall_score = Column(Float)
    technical_score = Column(Float)
    cultural_score = Column(Float)
    experience_score = Column(Float)
    
    # Stage tracking
    current_stage = Column(String(100))
    stage_updated_at = Column(DateTime(timezone=True))
    
    # Metadata
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
