"""
API dependencies
"""

from app.services.price_monitor import PriceMonitorService

# Global service instance
_price_monitor_service = None

def get_price_monitor_service() -> PriceMonitorService:
    """Get price monitor service instance"""
    global _price_monitor_service
    if _price_monitor_service is None:
        _price_monitor_service = PriceMonitorService()
    return _price_monitor_service
