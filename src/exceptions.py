"""
Standardized exception hierarchy for the AliExpress Affiliate API Service.

This module defines a comprehensive exception hierarchy that provides:
- Clear categorization of errors (transient vs permanent)
- Structured error details for logging and debugging
- Consistent error handling patterns across the application
- Type-safe exception handling with proper annotations

Exception Hierarchy:
    AliExpressServiceException (base)
    ├── ConfigurationError
    ├── APIError
    │   ├── TransientError
    │   │   └── RateLimitError
    │   └── PermanentError
    ├── ValidationError
    └── CacheError
"""

from typing import Dict, Optional, Any


class AliExpressServiceException(Exception):
    """
    Base exception for all AliExpress service errors.
    
    All custom exceptions in the service should inherit from this base class
    to enable consistent error handling and logging patterns.
    
    Attributes:
        message: Human-readable error message
        details: Additional context about the error (e.g., request params, error codes)
    
    Example:
        >>> raise AliExpressServiceException(
        ...     "Operation failed",
        ...     details={"operation": "search", "reason": "timeout"}
        ... )
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the exception with a message and optional details.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary containing additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message
    
    def __repr__(self) -> str:
        """Return detailed representation of the exception."""
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class ConfigurationError(AliExpressServiceException):
    """
    Configuration-related errors.
    
    Raised when there are issues with application configuration such as:
    - Missing required environment variables
    - Invalid configuration values
    - Configuration validation failures
    
    Example:
        >>> raise ConfigurationError(
        ...     "Missing required API key",
        ...     details={"env_var": "ALIEXPRESS_APP_KEY"}
        ... )
    """
    pass


class APIError(AliExpressServiceException):
    """
    Base class for AliExpress API-related errors.
    
    This serves as the parent class for all errors that occur when
    interacting with the AliExpress API.
    
    Subclasses:
        - TransientError: Temporary errors that may succeed on retry
        - PermanentError: Permanent errors that won't succeed on retry
    """
    pass


class TransientError(APIError):
    """
    Temporary errors that may succeed on retry.
    
    These errors indicate temporary conditions such as:
    - Network timeouts
    - Service temporarily unavailable
    - Rate limiting (see RateLimitError)
    - Temporary server errors (5xx)
    
    Retry logic should be applied when catching these exceptions.
    
    Example:
        >>> raise TransientError(
        ...     "API request timed out",
        ...     details={"timeout_seconds": 30, "endpoint": "/products/search"}
        ... )
    """
    pass


class PermanentError(APIError):
    """
    Permanent errors that won't succeed on retry.
    
    These errors indicate permanent conditions such as:
    - Invalid API credentials
    - Malformed requests (4xx errors)
    - Resource not found
    - Permission denied
    
    Retry logic should NOT be applied for these exceptions.
    
    Example:
        >>> raise PermanentError(
        ...     "Invalid API credentials",
        ...     details={"status_code": 401, "response": "Unauthorized"}
        ... )
    """
    pass


class RateLimitError(TransientError):
    """
    Rate limit exceeded error.
    
    Raised when the API rate limit has been exceeded. This is a special
    case of TransientError that includes information about when to retry.
    
    Attributes:
        message: Human-readable error message
        details: Additional error context
        retry_after: Number of seconds to wait before retrying (default: 60)
    
    Example:
        >>> raise RateLimitError(
        ...     "Rate limit exceeded",
        ...     retry_after=120,
        ...     details={"limit": 100, "window": "1 minute"}
        ... )
    """
    
    def __init__(
        self,
        message: str,
        retry_after: int = 60,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize rate limit error with retry information.
        
        Args:
            message: Human-readable error message
            retry_after: Number of seconds to wait before retrying
            details: Optional dictionary containing additional error context
        """
        super().__init__(message, details)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        """Return string representation including retry information."""
        base_str = super().__str__()
        return f"{base_str} | Retry after: {self.retry_after}s"


class ValidationError(AliExpressServiceException):
    """
    Data validation errors.
    
    Raised when input data fails validation checks such as:
    - Invalid parameter types
    - Missing required fields
    - Values outside acceptable ranges
    - Invalid format (e.g., malformed URLs, invalid IDs)
    
    Example:
        >>> raise ValidationError(
        ...     "Invalid product ID format",
        ...     details={"product_id": "abc", "expected_format": "numeric"}
        ... )
    """
    pass


class CacheError(AliExpressServiceException):
    """
    Cache-related errors.
    
    Raised when there are issues with caching operations such as:
    - Cache connection failures
    - Cache serialization/deserialization errors
    - Cache key conflicts
    - Cache storage full
    
    Example:
        >>> raise CacheError(
        ...     "Failed to connect to Redis cache",
        ...     details={"host": "localhost", "port": 6379, "error": "Connection refused"}
        ... )
    """
    pass
