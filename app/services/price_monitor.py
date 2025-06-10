"""
Amazon Price Monitor Service
Main business logic for price monitoring
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.core.config import settings
from app.services.price_extractor import PriceExtractor
from app.services.notification import NotificationService
from app.models.product import ProductConfig
from app.utils.exceptions import PriceMonitorError

logger = logging.getLogger(__name__)

class PriceMonitorService:
    """Main price monitoring service"""
    
    def __init__(self):
        self.config_file = settings.CONFIG_FILE
        self.price_history_file = settings.PRICE_HISTORY_FILE
        self.price_extractor = PriceExtractor()
        self.notification_service = NotificationService()
        self.price_history = {}
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Load existing configuration and history
        self.config = self._load_config()
        self._load_price_history()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        default_config = {
            "products": [],
            "check_interval_minutes": settings.DEFAULT_CHECK_INTERVAL,
            "email_notifications": {
                "enabled": False,
                "smtp_server": settings.SMTP_SERVER,
                "smtp_port": settings.SMTP_PORT,
                "sender_email": "",
                "recipient_email": ""
            },
            "desktop_notifications": {
                "enabled": True
            }
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise PriceMonitorError(f"Failed to save configuration: {e}")
    
    def _load_price_history(self):
        """Load price history from file"""
        try:
            if self.price_history_file.exists():
                with open(self.price_history_file, 'r') as f:
                    self.price_history = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load price history: {e}")
            self.price_history = {}
    
    def save_price_history(self):
        """Save price history to file"""
        try:
            with open(self.price_history_file, 'w') as f:
                json.dump(self.price_history, f, indent=4)
            logger.info("Price history saved successfully")
        except Exception as e:
            logger.error(f"Failed to save price history: {e}")
    
    # Configuration management
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration"""
        # Validate configuration
        self._validate_config(new_config)
        self._save_config(new_config)
    
    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration data"""
        required_fields = ["products", "check_interval_minutes"]
        for field in required_fields:
            if field not in config:
                raise PriceMonitorError(f"Missing required field: {field}")
        
        # Validate check interval
        interval = config["check_interval_minutes"]
        if not (settings.MIN_CHECK_INTERVAL <= interval <= settings.MAX_CHECK_INTERVAL):
            raise PriceMonitorError(
                f"Check interval must be between {settings.MIN_CHECK_INTERVAL} "
                f"and {settings.MAX_CHECK_INTERVAL} minutes"
            )
    
    # Product management
    def get_products(self) -> List[Dict[str, Any]]:
        """Get all monitored products"""
        return self.config.get("products", [])
    
    def add_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new product to monitor"""
        products = self.config.get("products", [])
        products.append(product)
        
        updated_config = self.config.copy()
        updated_config["products"] = products
        self.update_config(updated_config)
        
        return product
    
    def update_product(self, index: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific product"""
        products = self.config.get("products", [])
        
        if index < 0 or index >= len(products):
            raise PriceMonitorError("Product not found")
        
        # Update product fields
        for key, value in updates.items():
            if value is not None:
                products[index][key] = value
        
        updated_config = self.config.copy()
        updated_config["products"] = products
        self.update_config(updated_config)
        
        return products[index]
    
    def delete_product(self, index: int) -> Dict[str, Any]:
        """Delete a product from monitoring"""
        products = self.config.get("products", [])
        
        if index < 0 or index >= len(products):
            raise PriceMonitorError("Product not found")
        
        removed_product = products.pop(index)
        
        updated_config = self.config.copy()
        updated_config["products"] = products
        self.update_config(updated_config)
        
        return removed_product
    
    # Price checking
    async def check_single_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Check price for a single product"""
        url = product["url"]
        target_price = product["target_price"]
        product_name = product["name"]
        
        logger.info(f"Checking price for: {product_name}")
        
        try:
            current_price = await self.price_extractor.extract_price(url)
            
            if current_price is None:
                logger.warning(f"Could not extract price for {product_name} - Amazon may be blocking requests")
                return {
                    "name": product_name,
                    "error": "Could not extract price - site may be blocking requests"
                }
            
            # Store price history
            if url not in self.price_history:
                self.price_history[url] = []
            
            self.price_history[url].append({
                "timestamp": datetime.now().isoformat(),
                "price": current_price
            })
            
            logger.info(f"{product_name}: Current price ${current_price:.2f}, Target: ${target_price:.2f}")
            
            result = {
                "name": product_name,
                "current_price": current_price,
                "target_price": target_price,
                "price_met": current_price <= target_price
            }
            
            # Check if price dropped below target
            if current_price <= target_price:
                logger.info(f"🎉 Price alert triggered for {product_name}!")
                await self.notification_service.send_price_alert(
                    product_name, current_price, target_price, url, self.config
                )
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            if "net::ERR_ABORTED" in error_msg or "frame was detached" in error_msg:
                error_msg = "Amazon blocked the request - try again later"
            elif "timeout" in error_msg.lower():
                error_msg = "Request timed out - Amazon may be slow"
            
            logger.error(f"Error checking price for {product_name}: {error_msg}")
            return {
                "name": product_name,
                "error": error_msg
            }
    
    async def check_all_products(self) -> List[Dict[str, Any]]:
        """Check prices for all products"""
        results = []
        products = self.get_products()
        
        for product in products:
            result = await self.check_single_product(product)
            results.append(result)
            
            # Delay between requests to be respectful
            await asyncio.sleep(settings.CRAWL_DELAY)
        
        # Save price history after checking all products
        self.save_price_history()
        
        return results
    
    # Monitoring control
    async def start_monitoring(self):
        """Start continuous price monitoring"""
        if self.is_monitoring:
            raise PriceMonitorError("Monitoring is already running")
        
        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Price monitoring started")
    
    async def stop_monitoring(self):
        """Stop price monitoring"""
        if not self.is_monitoring:
            raise PriceMonitorError("Monitoring is not running")
        
        self.is_monitoring = False
        
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Price monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")
        
        try:
            while self.is_monitoring:
                await self.check_all_products()
                
                if self.is_monitoring:
                    wait_minutes = self.config.get("check_interval_minutes", settings.DEFAULT_CHECK_INTERVAL)
                    logger.info(f"Waiting {wait_minutes} minutes until next check...")
                    await asyncio.sleep(wait_minutes * 60)
                    
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            self.is_monitoring = False
    
    # Status
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "is_running": self.is_monitoring,
            "last_check": datetime.now() if self.is_monitoring else None,
            "total_products": len(self.get_products()),
            "check_interval_minutes": self.config.get("check_interval_minutes", settings.DEFAULT_CHECK_INTERVAL)
        }