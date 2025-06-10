"""
Pytest configuration and fixtures for Amazon Price Monitor tests
"""

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.config import Settings, settings
from app.services.price_monitor import PriceMonitorService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with temporary directories"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        test_settings = Settings(
            PROJECT_NAME="Amazon Price Monitor Test",
            DEBUG=True,
            LOG_LEVEL="DEBUG",
            DATA_DIR=temp_path / "data",
            CONFIG_FILE=temp_path / "data" / "config.json",
            PRICE_HISTORY_FILE=temp_path / "data" / "price_history.json",
            LOG_DIR=temp_path / "data" / "logs",
            DEFAULT_CHECK_INTERVAL=60,
            CRAWL_DELAY=1,  # Faster for tests
            MAX_RETRIES=2   # Fewer retries for tests
        )
        
        # Create directories
        test_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
        test_settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        yield test_settings


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Sample test configuration"""
    return {
        "products": [
            {
                "name": "Test Product 1",
                "url": "https://www.amazon.com/test-product-1/dp/B123456789",
                "target_price": 50.00
            },
            {
                "name": "Test Product 2", 
                "url": "https://www.amazon.com/test-product-2/dp/B987654321",
                "target_price": 100.00
            }
        ],
        "check_interval_minutes": 60,
        "email_notifications": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "test@example.com",
            "recipient_email": "recipient@example.com"
        },
        "desktop_notifications": {
            "enabled": True
        }
    }


@pytest.fixture
def mock_price_extractor():
    """Mock price extractor for testing"""
    mock = AsyncMock()
    mock.extract_price.return_value = 45.99
    return mock


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing"""
    mock = AsyncMock()
    mock.send_price_alert.return_value = None
    return mock


@pytest.fixture
async def price_monitor_service(test_settings, test_config, monkeypatch):
    """Create a price monitor service for testing"""
    # Patch the settings
    monkeypatch.setattr("app.core.config.settings", test_settings)
    
    # Create config file
    with open(test_settings.CONFIG_FILE, 'w') as f:
        json.dump(test_config, f)
    
    service = PriceMonitorService()
    yield service
    
    # Cleanup
    if service.is_monitoring:
        await service.stop_monitoring()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> Generator[AsyncClient, None, None]:
    """Create an async test client for the FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_products():
    """Sample products for testing"""
    return [
        {
            "name": "Echo Dot (3rd Gen)",
            "url": "https://www.amazon.com/gp/product/B0757911C2",
            "target_price": 30.00
        },
        {
            "name": "iPad Air",
            "url": "https://www.amazon.com/gp/product/B09G9FPHY6", 
            "target_price": 500.00
        }
    ]


@pytest.fixture
def sample_price_history():
    """Sample price history data"""
    return {
        "https://www.amazon.com/gp/product/B0757911C2": [
            {
                "timestamp": "2025-06-09T10:00:00",
                "price": 32.99
            },
            {
                "timestamp": "2025-06-09T14:00:00", 
                "price": 29.99
            }
        ],
        "https://www.amazon.com/gp/product/B09G9FPHY6": [
            {
                "timestamp": "2025-06-09T10:00:00",
                "price": 520.00
            }
        ]
    }


@pytest.fixture
def mock_html_content():
    """Mock HTML content from Amazon pages"""
    return """
    <html>
    <body>
        <span class="a-price-whole">29</span>
        <span class="a-price-fraction">99</span>
        <span id="productTitle">Test Product</span>
    </body>
    </html>
    """


@pytest.fixture
def mock_crawl4ai_result():
    """Mock Crawl4AI result"""
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.extracted_content = json.dumps({
        "price": "$29.99",
        "title": "Test Product"
    })
    mock_result.html = """
    <span class="a-price-whole">29</span>
    <span class="a-price-fraction">99</span>
    """
    return mock_result


# Pytest markers
pytestmark = pytest.mark.asyncio