import pytest
import asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Import the models and services
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "services" / "job-service"))

from database import Base
from models import Job, JobTemplate
from services.job_service import JobService
from main import app
import schemas

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_job_service.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    from main import get_db
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

class TestJobService:
    def test_create_job(self, db):
        service = JobService(db)
        
        job_data = schemas.JobCreate(
            title="Software Engineer",
            description="We are looking for a skilled software engineer...",
            department="Engineering",
            location="San Francisco, CA",
            employment_type="full_time",
            experience_level="mid",
            salary_range_min=80000,
            salary_range_max=120000,
            required_skills=["Python", "JavaScript", "SQL"],
            preferred_skills=["React", "Docker"],
            requirements=["Bachelor's degree in Computer Science", "3+ years experience"],
            status="active",
            created_by=uuid4()
        )
        
        job = service.create_job(job_data)
        
        assert job.title == "Software Engineer"
        assert job.department == "Engineering"
        assert job.status == "active"
        assert len(job.required_skills) == 3
        assert "Python" in job.required_skills

    def test_get_job(self, db):
        service = JobService(db)
        
        # Create a job first
        job_data = schemas.JobCreate(
            title="Data Scientist",
            description="Data scientist role",
            department="Data",
            location="Remote",
            employment_type="full_time",
            experience_level="senior",
            status="active",
            created_by=uuid4()
        )
        
        created_job = service.create_job(job_data)
        
        # Retrieve the job
        retrieved_job = service.get_job(created_job.id)
        
        assert retrieved_job is not None
        assert retrieved_job.title == "Data Scientist"
        assert retrieved_job.department == "Data"

    def test_search_jobs(self, db):
        service = JobService(db)
        
        # Create multiple jobs
        jobs_data = [
            schemas.JobCreate(
                title="Python Developer",
                description="Python development role",
                department="Engineering",
                location="New York, NY",
                employment_type="full_time",
                experience_level="mid",
                required_skills=["Python", "Django"],
                status="active",
                created_by=uuid4()
            ),
            schemas.JobCreate(
                title="JavaScript Developer", 
                description="Frontend development role",
                department="Engineering",
                location="San Francisco, CA",
                employment_type="full_time",
                experience_level="junior",
                required_skills=["JavaScript", "React"],
                status="active",
                created_by=uuid4()
            ),
            schemas.JobCreate(
                title="Product Manager",
                description="Product management role",
                department="Product",
                location="Los Angeles, CA",
                employment_type="full_time",
                experience_level="senior",
                status="active",
                created_by=uuid4()
            )
        ]
        
        for job_data in jobs_data:
            service.create_job(job_data)
        
        # Test department filter
        engineering_jobs = service.search_jobs(department="Engineering")
        assert len(engineering_jobs.jobs) == 2
        
        # Test skill search
        python_jobs = service.search_jobs(skills=["Python"])
        assert len(python_jobs.jobs) == 1
        assert python_jobs.jobs[0].title == "Python Developer"
        
        # Test location search
        sf_jobs = service.search_jobs(location="San Francisco")
        assert len(sf_jobs.jobs) == 1

    def test_update_job(self, db):
        service = JobService(db)
        
        # Create a job
        job_data = schemas.JobCreate(
            title="DevOps Engineer",
            description="DevOps role",
            department="Engineering",
            location="Austin, TX",
            employment_type="full_time",
            experience_level="mid",
            status="active",
            created_by=uuid4()
        )
        
        job = service.create_job(job_data)
        
        # Update the job
        update_data = schemas.JobUpdate(
            title="Senior DevOps Engineer",
            experience_level="senior",
            salary_range_min=100000,
            salary_range_max=150000
        )
        
        updated_job = service.update_job(job.id, update_data)
        
        assert updated_job is not None
        assert updated_job.title == "Senior DevOps Engineer"
        assert updated_job.experience_level == "senior"
        assert updated_job.salary_range_min == 100000

    def test_job_template_crud(self, db):
        service = JobService(db)
        
        # Create a job template
        template_data = schemas.JobTemplateCreate(
            name="Software Engineer Template",
            description="Standard template for software engineer positions",
            title="Software Engineer",
            description_template="We are seeking a {{ experience_level }} Software Engineer...",
            department="Engineering",
            employment_type="full_time",
            required_skills=["Programming", "Problem Solving"],
            is_active=True,
            created_by=uuid4()
        )
        
        template = service.create_job_template(template_data)
        
        assert template.name == "Software Engineer Template"
        assert template.is_active is True
        
        # Get template
        retrieved_template = service.get_job_template(template.id)
        assert retrieved_template is not None
        
        # Update template
        update_data = schemas.JobTemplateUpdate(
            name="Senior Software Engineer Template",
            is_active=False
        )
        
        updated_template = service.update_job_template(template.id, update_data)
        assert updated_template.name == "Senior Software Engineer Template"
        assert updated_template.is_active is False

class TestJobAPI:
    def test_create_job_endpoint(self, client):
        Base.metadata.create_all(bind=engine)
        
        job_data = {
            "title": "API Test Job",
            "description": "Test job created via API",
            "department": "Testing",
            "location": "Test City",
            "employment_type": "full_time",
            "experience_level": "mid",
            "status": "active",
            "created_by": str(uuid4())
        }
        
        response = client.post("/api/v1/jobs", json=job_data)
        assert response.status_code == 200
        
        job = response.json()
        assert job["title"] == "API Test Job"
        assert job["department"] == "Testing"

    def test_get_jobs_endpoint(self, client):
        Base.metadata.create_all(bind=engine)
        
        response = client.get("/api/v1/jobs")
        assert response.status_code == 200
        
        jobs = response.json()
        assert "jobs" in jobs
        assert "total" in jobs

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        
        health = response.json()
        assert health["status"] == "healthy"
        assert health["service"] == "job-service"
