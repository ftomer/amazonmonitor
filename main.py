#!/usr/bin/env python3
"""
Amazon Price Monitor using Crawl4AI
Monitors Amazon product prices and sends notifications when price drops below threshold
"""

import asyncio
import json
import re
import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import logging

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    print("Please install crawl4ai: pip install crawl4ai")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('price_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AmazonPriceMonitor:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the price monitor with configuration"""
        self.config = self.load_config(config_file)
        self.price_history = {}
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config if not exists
            default_config = {
                "products": [
                    {
                        "name": "Example Product",
                        "url": "https://www.amazon.com/gp/product/B0757911C2/ref=ox_sc_act_title_1?smid=A2XZ7JICGUQ1CX&psc=1",
                        "target_price": 50.00
                    }
                ],
                "check_interval_minutes": 60,
                "email_notifications": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_email@gmail.com",
                    "sender_password": "your_app_password",
                    "recipient_email": "recipient@gmail.com"
                },
                "desktop_notifications": {
                    "enabled": True
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            logger.info(f"Created default config file: {config_file}")
            logger.info("Please edit the config file with your product URLs and notification settings")
            return default_config
    
    async def extract_price_from_amazon(self, url: str) -> Optional[float]:
        """Extract price from Amazon product page using Crawl4AI"""
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Configure crawler for Amazon
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy="LLMExtractionStrategy",
                    extraction_schema={
                        "type": "object",
                        "properties": {
                            "price": {
                                "type": "string", 
                                "description": "Current price of the product in dollars"
                            },
                            "title": {
                                "type": "string",
                                "description": "Product title"
                            },
                            "availability": {
                                "type": "string",
                                "description": "Product availability status"
                            }
                        }
                    },
                    instruction="Extract the current price, product title, and availability from this Amazon product page"
                )
                
                if result.success:
                    # Try to extract structured data first
                    if result.extracted_content:
                        try:
                            data = json.loads(result.extracted_content)
                            price_str = data.get('price', '')
                            logger.info(f"Extracted structured data: {data}")
                            
                            # Parse price from structured data
                            price = self.parse_price(price_str)
                            if price:
                                return price
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse structured data as JSON")
                    
                    # Fallback to regex parsing of HTML content
                    html_content = result.html
                    price = self.extract_price_from_html(html_content)
                    return price
                else:
                    logger.error(f"Failed to crawl URL: {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extracting price from {url}: {str(e)}")
            return None
    
    def extract_price_from_html(self, html_content: str) -> Optional[float]:
        """Extract price from HTML content using regex patterns"""
        # Common Amazon price patterns
        price_patterns = [
            r'<span class="a-price-whole">([0-9,]+)</span>',
            r'<span class="a-price-amount">.*?\$([0-9,]+\.?[0-9]*)',
            r'"priceAmount":([0-9]+\.?[0-9]*)',
            r'<span[^>]*class="[^"]*a-price[^"]*"[^>]*>.*?\$([0-9,]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                try:
                    # Take the first match and clean it
                    price_str = matches[0].replace(',', '')
                    price = float(price_str)
                    logger.info(f"Extracted price using pattern: ${price}")
                    return price
                except (ValueError, IndexError):
                    continue
        
        logger.warning("Could not extract price from HTML content")
        return None
    
    def parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float"""
        if not price_str:
            return None
            
        # Remove currency symbols and extract numeric value
        price_clean = re.sub(r'[^\d.,]', '', price_str)
        price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean)
        except ValueError:
            logger.warning(f"Could not parse price: {price_str}")
            return None
    
    def send_email_notification(self, product_name: str, current_price: float, target_price: float, url: str):
        """Send email notification"""
        if not self.config["email_notifications"]["enabled"]:
            return
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email_notifications"]["sender_email"]
            msg['To'] = self.config["email_notifications"]["recipient_email"]
            msg['Subject'] = f"Price Alert: {product_name}"
            
            body = f"""
            Great news! The price for {product_name} has dropped!
            
            Current Price: ${current_price:.2f}
            Target Price: ${target_price:.2f}
            Savings: ${current_price - target_price:.2f}
            
            Product URL: {url}
            
            Happy shopping!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(
                self.config["email_notifications"]["smtp_server"],
                self.config["email_notifications"]["smtp_port"]
            )
            server.starttls()
            server.login(
                self.config["email_notifications"]["sender_email"],
                self.config["email_notifications"]["sender_password"]
            )
            
            text = msg.as_string()
            server.sendmail(
                self.config["email_notifications"]["sender_email"],
                self.config["email_notifications"]["recipient_email"],
                text
            )
            server.quit()
            
            logger.info(f"Email notification sent for {product_name}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
    
    def send_desktop_notification(self, product_name: str, current_price: float, target_price: float):
        """Send desktop notification"""
        if not self.config["desktop_notifications"]["enabled"]:
            return
            
        try:
            # Try to use plyer for cross-platform notifications
            try:
                from plyer import notification
                notification.notify(
                    title="Amazon Price Alert!",
                    message=f"{product_name}\nPrice dropped to ${current_price:.2f}\nTarget: ${target_price:.2f}",
                    timeout=10
                )
                logger.info(f"Desktop notification sent for {product_name}")
            except ImportError:
                # Fallback to console notification
                print(f"\n🔔 PRICE ALERT! 🔔")
                print(f"Product: {product_name}")
                print(f"Current Price: ${current_price:.2f}")
                print(f"Target Price: ${target_price:.2f}")
                print(f"You save: ${current_price - target_price:.2f}")
                
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {str(e)}")
    
    async def check_single_product(self, product: Dict[str, Any]) -> bool:
        """Check price for a single product"""
        url = product["url"]
        target_price = product["target_price"]
        product_name = product["name"]
        
        logger.info(f"Checking price for: {product_name}")
        
        current_price = await self.extract_price_from_amazon(url)
        
        if current_price is None:
            logger.warning(f"Could not extract price for {product_name}")
            return False
        
        # Store price history
        if url not in self.price_history:
            self.price_history[url] = []
        
        self.price_history[url].append({
            "timestamp": datetime.now().isoformat(),
            "price": current_price
        })
        
        logger.info(f"{product_name}: Current price ${current_price:.2f}, Target: ${target_price:.2f}")
        
        # Check if price dropped below target
        if current_price <= target_price:
            logger.info(f"🎉 Price alert triggered for {product_name}!")
            self.send_email_notification(product_name, current_price, target_price, url)
            self.send_desktop_notification(product_name, current_price, target_price)
            return True
        
        return False
    
    async def monitor_prices(self):
        """Main monitoring loop"""
        logger.info("Starting Amazon price monitor...")
        
        while True:
            try:
                for product in self.config["products"]:
                    await self.check_single_product(product)
                    # Small delay between products to be respectful
                    await asyncio.sleep(5)
                
                # Wait for next check cycle
                wait_minutes = self.config["check_interval_minutes"]
                logger.info(f"Waiting {wait_minutes} minutes until next check...")
                await asyncio.sleep(wait_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def save_price_history(self, filename: str = "price_history.json"):
        """Save price history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.price_history, f, indent=4)
            logger.info(f"Price history saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save price history: {str(e)}")

async def main():
    """Main function"""
    monitor = AmazonPriceMonitor()
    
    try:
        await monitor.monitor_prices()
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    finally:
        monitor.save_price_history()

if __name__ == "__main__":
    asyncio.run(main())