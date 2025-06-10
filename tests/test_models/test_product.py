"""
Tests for Product models
"""

import pytest
from pydantic import ValidationError
from app.models.product import Product, ProductCreate, ProductUpdate


class TestProductModels:
    """Test Product model validation"""
    
    def test_product_create_valid(self):
        """Test creating a valid product"""
        product_data = {
            "name": "Test Product",
            "url": "https://www.amazon.com/test-product/dp/B123456789",
            "target_price": 50.00
        }
        
        product = ProductCreate(**product_data)
        
        assert product.name == "Test Product"
        assert str(product.url) == "https://www.amazon.com/test-product/dp/B123456789"
        assert product.target_price == 50.00
    
    def test_product_create_invalid_url(self):
        """Test creating product with invalid URL"""
        product_data = {
            "name": "Test Product",
            "url": "not-a-valid-url",
            "target_price": 50.00
        }
        
        with pytest.raises(ValidationError):
            ProductCreate(**product_data)
    
    def test_product_create_negative_price(self):
        """Test creating product with negative price"""
        product_data = {
            "name": "Test Product",
            "url": "https://www.amazon.com/test-product/dp/B123456789",
            "target_price": -10.00
        }
        
        with pytest.raises(ValidationError, match="Target price must be positive"):
            ProductCreate(**product_data)
    
    def test_product_create_zero_price(self):
        """Test creating product with zero price"""
        product_data = {
            "name": "Test Product",
            "url": "https://www.amazon.com/test-product/dp/B123456789",
            "target_price": 0.00
        }
        
        with pytest.raises(ValidationError, match="Target price must be positive"):
            ProductCreate(**product_data)
    
    def test_product_update_partial(self):
        """Test partial product update"""
        update_data = {
            "name": "Updated Name",
            "target_price": 75.00
        }
        
        update = ProductUpdate(**update_data)
        
        assert update.name == "Updated Name"
        assert update.url is None
        assert update.target_price == 75.00
    
    def test_product_update_empty(self):
        """Test empty product update"""
        update = ProductUpdate()
        
        assert update.name is None
        assert update.url is None
        assert update.target_price is None
    
    def test_product_update_negative_price(self):
        """Test product update with negative price"""
        update_data = {
            "target_price": -5.00
        }
        
        with pytest.raises(ValidationError, match="Target price must be positive"):
            ProductUpdate(**update_data)
    
    def test_product_full_model(self):
        """Test full Product model"""
        product_data = {
            "name": "Full Test Product",
            "url": "https://www.amazon.com/full-test/dp/B987654321",
            "target_price": 99.99
        }
        
        product = Product(**product_data)
        
        assert product.name == "Full Test Product"
        assert str(product.url) == "https://www.amazon.com/full-test/dp/B987654321"
        assert product.target_price == 99.99
    
    def test_product_model_inheritance(self):
        """Test that Product inherits from ProductBase correctly"""
        product_data = {
            "name": "Inheritance Test",
            "url": "https://www.amazon.com/inheritance/dp/B111111111",
            "target_price": 25.50
        }
        
        # Both should work identically
        product_create = ProductCreate(**product_data)
        product = Product(**product_data)
        
        assert product_create.name == product.name
        assert product_create.url == product.url
        assert product_create.target_price == product.target_price
    
    def test_product_json_serialization(self):
        """Test JSON serialization of product models"""
        product_data = {
            "name": "JSON Test Product",
            "url": "https://www.amazon.com/json-test/dp/B222222222",
            "target_price": 33.33
        }
        
        product = Product(**product_data)
        json_data = product.dict()
        
        assert json_data["name"] == "JSON Test Product"
        assert json_data["url"] == "https://www.amazon.com/json-test/dp/B222222222"
        assert json_data["target_price"] == 33.33