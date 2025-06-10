"""
Products API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.services.price_monitor import PriceMonitorService
from app.models.product import Product, ProductCreate, ProductUpdate
from app.api.deps import get_price_monitor_service
from app.utils.exceptions import PriceMonitorError

router = APIRouter()

@router.get("/", response_model=List[Product])
async def get_products(
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Get all monitored products"""
    products = service.get_products()
    return [Product(**product) for product in products]

@router.post("/", response_model=Product)
async def add_product(
    product: ProductCreate,
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Add a new product to monitor"""
    try:
        product_dict = {
            "name": product.name,
            "url": str(product.url),
            "target_price": product.target_price
        }
        result = service.add_product(product_dict)
        return Product(**result)
    except PriceMonitorError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{product_index}", response_model=Product)
async def update_product(
    product_index: int,
    product_update: ProductUpdate,
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Update a specific product"""
    try:
        updates = {}
        if product_update.name is not None:
            updates["name"] = product_update.name
        if product_update.url is not None:
            updates["url"] = str(product_update.url)
        if product_update.target_price is not None:
            updates["target_price"] = product_update.target_price
        
        result = service.update_product(product_index, updates)
        return Product(**result)
    except PriceMonitorError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))

@router.delete("/{product_index}")
async def delete_product(
    product_index: int,
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Delete a product from monitoring"""
    try:
        removed = service.delete_product(product_index)
        return {"message": f"Product '{removed['name']}' removed successfully"}
    except PriceMonitorError as e:
        raise HTTPException(status_code=404, detail=str(e))
