"""
Sample data fixtures for testing
"""

# Sample Amazon HTML responses
AMAZON_HTML_WITH_PRICE = """
<!DOCTYPE html>
<html>
<head><title>Amazon Product</title></head>
<body>
    <div id="productTitle">Test Product Name</div>
    <div class="a-section a-spacing-none a-spacing-top-mini">
        <span class="a-price a-text-price a-size-medium a-color-base">
            <span class="a-offscreen">$29.99</span>
            <span aria-hidden="true">
                <span class="a-price-symbol">$</span>
                <span class="a-price-whole">29</span>
                <span class="a-price-fraction">99</span>
            </span>
        </span>
    </div>
    <div id="availability">
        <span class="a-size-medium a-color-success">In Stock</span>
    </div>
</body>
</html>
"""

AMAZON_HTML_NO_PRICE = """
<!DOCTYPE html>
<html>
<head><title>Amazon Product</title></head>
<body>
    <div id="productTitle">Test Product Name</div>
    <div id="availability">
        <span class="a-size-medium a-color-error">Currently unavailable</span>
    </div>
</body>
</html>
"""

AMAZON_HTML_HIGH_PRICE = """
<!DOCTYPE html>
<html>
<head><title>Amazon Product</title></head>
<body>
    <div id="productTitle">Expensive Product</div>
    <div class="a-section">
        <span class="a-price">
            <span class="a-price-symbol">$</span>
            <span class="a-price-whole">1,299</span>
            <span class="a-price-fraction">99</span>
        </span>
    </div>
</body>
</html>
"""

# Sample JSON responses
CRAWL4AI_SUCCESS_RESPONSE = {
    "success": True,
    "extracted_content": '{"price": "$29.99", "title": "Test Product", "availability": "In Stock"}',
    "html": AMAZON_HTML_WITH_PRICE
}

CRAWL4AI_FAILURE_RESPONSE = {
    "success": False,
    "extracted_content": None,
    "html": ""
}

# Sample configuration data
SAMPLE_CONFIG = {
    "products": [
        {
            "name": "Echo Dot (3rd Gen)",
            "url": "https://www.amazon.com/gp/product/B0757911C2",
            "target_price": 30.00
        },
        {
            "name": "iPad Air",
            "url": "https://www.amazon.com/gp/product/B09G9FPHY6",
            "target_price": 500.00
        }
    ],
    "check_interval_minutes": 300,
    "email_notifications": {
        "enabled": True,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "test@example.com",
        "recipient_email": "recipient@example.com"
    },
    "desktop_notifications": {
        "enabled": True
    }
}

# Sample price history data
SAMPLE_PRICE_HISTORY = {
    "https://www.amazon.com/gp/product/B0757911C2": [
        {
            "timestamp": "2025-06-09T10:00:00",
            "price": 32.99
        },
        {
            "timestamp": "2025-06-09T14:00:00",
            "price": 29.99
        },
        {
            "timestamp": "2025-06-09T18:00:00",
            "price": 28.99
        }
    ],
    "https://www.amazon.com/gp/product/B09G9FPHY6": [
        {
            "timestamp": "2025-06-09T10:00:00",
            "price": 520.00
        },
        {
            "timestamp": "2025-06-09T14:00:00",
            "price": 499.99
        }
    ]
}

# Sample API responses
API_STATUS_RESPONSE = {
    "is_running": False,
    "last_check": None,
    "total_products": 2,
    "active_alerts": 0
}

API_PRODUCTS_RESPONSE = [
    {
        "name": "Echo Dot (3rd Gen)",
        "url": "https://www.amazon.com/gp/product/B0757911C2",
        "target_price": 30.00
    },
    {
        "name": "iPad Air",
        "url": "https://www.amazon.com/gp/product/B09G9FPHY6",
        "target_price": 500.00
    }
]

API_PRICE_CHECK_RESPONSE = [
    {
        "name": "Echo Dot (3rd Gen)",
        "current_price": 28.99,
        "target_price": 30.00,
        "price_met": True
    },
    {
        "name": "iPad Air",
        "current_price": 520.00,
        "target_price": 500.00,
        "price_met": False
    }
]