from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    location = Column(JSON)  # {city, state, country, coordinates}
    linkedin_url = Column(String(500))
    portfolio_url = Column(String(500))
    
    # Professional Summary
    summary = Column(Text)
    
    # Experience and Education (stored as JSON for flexibility)
    experience = Column(JSON)  # Array of experience objects
    education = Column(JSON)   # Array of education objects
    skills = Column(JSON)      # Technical, soft skills, certifications
    
    # Career Metrics
    total_years_experience = Column(Float)
    average_tenure = Column(Float)
    career_progression_score = Column(Float)
    
    # ATS Metadata
    source = Column(String(100))  # web, email, api, etc.
    source_details = Column(JSON)
    
    # Parsing Information
    parsing_confidence = Column(Float)
    parsing_metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship("ResumeFile", back_populates="candidate")

class ResumeFile(Base):
    __tablename__ = "resume_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidate_profiles.id"), nullable=True)
    
    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    content_type = Column(String(100))
    file_hash = Column(String(64))  # SHA-256 hash for deduplication
    
    # Processing Status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text)
    
    # Extracted Content
    raw_text = Column(Text)
    parsed_data = Column(JSON)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    candidate = relationship("CandidateProfile", back_populates="resumes")
