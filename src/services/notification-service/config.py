import os
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://vetterati_user:vetterati_pass@localhost:5432/vetterati_db")
    
    # Redis for caching and queues
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # RabbitMQ for message queuing
    rabbitmq_url: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    
    # Email configuration
    smtp_host: str = os.getenv("SMTP_HOST", "localhost")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "noreply@vetterati.com")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "Vetterati")
    
    # Push notification configuration
    firebase_credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    
    # SMS configuration (Twilio)
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_number: str = os.getenv("TWILIO_FROM_NUMBER", "")
    
    # Slack configuration
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
    
    # Application settings
    app_name: str = "Notification Service"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    rate_limit_per_hour: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # Template service
    template_service_url: str = os.getenv("TEMPLATE_SERVICE_URL", "http://localhost:8009")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
