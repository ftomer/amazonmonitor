"""
Product models for Amazon Price Monitor
"""

from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator

class ProductBase(BaseModel):
    """Base product model"""
    name: str
    url: HttpUrl
    target_price: float
    
    @field_validator('target_price')
    @classmethod
    def validate_target_price(cls, v):
        if v <= 0:
            raise ValueError('Target price must be positive')
        return v

class ProductCreate(ProductBase):
    """Model for creating a new product"""
    pass

class ProductUpdate(BaseModel):
    """Model for updating a product"""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    target_price: Optional[float] = None
    
    @field_validator('target_price')
    @classmethod
    def validate_target_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Target price must be positive')
        return v

class Product(ProductBase):
    """Full product model"""
    pass

class ProductConfig(BaseModel):
    """Product configuration model"""
    name: str
    url: str
    target_price: float
''')

    # app/models/monitoring.py
    create_file("app/models/monitoring.py", '''"""
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