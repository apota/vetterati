from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import redis
from elasticsearch import Elasticsearch

# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Metadata for reflection
metadata = MetaData()

# Redis setup
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

# Elasticsearch setup
es_client = Elasticsearch([settings.elasticsearch_url])

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Redis dependency
def get_redis():
    return redis_client

# Elasticsearch dependency
def get_elasticsearch():
    return es_client
