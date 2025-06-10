"""
Tests for PriceMonitorService
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.price_monitor import PriceMonitorService
from app.utils.exceptions import PriceMonitorError


class TestPriceMonitorService:
    """Test PriceMonitorService functionality"""
    
    @pytest.fixture
    async def service(self, test_settings, test_config, monkeypatch):
        """Create a price monitor service for testing"""
        monkeypatch.setattr("app.core.config.settings", test_settings)
        
        # Create config file
        with open(test_settings.CONFIG_FILE, 'w') as f:
            json.dump(test_config, f)
        
        service = PriceMonitorService()
        yield service
        
        if service.is_monitoring:
            await service.stop_monitoring()
    
    def test_load_config(self, service, test_config):
        """Test configuration loading"""
        assert service.config == test_config
        assert len(service.get_products()) == 2
    
    def test_get_products(self, service):
        """Test getting products"""
        products = service.get_products()
        
        assert isinstance(products, list)
        assert len(products) == 2
        assert products[0]["name"] == "Test Product 1"
        assert products[1]["name"] == "Test Product 2"
    
    def test_add_product(self, service):
        """Test adding a new product"""
        new_product = {
            "name": "New Test Product",
            "url": "https://www.amazon.com/new-test/dp/B444444444",
            "target_price": 75.00
        }
        
        result = service.add_product(new_product)
        
        assert result == new_product
        products = service.get_products()
        assert len(products) == 3
        assert products[-1]["name"] == "New Test Product"
    
    def test_update_product(self, service):
        """Test updating an existing product"""
        updates = {
            "name": "Updated Test Product",
            "target_price": 60.00
        }
        
        result = service.update_product(0, updates)
        
        assert result["name"] == "Updated Test Product"
        assert result["target_price"] == 60.00
        assert result["url"] == "https://www.amazon.com/test-product-1/dp/B123456789"
    
    def test_update_nonexistent_product(self, service):
        """Test updating a product that doesn't exist"""
        with pytest.raises(PriceMonitorError, match="Product not found"):
            service.update_product(999, {"name": "Should fail"})
    
    def test_delete_product(self, service):
        """Test deleting a product"""
        original_count = len(service.get_products())
        
        removed = service.delete_product(0)
        
        assert removed["name"] == "Test Product 1"
        assert len(service.get_products()) == original_count - 1
    
    def test_delete_nonexistent_product(self, service):
        """Test deleting a product that doesn't exist"""
        with pytest.raises(PriceMonitorError, match="Product not found"):
            service.delete_product(999)
    
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_single_product_success(self, mock_extract, service):
        """Test checking a single product successfully"""
        mock_extract.return_value = 45.99
        
        product = service.get_products()[0]
        result = await service.check_single_product(product)
        
        assert result["name"] == "Test Product 1"
        assert result["current_price"] == 45.99
        assert result["target_price"] == 50.00
        assert result["price_met"] is True  # 45.99 <= 50.00
    
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_single_product_price_not_met(self, mock_extract, service):
        """Test checking a single product where target not met"""
        mock_extract.return_value = 55.99
        
        product = service.get_products()[0]
        result = await service.check_single_product(product)
        
        assert result["current_price"] == 55.99
        assert result["price_met"] is False  # 55.99 > 50.00
    
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_single_product_extraction_failure(self, mock_extract, service):
        """Test checking a single product when price extraction fails"""
        mock_extract.return_value = None
        
        product = service.get_products()[0]
        result = await service.check_single_product(product)
        
        assert "error" in result
        assert result["name"] == "Test Product 1"
    
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    async def test_check_all_products(self, mock_extract, service):
        """Test checking all products"""
        mock_extract.side_effect = [45.99, 95.00]  # Two different prices
        
        results = await service.check_all_products()
        
        assert len(results) == 2
        assert results[0]["current_price"] == 45.99
        assert results[1]["current_price"] == 95.00
        assert results[0]["price_met"] is True   # 45.99 <= 50.00
        assert results[1]["price_met"] is True   # 95.00 <= 100.00
    
    async def test_start_monitoring(self, service):
        """Test starting monitoring"""
        assert not service.is_monitoring
        
        await service.start_monitoring()
        
        assert service.is_monitoring
        assert service.monitor_task is not None
    
    async def test_start_monitoring_already_running(self, service):
        """Test starting monitoring when already running"""
        await service.start_monitoring()
        
        with pytest.raises(PriceMonitorError, match="already running"):
            await service.start_monitoring()
    
    async def test_stop_monitoring(self, service):
        """Test stopping monitoring"""
        await service.start_monitoring()
        assert service.is_monitoring
        
        await service.stop_monitoring()
        
        assert not service.is_monitoring
    
    async def test_stop_monitoring_not_running(self, service):
        """Test stopping monitoring when not running"""
        assert not service.is_monitoring
        
        with pytest.raises(PriceMonitorError, match="not running"):
            await service.stop_monitoring()
    
    def test_get_status(self, service):
        """Test getting service status"""
        status = service.get_status()
        
        assert "is_running" in status
        assert "total_products" in status
        assert "check_interval_minutes" in status
        assert status["is_running"] is False
        assert status["total_products"] == 2
    
    def test_validate_config_valid(self, service):
        """Test config validation with valid data"""
        valid_config = {
            "products": [],
            "check_interval_minutes": 120,
            "email_notifications": {"enabled": False}
        }
        
        # Should not raise an exception
        service._validate_config(valid_config)
    
    def test_validate_config_missing_field(self, service):
        """Test config validation with missing required field"""
        invalid_config = {
            "check_interval_minutes": 120
            # Missing "products" field
        }
        
        with pytest.raises(PriceMonitorError, match="Missing required field"):
            service._validate_config(invalid_config)
    
    def test_validate_config_invalid_interval(self, service):
        """Test config validation with invalid check interval"""
        invalid_config = {
            "products": [],
            "check_interval_minutes": 30  # Too short (< 60)
        }
        
        with pytest.raises(PriceMonitorError, match="Check interval must be"):
            service._validate_config(invalid_config)