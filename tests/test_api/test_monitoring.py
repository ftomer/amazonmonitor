"""
Tests for monitoring API endpoints
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


class TestMonitoringAPI:
    """Test monitoring API endpoints"""
    
    def test_start_monitoring(self, client: TestClient):
        """Test starting monitoring"""
        response = client.post("/api/v1/monitor/start")
        
        # Should either start successfully or indicate already running
        assert response.status_code in [200, 400]
        
        data = response.json()
        assert "message" in data
    
    def test_stop_monitoring(self, client: TestClient):
        """Test stopping monitoring"""
        # Try to start first
        client.post("/api/v1/monitor/start")
        
        # Then stop
        response = client.post("/api/v1/monitor/stop")
        
        assert response.status_code in [200, 400]  # Success or not running
        data = response.json()
        assert "message" in data
    
    @patch('app.services.price_extractor.PriceExtractor.extract_price')
    def test_check_prices_now(self, mock_extract, client: TestClient):
        """Test manual price check"""
        # Mock the price extraction
        mock_extract.return_value = 45.99
        
        # Add a product first
        product_data = {
            "name": "Test Check Product",
            "url": "https://www.amazon.com/test-check/dp/B333333333",
            "target_price": 50.00
        }
        
        add_response = client.post("/api/v1/products/", json=product_data)
        assert add_response.status_code == 200
        
        # Check prices now
        response = client.post("/api/v1/monitor/check-now")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            result = data[0]
            assert "name" in result
            assert "current_price" in result or "error" in result
    
    def test_get_price_history(self, client: TestClient):
        """Test getting price history"""
        response = client.get("/api/v1/monitor/price-history")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be a dictionary (could be empty)
        assert isinstance(data, dict)
    
    def test_get_logs(self, client: TestClient):
        """Test getting logs"""
        response = client.get("/api/v1/monitor/logs")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert isinstance(data["logs"], list)
    
    def test_get_logs_with_limit(self, client: TestClient):
        """Test getting logs with line limit"""
        response = client.get("/api/v1/monitor/logs?lines=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert isinstance(data["logs"], list)
        assert len(data["logs"]) <= 10