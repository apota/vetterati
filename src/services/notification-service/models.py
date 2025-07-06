from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from database import Base

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationChannel(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"

class NotificationPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    channel = Column(Enum(NotificationChannel), nullable=False)
    subject_template = Column(Text)
    body_template = Column(Text, nullable=False)
    
    # Template metadata
    variables = Column(JSONB)  # Expected template variables
    tags = Column(JSONB)  # For categorization
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True))
    
    # Relationships
    notifications = relationship("Notification", back_populates="template")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("notification_templates.id"))
    
    # Recipient information
    recipient_user_id = Column(UUID(as_uuid=True))  # Internal user ID
    recipient_email = Column(String(255))
    recipient_phone = Column(String(20))
    recipient_device_token = Column(Text)  # For push notifications
    recipient_slack_channel = Column(String(100))
    
    # Notification content
    channel = Column(Enum(NotificationChannel), nullable=False)
    subject = Column(Text)
    body = Column(Text, nullable=False)
    context_data = Column(JSONB)  # Template context
    
    # Metadata
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Scheduling
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    failed_at = Column(DateTime)
    
    # Error handling
    failure_reason = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Tracking
    external_id = Column(String(255))  # ID from external service
    delivery_status = Column(String(50))  # delivered, bounced, etc.
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship("NotificationTemplate", back_populates="notifications")

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    slack_enabled = Column(Boolean, default=False)
    
    # Category preferences
    workflow_notifications = Column(Boolean, default=True)
    interview_reminders = Column(Boolean, default=True)
    application_updates = Column(Boolean, default=True)
    system_alerts = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=False)
    
    # Timing preferences
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))  # HH:MM format
    timezone = Column(String(50), default="UTC")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id"))
    
    # Log entry details
    level = Column(String(20))  # info, warning, error
    message = Column(Text)
    details = Column(JSONB)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    notification = relationship("Notification")
