from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import redis
from elasticsearch import Elasticsearch
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL Database
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
metadata = MetaData()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis Connection
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def get_redis():
    """Get Redis client."""
    return redis_client

# Elasticsearch Connection
es_client = Elasticsearch([settings.elasticsearch_url])

def get_elasticsearch():
    """Get Elasticsearch client."""
    return es_client

def init_elasticsearch():
    """Initialize Elasticsearch index for candidates with retry mechanism."""
    index_name = settings.elasticsearch_index
    
    # Retry connection to Elasticsearch
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Test connection
            es_client.cluster.health(wait_for_status='yellow', timeout='30s')
            logger.info(f"Elasticsearch is ready after {attempt + 1} attempts")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to Elasticsearch after {max_retries} attempts: {str(e)}")
                raise
            logger.info(f"Elasticsearch not ready, attempt {attempt + 1}/{max_retries}, retrying in {retry_delay}s...")
            time.sleep(retry_delay)
    
    # Create index if it doesn't exist
    if not es_client.indices.exists(index=index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "first_name": {"type": "text", "analyzer": "standard"},
                    "last_name": {"type": "text", "analyzer": "standard"},
                    "full_name": {"type": "text", "analyzer": "standard"},
                    "email": {"type": "keyword"},
                    "phone": {"type": "keyword"},
                    "location": {
                        "properties": {
                            "city": {"type": "text"},
                            "state": {"type": "keyword"},
                            "country": {"type": "keyword"},
                            "coordinates": {"type": "geo_point"}
                        }
                    },
                    "skills": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "keyword"},
                            "level": {"type": "keyword"},
                            "years_experience": {"type": "integer"}
                        }
                    },
                    "experience": {
                        "type": "nested",
                        "properties": {
                            "company": {"type": "text"},
                            "position": {"type": "text"},
                            "start_date": {"type": "date"},
                            "end_date": {"type": "date"},
                            "current": {"type": "boolean"},
                            "description": {"type": "text"},
                            "skills": {"type": "keyword"}
                        }
                    },
                    "education": {
                        "type": "nested",
                        "properties": {
                            "institution": {"type": "text"},
                            "degree": {"type": "text"},
                            "field": {"type": "text"},
                            "start_date": {"type": "date"},
                            "end_date": {"type": "date"},
                            "gpa": {"type": "float"}
                        }
                    },
                    "total_years_experience": {"type": "integer"},
                    "career_level": {"type": "keyword"},
                    "summary": {"type": "text"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "status": {"type": "keyword"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "skill_analyzer": {
                            "type": "custom",
                            "tokenizer": "keyword",
                            "filter": ["lowercase"]
                        }
                    }
                }
            }
        }
        
        es_client.indices.create(index=index_name, body=mapping)
        print(f"Created Elasticsearch index: {index_name}")

def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize database and elasticsearch."""
    create_tables()
    init_elasticsearch()
