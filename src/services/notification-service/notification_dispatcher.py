from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import asyncio
import aiohttp
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationSender(ABC):
    """Abstract base class for notification senders"""
    
    @abstractmethod
    async def send(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification and return result"""
        pass

class EmailSender(NotificationSender):
    """Email notification sender"""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
    
    async def send(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # In a real implementation, you would use an email service like:
            # - SMTP with aiosmtplib
            # - SendGrid API
            # - AWS SES
            # - Mailgun API
            
            # For now, simulate email sending
            logger.info(f"Sending email to {notification_data.get('recipient_email')}")
            await asyncio.sleep(0.1)  # Simulate sending time
            
            return {
                "success": True,
                "external_id": f"email_{datetime.utcnow().timestamp()}",
                "provider": "smtp",
                "delivery_status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class SMSSender(NotificationSender):
    """SMS notification sender"""
    
    def __init__(self, sms_config: Dict[str, Any]):
        self.sms_config = sms_config
    
    async def send(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            # In a real implementation, you would use an SMS service like:
            # - Twilio
            # - AWS SNS
            # - Vonage (Nexmo)
            
            # For now, simulate SMS sending
            logger.info(f"Sending SMS to {notification_data.get('recipient_phone')}")
            await asyncio.sleep(0.1)  # Simulate sending time
            
            return {
                "success": True,
                "external_id": f"sms_{datetime.utcnow().timestamp()}",
                "provider": "twilio",
                "delivery_status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class PushSender(NotificationSender):
    """Push notification sender"""
    
    def __init__(self, push_config: Dict[str, Any]):
        self.push_config = push_config
    
    async def send(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send push notification"""
        try:
            # In a real implementation, you would use push services like:
            # - Firebase Cloud Messaging (FCM)
            # - Apple Push Notification Service (APNS)
            # - OneSignal
            
            # For now, simulate push sending
            logger.info(f"Sending push notification to device {notification_data.get('recipient_device_token')}")
            await asyncio.sleep(0.1)  # Simulate sending time
            
            return {
                "success": True,
                "external_id": f"push_{datetime.utcnow().timestamp()}",
                "provider": "fcm",
                "delivery_status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class SlackSender(NotificationSender):
    """Slack notification sender"""
    
    def __init__(self, slack_config: Dict[str, Any]):
        self.slack_config = slack_config
        self.webhook_url = slack_config.get("webhook_url")
        self.bot_token = slack_config.get("bot_token")
    
    async def send(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack notification"""
        try:
            # For webhook-based sending
            if self.webhook_url:
                return await self._send_webhook(notification_data)
            
            # For bot token-based sending
            if self.bot_token:
                return await self._send_via_api(notification_data)
            
            raise ValueError("No Slack configuration available")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_webhook(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send via Slack webhook"""
        payload = {
            "text": notification_data.get("body"),
            "channel": notification_data.get("recipient_slack_channel")
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 200:
                    return {
                        "success": True,
                        "external_id": f"slack_webhook_{datetime.utcnow().timestamp()}",
                        "provider": "slack_webhook",
                        "delivery_status": "sent"
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"Slack webhook failed: {response.status} - {error_text}")
    
    async def _send_via_api(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send via Slack API"""
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": notification_data.get("recipient_slack_channel"),
            "text": notification_data.get("body")
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                result = await response.json()
                if result.get("ok"):
                    return {
                        "success": True,
                        "external_id": result.get("ts"),
                        "provider": "slack_api",
                        "delivery_status": "sent"
                    }
                else:
                    raise Exception(f"Slack API error: {result.get('error')}")

class WebhookSender(NotificationSender):
    """Webhook notification sender"""
    
    def __init__(self, webhook_config: Dict[str, Any]):
        self.webhook_config = webhook_config
    
    async def send(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            webhook_url = notification_data.get("webhook_url") or self.webhook_config.get("default_url")
            if not webhook_url:
                raise ValueError("No webhook URL provided")
            
            payload = {
                "notification_id": notification_data.get("id"),
                "subject": notification_data.get("subject"),
                "body": notification_data.get("body"),
                "timestamp": datetime.utcnow().isoformat(),
                "context_data": notification_data.get("context_data", {})
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status in [200, 201, 202]:
                        return {
                            "success": True,
                            "external_id": f"webhook_{datetime.utcnow().timestamp()}",
                            "provider": "webhook",
                            "delivery_status": "sent"
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Webhook failed: {response.status} - {error_text}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }

class NotificationDispatcher:
    """Main dispatcher for routing notifications to appropriate senders"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.senders = self._initialize_senders()
    
    def _initialize_senders(self) -> Dict[str, NotificationSender]:
        """Initialize notification senders based on configuration"""
        senders = {}
        
        if self.config.get("email"):
            senders["email"] = EmailSender(self.config["email"])
        
        if self.config.get("sms"):
            senders["sms"] = SMSSender(self.config["sms"])
        
        if self.config.get("push"):
            senders["push"] = PushSender(self.config["push"])
        
        if self.config.get("slack"):
            senders["slack"] = SlackSender(self.config["slack"])
        
        if self.config.get("webhook"):
            senders["webhook"] = WebhookSender(self.config["webhook"])
        
        return senders
    
    async def send_notification(self, channel: str, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification via specified channel"""
        sender = self.senders.get(channel)
        if not sender:
            return {
                "success": False,
                "error": f"No sender configured for channel: {channel}"
            }
        
        try:
            result = await sender.send(notification_data)
            logger.info(f"Notification sent via {channel}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to send notification via {channel}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_channels(self) -> list:
        """Get list of available notification channels"""
        return list(self.senders.keys())
