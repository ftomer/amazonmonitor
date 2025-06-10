"""
Configuration management for Amazon Price Monitor
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # Project info
    PROJECT_NAME: str = "Amazon Price Monitor"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Monitor Amazon product prices and get alerts"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Data directories
    DATA_DIR: Path = Path("data")
    CONFIG_FILE: Path = Path("data/config.json")
    PRICE_HISTORY_FILE: Path = Path("data/price_history.json")
    LOG_DIR: Path = Path("data/logs")
    
    # Email settings (from environment)
    SMTP_SENDER_EMAIL: Optional[str] = None
    SMTP_SENDER_PASSWORD: Optional[str] = None
    SMTP_RECIPIENT_EMAIL: Optional[str] = None
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    
    # Monitoring settings
    DEFAULT_CHECK_INTERVAL: int = 300  # 5 hours in minutes
    MAX_CHECK_INTERVAL: int = 1440     # 24 hours in minutes
    MIN_CHECK_INTERVAL: int = 60       # 1 hour in minutes
    
    # Crawling settings
    CRAWL_DELAY: int = 5  # Seconds between requests
    CRAWL_TIMEOUT: int = 30  # Seconds
    MAX_RETRIES: int = 3
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Assemble CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @model_validator(mode="after")
    def create_directories(self):
        """Create directories if they don't exist"""
        # Convert string paths to Path objects and create directories
        if isinstance(self.DATA_DIR, str):
            self.DATA_DIR = Path(self.DATA_DIR)
        if isinstance(self.LOG_DIR, str):
            self.LOG_DIR = Path(self.LOG_DIR)
        if isinstance(self.CONFIG_FILE, str):
            self.CONFIG_FILE = Path(self.CONFIG_FILE)
        if isinstance(self.PRICE_HISTORY_FILE, str):
            self.PRICE_HISTORY_FILE = Path(self.PRICE_HISTORY_FILE)
            
        # Create directories
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Update file paths to use DATA_DIR if they're relative
        if not self.CONFIG_FILE.is_absolute():
            self.CONFIG_FILE = self.DATA_DIR / self.CONFIG_FILE.name
        if not self.PRICE_HISTORY_FILE.is_absolute():
            self.PRICE_HISTORY_FILE = self.DATA_DIR / self.PRICE_HISTORY_FILE.name
            
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()