from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Candidate Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://ats_user:ats_password@localhost:5432/vetterati_ats"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Elasticsearch
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "candidates"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External Services
    auth_service_url: str = "http://localhost:5001"
    resume_service_url: str = "http://localhost:8001"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Search
    max_search_results: int = 1000
    search_timeout: int = 30
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = ["pdf", "doc", "docx", "txt"]
    
    # Location Services
    enable_geocoding: bool = True
    geocoding_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
