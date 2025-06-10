"""
Notification service for price alerts
"""

import os
import smtplib
import subprocess
import platform
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for sending price alert notifications"""
    
    async def send_price_alert(self, product_name: str, current_price: float, 
                             target_price: float, url: str, config: Dict[str, Any]):
        """Send price alert notification"""
        
        # Send email notification
        if config.get("email_notifications", {}).get("enabled"):
            await self._send_email_notification(product_name, current_price, target_price, url, config)
        
    async def _send_email_notification(self, product_name: str, current_price: float,
                                     target_price: float, url: str, config: Dict[str, Any]):
        """Send email notification"""
        try:
             # Get email settings from environment variables (prioritized) and config fallback
            sender_email = os.getenv("SMTP_SENDER_EMAIL") or settings.SMTP_SENDER_EMAIL
            sender_password = os.getenv("SMTP_SENDER_PASSWORD") or settings.SMTP_SENDER_PASSWORD
            recipient_email = os.getenv("SMTP_RECIPIENT_EMAIL") or settings.SMTP_RECIPIENT_EMAIL

            smtp_server = os.getenv("SMTP_SERVER") or settings.SMTP_SERVER
            smtp_port = int(os.getenv("SMTP_PORT", settings.SMTP_PORT))
            
            
            # Validate required fields
            if not all([sender_email, sender_password, recipient_email]):
                missing_fields = []
                if not sender_email:
                    missing_fields.append("SMTP_SENDER_EMAIL")
                if not sender_password:
                    missing_fields.append("SMTP_SENDER_PASSWORD")
                if not recipient_email:
                    missing_fields.append("SMTP_RECIPIENT_EMAIL")
                
                logger.error(f"Missing email credentials in .env file: {', '.join(missing_fields)}")
                return
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Price Alert: {product_name}"
            savings = target_price - current_price

            body = f"""
🎉 Great news! The price for {product_name} has dropped below your target!

💰 Current Price: ${current_price:.2f}
🎯 Target Price: ${target_price:.2f}
💵 You save: ${savings:.2f}

🛒 Product URL: {url}

Happy shopping! 🛍️

---
Amazon Price Monitor
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            
            logger.info(f"Email notification sent for {product_name}")
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed - check your email credentials in .env file")
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    