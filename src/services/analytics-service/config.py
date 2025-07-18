import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database settings
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/vetterati"
    )
    
    # Service settings
    service_name: str = "analytics-service"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # External service URLs
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    resume_service_url: str = os.getenv("RESUME_SERVICE_URL", "http://resume-service:8002")
    ahp_service_url: str = os.getenv("AHP_SERVICE_URL", "http://ahp-service:8003")
    workflow_service_url: str = os.getenv("WORKFLOW_SERVICE_URL", "http://workflow-service:8004")
    
    # Caching settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    
    # Analytics settings
    batch_size: int = int(os.getenv("BATCH_SIZE", "1000"))
    max_concurrent_queries: int = int(os.getenv("MAX_CONCURRENT_QUERIES", "10"))
    
    # ML/Predictive settings
    model_retrain_interval_hours: int = int(os.getenv("MODEL_RETRAIN_INTERVAL_HOURS", "24"))
    min_data_points_for_prediction: int = int(os.getenv("MIN_DATA_POINTS_FOR_PREDICTION", "50"))
    
    # Export settings
    export_temp_dir: str = os.getenv("EXPORT_TEMP_DIR", "/tmp/analytics_exports")
    max_export_size_mb: int = int(os.getenv("MAX_EXPORT_SIZE_MB", "50"))
    
    class Config:
        env_file = ".env"
        protected_namespaces = ()

@lru_cache()
def get_settings():
    return Settings()
