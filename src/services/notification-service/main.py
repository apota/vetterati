from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging
import os

from database import get_db, engine
from models import Base
from services.notification_service import NotificationService
from notification_dispatcher import NotificationDispatcher
from sample_templates import SAMPLE_TEMPLATES
import schemas

# Create database tables
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize notification dispatcher
notification_config = {
    "email": {
        "smtp_host": os.getenv("SMTP_HOST", "localhost"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_username": os.getenv("SMTP_USERNAME", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "smtp_use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    },
    "sms": {
        "provider": os.getenv("SMS_PROVIDER", "twilio"),
        "account_sid": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "auth_token": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "from_number": os.getenv("TWILIO_FROM_NUMBER", "")
    },
    "slack": {
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
        "bot_token": os.getenv("SLACK_BOT_TOKEN", "")
    },
    "push": {
        "firebase_key": os.getenv("FIREBASE_SERVER_KEY", ""),
        "apns_key": os.getenv("APNS_KEY", "")
    },
    "webhook": {
        "default_url": os.getenv("DEFAULT_WEBHOOK_URL", "")
    }
}

dispatcher = NotificationDispatcher(notification_config)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vetterati Notification Service",
    description="Microservice for managing notifications, templates, and user preferences",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service", "timestamp": datetime.utcnow()}

# Template endpoints
@app.post("/api/v1/templates", response_model=schemas.NotificationTemplate)
async def create_template(
    template: schemas.NotificationTemplateCreate,
    service: NotificationService = Depends(get_notification_service)
):
    """Create a new notification template"""
    try:
        return service.create_template(template)
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/templates", response_model=List[schemas.NotificationTemplate])
async def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    channel: Optional[schemas.NotificationChannel] = None,
    is_active: Optional[bool] = None,
    service: NotificationService = Depends(get_notification_service)
):
    """Get all notification templates with optional filtering"""
    return service.get_templates(skip=skip, limit=limit, channel=channel, is_active=is_active)

@app.get("/api/v1/templates/{template_id}", response_model=schemas.NotificationTemplate)
async def get_template(
    template_id: UUID,
    service: NotificationService = Depends(get_notification_service)
):
    """Get a specific notification template"""
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.put("/api/v1/templates/{template_id}", response_model=schemas.NotificationTemplate)
async def update_template(
    template_id: UUID,
    template_update: schemas.NotificationTemplateUpdate,
    service: NotificationService = Depends(get_notification_service)
):
    """Update a notification template"""
    template = service.update_template(template_id, template_update)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.delete("/api/v1/templates/{template_id}")
async def delete_template(
    template_id: UUID,
    service: NotificationService = Depends(get_notification_service)
):
    """Delete a notification template"""
    if not service.delete_template(template_id):
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

@app.post("/api/v1/templates/{template_id}/render", response_model=schemas.TemplateRenderResponse)
async def render_template(
    template_id: UUID,
    render_request: schemas.TemplateRenderRequest,
    service: NotificationService = Depends(get_notification_service)
):
    """Render a template with provided context data"""
    return service.render_template(template_id, render_request.context_data)

# Notification endpoints
@app.post("/api/v1/notifications", response_model=schemas.Notification)
async def create_notification(
    notification: schemas.NotificationCreate,
    background_tasks: BackgroundTasks,
    service: NotificationService = Depends(get_notification_service)
):
    """Create a new notification"""
    try:
        created_notification = service.create_notification(notification)
        
        # Queue notification for processing in background
        background_tasks.add_task(process_notification, created_notification.id, service)
        
        return created_notification
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/notifications/bulk", response_model=schemas.BulkNotificationResponse)
async def create_bulk_notifications(
    bulk_request: schemas.BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    service: NotificationService = Depends(get_notification_service)
):
    """Create multiple notifications from a template"""
    try:
        result = service.create_bulk_notifications(bulk_request)
        
        # Queue all notifications for processing
        for notification_id in result.notification_ids:
            background_tasks.add_task(process_notification, notification_id, service)
        
        return result
    except Exception as e:
        logger.error(f"Failed to create bulk notifications: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/notifications", response_model=schemas.NotificationSearchResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[List[schemas.NotificationStatus]] = Query(None),
    channel: Optional[List[schemas.NotificationChannel]] = Query(None),
    priority: Optional[List[schemas.NotificationPriority]] = Query(None),
    recipient_user_id: Optional[UUID] = None,
    template_id: Optional[UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    service: NotificationService = Depends(get_notification_service)
):
    """Get notifications with optional filtering"""
    filters = schemas.NotificationFilter(
        status=status,
        channel=channel,
        priority=priority,
        recipient_user_id=recipient_user_id,
        template_id=template_id,
        date_from=date_from,
        date_to=date_to
    )
    return service.get_notifications(skip=skip, limit=limit, filters=filters)

@app.get("/api/v1/notifications/{notification_id}", response_model=schemas.Notification)
async def get_notification(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service)
):
    """Get a specific notification"""
    notification = service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.put("/api/v1/notifications/{notification_id}", response_model=schemas.Notification)
async def update_notification(
    notification_id: UUID,
    notification_update: schemas.NotificationUpdate,
    service: NotificationService = Depends(get_notification_service)
):
    """Update a notification"""
    notification = service.update_notification(notification_id, notification_update)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@app.delete("/api/v1/notifications/{notification_id}")
async def delete_notification(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service)
):
    """Delete a notification"""
    if not service.delete_notification(notification_id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}

@app.get("/api/v1/notifications/{notification_id}/logs", response_model=List[schemas.NotificationLog])
async def get_notification_logs(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service)
):
    """Get logs for a specific notification"""
    return service.get_notification_logs(notification_id)

# User preference endpoints
@app.get("/api/v1/users/{user_id}/preferences", response_model=schemas.NotificationPreference)
async def get_user_preferences(
    user_id: UUID,
    service: NotificationService = Depends(get_notification_service)
):
    """Get notification preferences for a user"""
    preferences = service.get_user_preferences(user_id)
    if not preferences:
        # Create default preferences if none exist
        default_prefs = schemas.NotificationPreferenceCreate(user_id=user_id)
        preferences = service.create_user_preferences(default_prefs)
    return preferences

@app.post("/api/v1/users/{user_id}/preferences", response_model=schemas.NotificationPreference)
async def create_user_preferences(
    user_id: UUID,
    preferences: schemas.NotificationPreferenceCreate,
    service: NotificationService = Depends(get_notification_service)
):
    """Create notification preferences for a user"""
    # Ensure the user_id matches
    preferences.user_id = user_id
    try:
        return service.create_user_preferences(preferences)
    except Exception as e:
        logger.error(f"Failed to create user preferences: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/v1/users/{user_id}/preferences", response_model=schemas.NotificationPreference)
async def update_user_preferences(
    user_id: UUID,
    preferences_update: schemas.NotificationPreferenceUpdate,
    service: NotificationService = Depends(get_notification_service)
):
    """Update notification preferences for a user"""
    preferences = service.update_user_preferences(user_id, preferences_update)
    if not preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return preferences

# Statistics endpoints
@app.get("/api/v1/stats", response_model=schemas.NotificationStatsResponse)
async def get_notification_stats(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    service: NotificationService = Depends(get_notification_service)
):
    """Get notification statistics"""
    return service.get_notification_stats(date_from=date_from, date_to=date_to)

# Queue processing endpoints (for internal use)
@app.get("/api/v1/queue/pending", response_model=List[schemas.Notification])
async def get_pending_notifications(
    limit: int = Query(100, ge=1, le=1000),
    service: NotificationService = Depends(get_notification_service)
):
    """Get pending notifications for processing"""
    return service.get_pending_notifications(limit=limit)

@app.post("/api/v1/queue/process")
async def process_notification_queue(
    background_tasks: BackgroundTasks,
    service: NotificationService = Depends(get_notification_service)
):
    """Process pending notifications in the queue"""
    pending_notifications = service.get_pending_notifications(limit=100)
    
    for notification in pending_notifications:
        background_tasks.add_task(process_notification, notification.id, service)
    
    return {
        "message": f"Queued {len(pending_notifications)} notifications for processing",
        "queued_count": len(pending_notifications)
    }

# Webhook endpoints for delivery status updates
@app.post("/api/v1/webhooks/delivery-status")
async def update_delivery_status(
    webhook_data: dict,
    service: NotificationService = Depends(get_notification_service)
):
    """Handle delivery status updates from external services"""
    try:
        # This is a placeholder for webhook handling
        # Implementation would depend on the specific external service format
        notification_id = webhook_data.get("notification_id")
        status = webhook_data.get("status")
        
        if notification_id and status:
            # Update notification based on webhook data
            logger.info(f"Received delivery status update for {notification_id}: {status}")
            return {"message": "Delivery status updated"}
        
        return {"message": "Invalid webhook data"}
    except Exception as e:
        logger.error(f"Failed to process webhook: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Background task for processing notifications
async def process_notification(notification_id: UUID, service: NotificationService):
    """Background task to process a notification"""
    try:
        # Mark as queued
        service.mark_notification_queued(notification_id)
        
        # Get the notification
        notification = service.get_notification(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found for processing")
            return
        
        logger.info(f"Processing notification {notification_id} via {notification.channel}")
        
        # Check user preferences if recipient_user_id is available
        if notification.recipient_user_id:
            preferences = service.get_user_preferences(notification.recipient_user_id)
            if preferences:
                # Check if user has disabled this channel
                channel_enabled = getattr(preferences, f"{notification.channel}_enabled", True)
                if not channel_enabled:
                    logger.info(f"User {notification.recipient_user_id} has disabled {notification.channel} notifications")
                    service.mark_notification_failed(
                        notification_id, 
                        f"User has disabled {notification.channel} notifications",
                        should_retry=False
                    )
                    return
        
        # Prepare notification data for dispatcher
        notification_data = {
            "id": str(notification.id),
            "recipient_email": notification.recipient_email,
            "recipient_phone": notification.recipient_phone,
            "recipient_device_token": notification.recipient_device_token,
            "recipient_slack_channel": notification.recipient_slack_channel,
            "subject": notification.subject,
            "body": notification.body,
            "context_data": notification.context_data
        }
        
        # Send via appropriate channel
        result = await dispatcher.send_notification(notification.channel, notification_data)
        
        if result.get("success"):
            # Mark as sent
            service.mark_notification_sent(
                notification_id, 
                external_id=result.get("external_id")
            )
            logger.info(f"Successfully processed notification {notification_id}")
        else:
            # Mark as failed
            service.mark_notification_failed(
                notification_id, 
                result.get("error", "Unknown error")
            )
            logger.error(f"Failed to process notification {notification_id}: {result.get('error')}")
        
    except Exception as e:
        logger.error(f"Failed to process notification {notification_id}: {e}")
        service.mark_notification_failed(notification_id, str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize sample templates on startup"""
    try:
        with next(get_db()) as db:
            service = NotificationService(db)
            
            # Check if we have any templates
            existing_templates = service.get_templates(limit=1)
            if not existing_templates:
                logger.info("Creating sample notification templates...")
                
                for template_data in SAMPLE_TEMPLATES:
                    try:
                        template_create = schemas.NotificationTemplateCreate(**template_data)
                        service.create_template(template_create)
                        logger.info(f"Created template: {template_data['name']}")
                    except Exception as e:
                        logger.error(f"Failed to create template {template_data['name']}: {e}")
                
                logger.info("Sample templates created successfully")
                
    except Exception as e:
        logger.error(f"Failed to initialize sample templates: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
