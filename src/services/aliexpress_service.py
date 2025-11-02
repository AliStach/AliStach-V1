"""AliExpress API service using the official Python SDK."""

import logging
import time
import json
from typing import List, Optional, Dict, Any
from aliexpress_api import AliexpressApi, models
from ..utils.config import Config
from ..models.responses import (
    CategoryResponse, ProductResponse, ProductSearchResponse, ProductDetailResponse,
    AffiliateLink, HotProductResponse, PromoProductResponse, ShippingInfo, ServiceResponse
)


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AliExpressServiceException(Exception):
    """Base exception for AliExpress service errors."""
    pass


class APIError(AliExpressServiceException):
    """Raised when AliExpress API calls fail."""
    pass


class ValidationError(AliExpressServiceException):
    """Raised when input validation fails."""
    pass


class PermissionError(AliExpressServiceException):
    """Raised when API permissions are insufficient."""
    pass


class RateLimitError(AliExpressServiceException):
    """Raised when API rate limits are exceeded."""
    pass


class AliExpressService:
    """Service class for interacting with AliExpress API using the official SDK."""
    
    def __init__(self, config: Config):
        """Initialize the AliExpress service with configuration."""
        self.config = config
        
        try:
            # Initialize the AliExpress API client
            self.api = AliexpressApi(
                key=config.app_key,
                secret=config.app_secret,
                language=getattr(models.Language, config.language),
                currency=getattr(models.Currency, config.currency),
                tracking_id=config.tracking_id
            )
            logger.info(f"AliExpress API initialized with language={config.language}, currency={config.currency}")
        except Exception as e:
            logger.error(f"Failed to initialize AliExpress API: {e}")
            raise APIError(f"Failed to initialize AliExpress API: {e}")
    
    def _handle_api_error(self, error: Exception, operation: str) -> None:
        """Enhanced error handling with permission and rate limit detection."""
        error_str = str(error).lower()
        
        # Check for permission errors
        if any(phrase in error_str for phrase in [
            'permission', 'not have permission', 'access denied', 'unauthorized',
            'app does not have permission', 'insufficient privileges'
        ]):
            guidance = self._get_permission_guidance(operation)
            raise PermissionError(f"Insufficient API permissions for {operation}. {guidance}")
        
        # Check for rate limiting
        if any(phrase in error_str for phrase in [
            'rate limit', 'too many requests', 'quota exceeded', 'throttled'
        ]):
            raise RateLimitError(f"API rate limit exceeded for {operation}. Please wait before retrying.")
        
        # Check for invalid parameters
        if any(phrase in error_str for phrase in [
            'invalid parameter', 'missing parameter', 'parameter error'
        ]):
            raise ValidationError(f"Invalid parameters for {operation}: {error}")
        
        # Generic API error
        raise APIError(f"API call failed for {operation}: {error}")
    
    def _get_permission_guidance(self, operation: str) -> str:
        """Get specific guidance for permission errors."""
        guidance_map = {
            'hot_products': 'Hot products require special API permissions. Contact AliExpress to enable this feature.',
            'orders': 'Order tracking requires affiliate account with commission tracking enabled.',
            'affiliate_links': 'Affiliate link generation requires valid affiliate account status.',
            'product_details': 'Product details may require enhanced API access level.',
            'smart_match': 'Smart matching requires advanced API permissions and device_id parameter.'
        }
        
        return guidance_map.get(operation, 
            'This operation requires special API permissions. Check your AliExpress affiliate account settings.')
    
    def _retry_api_call(self, func, max_retries: int = 2, delay: float = 1.0):
        """Retry API calls with exponential backoff."""
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                error_str = str(e).lower()
                # Only retry on transient errors
                if any(phrase in error_str for phrase in [
                    'timeout', 'connection', 'network', 'temporary'
                ]):
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    raise e
    
    def get_parent_categories(self) -> List[CategoryResponse]:
        """Get all parent categories from AliExpress."""
        try:
            logger.info("Fetching parent categories from AliExpress API")
            categories = self.api.get_parent_categories()
            
            result = []
            for category in categories:
                result.append(CategoryResponse(
                    category_id=str(category.category_id),
                    category_name=category.category_name
                ))
            
            logger.info(f"Successfully retrieved {len(result)} parent categories")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get parent categories: {e}")
            raise APIError(f"Failed to get parent categories: {e}")
    
    def get_child_categories(self, parent_id: str) -> List[CategoryResponse]:
        """Get child categories for a given parent category ID."""
        if not parent_id or not parent_id.strip():
            raise ValidationError("parent_id cannot be empty")
        
        try:
            logger.info(f"Fetching child categories for parent_id={parent_id}")
            categories = self.api.get_child_categories(parent_id)
            
            result = []
            for category in categories:
                result.append(CategoryResponse(
                    category_id=str(category.category_id),
                    category_name=category.category_name,
                    parent_id=parent_id
                ))
            
            logger.info(f"Successfully retrieved {len(result)} child categories for parent_id={parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get child categories for parent_id={parent_id}: {e}")
            raise APIError(f"Failed to get child categories: {e}")
    
    def search_products(self, 
                       keywords: Optional[str] = None,
                       category_ids: Optional[str] = None,
                       page_no: int = 1,
                       page_size: int = 20,
                       sort: Optional[str] = None,
                       **kwargs) -> ProductSearchResponse:
        """Search for products using various criteria."""
        
        if page_size > 50:
            raise ValidationError("page_size cannot exceed 50")
        if page_no < 1:
            raise ValidationError("page_no must be at least 1")
        
        try:
            logger.info(f"Searching products with keywords='{keywords}', category_ids='{category_ids}', page={page_no}")
            
            # Prepare search parameters
            search_params = {
                'page_no': page_no,
                'page_size': page_size
            }
            
            if keywords:
                search_params['keywords'] = keywords
            if category_ids:
                search_params['category_ids'] = category_ids
            if sort:
                search_params['sort'] = sort
            
            # Add any additional parameters
            search_params.update(kwargs)
            
            # Call the SDK method
            products_result = self.api.get_products(**search_params)
            
            # Convert to our response format
            products = []
            if hasattr(products_result, 'products') and products_result.products:
                for product in products_result.products:
                    # Debug: log available attributes
                    logger.debug(f"Product attributes: {dir(product)}")
                    
                    # Use safe attribute access with fallbacks
                    product_id = getattr(product, 'product_id', 'unknown')
                    product_title = getattr(product, 'product_title', 'No title')
                    product_url = getattr(product, 'product_detail_url', 
                                        getattr(product, 'product_url', 'No URL'))
                    
                    # Handle price fields with various possible names
                    price = getattr(product, 'target_sale_price', 
                                  getattr(product, 'sale_price', 
                                        getattr(product, 'price', '0.00')))
                    
                    currency = getattr(product, 'target_sale_price_currency',
                                     getattr(product, 'currency', self.config.currency))
                    
                    image_url = getattr(product, 'product_main_image_url',
                                      getattr(product, 'image_url', None))
                    
                    commission_rate = getattr(product, 'commission_rate', None)
                    
                    products.append(ProductResponse(
                        product_id=str(product_id),
                        product_title=str(product_title),
                        product_url=str(product_url),
                        price=str(price),
                        currency=str(currency),
                        image_url=image_url,
                        commission_rate=str(commission_rate) if commission_rate else None
                    ))
            
            total_count = getattr(products_result, 'total_record_count', len(products))
            
            result = ProductSearchResponse(
                products=products,
                total_record_count=total_count,
                current_page=page_no,
                page_size=page_size
            )
            
            logger.info(f"Successfully found {len(products)} products (total: {total_count})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search products: {e}")
            raise APIError(f"Failed to search products: {e}")
    
    def get_products(self, 
                    keywords: Optional[str] = None,
                    max_sale_price: Optional[float] = None,
                    min_sale_price: Optional[float] = None,
                    category_id: Optional[str] = None,
                    page_no: int = 1,
                    page_size: int = 20,
                    sort: Optional[str] = None,
                    **kwargs) -> ProductSearchResponse:
        """Get products with enhanced filtering options."""
        
        if page_size > 50:
            raise ValidationError("page_size cannot exceed 50")
        if page_no < 1:
            raise ValidationError("page_no must be at least 1")
        
        try:
            logger.info(f"Getting products with keywords='{keywords}', price_range={min_sale_price}-{max_sale_price}")
            
            # Prepare search parameters
            search_params = {
                'page_no': page_no,
                'page_size': page_size
            }
            
            if keywords:
                search_params['keywords'] = keywords
            if max_sale_price is not None:
                search_params['max_sale_price'] = int(max_sale_price * 100)  # Convert to cents
            if min_sale_price is not None:
                search_params['min_sale_price'] = int(min_sale_price * 100)  # Convert to cents
            if category_id:
                search_params['category_ids'] = category_id
            if sort:
                search_params['sort'] = sort
            
            # Add any additional parameters
            search_params.update(kwargs)
            
            # Call the SDK method
            products_result = self.api.get_products(**search_params)
            
            # Convert to our response format
            products = []
            if hasattr(products_result, 'products') and products_result.products:
                for product in products_result.products:
                    products.append(self._convert_product_to_response(product))
            
            total_count = getattr(products_result, 'total_record_count', len(products))
            
            result = ProductSearchResponse(
                products=products,
                total_record_count=total_count,
                current_page=page_no,
                page_size=page_size
            )
            
            logger.info(f"Successfully found {len(products)} products (total: {total_count})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get products: {e}")
            raise APIError(f"Failed to get products: {e}")
    
    def get_products_details(self, product_ids: List[str]) -> List[ProductDetailResponse]:
        """Get detailed information for specific products."""
        
        if not product_ids:
            raise ValidationError("product_ids cannot be empty")
        if len(product_ids) > 20:
            raise ValidationError("Cannot request details for more than 20 products at once")
        
        try:
            logger.info(f"Getting product details for {len(product_ids)} products")
            
            # Call the SDK method
            details_result = self.api.get_products_details(product_ids)
            
            products = []
            if hasattr(details_result, 'products') and details_result.products:
                for product in details_result.products:
                    products.append(ProductDetailResponse(
                        product_id=str(getattr(product, 'product_id', 'unknown')),
                        product_title=str(getattr(product, 'product_title', 'No title')),
                        product_url=str(getattr(product, 'product_detail_url', 
                                              getattr(product, 'product_url', 'No URL'))),
                        price=str(getattr(product, 'target_sale_price', '0.00')),
                        currency=str(getattr(product, 'target_sale_price_currency', self.config.currency)),
                        image_url=getattr(product, 'product_main_image_url', None),
                        gallery_images=getattr(product, 'product_small_image_urls', []),
                        description=getattr(product, 'product_detail', None),
                        specifications=getattr(product, 'product_properties', None),
                        shipping_info=getattr(product, 'logistics_info', None),
                        seller_info=getattr(product, 'seller_info', None)
                    ))
            
            logger.info(f"Successfully retrieved details for {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Failed to get product details: {e}")
            raise APIError(f"Failed to get product details: {e}")
    
    def get_affiliate_links(self, urls: List[str]) -> List[AffiliateLink]:
        """Generate affiliate links for given product URLs."""
        
        if not urls:
            raise ValidationError("urls cannot be empty")
        if len(urls) > 50:
            raise ValidationError("Cannot process more than 50 URLs at once")
        
        try:
            logger.info(f"Generating affiliate links for {len(urls)} URLs")
            
            # Call the SDK method
            links_result = self.api.get_affiliate_links(urls)
            
            affiliate_links = []
            if hasattr(links_result, 'promotion_links') and links_result.promotion_links:
                for link_data in links_result.promotion_links:
                    affiliate_links.append(AffiliateLink(
                        original_url=str(getattr(link_data, 'source_value', '')),
                        affiliate_url=str(getattr(link_data, 'promotion_link', '')),
                        tracking_id=self.config.tracking_id,
                        commission_rate=str(getattr(link_data, 'commission_rate', None))
                    ))
            
            logger.info(f"Successfully generated {len(affiliate_links)} affiliate links")
            return affiliate_links
            
        except Exception as e:
            logger.error(f"Failed to generate affiliate links: {e}")
            raise APIError(f"Failed to generate affiliate links: {e}")
    
    def get_hotproducts(self, 
                       keywords: Optional[str] = None,
                       max_sale_price: Optional[float] = None,
                       sort: Optional[str] = None,
                       page_size: int = 20) -> HotProductResponse:
        """Get hot/trending products."""
        
        if page_size > 50:
            raise ValidationError("page_size cannot exceed 50")
        
        try:
            logger.info(f"Getting hot products with keywords='{keywords}', max_price={max_sale_price}")
            
            def _call_api():
                # Prepare search parameters
                search_params = {
                    'page_size': page_size
                }
                
                if keywords:
                    search_params['keywords'] = keywords
                if max_sale_price is not None:
                    search_params['max_sale_price'] = int(max_sale_price * 100)  # Convert to cents
                if sort:
                    search_params['sort'] = sort
                
                return self.api.get_hotproducts(**search_params)
            
            # Call with retry logic
            hot_result = self._retry_api_call(_call_api)
            
            products = []
            if hasattr(hot_result, 'products') and hot_result.products:
                for product in hot_result.products:
                    products.append(self._convert_product_to_response(product))
            
            total_count = getattr(hot_result, 'total_record_count', len(products))
            
            result = HotProductResponse(
                products=products,
                total_count=total_count
            )
            
            logger.info(f"Successfully found {len(products)} hot products")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get hot products: {e}")
            self._handle_api_error(e, 'hot_products')
    
    def get_order_list(self, 
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      page_no: int = 1,
                      page_size: int = 20) -> Dict[str, Any]:
        """Get order list (requires special permissions)."""
        
        if page_size > 50:
            raise ValidationError("page_size cannot exceed 50")
        if page_no < 1:
            raise ValidationError("page_no must be at least 1")
        
        try:
            logger.info(f"Getting order list for page {page_no}")
            
            # Prepare parameters
            params = {
                'page_no': page_no,
                'page_size': page_size
            }
            
            if start_time:
                params['start_time'] = start_time
            if end_time:
                params['end_time'] = end_time
            
            # Call the SDK method
            orders_result = self.api.get_order_list(**params)
            
            # Convert to dictionary format
            result = {
                'orders': [],
                'total_count': 0,
                'current_page': page_no,
                'page_size': page_size
            }
            
            if hasattr(orders_result, 'orders') and orders_result.orders:
                for order in orders_result.orders:
                    result['orders'].append({
                        'order_id': getattr(order, 'order_id', 'unknown'),
                        'order_status': getattr(order, 'order_status', 'unknown'),
                        'commission_rate': getattr(order, 'commission_rate', '0'),
                        'order_amount': getattr(order, 'order_amount', '0'),
                        'created_time': getattr(order, 'created_time', None)
                    })
                
                result['total_count'] = getattr(orders_result, 'total_count', len(result['orders']))
            
            logger.info(f"Successfully retrieved {len(result['orders'])} orders")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get order list: {e}")
            raise APIError(f"Failed to get order list: {e}")
    
    def smart_match_product(self, 
                           product_url: str,
                           target_language: Optional[str] = None,
                           target_currency: Optional[str] = None,
                           device_id: Optional[str] = None) -> Dict[str, Any]:
        """Smart match product by URL."""
        
        if not product_url or not product_url.strip():
            raise ValidationError("product_url cannot be empty")
        
        try:
            logger.info(f"Smart matching product: {product_url}")
            
            def _call_api():
                # Prepare parameters
                params = {
                    'product_url': product_url,
                    'device_id': device_id or 'default_device_id'  # SDK requires device_id
                }
                
                if target_language:
                    params['target_language'] = target_language
                if target_currency:
                    params['target_currency'] = target_currency
                
                return self.api.smart_match_product(**params)
            
            # Call with retry logic
            match_result = self._retry_api_call(_call_api)
            
            # Convert to dictionary format
            result = {
                'matched': False,
                'product_info': None
            }
            
            if match_result:
                result['matched'] = True
                result['product_info'] = {
                    'product_id': getattr(match_result, 'product_id', 'unknown'),
                    'product_title': getattr(match_result, 'product_title', 'No title'),
                    'product_url': getattr(match_result, 'product_url', product_url),
                    'price': getattr(match_result, 'target_sale_price', '0.00'),
                    'currency': getattr(match_result, 'target_sale_price_currency', self.config.currency)
                }
            
            logger.info(f"Smart match result: {'matched' if result['matched'] else 'no match'}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to smart match product: {e}")
            self._handle_api_error(e, 'smart_match')
    
    def _convert_product_to_response(self, product) -> ProductResponse:
        """Helper method to convert SDK product to ProductResponse."""
        return ProductResponse(
            product_id=str(getattr(product, 'product_id', 'unknown')),
            product_title=str(getattr(product, 'product_title', 'No title')),
            product_url=str(getattr(product, 'product_detail_url', 
                                  getattr(product, 'product_url', 'No URL'))),
            price=str(getattr(product, 'target_sale_price', '0.00')),
            currency=str(getattr(product, 'target_sale_price_currency', self.config.currency)),
            image_url=getattr(product, 'product_main_image_url', None),
            commission_rate=str(getattr(product, 'commission_rate', None)) if getattr(product, 'commission_rate', None) else None,
            original_price=str(getattr(product, 'target_original_price', None)) if getattr(product, 'target_original_price', None) else None,
            discount=str(getattr(product, 'discount', None)) if getattr(product, 'discount', None) else None,
            evaluate_rate=str(getattr(product, 'evaluate_rate', None)) if getattr(product, 'evaluate_rate', None) else None,
            orders_count=getattr(product, 'volume', None)
        )
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get service information and status."""
        return {
            'service': 'AliExpress API Service',
            'version': '2.0.0',
            'language': self.config.language,
            'currency': self.config.currency,
            'tracking_id': self.config.tracking_id,
            'status': 'active',
            'supported_endpoints': [
                'categories', 'products', 'product_details', 'affiliate_links',
                'hot_products', 'orders', 'smart_match'
            ],
            'sdk_methods': [
                'get_parent_categories', 'get_child_categories', 'get_products',
                'get_products_details', 'get_affiliate_links', 'get_hotproducts',
                'get_order_list', 'smart_match_product'
            ],
            'notes': {
                'hot_products': 'Requires special API permissions',
                'orders': 'Requires affiliate account with order tracking permissions',
                'affiliate_links': 'Works with valid AliExpress product URLs'
            }
        }