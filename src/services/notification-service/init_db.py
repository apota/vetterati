#!/usr/bin/env python3
"""
Database initialization script for the Notification Service
"""

import sys
import os
from pathlib import Path

# Add the service directory to Python path
service_dir = Path(__file__).parent
sys.path.insert(0, str(service_dir))

from database import engine, Base
from models import NotificationTemplate, Notification, NotificationPreference, NotificationLog
from services.notification_service import NotificationService
from sample_templates import SAMPLE_TEMPLATES
import schemas
from sqlalchemy.orm import sessionmaker

def init_database():
    """Initialize the database with tables and sample data"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        service = NotificationService(db)
        
        # Check if we already have templates
        existing_templates = service.get_templates(limit=1)
        if existing_templates:
            print("✓ Sample templates already exist")
            return
        
        print("Creating sample notification templates...")
        
        created_count = 0
        for template_data in SAMPLE_TEMPLATES:
            try:
                template_create = schemas.NotificationTemplateCreate(**template_data)
                template = service.create_template(template_create)
                print(f"✓ Created template: {template.name}")
                created_count += 1
            except Exception as e:
                print(f"✗ Failed to create template {template_data['name']}: {e}")
        
        print(f"✓ Created {created_count} sample templates")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("✓ Notification service database initialization complete")
