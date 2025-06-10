"""
Custom exceptions for Amazon Price Monitor
"""

class PriceMonitorError(Exception):
    """Base exception for price monitor errors"""
    pass

class PriceExtractionError(PriceMonitorError):
    """Error during price extraction"""
    pass

class ConfigurationError(PriceMonitorError):
    """Error in configuration"""
    pass

class NotificationError(PriceMonitorError):
    """Error sending notifications"""
    pass
