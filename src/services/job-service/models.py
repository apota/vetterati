from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, DECIMAL
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    requirements = Column(Text)
    responsibilities = Column(Text)
    benefits = Column(Text)
    
    # Job Details
    department = Column(String(100), index=True)
    location = Column(String(200))
    employment_type = Column(String(50))  # full-time, part-time, contract, internship
    experience_level = Column(String(50))  # entry, mid, senior, executive
    salary_min = Column(DECIMAL(10, 2))
    salary_max = Column(DECIMAL(10, 2))
    salary_currency = Column(String(3), default='USD')
    
    # Status and Workflow
    status = Column(String(50), default='draft', index=True)  # draft, active, paused, closed
    priority = Column(String(20), default='medium')  # low, medium, high, urgent
    
    # Skills and Requirements
    required_skills = Column(ARRAY(String))
    preferred_skills = Column(ARRAY(String))
    certifications = Column(ARRAY(String))
    languages = Column(ARRAY(String))
    
    # AHP Configuration
    ahp_hierarchy_id = Column(UUID(as_uuid=True))
    ideal_profiles = Column(JSON)  # Array of profile configurations
    scoring_weights = Column(JSON)  # Custom scoring weights
    
    # SEO and Marketing
    slug = Column(String(250), unique=True, index=True)
    seo_title = Column(String(200))
    seo_description = Column(Text)
    keywords = Column(ARRAY(String))
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    posted_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    
    # External integrations
    external_job_board_ids = Column(JSON)  # IDs from various job boards
    
    # Relationships
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Application Details
    status = Column(String(50), default='applied', index=True)  # applied, screening, interview, offer, rejected, withdrawn
    source = Column(String(100))  # website, linkedin, referral, etc.
    cover_letter = Column(Text)
    
    # AHP Scoring
    ahp_score = Column(DECIMAL(5, 2))
    ahp_breakdown = Column(JSON)  # Detailed scoring breakdown
    
    # Tracking
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applications")

class JobTemplate(Base):
    __tablename__ = "job_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_data = Column(JSON)  # Reusable job posting template
    category = Column(String(100))
    
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class JobView(Base):
    __tablename__ = "job_views"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Viewer Information
    visitor_id = Column(String(100))  # Anonymous visitor tracking
    user_id = Column(UUID(as_uuid=True))  # Logged in user
    ip_address = Column(String(45))
    user_agent = Column(Text)
    referrer = Column(String(500))
    
    # Viewing Details
    viewed_at = Column(DateTime(timezone=True), server_default=func.now())
    session_duration = Column(Integer)  # seconds
    
    job = relationship("Job")
