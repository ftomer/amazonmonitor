"""
Tests for PriceExtractor service

run with:
python -m pytest tests/test_services/test_price_extractor.py -v
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.price_extractor import PriceExtractor


class TestPriceExtractor:
    """Test PriceExtractor functionality"""
    
    @pytest.fixture
    def extractor(self):
        """Create a price extractor instance"""
        return PriceExtractor()
    
    def test_parse_price_valid(self, extractor):
        """Test parsing valid price strings"""
        test_cases = [
            ("$29.99", 29.99),
            ("29.99", 29.99),
            ("$1,234.56", 1234.56),
            ("1,234.56", 1234.56),
            ("45", 45.0),
            ("Price: $99.95", 99.95)
        ]
        
        for price_str, expected in test_cases:
            result = extractor._parse_price(price_str)
            assert result == expected, f"Failed for {price_str}"
    
    def test_parse_price_invalid(self, extractor):
        """Test parsing invalid price strings"""
        invalid_cases = [
            "",
            None,
            "No price found",
            "abc",
            "Currently unavailable"
        ]
        
        for price_str in invalid_cases:
            result = extractor._parse_price(price_str)
            assert result is None, f"Should return None for {price_str}"
    
    def test_extract_price_from_html(self, extractor):
        """Test extracting price from HTML content"""
        html_content = '''
        <div class="pricing">
            <span class="a-price-whole">29</span>
            <span class="a-price-fraction">99</span>
        </div>
        '''
        
        result = extractor._extract_price_from_html(html_content)
        assert result == 29.0  # Should extract the whole number part
    
    def test_extract_price_from_html_with_dollar_sign(self, extractor):
        """Test extracting price with dollar sign"""
        html_content = '''
        <div class="price">
            Price: $45.99
        </div>
        '''
        
        result = extractor._extract_price_from_html(html_content)
        assert result == 45.99
    
    def test_extract_price_from_html_no_price(self, extractor):
        """Test extracting price from HTML with no price"""
        html_content = '''
        <div class="product">
            <h1>Product Title</h1>
            <p>Description</p>
        </div>
        '''
        
        result = extractor._extract_price_from_html(html_content)
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.AsyncWebCrawler')
    async def test_extract_price_success_structured(self, mock_crawler_class, extractor):
        """Test successful price extraction using structured data"""
        # Create mock result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.extracted_content = '{"price": "$29.99", "title": "Test Product"}'
        mock_result.html = "<html>...</html>"
        
        # Create mock crawler
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        url = "https://www.amazon.com/test-product/dp/B123456789"
        result = await extractor.extract_price(url)
        
        assert result == 29.99
        mock_crawler.arun.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.AsyncWebCrawler')
    async def test_extract_price_success_html_fallback(self, mock_crawler_class, extractor):
        """Test successful price extraction using HTML fallback"""
        # Create mock result with no structured data
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.extracted_content = None
        mock_result.html = '<span class="a-price-whole">45</span>'
        
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        url = "https://www.amazon.com/test-product/dp/B123456789"
        result = await extractor.extract_price(url)
        
        assert result == 45.0
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.AsyncWebCrawler')
    async def test_extract_price_crawl_failure(self, mock_crawler_class, extractor):
        """Test price extraction when crawling fails"""
        mock_result = MagicMock()
        mock_result.success = False
        
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        url = "https://www.amazon.com/test-product/dp/B123456789"
        result = await extractor.extract_price(url)
        
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.AsyncWebCrawler')
    async def test_extract_price_exception(self, mock_crawler_class, extractor):
        """Test price extraction when an exception occurs"""
        mock_crawler = AsyncMock()
        mock_crawler.arun.side_effect = Exception("Network error")
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        url = "https://www.amazon.com/test-product/dp/B123456789"
        result = await extractor.extract_price(url)
        
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.AsyncWebCrawler')
    async def test_extract_price_with_retries(self, mock_crawler_class, extractor):
        """Test price extraction with retries"""
        # Mock extractor with fewer retries for faster testing
        extractor.max_retries = 2
        
        mock_result = MagicMock()
        mock_result.success = False
        
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        url = "https://www.amazon.com/test-product/dp/B123456789"
        result = await extractor.extract_price(url)
        
        assert result is None
        # Should have tried max_retries times
        assert mock_crawler.arun.call_count == 2
    
    def test_extract_price_from_html_patterns(self, extractor):
        """Test various HTML patterns for price extraction"""
        test_cases = [
            # Pattern 1: a-price-whole
            ('<span class="a-price-whole">25</span>', 25.0),
            
            # Pattern 2: priceAmount in JSON
            ('{"priceAmount":39.99}', 39.99),
            
            # Pattern 3: Dollar sign pattern
            ('Price: $75.50', 75.50),
            
            # Pattern 4: Comma separated price
            ('<span class="a-price-whole">1,299</span>', 1299.0),
        ]
        
        for html, expected in test_cases:
            result = extractor._extract_price_from_html(html)
            assert result == expected, f"Failed for HTML: {html}"
    
    @pytest.mark.asyncio
    async def test_extract_price_invalid_url(self, extractor):
        """Test price extraction with invalid URL"""
        invalid_url = "not-a-valid-url"
        result = await extractor.extract_price(invalid_url)
        
        # Should handle invalid URLs gracefully
        assert result is None
    
    @pytest.mark.asyncio
    async def test_extract_price_empty_url(self, extractor):
        """Test price extraction with empty URL"""
        empty_url = ""
        result = await extractor.extract_price(empty_url)
        
        # Should handle empty URLs gracefully
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.price_extractor.AsyncWebCrawler')
    async def test_extract_price_partial_html_content(self, mock_crawler_class, extractor):
        """Test price extraction with partial HTML content"""
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.extracted_content = None
        mock_result.html = '<div>Some content without price</div>'
        
        mock_crawler = AsyncMock()
        mock_crawler.arun.return_value = mock_result
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        url = "https://www.amazon.com/test-product/dp/B123456789"
        result = await extractor.extract_price(url)
        
        # Should return None when no price is found in HTML
        assert result is None