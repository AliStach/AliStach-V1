"""Service compatibility exceptions and error handling utilities."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ServiceCompatibilityError(Exception):
    """Base class for service compatibility issues."""
    
    def __init__(self, message: str, service_type: str = "unknown", 
                 error_code: str = "SERVICE_COMPATIBILITY_ERROR"):
        super().__init__(message)
        self.service_type = service_type
        self.error_code = error_code


class SmartSearchUnavailableError(ServiceCompatibilityError):
    """Raised when smart search functionality is not available."""
    
    def __init__(self, service_type: str = "basic"):
        message = (
            f"Smart search functionality unavailable with {service_type} service. "
            f"Enhanced service required for smart search capabilities."
        )
        super().__init__(message, service_type, "SMART_SEARCH_UNAVAILABLE")


class EnhancedFeaturesDisabledError(ServiceCompatibilityError):
    """Raised when enhanced features are disabled in current environment."""
    
    def __init__(self, environment: str = "serverless"):
        message = (
            f"Enhanced features disabled in {environment} environment. "
            f"Set ENABLE_ENHANCED_FEATURES=true to force enable."
        )
        super().__init__(message, "basic", "ENHANCED_FEATURES_DISABLED")


def create_service_compatibility_error_response(error: ServiceCompatibilityError) -> Dict[str, Any]:
    """
    Create standardized error response for service compatibility issues.
    
    Args:
        error: ServiceCompatibilityError instance
        
    Returns:
        Dictionary with error response format
    """
    return {
        "success": False,
        "error": str(error),
        "error_code": error.error_code,
        "service_info": {
            "service_type": error.service_type,
            "enhanced_features_available": False,
            "fallback_used": True,
            "environment": "serverless" if error.service_type == "basic" else "unknown"
        },
        "available_alternatives": [
            "Use /api/products/search for basic product search",
            "Use /api/products for enhanced product search",
            "Enable enhanced features with ENABLE_ENHANCED_FEATURES=true"
        ]
    }


def create_attribute_error_response(service_type: str, missing_method: str, 
                                  environment_info: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Create error response for AttributeError scenarios.
    
    Args:
        service_type: Type of service that caused the error
        missing_method: Name of the missing method
        environment_info: Optional environment information
        
    Returns:
        Dictionary with error response format
    """
    return {
        "success": False,
        "error": f"Method '{missing_method}' not available on {service_type} service",
        "error_code": "METHOD_NOT_AVAILABLE",
        "service_info": {
            "service_type": service_type,
            "missing_method": missing_method,
            "enhanced_features_available": False,
            "environment": environment_info.get('is_serverless', False) if environment_info else "unknown"
        },
        "available_alternatives": [
            "Use /api/products/search for basic product search",
            "Enable enhanced features with ENABLE_ENHANCED_FEATURES=true",
            "Check service capabilities before calling methods"
        ],
        "debugging_info": {
            "suggestion": f"Check if service supports '{missing_method}' using hasattr() before calling",
            "environment_details": environment_info if environment_info else {}
        }
    }