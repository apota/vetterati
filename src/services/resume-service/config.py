from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql+asyncpg://ats_user:ats_password@postgres:5432/vetterati_ats"
    
    # Redis
    redis_url: str = "redis://redis:6379"
    
    # Elasticsearch
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "candidates"
    
    # File Storage
    upload_dir: str = "/app/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # AI/ML Models
    spacy_model: str = "en_core_web_sm"
    
    # Service URLs
    auth_service_url: str = "http://auth-service"
    
    # Security
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
