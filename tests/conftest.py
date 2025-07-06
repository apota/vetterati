import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, patch

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_db_session():
    """Mock database session for testing."""
    session = Mock(spec=AsyncSession)
    session.execute = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session

@pytest.fixture
async def async_client():
    """HTTP client for testing API endpoints."""
    async with AsyncClient() as client:
        yield client

@pytest.fixture
def mock_auth_token():
    """Mock JWT token for authentication testing."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMTIzNDU2Nzg5MCIsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsImV4cCI6MTYwOTQ1OTIwMH0.test_signature"

@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "linkedin_url": "https://linkedin.com/in/johndoe",
        "current_company": "Tech Corp",
        "current_position": "Software Engineer",
        "experience_years": 5,
        "education_level": "bachelors",
        "skills": ["Python", "JavaScript", "React", "SQL"],
        "source": "linkedin",
        "location": "San Francisco, CA",
        "salary_expectation": 120000
    }

@pytest.fixture
def sample_job_posting_data():
    """Sample job posting data for testing."""
    return {
        "title": "Senior Software Engineer",
        "description": "We are looking for an experienced software engineer...",
        "department": "Engineering",
        "location": "San Francisco, CA",
        "job_type": "full_time",
        "job_level": "senior",
        "salary_min": 120000,
        "salary_max": 160000,
        "required_experience": 5,
        "required_education": "bachelors",
        "required_skills": ["Python", "JavaScript", "SQL"],
        "nice_to_have_skills": ["React", "AWS", "Docker"],
        "benefits": ["Health Insurance", "401k", "Remote Work"],
        "remote_friendly": True,
        "visa_sponsorship": False,
        "hiring_manager_id": "manager-123"
    }

@pytest.fixture
def sample_application_data():
    """Sample application data for testing."""
    return {
        "candidate_id": "candidate-123",
        "job_posting_id": "job-123",
        "cover_letter": "I am excited to apply for this position...",
        "additional_notes": "Available to start immediately"
    }
