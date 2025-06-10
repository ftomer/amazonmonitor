"""
Tests for custom exceptions
"""

import pytest
from app.utils.exceptions import (
    PriceMonitorError,
    PriceExtractionError,
    ConfigurationError,
    NotificationError
)


class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_price_monitor_error_base(self):
        """Test base PriceMonitorError"""
        error_message = "Base error occurred"
        
        with pytest.raises(PriceMonitorError, match=error_message):
            raise PriceMonitorError(error_message)
    
    def test_price_extraction_error(self):
        """Test PriceExtractionError"""
        error_message = "Failed to extract price"
        
        with pytest.raises(PriceExtractionError, match=error_message):
            raise PriceExtractionError(error_message)
        
        # Should also be instance of base class
        with pytest.raises(PriceMonitorError):
            raise PriceExtractionError(error_message)
    
    def test_configuration_error(self):
        """Test ConfigurationError"""
        error_message = "Invalid configuration"
        
        with pytest.raises(ConfigurationError, match=error_message):
            raise ConfigurationError(error_message)
        
        # Should also be instance of base class
        with pytest.raises(PriceMonitorError):
            raise ConfigurationError(error_message)
    
    def test_notification_error(self):
        """Test NotificationError"""
        error_message = "Failed to send notification"
        
        with pytest.raises(NotificationError, match=error_message):
            raise NotificationError(error_message)
        
        # Should also be instance of base class
        with pytest.raises(PriceMonitorError):
            raise NotificationError(error_message)
    
    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy"""
        # All custom exceptions should inherit from PriceMonitorError
        assert issubclass(PriceExtractionError, PriceMonitorError)
        assert issubclass(ConfigurationError, PriceMonitorError)
        assert issubclass(NotificationError, PriceMonitorError)
        
        # And PriceMonitorError should inherit from Exception
        assert issubclass(PriceMonitorError, Exception)
    
    def test_exception_with_no_message(self):
        """Test exceptions with no message"""
        with pytest.raises(PriceMonitorError):
            raise PriceMonitorError()
        
        with pytest.raises(PriceExtractionError):
            raise PriceExtractionError()
    
    def test_exception_string_representation(self):
        """Test string representation of exceptions"""
        error_message = "Test error message"
        
        error = PriceMonitorError(error_message)
        assert str(error) == error_message
        
        error = PriceExtractionError(error_message)
        assert str(error) == error_message