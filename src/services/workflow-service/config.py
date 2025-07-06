from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql+asyncpg://ats_user:ats_password@postgres:5432/vetterati_ats"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://ats_user:ats_password@rabbitmq:5672"
    
    # Service URLs
    auth_service_url: str = "http://auth-service"
    resume_service_url: str = "http://resume-service:8000"
    ahp_service_url: str = "http://ahp-service"
    
    # Workflow settings
    default_workflow_timeout_hours: int = 72
    interview_reminder_hours: int = 24
    
    # Email settings
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    
    # Calendar integration
    calendar_provider: str = "google"  # google, outlook, etc.
    calendar_api_key: str = ""
    
    # Security
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
