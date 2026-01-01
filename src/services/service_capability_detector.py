"""Service capability detection utilities for determining service features."""

import logging
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)


class ServiceCapabilityDetector:
    """Utility class for detecting service capabilities and features."""
    
    @staticmethod
    def has_smart_search(service) -> bool:
        """
        Check if service supports smart_product_search method.
        
        Args:
            service: Service instance to check
            
        Returns:
            True if service has smart_product_search method
        """
        return hasattr(service, 'smart_product_search') and callable(getattr(service, 'smart_product_search'))
    
    @staticmethod
    def get_service_type(service) -> str:
        """
        Return 'enhanced' or 'basic' based on service type.
        
        Args:
            service: Service instance to analyze
            
        Returns:
            String indicating service type
        """
        # Check class name first for more reliable detection
        class_name = service.__class__.__name__
        
        if class_name == 'EnhancedAliExpressService':
            return "enhanced"
        elif class_name == 'AliExpressService':
            return "basic"
        elif class_name == 'UnknownService':
            return "unknown"
        
        # Fallback to method-based detection for real services
        # But be more strict - check if it's actually callable
        has_smart_search = (hasattr(service, 'smart_product_search') and 
                           callable(getattr(service, 'smart_product_search', None)))
        has_cache_service = hasattr(service, 'cache_service')
        has_get_products = (hasattr(service, 'get_products') and 
                           callable(getattr(service, 'get_products', None)))
        has_search_products = (hasattr(service, 'search_products') and 
                              callable(getattr(service, 'search_products', None)))
        
        if has_smart_search and has_cache_service:
            return "enhanced"
        elif has_get_products and has_search_products:
            return "basic"
        else:
            return "unknown"
    
    @staticmethod
    def get_capabilities(service) -> Dict[str, bool]:
        """
        Return dictionary of available capabilities.
        
        Args:
            service: Service instance to analyze
            
        Returns:
            Dictionary with capability flags
        """
        has_smart_search = ServiceCapabilityDetector.has_smart_search(service)
        has_caching = hasattr(service, 'cache_service')
        has_image_processing = hasattr(service, 'image_service')
        supports_affiliate_links = hasattr(service, 'get_affiliate_links')
        
        capabilities = {
            'has_smart_search': has_smart_search,
            'has_caching': has_caching,
            'has_image_processing': has_image_processing,
            'supports_affiliate_links': supports_affiliate_links,
            'has_enhanced_features': has_smart_search and has_caching,  # Enhanced if has both smart search and caching
        }
        
        logger.debug(f"Service capabilities detected: {capabilities}")
        return capabilities
    
    @staticmethod
    def is_enhanced_service(service) -> bool:
        """
        Check if service is an enhanced service instance.
        
        Args:
            service: Service instance to check
            
        Returns:
            True if service is enhanced service
        """
        return ServiceCapabilityDetector.get_service_type(service) == "enhanced"
    
    @staticmethod
    def is_basic_service(service) -> bool:
        """
        Check if service is a basic service instance.
        
        Args:
            service: Service instance to check
            
        Returns:
            True if service is basic service
        """
        return ServiceCapabilityDetector.get_service_type(service) == "basic"