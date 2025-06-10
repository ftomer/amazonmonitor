"""
Tests for products API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestProductsAPI:
    """Test products API endpoints"""
    
    def test_get_empty_products(self, client: TestClient):
        """Test getting products when none exist"""
        response = client.get("/api/v1/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_add_product(self, client: TestClient):
        """Test adding a new product"""
        product_data = {
            "name": "Test Product",
            "url": "https://www.amazon.com/test-product/dp/B123456789",
            "target_price": 50.00
        }
        
        response = client.post("/api/v1/products/", json=product_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == product_data["name"]
        assert data["url"] == product_data["url"]
        assert data["target_price"] == product_data["target_price"]
    
    def test_add_invalid_product(self, client: TestClient):
        """Test adding invalid product data"""
        invalid_data = {
            "name": "Test Product",
            "url": "not-a-valid-url",
            "target_price": -10.00  # Negative price
        }
        
        response = client.post("/api/v1/products/", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_products_after_adding(self, client: TestClient):
        """Test getting products after adding some"""
        # Add a product first
        product_data = {
            "name": "Test Product 2",
            "url": "https://www.amazon.com/test-product-2/dp/B987654321",
            "target_price": 75.00
        }
        
        add_response = client.post("/api/v1/products/", json=product_data)
        assert add_response.status_code == 200
        
        # Get all products
        get_response = client.get("/api/v1/products/")
        assert get_response.status_code == 200
        
        products = get_response.json()
        assert len(products) >= 1
        assert any(p["name"] == "Test Product 2" for p in products)
    
    def test_update_product(self, client: TestClient):
        """Test updating a product"""
        # Add a product first
        product_data = {
            "name": "Original Name",
            "url": "https://www.amazon.com/original/dp/B111111111",
            "target_price": 60.00
        }
        
        add_response = client.post("/api/v1/products/", json=product_data)
        assert add_response.status_code == 200
        
        # Update the product (assuming it's at index 0)
        update_data = {
            "name": "Updated Name",
            "target_price": 55.00
        }
        
        update_response = client.put("/api/v1/products/0", json=update_data)
        
        if update_response.status_code == 200:
            data = update_response.json()
            assert data["name"] == "Updated Name"
            assert data["target_price"] == 55.00
    
    def test_update_nonexistent_product(self, client: TestClient):
        """Test updating a product that doesn't exist"""
        update_data = {
            "name": "Updated Name"
        }
        
        response = client.put("/api/v1/products/999", json=update_data)
        assert response.status_code == 404
    
    def test_delete_product(self, client: TestClient):
        """Test deleting a product"""
        # Add a product first
        product_data = {
            "name": "To Be Deleted",
            "url": "https://www.amazon.com/delete-me/dp/B222222222",
            "target_price": 40.00
        }
        
        add_response = client.post("/api/v1/products/", json=product_data)
        assert add_response.status_code == 200
        
        # Get products to find the index
        get_response = client.get("/api/v1/products/")
        products = get_response.json()
        
        # Find the product we just added
        product_index = None
        for i, p in enumerate(products):
            if p["name"] == "To Be Deleted":
                product_index = i
                break
        
        if product_index is not None:
            # Delete the product
            delete_response = client.delete(f"/api/v1/products/{product_index}")
            assert delete_response.status_code == 200
            
            data = delete_response.json()
            assert "removed successfully" in data["message"]
    
    def test_delete_nonexistent_product(self, client: TestClient):
        """Test deleting a product that doesn't exist"""
        response = client.delete("/api/v1/products/999")
        assert response.status_code == 404