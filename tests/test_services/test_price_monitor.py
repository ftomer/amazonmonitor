"""
Tests for PriceMonitorService

run with:
python -m pytest tests/test_services/test_price_monitor.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.price_monitor import PriceMonitorService
from app.utils.exceptions import PriceMonitorError


class TestPriceMonitorService:
    """Test PriceMonitorService functionality"""
    
    @pytest.fixture
    def isolated_service(self, test_settings, monkeypatch):
        """Create an isolated price monitor service for each test"""
        # Create a fresh temporary directory for each test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create isolated test settings
            isolated_settings = test_settings.__class__(
                PROJECT_NAME="Amazon Price Monitor Test",
                DEBUG=True,
                LOG_LEVEL="DEBUG",
                DATA_DIR=temp_path / "data",
                CONFIG_FILE=temp_path / "data" / "config.json",
                PRICE_HISTORY_FILE=temp_path / "data" / "price_history.json",
                LOG_DIR=temp_path / "data" / "logs",
                DEFAULT_CHECK_INTERVAL=60,
                CRAWL_DELAY=1,
                MAX_RETRIES=2
            )
            
            # Create directories
            isolated_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
            isolated_settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create fresh test config for each test
            fresh_config = {
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
            
            # Write config file
            with open(isolated_settings.CONFIG_FILE, 'w') as f:
                json.dump(fresh_config, f)
            
            monkeypatch.setattr("app.core.config.settings", isolated_settings)
            
            yield PriceMonitorService()
    
    def test_load_config(self, isolated_service):
        """Test configuration loading"""
        config = isolated_service.config
        assert len(config["products"]) == 2
        assert config["check_interval_minutes"] == 60
        assert len(isolated_service.get_products()) == 2
    
    def test_get_products(self, isolated_service):
        """Test getting products"""
        products = isolated_service.get_products()
        
        assert isinstance(products, list)
        assert len(products) == 2
        assert products[0]["name"] == "Test Product 1"
        assert products[1]["name"] == "Test Product 2"
    
    def test_add_product(self, isolated_service):
        """Test adding a new product"""
        new_product = {
            "name": "New Test Product",
            "url": "https://www.amazon.com/new-test/dp/B444444444",
            "target_price": 75.00
        }
        
        result = isolated_service.add_product(new_product)
        
        assert result == new_product
        products = isolated_service.get_products()
        assert len(products) == 3
        assert products[-1]["name"] == "New Test Product"
    
    def test_update_product(self, isolated_service):
        """Test updating an existing product"""
        updates = {
            "name": "Updated Test Product",
            "target_price": 60.00
        }
        
        result = isolated_service.update_product(0, updates)
        
        assert result["name"] == "Updated Test Product"
        assert result["target_price"] == 60.00
        assert result["url"] == "https://www.amazon.com/test-product-1/dp/B123456789"
    
    def test_update_nonexistent_product(self, isolated_service):
        """Test updating a product that doesn't exist"""
        with pytest.raises(PriceMonitorError, match="Product not found"):
            isolated_service.update_product(999, {"name": "Should fail"})
    
    def test_delete_product(self, isolated_service):
        """Test deleting a product"""
        original_count = len(isolated_service.get_products())
        
        removed = isolated_service.delete_product(0)
        
        assert removed["name"] == "Test Product 1"
        assert len(isolated_service.get_products()) == original_count - 1
    
    def test_delete_nonexistent_product(self, isolated_service):
        """Test deleting a product that doesn't exist"""
        with pytest.raises(PriceMonitorError, match="Product not found"):
            isolated_service.delete_product(999)
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_single_product_success(self, mock_extract, isolated_service):
        """Test checking a single product successfully"""
        mock_extract.return_value = 45.99
        
        product = isolated_service.get_products()[0]
        result = await isolated_service.check_single_product(product)
        
        assert result["name"] == "Test Product 1"
        assert result["current_price"] == 45.99
        assert result["target_price"] == 50.00
        assert result["price_met"] is True  # 45.99 <= 50.00
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_single_product_price_not_met(self, mock_extract, isolated_service):
        """Test checking a single product where target not met"""
        mock_extract.return_value = 55.99
        
        product = isolated_service.get_products()[0]
        result = await isolated_service.check_single_product(product)
        
        assert result["current_price"] == 55.99
        assert result["price_met"] is False  # 55.99 > 50.00
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_single_product_extraction_failure(self, mock_extract, isolated_service):
        """Test checking a single product when price extraction fails"""
        mock_extract.return_value = None
        
        product = isolated_service.get_products()[0]
        result = await isolated_service.check_single_product(product)
        
        assert "error" in result
        assert result["name"] == "Test Product 1"
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_all_products(self, mock_extract, isolated_service):
        """Test checking all products"""
        mock_extract.side_effect = [45.99, 95.00]  # Two different prices
        
        results = await isolated_service.check_all_products()
        
        assert len(results) == 2
        assert results[0]["current_price"] == 45.99
        assert results[1]["current_price"] == 95.00
        assert results[0]["price_met"] is True   # 45.99 <= 50.00
        assert results[1]["price_met"] is True   # 95.00 <= 100.00
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, isolated_service):
        """Test starting monitoring"""
        assert not isolated_service.is_monitoring
        
        await isolated_service.start_monitoring()
        
        assert isolated_service.is_monitoring
        assert isolated_service.monitor_task is not None
        
        # Clean up
        await isolated_service.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_start_monitoring_already_running(self, isolated_service):
        """Test starting monitoring when already running"""
        await isolated_service.start_monitoring()
        
        with pytest.raises(PriceMonitorError, match="already running"):
            await isolated_service.start_monitoring()
        
        # Clean up
        await isolated_service.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, isolated_service):
        """Test stopping monitoring"""
        await isolated_service.start_monitoring()
        assert isolated_service.is_monitoring
        
        await isolated_service.stop_monitoring()
        
        assert not isolated_service.is_monitoring
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_not_running(self, isolated_service):
        """Test stopping monitoring when not running"""
        assert not isolated_service.is_monitoring
        
        with pytest.raises(PriceMonitorError, match="not running"):
            await isolated_service.stop_monitoring()
    
    def test_get_status(self, isolated_service):
        """Test getting service status"""
        status = isolated_service.get_status()
        
        assert "is_running" in status
        assert "total_products" in status
        assert "check_interval_minutes" in status
        assert status["is_running"] is False
        assert status["total_products"] == 2
    
    def test_validate_config_valid(self, isolated_service):
        """Test config validation with valid data"""
        valid_config = {
            "products": [],
            "check_interval_minutes": 120,
            "email_notifications": {"enabled": False}
        }
        
        # Should not raise an exception
        isolated_service._validate_config(valid_config)
    
    def test_validate_config_missing_field(self, isolated_service):
        """Test config validation with missing required field"""
        invalid_config = {
            "check_interval_minutes": 120
            # Missing "products" field
        }
        
        with pytest.raises(PriceMonitorError, match="Missing required field"):
            isolated_service._validate_config(invalid_config)
    
    def test_validate_config_invalid_interval(self, isolated_service):
        """Test config validation with invalid check interval"""
        invalid_config = {
            "products": [],
            "check_interval_minutes": 30  # Too short (< 60)
        }
        
        with pytest.raises(PriceMonitorError, match="Check interval must be"):
            isolated_service._validate_config(invalid_config)
    
    @pytest.mark.asyncio
    async def test_save_config(self, isolated_service):
        """Test saving configuration to file"""
        # Add a new product
        new_product = {
            "name": "Test Save Product",
            "url": "https://www.amazon.com/save-test/dp/B555555555",
            "target_price": 88.00
        }
        isolated_service.add_product(new_product)
        
        # Use the correct private method name
        isolated_service._save_config()
        
        # Verify file was written by reading it
        from app.core.config import settings
        assert settings.CONFIG_FILE.exists()
        
        # Load and verify content
        with open(settings.CONFIG_FILE, 'r') as f:
            saved_config = json.load(f)
        
        assert len(saved_config["products"]) == 3
        assert saved_config["products"][-1]["name"] == "Test Save Product"
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_integration(self, isolated_service):
        """Test that monitoring can start and stop without errors"""
        with patch('app.services.price_extractor.PriceExtractor.extract_price') as mock_extract:
            mock_extract.return_value = 45.99
            
            # Start monitoring
            await isolated_service.start_monitoring()
            assert isolated_service.is_monitoring
            
            # Let it run briefly
            import asyncio
            await asyncio.sleep(0.1)
            
            # Stop monitoring
            await isolated_service.stop_monitoring()
            assert not isolated_service.is_monitoring
    
    def test_product_crud_operations(self, isolated_service):
        """Test complete CRUD operations on products"""
        initial_count = len(isolated_service.get_products())
        
        # Create
        new_product = {
            "name": "CRUD Test Product",
            "url": "https://www.amazon.com/crud-test/dp/B666666666",
            "target_price": 25.00
        }
        added = isolated_service.add_product(new_product)
        assert len(isolated_service.get_products()) == initial_count + 1
        
        # Read
        products = isolated_service.get_products()
        crud_product = products[-1]
        assert crud_product["name"] == "CRUD Test Product"
        
        # Update
        updates = {"target_price": 30.00}
        updated = isolated_service.update_product(len(products) - 1, updates)
        assert updated["target_price"] == 30.00
        assert updated["name"] == "CRUD Test Product"  # Unchanged
        
        # Delete
        deleted = isolated_service.delete_product(len(isolated_service.get_products()) - 1)
        assert deleted["name"] == "CRUD Test Product"
        assert len(isolated_service.get_products()) == initial_count