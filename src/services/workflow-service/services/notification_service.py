import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
import pika
import json
import asyncio
from datetime import datetime
import httpx

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class NotificationService:
    """Service for sending notifications via various channels"""
    
    def __init__(self):
        self.smtp_config = {
            'host': settings.smtp_host,
            'port': settings.smtp_port,
            'username': settings.smtp_username,
            'password': settings.smtp_password,
            'use_tls': settings.smtp_use_tls
        }
    
    async def send_workflow_notification(
        self, 
        workflow_id: str,
        action: str,
        recipients: Optional[List[str]] = None
    ):
        """Send notification for workflow state change"""
        try:
            # Get workflow details
            workflow_data = await self._get_workflow_data(workflow_id)
            if not workflow_data:
                logger.error(f"Could not get workflow data for {workflow_id}")
                return
            
            # Determine recipients if not provided
            if not recipients:
                recipients = await self._get_workflow_recipients(workflow_data, action)
            
            # Generate notification content
            notification_content = self._generate_workflow_notification_content(
                workflow_data, action
            )
            
            # Send notifications
            for recipient in recipients:
                await self._send_email_notification(
                    recipient,
                    notification_content['subject'],
                    notification_content['body'],
                    notification_content.get('html_body')
                )
            
            logger.info(f"Sent workflow notifications for {workflow_id} action: {action}")
            
        except Exception as e:
            logger.error(f"Error sending workflow notification: {e}")
    
    async def send_interview_notification(
        self, 
        interview_id: str,
        notification_type: str,
        recipients: Optional[List[str]] = None
    ):
        """Send notification for interview events"""
        try:
            # Get interview details
            interview_data = await self._get_interview_data(interview_id)
            if not interview_data:
                logger.error(f"Could not get interview data for {interview_id}")
                return
            
            # Determine recipients if not provided
            if not recipients:
                recipients = await self._get_interview_recipients(interview_data, notification_type)
            
            # Generate notification content
            notification_content = self._generate_interview_notification_content(
                interview_data, notification_type
            )
            
            # Send notifications
            for recipient in recipients:
                await self._send_email_notification(
                    recipient,
                    notification_content['subject'],
                    notification_content['body'],
                    notification_content.get('html_body')
                )
            
            logger.info(f"Sent interview notifications for {interview_id} type: {notification_type}")
            
        except Exception as e:
            logger.error(f"Error sending interview notification: {e}")
    
    async def send_reminder_notification(
        self, 
        reminder_type: str,
        reminder_data: Dict[str, Any]
    ):
        """Send reminder notifications"""
        try:
            if reminder_type == "interview_reminder":
                await self._send_interview_reminder(reminder_data)
            elif reminder_type == "deadline_reminder":
                await self._send_deadline_reminder(reminder_data)
            elif reminder_type == "follow_up_reminder":
                await self._send_follow_up_reminder(reminder_data)
            
        except Exception as e:
            logger.error(f"Error sending reminder notification: {e}")
    
    async def _send_email_notification(
        self, 
        recipient: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.smtp_username
            msg['To'] = recipient
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            if self.smtp_config['use_tls']:
                server.starttls()
            
            if self.smtp_config['username'] and self.smtp_config['password']:
                server.login(self.smtp_config['username'], self.smtp_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {recipient}")
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
    
    async def _send_slack_notification(
        self, 
        channel: str,
        message: str,
        webhook_url: Optional[str] = None
    ):
        """Send Slack notification"""
        try:
            if not webhook_url:
                logger.warning("Slack webhook URL not configured")
                return
            
            payload = {
                'channel': channel,
                'text': message,
                'username': 'ATS Bot'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
            
            logger.info(f"Slack notification sent to {channel}")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def _get_workflow_data(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow data for notifications"""
        try:
            # This would typically make an API call to the workflow service
            # For now, return mock data
            return {
                'id': workflow_id,
                'candidate_name': 'John Doe',
                'job_title': 'Software Engineer',
                'current_state': 'technical_interview',
                'candidate_email': 'john.doe@example.com',
                'recruiter_email': 'recruiter@company.com',
                'hiring_manager_email': 'manager@company.com'
            }
        except Exception as e:
            logger.error(f"Error getting workflow data: {e}")
            return None
    
    async def _get_interview_data(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """Get interview data for notifications"""
        try:
            # This would typically make an API call to the workflow service
            # For now, return mock data
            return {
                'id': interview_id,
                'candidate_name': 'John Doe',
                'candidate_email': 'john.doe@example.com',
                'interviewer_emails': ['interviewer@company.com'],
                'interview_type': 'technical',
                'scheduled_start': '2024-01-15T10:00:00Z',
                'meeting_url': 'https://zoom.us/j/123456789',
                'job_title': 'Software Engineer'
            }
        except Exception as e:
            logger.error(f"Error getting interview data: {e}")
            return None
    
    async def _get_workflow_recipients(
        self, 
        workflow_data: Dict[str, Any],
        action: str
    ) -> List[str]:
        """Determine recipients for workflow notifications"""
        recipients = []
        
        # Always notify candidate for certain actions
        candidate_actions = ['offer_extended', 'rejected', 'interview_scheduled']
        if action in candidate_actions and workflow_data.get('candidate_email'):
            recipients.append(workflow_data['candidate_email'])
        
        # Always notify recruiter
        if workflow_data.get('recruiter_email'):
            recipients.append(workflow_data['recruiter_email'])
        
        # Notify hiring manager for important actions
        manager_actions = ['offer_extended', 'hired', 'rejected']
        if action in manager_actions and workflow_data.get('hiring_manager_email'):
            recipients.append(workflow_data['hiring_manager_email'])
        
        return recipients
    
    async def _get_interview_recipients(
        self, 
        interview_data: Dict[str, Any],
        notification_type: str
    ) -> List[str]:
        """Determine recipients for interview notifications"""
        recipients = []
        
        # Always notify candidate
        if interview_data.get('candidate_email'):
            recipients.append(interview_data['candidate_email'])
        
        # Always notify interviewers
        if interview_data.get('interviewer_emails'):
            recipients.extend(interview_data['interviewer_emails'])
        
        return recipients
    
    def _generate_workflow_notification_content(
        self, 
        workflow_data: Dict[str, Any],
        action: str
    ) -> Dict[str, str]:
        """Generate notification content for workflow events"""
        candidate_name = workflow_data.get('candidate_name', 'Candidate')
        job_title = workflow_data.get('job_title', 'Position')
        
        templates = {
            'screen': {
                'subject': f'Application Update - {job_title}',
                'body': f'Dear {candidate_name},\n\nYour application for {job_title} is being reviewed. We will contact you soon with next steps.\n\nBest regards,\nHiring Team'
            },
            'schedule_phone': {
                'subject': f'Phone Interview Scheduled - {job_title}',
                'body': f'Dear {candidate_name},\n\nCongratulations! We would like to schedule a phone interview for the {job_title} position.\n\nBest regards,\nHiring Team'
            },
            'offer_extended': {
                'subject': f'Job Offer - {job_title}',
                'body': f'Dear {candidate_name},\n\nWe are pleased to extend an offer for the {job_title} position. Please review the attached offer details.\n\nBest regards,\nHiring Team'
            },
            'rejected': {
                'subject': f'Application Update - {job_title}',
                'body': f'Dear {candidate_name},\n\nThank you for your interest in the {job_title} position. While we were impressed with your qualifications, we have decided to move forward with other candidates.\n\nBest regards,\nHiring Team'
            }
        }
        
        return templates.get(action, {
            'subject': f'Application Update - {job_title}',
            'body': f'Dear {candidate_name},\n\nThere has been an update to your application for {job_title}.\n\nBest regards,\nHiring Team'
        })
    
    def _generate_interview_notification_content(
        self, 
        interview_data: Dict[str, Any],
        notification_type: str
    ) -> Dict[str, str]:
        """Generate notification content for interview events"""
        candidate_name = interview_data.get('candidate_name', 'Candidate')
        job_title = interview_data.get('job_title', 'Position')
        interview_type = interview_data.get('interview_type', 'interview')
        
        templates = {
            'scheduled': {
                'subject': f'Interview Scheduled - {job_title}',
                'body': f'Dear {candidate_name},\n\nYour {interview_type} interview for {job_title} has been scheduled.\n\nDetails:\nDate/Time: {interview_data.get("scheduled_start", "TBD")}\nMeeting Link: {interview_data.get("meeting_url", "TBD")}\n\nBest regards,\nHiring Team'
            },
            'reminder': {
                'subject': f'Interview Reminder - {job_title}',
                'body': f'Dear {candidate_name},\n\nThis is a friendly reminder about your {interview_type} interview for {job_title} scheduled for tomorrow.\n\nBest regards,\nHiring Team'
            },
            'cancelled': {
                'subject': f'Interview Cancelled - {job_title}',
                'body': f'Dear {candidate_name},\n\nWe need to cancel your {interview_type} interview for {job_title}. We will reschedule soon.\n\nBest regards,\nHiring Team'
            }
        }
        
        return templates.get(notification_type, {
            'subject': f'Interview Update - {job_title}',
            'body': f'Dear {candidate_name},\n\nThere has been an update to your interview for {job_title}.\n\nBest regards,\nHiring Team'
        })
    
    async def _send_interview_reminder(self, reminder_data: Dict[str, Any]):
        """Send interview reminder notifications"""
        interview_data = reminder_data.get('interview_data', {})
        await self.send_interview_notification(
            interview_data.get('id'),
            'reminder'
        )
    
    async def _send_deadline_reminder(self, reminder_data: Dict[str, Any]):
        """Send deadline reminder notifications"""
        # Implementation for deadline reminders
        pass
    
    async def _send_follow_up_reminder(self, reminder_data: Dict[str, Any]):
        """Send follow-up reminder notifications"""
        # Implementation for follow-up reminders
        pass
