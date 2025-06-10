"""
Tests for NotificationService
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.notification import NotificationService


class TestNotificationService:
    """Test NotificationService functionality"""
    
    @pytest.fixture
    def notification_service(self):
        """Create a notification service instance"""
        return NotificationService()
    
    @patch.dict('os.environ', {
        'SMTP_SENDER_EMAIL': 'test@example.com',
        'SMTP_SENDER_PASSWORD': 'test_password',
        'SMTP_RECIPIENT_EMAIL': 'recipient@example.com'
    })
    @patch('smtplib.SMTP')
    async def test_send_email_notification_success(self, mock_smtp, notification_service):
        """Test successful email notification"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        config = {
            "email_notifications": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "test@example.com",
                "recipient_email": "recipient@example.com"
            }
        }
        
        await notification_service._send_email_notification(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test@example.com", "test_password")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    async def test_send_email_notification_missing_credentials(self, notification_service):
        """Test email notification with missing credentials"""
        config = {
            "email_notifications": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "",  # Missing
                "recipient_email": ""  # Missing
            }
        }
        
        # Should not raise exception, just log error
        await notification_service._send_email_notification(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
    
    @patch('smtplib.SMTP')
    async def test_send_email_notification_smtp_error(self, mock_smtp, notification_service):
        """Test email notification with SMTP error"""
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        config = {
            "email_notifications": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "test@example.com",
                "recipient_email": "recipient@example.com"
            }
        }
        
        # Should not raise exception, just log error
        await notification_service._send_email_notification(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
    
    
    @patch.object(NotificationService, '_send_email_notification')
    async def test_send_price_alert_both_enabled(self, mock_desktop, mock_email, notification_service):
        """Test sending price alert with both notifications enabled"""
        config = {
            "email_notifications": {"enabled": True},
            "desktop_notifications": {"enabled": True}
        }
        
        await notification_service.send_price_alert(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
        
        mock_email.assert_called_once()
        mock_desktop.assert_called_once()
    
    @patch.object(NotificationService, '_send_email_notification')
    async def test_send_price_alert_email_only(self, mock_desktop, mock_email, notification_service):
        """Test sending price alert with only email enabled"""
        config = {
            "email_notifications": {"enabled": True},
            "desktop_notifications": {"enabled": False}
        }
        
        await notification_service.send_price_alert(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
        
        mock_email.assert_called_once()
        mock_desktop.assert_not_called()
    
    @patch.object(NotificationService, '_send_email_notification')
    async def test_send_price_alert_desktop_only(self, mock_desktop, mock_email, notification_service):
        """Test sending price alert with only desktop enabled"""
        config = {
            "email_notifications": {"enabled": False},
            "desktop_notifications": {"enabled": True}
        }
        
        await notification_service.send_price_alert(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
        
        mock_email.assert_not_called()
        mock_desktop.assert_called_once()
    
    @patch.object(NotificationService, '_send_email_notification')
    async def test_send_price_alert_none_enabled(self, mock_desktop, mock_email, notification_service):
        """Test sending price alert with no notifications enabled"""
        config = {
            "email_notifications": {"enabled": False},
            "desktop_notifications": {"enabled": False}
        }
        
        await notification_service.send_price_alert(
            "Test Product", 25.99, 30.00, "https://amazon.com/test", config
        )
        
        mock_email.assert_not_called()
        mock_desktop.assert_not_called()