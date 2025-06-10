"""
Tests for status API endpoints

run with:
python -m pytest tests/test_api/test_status.py -v
"""

from fastapi.testclient import TestClient


class TestStatusAPI:
    """Test status API endpoints"""
    
    def test_get_status(self, client: TestClient):
        """Test getting monitor status"""
        response = client.get("/api/v1/status/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "is_running" in data
        assert "total_products" in data
        assert isinstance(data["is_running"], bool)
        assert isinstance(data["total_products"], int)
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/api/v1/status/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        # Should return either file response or JSON
        if response.headers.get("content-type") == "application/json":
            data = response.json()
            assert "message" in data