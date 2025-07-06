from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from jinja2 import Template, TemplateError
import json
import logging

from models import (
    Notification, NotificationTemplate, NotificationPreference, NotificationLog,
    NotificationStatus, NotificationChannel, NotificationPriority
)
import schemas

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    # Template CRUD operations
    def create_template(self, template: schemas.NotificationTemplateCreate) -> schemas.NotificationTemplate:
        db_template = NotificationTemplate(
            name=template.name,
            description=template.description,
            channel=template.channel,
            subject_template=template.subject_template,
            body_template=template.body_template,
            variables=template.variables,
            tags=template.tags,
            is_active=template.is_active
        )
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return schemas.NotificationTemplate.from_orm(db_template)

    def get_template(self, template_id: UUID) -> Optional[schemas.NotificationTemplate]:
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()
        return schemas.NotificationTemplate.from_orm(template) if template else None

    def get_templates(
        self, 
        skip: int = 0, 
        limit: int = 100,
        channel: Optional[NotificationChannel] = None,
        is_active: Optional[bool] = None
    ) -> List[schemas.NotificationTemplate]:
        query = self.db.query(NotificationTemplate)
        
        if channel:
            query = query.filter(NotificationTemplate.channel == channel)
        if is_active is not None:
            query = query.filter(NotificationTemplate.is_active == is_active)
            
        templates = query.offset(skip).limit(limit).all()
        return [schemas.NotificationTemplate.from_orm(t) for t in templates]

    def update_template(
        self, 
        template_id: UUID, 
        template_update: schemas.NotificationTemplateUpdate
    ) -> Optional[schemas.NotificationTemplate]:
        db_template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()
        
        if not db_template:
            return None
            
        update_data = template_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
            
        db_template.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_template)
        return schemas.NotificationTemplate.from_orm(db_template)

    def delete_template(self, template_id: UUID) -> bool:
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()
        
        if template:
            self.db.delete(template)
            self.db.commit()
            return True
        return False

    # Template rendering
    def render_template(
        self, 
        template_id: UUID, 
        context_data: Dict[str, Any]
    ) -> schemas.TemplateRenderResponse:
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.id == template_id
        ).first()
        
        if not template:
            return schemas.TemplateRenderResponse(
                rendered_successfully=False,
                errors=["Template not found"],
                body=""
            )
        
        errors = []
        subject = None
        body = ""
        
        try:
            # Render subject if exists
            if template.subject_template:
                subject_tmpl = Template(template.subject_template)
                subject = subject_tmpl.render(**context_data)
            
            # Render body
            body_tmpl = Template(template.body_template)
            body = body_tmpl.render(**context_data)
            
        except TemplateError as e:
            errors.append(f"Template rendering error: {str(e)}")
            
        return schemas.TemplateRenderResponse(
            subject=subject,
            body=body,
            rendered_successfully=len(errors) == 0,
            errors=errors if errors else None
        )

    # Notification CRUD operations
    def create_notification(self, notification: schemas.NotificationCreate) -> schemas.Notification:
        # Render template if template_id is provided
        if notification.template_id:
            template_render = self.render_template(
                notification.template_id, 
                notification.context_data or {}
            )
            if template_render.rendered_successfully:
                notification.subject = template_render.subject
                notification.body = template_render.body
            else:
                logger.error(f"Failed to render template {notification.template_id}: {template_render.errors}")
        
        db_notification = Notification(
            template_id=notification.template_id,
            recipient_user_id=notification.recipient_user_id,
            recipient_email=notification.recipient_email,
            recipient_phone=notification.recipient_phone,
            recipient_device_token=notification.recipient_device_token,
            recipient_slack_channel=notification.recipient_slack_channel,
            channel=notification.channel,
            subject=notification.subject,
            body=notification.body,
            context_data=notification.context_data,
            priority=notification.priority,
            scheduled_at=notification.scheduled_at or datetime.utcnow()
        )
        
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        
        # Log creation
        self._log_notification(db_notification.id, "info", "Notification created")
        
        return schemas.Notification.from_orm(db_notification)

    def get_notification(self, notification_id: UUID) -> Optional[schemas.Notification]:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        return schemas.Notification.from_orm(notification) if notification else None

    def get_notifications(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[schemas.NotificationFilter] = None
    ) -> schemas.NotificationSearchResponse:
        query = self.db.query(Notification)
        
        if filters:
            if filters.status:
                query = query.filter(Notification.status.in_(filters.status))
            if filters.channel:
                query = query.filter(Notification.channel.in_(filters.channel))
            if filters.priority:
                query = query.filter(Notification.priority.in_(filters.priority))
            if filters.recipient_user_id:
                query = query.filter(Notification.recipient_user_id == filters.recipient_user_id)
            if filters.template_id:
                query = query.filter(Notification.template_id == filters.template_id)
            if filters.date_from:
                query = query.filter(Notification.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Notification.created_at <= filters.date_to)
        
        total = query.count()
        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
        return schemas.NotificationSearchResponse(
            notifications=[schemas.Notification.from_orm(n) for n in notifications],
            total=total,
            page=skip // limit + 1,
            size=limit,
            total_pages=(total + limit - 1) // limit
        )

    def update_notification(
        self, 
        notification_id: UUID, 
        notification_update: schemas.NotificationUpdate
    ) -> Optional[schemas.Notification]:
        db_notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not db_notification:
            return None
            
        update_data = notification_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_notification, field, value)
            
        db_notification.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_notification)
        
        # Log update
        self._log_notification(notification_id, "info", f"Notification updated: {update_data}")
        
        return schemas.Notification.from_orm(db_notification)

    def delete_notification(self, notification_id: UUID) -> bool:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False

    # Bulk operations
    def create_bulk_notifications(
        self, 
        bulk_request: schemas.BulkNotificationCreate
    ) -> schemas.BulkNotificationResponse:
        template = self.db.query(NotificationTemplate).filter(
            NotificationTemplate.id == bulk_request.template_id
        ).first()
        
        if not template:
            return schemas.BulkNotificationResponse(
                total_requested=len(bulk_request.recipients),
                successfully_queued=0,
                failed=len(bulk_request.recipients),
                notification_ids=[],
                errors=["Template not found"]
            )
        
        notification_ids = []
        errors = []
        successfully_queued = 0
        
        for recipient_data in bulk_request.recipients:
            try:
                # Merge context data
                context = {**(bulk_request.context_data or {}), **recipient_data}
                
                notification_create = schemas.NotificationCreate(
                    template_id=bulk_request.template_id,
                    channel=template.channel,
                    priority=bulk_request.priority,
                    scheduled_at=bulk_request.scheduled_at,
                    context_data=context,
                    **recipient_data
                )
                
                notification = self.create_notification(notification_create)
                notification_ids.append(notification.id)
                successfully_queued += 1
                
            except Exception as e:
                errors.append(f"Failed to create notification for {recipient_data}: {str(e)}")
        
        return schemas.BulkNotificationResponse(
            total_requested=len(bulk_request.recipients),
            successfully_queued=successfully_queued,
            failed=len(bulk_request.recipients) - successfully_queued,
            notification_ids=notification_ids,
            errors=errors if errors else None
        )

    # Notification preferences
    def get_user_preferences(self, user_id: UUID) -> Optional[schemas.NotificationPreference]:
        preference = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        return schemas.NotificationPreference.from_orm(preference) if preference else None

    def create_user_preferences(
        self, 
        preferences: schemas.NotificationPreferenceCreate
    ) -> schemas.NotificationPreference:
        db_preference = NotificationPreference(**preferences.dict())
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        return schemas.NotificationPreference.from_orm(db_preference)

    def update_user_preferences(
        self, 
        user_id: UUID, 
        preferences_update: schemas.NotificationPreferenceUpdate
    ) -> Optional[schemas.NotificationPreference]:
        db_preference = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id
        ).first()
        
        if not db_preference:
            return None
            
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_preference, field, value)
            
        db_preference.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_preference)
        return schemas.NotificationPreference.from_orm(db_preference)

    # Statistics
    def get_notification_stats(
        self, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> schemas.NotificationStatsResponse:
        # Default to last 30 days if no dates provided
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Overall stats
        base_query = self.db.query(Notification).filter(
            and_(
                Notification.created_at >= date_from,
                Notification.created_at <= date_to
            )
        )
        
        total_notifications = base_query.count()
        pending = base_query.filter(Notification.status == NotificationStatus.PENDING).count()
        queued = base_query.filter(Notification.status == NotificationStatus.QUEUED).count()
        sent = base_query.filter(Notification.status == NotificationStatus.SENT).count()
        failed = base_query.filter(Notification.status == NotificationStatus.FAILED).count()
        cancelled = base_query.filter(Notification.status == NotificationStatus.CANCELLED).count()
        
        delivery_rate = (sent / total_notifications * 100) if total_notifications > 0 else 0
        
        overall_stats = schemas.NotificationStats(
            total_notifications=total_notifications,
            pending=pending,
            queued=queued,
            sent=sent,
            failed=failed,
            cancelled=cancelled,
            delivery_rate=delivery_rate
        )
        
        # Stats by channel
        channel_stats = []
        for channel in NotificationChannel:
            channel_query = base_query.filter(Notification.channel == channel)
            channel_total = channel_query.count()
            if channel_total > 0:
                channel_sent = channel_query.filter(Notification.status == NotificationStatus.SENT).count()
                channel_failed = channel_query.filter(Notification.status == NotificationStatus.FAILED).count()
                channel_delivery_rate = (channel_sent / channel_total * 100) if channel_total > 0 else 0
                
                channel_stats.append(schemas.ChannelStats(
                    channel=channel,
                    total=channel_total,
                    sent=channel_sent,
                    failed=channel_failed,
                    delivery_rate=channel_delivery_rate
                ))
        
        return schemas.NotificationStatsResponse(
            overall=overall_stats,
            by_channel=channel_stats,
            time_period=f"{date_from.isoformat()} to {date_to.isoformat()}",
            generated_at=datetime.utcnow()
        )

    # Queue processing methods
    def get_pending_notifications(self, limit: int = 100) -> List[schemas.Notification]:
        notifications = self.db.query(Notification).filter(
            and_(
                Notification.status == NotificationStatus.PENDING,
                Notification.scheduled_at <= datetime.utcnow()
            )
        ).limit(limit).all()
        
        return [schemas.Notification.from_orm(n) for n in notifications]

    def mark_notification_queued(self, notification_id: UUID) -> bool:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.status = NotificationStatus.QUEUED
            notification.updated_at = datetime.utcnow()
            self.db.commit()
            self._log_notification(notification_id, "info", "Notification queued for sending")
            return True
        return False

    def mark_notification_sent(self, notification_id: UUID, external_id: Optional[str] = None) -> bool:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            if external_id:
                notification.external_id = external_id
            notification.updated_at = datetime.utcnow()
            self.db.commit()
            self._log_notification(notification_id, "info", "Notification sent successfully")
            return True
        return False

    def mark_notification_failed(
        self, 
        notification_id: UUID, 
        failure_reason: str,
        should_retry: bool = True
    ) -> bool:
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.failure_reason = failure_reason
            notification.failed_at = datetime.utcnow()
            notification.retry_count += 1
            
            if should_retry and notification.retry_count < notification.max_retries:
                # Reset to pending for retry
                notification.status = NotificationStatus.PENDING
                # Schedule retry with exponential backoff
                retry_delay = min(300, 30 * (2 ** notification.retry_count))  # Max 5 minutes
                notification.scheduled_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                self._log_notification(notification_id, "warning", f"Notification failed, scheduling retry #{notification.retry_count}")
            else:
                notification.status = NotificationStatus.FAILED
                self._log_notification(notification_id, "error", f"Notification permanently failed: {failure_reason}")
            
            notification.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def _log_notification(self, notification_id: UUID, level: str, message: str, details: Optional[Dict[str, Any]] = None):
        """Helper method to log notification events"""
        log_entry = NotificationLog(
            notification_id=notification_id,
            level=level,
            message=message,
            details=details
        )
        self.db.add(log_entry)
        self.db.commit()

    def get_notification_logs(self, notification_id: UUID) -> List[schemas.NotificationLog]:
        """Get logs for a specific notification"""
        logs = self.db.query(NotificationLog).filter(
            NotificationLog.notification_id == notification_id
        ).order_by(NotificationLog.created_at).all()
        
        return [schemas.NotificationLog.from_orm(log) for log in logs]
