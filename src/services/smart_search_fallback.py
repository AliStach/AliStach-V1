"""Fallback implementation for smart search using basic AliExpress service."""

import logging
import time
from typing import Optional, Any
from datetime import datetime

from .aliexpress_service import AliExpressService, AliExpressServiceException

logger = logging.getLogger(__name__)


class SmartSearchFallback:
    """
    Fallback implementation that provides smart search compatibility using basic service.
    
    This class wraps a basic AliExpressService and provides a smart_product_search method
    that maintains the same response contract as the enhanced service while using only
    basic service capabilities.
    """
    
    def __init__(self, basic_service: AliExpressService):
        """
        Initialize fallback with basic service.
        
        Args:
            basic_service: Basic AliExpressService instance
        """
        self.basic_service = basic_service
        logger.info("SmartSearchFallback initialized with basic service")
    
    def __getattr__(self, name):
        """
        Delegate attribute access to the basic service.
        
        This allows the fallback to act as a proxy for the basic service
        while providing the enhanced smart_product_search method.
        """
        return getattr(self.basic_service, name)
    
    async def smart_product_search(self,
                                 keywords: Optional[str] = None,
                                 category_id: Optional[str] = None,
                                 max_sale_price: Optional[float] = None,
                                 min_sale_price: Optional[float] = None,
                                 page_no: int = 1,
                                 page_size: int = 20,
                                 sort: Optional[str] = None,
                                 generate_affiliate_links: bool = True,
                                 force_refresh: bool = False,
                                 **kwargs):
        """
        Provide compatible smart search using basic service.
        
        This method uses the basic service's get_products method to provide
        search functionality while maintaining the SmartSearchResponse format.
        
        Args:
            keywords: Search keywords
            category_id: Category filter
            max_sale_price: Maximum price filter
            min_sale_price: Minimum price filter
            page_no: Page number for pagination
            page_size: Results per page (max 50)
            sort: Sort order
            generate_affiliate_links: Whether to include affiliate links
            force_refresh: Force fresh API call (ignored in fallback)
            **kwargs: Additional search parameters (ignored in fallback)
            
        Returns:
            SmartSearchResponse with products and fallback metadata
        """
        start_time = time.time()
        
        logger.info(f"SmartSearchFallback: Processing search request with keywords='{keywords}', "
                   f"category_id='{category_id}', page_no={page_no}, page_size={page_size}")
        
        try:
            # DEBUGGING: Log before calling basic service
            logger.error(f"FALLBACK DEBUG: About to call basic_service.get_products with keywords='{keywords}'")
            
            # Use basic service's get_products method
            basic_result = self.basic_service.get_products(
                keywords=keywords,
                category_id=category_id,
                max_sale_price=max_sale_price,
                min_sale_price=min_sale_price,
                page_no=page_no,
                page_size=page_size,
                sort=sort,
                auto_generate_affiliate_links=generate_affiliate_links
            )
            
            # DEBUGGING: Log after basic service call
            logger.error(f"FALLBACK DEBUG: Basic service returned {len(basic_result.products)} products")
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"SmartSearchFallback: Basic service returned {len(basic_result.products)} products "
                       f"in {response_time_ms:.2f}ms")
            
            # DEBUGGING: Log before creating compatible response
            logger.error(f"FALLBACK DEBUG: About to create compatible response")
            
            # Convert to SmartSearchResponse format using the from_basic_search method
            smart_response = self._create_compatible_response(basic_result, response_time_ms)
            
            # DEBUGGING: Log after creating compatible response
            logger.error(f"FALLBACK DEBUG: Created compatible response with {len(smart_response.products)} products")
            
            logger.info(f"SmartSearchFallback: Successfully created compatible response with "
                       f"affiliate_links_cached={smart_response.affiliate_links_cached}, "
                       f"affiliate_links_generated={smart_response.affiliate_links_generated}")
            
            return smart_response
            
        except Exception as e:
            logger.error(f"SmartSearchFallback: Error during fallback search: {e}")
            raise AliExpressServiceException(f"Fallback search failed: {e}")
    
    def _create_compatible_response(self, basic_result, response_time_ms: float):
        """
        Convert basic search result to SmartSearchResponse format.
        
        This method ensures all required fields are properly initialized,
        preventing NameError exceptions while maintaining API compatibility.
        
        Args:
            basic_result: Result from basic service get_products call
            response_time_ms: Response time in milliseconds
            
        Returns:
            SmartSearchResponse with all required fields initialized for fallback
        """
        # Import here to avoid circular imports
        from .enhanced_aliexpress_service import SmartSearchResponse
        
        # Use the existing from_basic_search class method
        return SmartSearchResponse.from_basic_search(basic_result, response_time_ms)