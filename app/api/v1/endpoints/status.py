"""
Status API endpoints
"""

from fastapi import APIRouter, Depends
from app.services.price_monitor import PriceMonitorService
from app.models.monitoring import MonitorStatus
from app.api.deps import get_price_monitor_service

router = APIRouter()

@router.get("/", response_model=MonitorStatus)
async def get_status(
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Get current monitoring status"""
    return service.get_status()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
