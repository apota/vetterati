import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://ats_user:ats_password@postgres:5432/vetterati_ats"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # Elasticsearch
    elasticsearch_url: str = "http://elasticsearch:9200"
    
    # Service
    service_name: str = "job-service"
    service_version: str = "1.0.0"
    debug: bool = True
    
    # Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # File Storage
    upload_dir: str = "/app/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # External Services
    auth_service_url: str = "http://auth-service:80"
    resume_service_url: str = "http://resume-service:8000"
    ahp_service_url: str = "http://ahp-service:80"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

def get_settings():
    return settings
