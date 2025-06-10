"""
Main API router for Amazon Price Monitor
"""

from fastapi import APIRouter

from app.api.v1.endpoints import products, monitoring, status

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(monitoring.router, prefix="/monitor", tags=["monitoring"])

from app.api.v1.endpoints.monitoring import router as monitor_router

# Add config
@api_router.get("/config")
async def get_config():
    """Get current monitoring configuration - redirect to proper endpoint"""
    from app.api.deps import get_price_monitor_service
    from app.models.monitoring import MonitorConfig, NotificationSettings
    from app.models.product import Product
    
    service = get_price_monitor_service()
    config = service.config
    
    # Convert to Pydantic model
    products = [
        Product(
            name=p["name"],
            url=p["url"],
            target_price=p["target_price"]
        )
        for p in config.get("products", [])
    ]
    
    email_config = config.get("email_notifications", {})
    notifications = NotificationSettings(
        email_enabled=email_config.get("enabled", False),
        desktop_enabled=config.get("desktop_notifications", {}).get("enabled", True),
        smtp_server=email_config.get("smtp_server"),
        smtp_port=email_config.get("smtp_port"),
        sender_email=email_config.get("sender_email"),
        recipient_email=email_config.get("recipient_email")
    )
    
    return MonitorConfig(
        products=products,
        check_interval_minutes=config.get("check_interval_minutes", 300),
        email_notifications=notifications
    )

@api_router.put("/config")
async def update_config(config):
    """Update monitoring configuration"""
    from app.api.deps import get_price_monitor_service
    import os
    import json
    
    service = get_price_monitor_service()
    
    # Convert Pydantic model back to dict
    new_config = {
        "products": [
            {
                "name": p.get("name"),
                "url": str(p.get("url")),
                "target_price": p.get("target_price")
            }
            for p in config.get("products", [])
        ],
        "check_interval_minutes": config.get("check_interval_minutes", 300),
        "email_notifications": {
            "enabled": config.get("email_notifications", {}).get("email_enabled", False),
            "smtp_server": config.get("email_notifications", {}).get("smtp_server") or os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": config.get("email_notifications", {}).get("smtp_port") or int(os.getenv("SMTP_PORT", "587")),
            "sender_email": config.get("email_notifications", {}).get("sender_email") or os.getenv("SMTP_SENDER_EMAIL", ""),
            "sender_password": os.getenv("SMTP_SENDER_PASSWORD", ""),
            "recipient_email": config.get("email_notifications", {}).get("recipient_email") or os.getenv("SMTP_RECIPIENT_EMAIL", "")
        },
        "desktop_notifications": {
            "enabled": config.get("email_notifications", {}).get("desktop_enabled", True)
        }
    }
    
    # Save to file
    with open("config.json", "w") as f:
        json.dump(new_config, f, indent=4)
    
    # Reload monitor config
    service.config = new_config
    
    return {"message": "Configuration updated successfully"}

