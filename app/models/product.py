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
