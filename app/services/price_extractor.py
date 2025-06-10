"""
Price extraction service using Crawl4AI
"""

import asyncio
import json
import re
import logging
from typing import Optional

try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    raise ImportError("Please install crawl4ai: pip install crawl4ai")

from app.core.config import settings
from app.utils.exceptions import PriceExtractionError

logger = logging.getLogger(__name__)

class PriceExtractor:
    """Service for extracting prices from Amazon pages"""
    
    def __init__(self):
        self.timeout = settings.CRAWL_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
    
    async def extract_price(self, url: str) -> Optional[float]:
        """Extract price from Amazon product page"""
        for attempt in range(self.max_retries):
            try:
               # Add random delay to avoid being flagged as bot
               if attempt > 0:
                    await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff, max 10s
                
               async with AsyncWebCrawler(
                    verbose=False,
                    headless=True,
                    browser_type="chromium"
                ) as crawler:
                    result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    wait_for="domcontentloaded",
                    timeout=30,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    },
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
                                }
                            }
                        },
                        instruction="Extract the current price and product title from this Amazon page"
                    )
                    
                    if result.success:
                        # Try structured data first
                        if result.extracted_content:
                            try:
                                data = json.loads(result.extracted_content)
                                price_str = data.get('price', '')
                                logger.debug(f"Extracted data: {data}")
                                
                                price = self._parse_price(price_str)
                                if price:
                                    return price
                            except json.JSONDecodeError:
                                logger.debug("Failed to parse structured data")
                        
                        # Fallback to HTML parsing
                        price = self._extract_price_from_html(result.html)
                        if price:
                            return price
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {url}")
                    
            except Exception as e:
                error_msg = str(e)
                if "net::ERR_ABORTED" in error_msg or "frame was detached" in error_msg:
                    logger.warning(f"Amazon blocked request (attempt {attempt + 1}): {error_msg}")
                elif "timeout" in error_msg.lower():
                    logger.warning(f"Request timed out (attempt {attempt + 1}): {error_msg}")
                else:
                    logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")
    
                # Don't retry immediately on certain errors
                if "net::ERR_ABORTED" in error_msg and attempt < self.max_retries - 1:
                    await asyncio.sleep(5)  # Wait longer for blocked requests
                
        logger.error(f"Failed to extract price after {self.max_retries} attempts - Amazon may be blocking requests")
        return None
    
    def _extract_price_from_html(self, html: str) -> Optional[float]:
        """Extract price using regex patterns"""
        patterns = [
            r'<span class="a-price-whole">([0-9,]+)</span>',
            r'"priceAmount":([0-9]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                try:
                    price_str = matches[0].replace(',', '')
                    return float(price_str)
                except (ValueError, IndexError):
                    continue
        return None
    
    def _parse_price(self, price_str: str) -> Optional[float]:
        """Parse price string to float"""
        if not price_str:
            return None
        
        price_clean = re.sub(r'[^\d.,]', '', price_str).replace(',', '')
        try:
            return float(price_clean)
        except ValueError:
            return None
