#!/usr/bin/env python3
"""
FastAPI Backend for Amazon Price Monitor
Provides REST API endpoints for managing price monitoring
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
import uvicorn

# Import our price monitor
from amazon_price_monitor import AmazonPriceMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class Product(BaseModel):
    name: str
    url: HttpUrl
    target_price: float

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    target_price: Optional[float] = None

class NotificationSettings(BaseModel):
    email_enabled: bool = False
    desktop_enabled: bool = True
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    sender_email: Optional[str] = None
    sender_password: Optional[str] = None
    recipient_email: Optional[str] = None

class MonitorConfig(BaseModel):
    products: List[Product]
    check_interval_minutes: int = 60
    email_notifications: NotificationSettings

class PriceAlert(BaseModel):
    product_name: str
    current_price: float
    target_price: float
    timestamp: datetime
    url: str

class MonitorStatus(BaseModel):
    is_running: bool
    last_check: Optional[datetime]
    total_products: int
    active_alerts: int

# Global variables
app = FastAPI(title="Amazon Price Monitor", version="1.0.0")
monitor: Optional[AmazonPriceMonitor] = None
monitor_task: Optional[asyncio.Task] = None
is_monitoring = False

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for React frontend
static_path = Path("frontend/build")
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path / "static")), name="static")

@app.on_startup
async def startup_event():
    """Initialize the monitor on startup"""
    global monitor
    monitor = AmazonPriceMonitor()
    logger.info("Amazon Price Monitor API started")

@app.on_shutdown
async def shutdown_event():
    """Cleanup on shutdown"""
    global monitor_task
    if monitor_task and not monitor_task.done():
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    logger.info("Amazon Price Monitor API shut down")

# API Endpoints

@app.get("/")
async def read_root():
    """Serve React frontend"""
    frontend_path = static_path / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    return {"message": "Amazon Price Monitor API", "docs": "/docs"}

@app.get("/api/status", response_model=MonitorStatus)
async def get_monitor_status():
    """Get current monitoring status"""
    global monitor, is_monitoring
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    total_products = len(monitor.config.get("products", []))
    
    return MonitorStatus(
        is_running=is_monitoring,
        last_check=datetime.now() if is_monitoring else None,
        total_products=total_products,
        active_alerts=0  # You can implement alert counting logic
    )

@app.get("/api/config", response_model=MonitorConfig)
async def get_config():
    """Get current monitoring configuration"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    config = monitor.config
    
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
        check_interval_minutes=config.get("check_interval_minutes", 60),
        email_notifications=notifications
    )

@app.put("/api/config")
async def update_config(config: MonitorConfig):
    """Update monitoring configuration"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    # Convert Pydantic model back to dict
    new_config = {
        "products": [
            {
                "name": p.name,
                "url": str(p.url),
                "target_price": p.target_price
            }
            for p in config.products
        ],
        "check_interval_minutes": config.check_interval_minutes,
        "email_notifications": {
            "enabled": config.email_notifications.email_enabled,
            "smtp_server": config.email_notifications.smtp_server or "smtp.gmail.com",
            "smtp_port": config.email_notifications.smtp_port or 587,
            "sender_email": config.email_notifications.sender_email or "",
            "sender_password": config.email_notifications.sender_password or "",
            "recipient_email": config.email_notifications.recipient_email or ""
        },
        "desktop_notifications": {
            "enabled": config.email_notifications.desktop_enabled
        }
    }
    
    # Save to file
    with open("config.json", "w") as f:
        json.dump(new_config, f, indent=4)
    
    # Reload monitor config
    monitor.config = new_config
    
    return {"message": "Configuration updated successfully"}

@app.get("/api/products", response_model=List[Product])
async def get_products():
    """Get all monitored products"""
    config = await get_config()
    return config.products

@app.post("/api/products", response_model=Product)
async def add_product(product: Product):
    """Add a new product to monitor"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    # Add to current config
    monitor.config["products"].append({
        "name": product.name,
        "url": str(product.url),
        "target_price": product.target_price
    })
    
    # Save to file
    with open("config.json", "w") as f:
        json.dump(monitor.config, f, indent=4)
    
    return product

@app.put("/api/products/{product_index}")
async def update_product(product_index: int, product_update: ProductUpdate):
    """Update a specific product"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    products = monitor.config.get("products", [])
    
    if product_index < 0 or product_index >= len(products):
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields if provided
    if product_update.name is not None:
        products[product_index]["name"] = product_update.name
    if product_update.url is not None:
        products[product_index]["url"] = str(product_update.url)
    if product_update.target_price is not None:
        products[product_index]["target_price"] = product_update.target_price
    
    # Save to file
    with open("config.json", "w") as f:
        json.dump(monitor.config, f, indent=4)
    
    return products[product_index]

@app.delete("/api/products/{product_index}")
async def delete_product(product_index: int):
    """Delete a product from monitoring"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    products = monitor.config.get("products", [])
    
    if product_index < 0 or product_index >= len(products):
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Remove product
    removed_product = products.pop(product_index)
    
    # Save to file
    with open("config.json", "w") as f:
        json.dump(monitor.config, f, indent=4)
    
    return {"message": f"Product '{removed_product['name']}' removed successfully"}

@app.post("/api/monitor/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start price monitoring"""
    global monitor, monitor_task, is_monitoring
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    if is_monitoring:
        return {"message": "Monitoring is already running"}
    
    # Start monitoring in background
    is_monitoring = True
    monitor_task = asyncio.create_task(run_monitoring())
    
    return {"message": "Monitoring started successfully"}

@app.post("/api/monitor/stop")
async def stop_monitoring():
    """Stop price monitoring"""
    global monitor_task, is_monitoring
    
    if not is_monitoring:
        return {"message": "Monitoring is not running"}
    
    is_monitoring = False
    
    if monitor_task and not monitor_task.done():
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    
    return {"message": "Monitoring stopped successfully"}

@app.post("/api/check-now")
async def check_prices_now():
    """Manually trigger price check for all products"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    results = []
    
    for product in monitor.config.get("products", []):
        try:
            price = await monitor.extract_price_from_amazon(product["url"])
            results.append({
                "name": product["name"],
                "current_price": price,
                "target_price": product["target_price"],
                "price_met": price <= product["target_price"] if price else False
            })
        except Exception as e:
            results.append({
                "name": product["name"],
                "error": str(e)
            })
    
    return {"results": results}

@app.get("/api/price-history")
async def get_price_history():
    """Get price history data"""
    global monitor
    
    if not monitor:
        raise HTTPException(status_code=500, detail="Monitor not initialized")
    
    try:
        with open("price_history.json", "r") as f:
            price_history = json.load(f)
        return price_history
    except FileNotFoundError:
        return {}

@app.get("/api/logs")
async def get_logs(lines: int = 100):
    """Get recent log entries"""
    try:
        with open("price_monitor.log", "r") as f:
            log_lines = f.readlines()
        
        # Return last N lines
        return {"logs": log_lines[-lines:] if len(log_lines) > lines else log_lines}
    except FileNotFoundError:
        return {"logs": []}

async def run_monitoring():
    """Background task for monitoring prices"""
    global monitor, is_monitoring
    
    try:
        while is_monitoring:
            for product in monitor.config.get("products", []):
                if not is_monitoring:
                    break
                
                await monitor.check_single_product(product)
                await asyncio.sleep(5)  # Small delay between products
            
            if is_monitoring:
                wait_minutes = monitor.config.get("check_interval_minutes", 60)
                await asyncio.sleep(wait_minutes * 60)
                
    except asyncio.CancelledError:
        logger.info("Monitoring task cancelled")
    except Exception as e:
        logger.error(f"Error in monitoring task: {e}")
        is_monitoring = False

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )