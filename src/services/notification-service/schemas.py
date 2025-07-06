from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from enum import Enum

class NotificationStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Notification Template Schemas
class NotificationTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    channel: NotificationChannel
    subject_template: Optional[str] = None
    body_template: str
    variables: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: bool = True

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    channel: Optional[NotificationChannel] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class NotificationTemplate(NotificationTemplateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    channel: NotificationChannel
    subject: Optional[str] = None
    body: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    context_data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    template_id: Optional[UUID] = None
    recipient_user_id: Optional[UUID] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    recipient_device_token: Optional[str] = None
    recipient_slack_channel: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Validate that at least one recipient method is provided
        recipients = [
            self.recipient_user_id,
            self.recipient_email,
            self.recipient_phone,
            self.recipient_device_token,
            self.recipient_slack_channel
        ]
        if not any(recipients):
            raise ValueError('At least one recipient method must be provided')

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    scheduled_at: Optional[datetime] = None
    priority: Optional[NotificationPriority] = None

class Notification(NotificationBase):
    id: UUID
    template_id: Optional[UUID] = None
    recipient_user_id: Optional[UUID] = None
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_device_token: Optional[str] = None
    recipient_slack_channel: Optional[str] = None
    status: NotificationStatus
    sent_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int
    max_retries: int
    external_id: Optional[str] = None
    delivery_status: Optional[str] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Notification Preference Schemas
class NotificationPreferenceBase(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    slack_enabled: bool = False
    workflow_notifications: bool = True
    interview_reminders: bool = True
    application_updates: bool = True
    system_alerts: bool = True
    marketing_emails: bool = False
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: str = "UTC"

class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: UUID

class NotificationPreferenceUpdate(NotificationPreferenceBase):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    slack_enabled: Optional[bool] = None
    workflow_notifications: Optional[bool] = None
    interview_reminders: Optional[bool] = None
    application_updates: Optional[bool] = None
    system_alerts: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None

class NotificationPreference(NotificationPreferenceBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Notification Log Schemas
class NotificationLogBase(BaseModel):
    level: str
    message: str
    details: Optional[Dict[str, Any]] = None

class NotificationLogCreate(NotificationLogBase):
    notification_id: UUID

class NotificationLog(NotificationLogBase):
    id: UUID
    notification_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Bulk notification schemas
class BulkNotificationCreate(BaseModel):
    template_id: UUID
    recipients: List[Dict[str, Any]]  # List of recipient data
    context_data: Optional[Dict[str, Any]] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_at: Optional[datetime] = None

class BulkNotificationResponse(BaseModel):
    total_requested: int
    successfully_queued: int
    failed: int
    notification_ids: List[UUID]
    errors: Optional[List[str]] = None

# Template rendering schemas
class TemplateRenderRequest(BaseModel):
    template_id: UUID
    context_data: Dict[str, Any]

class TemplateRenderResponse(BaseModel):
    subject: Optional[str] = None
    body: str
    rendered_successfully: bool
    errors: Optional[List[str]] = None

# Statistics schemas
class NotificationStats(BaseModel):
    total_notifications: int
    pending: int
    queued: int
    sent: int
    failed: int
    cancelled: int
    delivery_rate: float
    average_send_time: Optional[float] = None  # in seconds

class ChannelStats(BaseModel):
    channel: NotificationChannel
    total: int
    sent: int
    failed: int
    delivery_rate: float

class NotificationStatsResponse(BaseModel):
    overall: NotificationStats
    by_channel: List[ChannelStats]
    time_period: str
    generated_at: datetime

# Search and filter schemas
class NotificationFilter(BaseModel):
    status: Optional[List[NotificationStatus]] = None
    channel: Optional[List[NotificationChannel]] = None
    priority: Optional[List[NotificationPriority]] = None
    recipient_user_id: Optional[UUID] = None
    template_id: Optional[UUID] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class NotificationSearchResponse(BaseModel):
    notifications: List[Notification]
    total: int
    page: int
    size: int
    total_pages: int
