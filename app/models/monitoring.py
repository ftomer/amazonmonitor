"""
Monitoring models for Amazon Price Monitor
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.models.product import Product

class NotificationSettings(BaseModel):
    """Notification settings model"""
    email_enabled: bool = False
    desktop_enabled: bool = True
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    sender_email: Optional[str] = None
    recipient_email: Optional[str] = None

class MonitorConfig(BaseModel):
    """Monitor configuration model"""
    products: List[Product]
    check_interval_minutes: int = 300
    email_notifications: NotificationSettings

class MonitorStatus(BaseModel):
    """Monitor status model"""
    is_running: bool
    last_check: Optional[datetime]
    total_products: int
    active_alerts: int = 0

class PriceCheck(BaseModel):
    """Price check result model"""
    name: str
    current_price: Optional[float] = None
    target_price: float
    price_met: bool = False
    error: Optional[str] = None

class PriceAlert(BaseModel):
    """Price alert model"""
    product_name: str
    current_price: float
    target_price: float
    timestamp: datetime
    url: str
