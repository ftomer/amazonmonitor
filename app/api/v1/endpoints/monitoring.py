"""
Monitoring API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.services.price_monitor import PriceMonitorService
from app.models.monitoring import PriceCheck
from app.api.deps import get_price_monitor_service
from app.utils.exceptions import PriceMonitorError

router = APIRouter()

@router.post("/start")
async def start_monitoring(
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Start price monitoring"""
    try:
        await service.start_monitoring()
        return {"message": "Monitoring started successfully"}
    except PriceMonitorError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stop")
async def stop_monitoring(
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Stop price monitoring"""
    try:
        await service.stop_monitoring()
        return {"message": "Monitoring stopped successfully"}
    except PriceMonitorError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/check-now", response_model=List[PriceCheck])
async def check_prices_now(
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Manually trigger price check for all products"""
    results = await service.check_all_products()
    return [PriceCheck(**result) for result in results]

@router.get("/price-history")
async def get_price_history(
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Get price history data"""
    return service.price_history

@router.get("/logs")
async def get_logs(
    lines: int = 100,
    service: PriceMonitorService = Depends(get_price_monitor_service)
):
    """Get recent log entries"""
    try:
        from app.core.config import settings
        log_file = settings.LOG_DIR / "app.log"
        
        if log_file.exists():
            with open(log_file, "r") as f:
                log_lines = f.readlines()
            return {"logs": log_lines[-lines:] if len(log_lines) > lines else log_lines}
        else:
            return {"logs": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read logs: {e}")
