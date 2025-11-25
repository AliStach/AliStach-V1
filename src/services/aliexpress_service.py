"""AliExpress API service using the official Python SDK."""

import logging
import time
import json
import os
from typing import List, Optional, Dict, Any
from aliexpress_api import AliexpressApi, models
from ..utils.config import Config
from ..models.responses import (
    CategoryResponse, ProductResponse, ProductSearchResponse, ProductDetailResponse,
    AffiliateLink, HotProductResponse, PromoProductResponse, ShippingInfo, ServiceResponse
)


# Get logger (don't configure at module level - let main.py handle it)
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
        """Initialize the AliExpress service with configuration.
        
        Args:
            config: Configuration object with API credentials
        """
        self.config = config
        
        # Initialize the AliExpress API client
        self.api = AliexpressApi(
            key=config.app_key,
            secret=config.app_secret,
            language=getattr(models.Language, config.language),
            currency=getattr(models.Currency, config.currency),
            tracking_id=config.tracking_id
        )
        logger.info(f"AliExpress API initialized with language={config.language}, currency={config.currency}")
    
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
    
    def _retry_api_call(self, func, max_retries: int = 2, delay: float = 1.0) -> Any:
        """Retry API calls with exponential backoff."""
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    # Log final failure before raising
                    logger.error(f"API call failed after {max_retries + 1} attempts: {e}")
                    raise e
                
                error_str = str(e).lower()
                # Only retry on transient errors
                if any(phrase in error_str for phrase in [
                    'timeout', 'connection', 'network', 'temporary', 'server error'
                ]):
                    wait_time = delay * (2 ** attempt)
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    # Non-retryable error, raise immediately
                    logger.error(f"Non-retryable error encountered: {e}")
                    raise e
        
        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
    
    def get_parent_categories(self) -> List[CategoryResponse]:
        """Get all parent categories from AliExpress."""
        try:
            logger.info("Fetching parent categories from AliExpress API")
            
            def _call_api():
                return self.api.get_parent_categories()
            
            # Use retry logic for better reliability
            categories = self._retry_api_call(_call_api)
            
            if not categories:
                logger.warning("No parent categories returned from API")
                return []
            
            result = []
            for category in categories:
                try:
                    result.append(CategoryResponse(
                        category_id=str(category.category_id),
                        category_name=category.category_name
                    ))
                except AttributeError as e:
                    logger.warning(f"Skipping malformed category data: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(result)} parent categories")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get parent categories: {e}")
            self._handle_api_error(e, 'parent_categories')
    
    def get_child_categories(self, parent_id: str) -> List[CategoryResponse]:
        """Get child categories for a given parent category ID."""
        if not parent_id or not parent_id.strip():
            raise ValidationError("parent_id cannot be empty")
        
        # Validate parent_id format (should be numeric)
        try:
            int(parent_id)
        except ValueError:
            raise ValidationError(f"parent_id must be a valid numeric ID, got: {parent_id}")
        
        try:
            logger.info(f"Fetching child categories for parent_id={parent_id}")
            
            def _call_api():
                return self.api.get_child_categories(parent_id)
            
            # Use retry logic for better reliability
            categories = self._retry_api_call(_call_api)
            
            if not categories:
                logger.info(f"No child categories found for parent_id={parent_id}")
                return []
            
            result = []
            for category in categories:
                try:
                    result.append(CategoryResponse(
                        category_id=str(category.category_id),
                        category_name=category.category_name,
                        parent_id=parent_id
                    ))
                except AttributeError as e:
                    logger.warning(f"Skipping malformed category data: {e}")
                    continue
            
            logger.info(f"Successfully retrieved {len(result)} child categories for parent_id={parent_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get child categories for parent_id={parent_id}: {e}")
            self._handle_api_error(e, 'child_categories')
    
    def search_products(self, 
                       keywords: Optional[str] = None,
                       category_ids: Optional[str] = None,
                       page_no: int = 1,
                       page_size: int = 20,
                       sort: Optional[str] = None,
                       auto_generate_affiliate_links: bool = True,
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
            
            # Convert to our response format and generate affiliate links
            products = []
            product_urls = []  # Collect URLs for batch affiliate link generation
            
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
                    
                    # Store product data temporarily
                    products.append({
                        'product_id': str(product_id),
                        'product_title': str(product_title),
                        'original_url': str(product_url),
                        'price': str(price),
                        'currency': str(currency),
                        'image_url': image_url,
                        'commission_rate': str(commission_rate) if commission_rate else None
                    })
                    
                    # Collect URLs for batch affiliate link generation
                    if auto_generate_affiliate_links and product_url != 'No URL':
                        product_urls.append(str(product_url))
            
            # Generate affiliate links in batch if requested
            affiliate_links_map = {}
            if auto_generate_affiliate_links and product_urls:
                try:
                    logger.info(f"Generating affiliate links for {len(product_urls)} products")
                    affiliate_links = self.get_affiliate_links(product_urls)
                    
                    # Create mapping from original URL to affiliate URL
                    for link in affiliate_links:
                        affiliate_links_map[link.original_url] = link.affiliate_url
                    
                    logger.info(f"Successfully generated {len(affiliate_links)} affiliate links")
                except Exception as e:
                    logger.warning(f"Failed to generate affiliate links: {e}")
                    # Continue without affiliate links rather than failing completely
            
            # Create final ProductResponse objects with affiliate links
            final_products = []
            for product_data in products:
                original_url = product_data['original_url']
                
                # Use affiliate link if available, otherwise use original URL
                final_url = affiliate_links_map.get(original_url, original_url)
                
                final_products.append(ProductResponse(
                    product_id=product_data['product_id'],
                    product_title=product_data['product_title'],
                    product_url=final_url,  # This is now an affiliate link!
                    price=product_data['price'],
                    currency=product_data['currency'],
                    image_url=product_data['image_url'],
                    commission_rate=product_data['commission_rate']
                ))
            
            total_count = getattr(products_result, 'total_record_count', len(final_products))
            
            result = ProductSearchResponse(
                products=final_products,
                total_record_count=total_count,
                current_page=page_no,
                page_size=page_size
            )
            
            affiliate_count = len(affiliate_links_map)
            logger.info(f"Successfully found {len(final_products)} products (total: {total_count})")
            logger.info(f"Generated {affiliate_count} affiliate links out of {len(product_urls)} products")
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
                    auto_generate_affiliate_links: bool = True,
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
            
            # Convert to our response format and generate affiliate links
            products = []
            product_urls = []
            
            if hasattr(products_result, 'products') and products_result.products:
                for product in products_result.products:
                    product_response = self._convert_product_to_response(product)
                    products.append(product_response)
                    
                    # Collect URLs for batch affiliate link generation
                    if auto_generate_affiliate_links and product_response.product_url != 'No URL':
                        product_urls.append(product_response.product_url)
            
            # Generate affiliate links in batch if requested
            if auto_generate_affiliate_links and product_urls:
                try:
                    logger.info(f"Generating affiliate links for {len(product_urls)} products")
                    affiliate_links = self.get_affiliate_links(product_urls)
                    
                    # Create mapping from original URL to affiliate URL
                    affiliate_links_map = {link.original_url: link.affiliate_url for link in affiliate_links}
                    
                    # Update product URLs with affiliate links
                    for product in products:
                        if product.product_url in affiliate_links_map:
                            product.product_url = affiliate_links_map[product.product_url]
                    
                    logger.info(f"Successfully generated {len(affiliate_links)} affiliate links")
                except Exception as e:
                    logger.warning(f"Failed to generate affiliate links: {e}")
                    # Continue without affiliate links rather than failing completely
            
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
            logger.debug(f"URLs to convert: {urls}")
            
            # Call the SDK method
            links_result = self.api.get_affiliate_links(urls)
            
            # Debug: Log the actual response structure
            logger.debug(f"Affiliate links response type: {type(links_result)}")
            logger.debug(f"Affiliate links response attributes: {dir(links_result)}")
            
            affiliate_links = []
            
            # Check different possible response formats
            if hasattr(links_result, 'promotion_links') and links_result.promotion_links:
                logger.info(f"Found promotion_links with {len(links_result.promotion_links)} items")
                for link_data in links_result.promotion_links:
                    logger.debug(f"Link data attributes: {dir(link_data)}")
                    affiliate_links.append(AffiliateLink(
                        original_url=str(getattr(link_data, 'source_value', '')),
                        affiliate_url=str(getattr(link_data, 'promotion_link', '')),
                        tracking_id=self.config.tracking_id,
                        commission_rate=str(getattr(link_data, 'commission_rate', None))
                    ))
            elif isinstance(links_result, list):
                logger.info(f"Response is a list with {len(links_result)} items")
                for link_data in links_result:
                    logger.debug(f"Link data attributes: {dir(link_data)}")
                    affiliate_links.append(AffiliateLink(
                        original_url=str(getattr(link_data, 'source_value', getattr(link_data, 'original_url', ''))),
                        affiliate_url=str(getattr(link_data, 'promotion_link', getattr(link_data, 'affiliate_url', ''))),
                        tracking_id=self.config.tracking_id,
                        commission_rate=str(getattr(link_data, 'commission_rate', None))
                    ))
            else:
                logger.warning(f"Unexpected response format: {links_result}")
                logger.warning(f"Response content: {str(links_result)[:200]}...")
            
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
    
    def search_products_by_image(self, image_url: str, **kwargs) -> Dict[str, Any]:
        """
        Search for products using image URL via AliExpress native image search API.
        
        This method calls the official AliExpress image search endpoint:
        aliexpress.affiliate.image.search
        
        Args:
            image_url: URL of the image to search for similar products
            **kwargs: Additional parameters like category_id, page_size, etc.
            
        Returns:
            Dictionary with search results including products and metadata
        """
        if not image_url or not image_url.strip():
            raise ValidationError("image_url cannot be empty")
        
        try:
            logger.info(f"Searching products by image: {image_url}")
            
            # Prepare parameters for the native AliExpress image search API
            search_params = {
                'image_url': image_url,
                'page_size': kwargs.get('page_size', 20),
                'page_no': kwargs.get('page_no', 1),
                'fields': 'product_id,product_title,product_main_image_url,target_sale_price,target_sale_price_currency,product_detail_url,commission_rate,category_id'
            }
            
            # Add optional parameters
            if kwargs.get('category_id'):
                search_params['category_id'] = kwargs['category_id']
            if kwargs.get('max_sale_price'):
                search_params['max_sale_price'] = int(kwargs['max_sale_price'] * 100)  # Convert to cents
            if kwargs.get('min_sale_price'):
                search_params['min_sale_price'] = int(kwargs['min_sale_price'] * 100)  # Convert to cents
            
            # Call the native AliExpress image search API
            # Since the SDK doesn't have this method, we'll call it directly
            result = self._call_image_search_api(search_params)
            
            logger.info(f"Image search completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search products by image: {e}")
            self._handle_api_error(e, 'image_search')
    
    def _call_image_search_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the native AliExpress image search API endpoint.
        
        Uses the same authentication and signing mechanism as the SDK.
        """
        import time
        import hashlib
        import hmac
        import requests
        from urllib.parse import quote
        
        # API endpoint for image search
        api_url = "https://api-sg.aliexpress.com/sync"
        
        # Prepare common parameters
        common_params = {
            'app_key': self.config.app_key,
            'method': 'aliexpress.affiliate.image.search',
            'timestamp': str(int(time.time() * 1000)),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'sha256',
            'tracking_id': self.config.tracking_id
        }
        
        # Merge with search parameters
        all_params = {**common_params, **params}
        
        # Generate signature
        signature = self._generate_api_signature(all_params, self.config.app_secret)
        all_params['sign'] = signature
        
        try:
            # Make the API request
            response = requests.post(api_url, data=all_params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for API errors
            if 'error_response' in result:
                error_info = result['error_response']
                raise APIError(f"AliExpress API error: {error_info.get('msg', 'Unknown error')}")
            
            # Parse the response
            if 'aliexpress_affiliate_image_search_response' in result:
                search_response = result['aliexpress_affiliate_image_search_response']
                return self._parse_image_search_response(search_response)
            else:
                raise APIError("Unexpected API response format")
                
        except requests.RequestException as e:
            raise APIError(f"Network error during image search: {e}")
        except Exception as e:
            raise APIError(f"Image search API call failed: {e}")
    
    def _generate_api_signature(self, params: Dict[str, Any], app_secret: str) -> str:
        """Generate API signature for AliExpress API calls."""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = ''.join([f'{k}{v}' for k, v in sorted_params])
        
        # Create signature string
        sign_string = app_secret + query_string + app_secret
        
        # Generate SHA256 hash
        signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().upper()
        
        return signature
    
    def _parse_image_search_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the AliExpress image search API response."""
        try:
            products = []
            
            # Extract products from response
            if 'result' in response and 'products' in response['result']:
                for product_data in response['result']['products']:
                    product = ProductResponse(
                        product_id=str(product_data.get('product_id', 'unknown')),
                        product_title=str(product_data.get('product_title', 'No title')),
                        product_url=str(product_data.get('product_detail_url', '')),
                        price=str(product_data.get('target_sale_price', '0.00')),
                        currency=str(product_data.get('target_sale_price_currency', self.config.currency)),
                        image_url=product_data.get('product_main_image_url'),
                        commission_rate=str(product_data.get('commission_rate', '')) if product_data.get('commission_rate') else None
                    )
                    products.append(product)
            
            # Extract metadata
            total_count = response.get('result', {}).get('total_record_count', len(products))
            current_page = response.get('result', {}).get('current_page', 1)
            
            return {
                'products': products,
                'total_record_count': total_count,
                'current_page': current_page,
                'page_size': len(products),
                'image_search_method': 'native_aliexpress_api'
            }
            
        except Exception as e:
            logger.error(f"Failed to parse image search response: {e}")
            raise APIError(f"Failed to parse image search response: {e}")

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
    
    def search_products_by_image(self, image_url: str, **kwargs) -> Dict[str, Any]:
        """
        Search for products using image URL via AliExpress native image search API.
        
        This method uses the official AliExpress image search endpoint:
        aliexpress.affiliate.image.search
        
        Args:
            image_url: URL of the image to search for similar products
            **kwargs: Additional parameters like category_ids, page_size, etc.
            
        Returns:
            Dictionary with search results including products and metadata
        """
        
        if not image_url or not image_url.strip():
            raise ValidationError("image_url cannot be empty")
        
        try:
            logger.info(f"Searching products by image: {image_url}")
            
            # Prepare parameters for the image search API
            search_params = {
                'image_url': image_url,
                'page_no': kwargs.get('page_no', 1),
                'page_size': kwargs.get('page_size', 20),
                'target_currency': self.config.currency,
                'target_language': self.config.language,
                'tracking_id': self.config.tracking_id
            }
            
            # Add optional parameters
            if kwargs.get('category_ids'):
                search_params['category_ids'] = kwargs['category_ids']
            if kwargs.get('max_sale_price'):
                search_params['max_sale_price'] = int(kwargs['max_sale_price'] * 100)
            if kwargs.get('min_sale_price'):
                search_params['min_sale_price'] = int(kwargs['min_sale_price'] * 100)
            if kwargs.get('sort'):
                search_params['sort'] = kwargs['sort']
            
            # Make direct API call to AliExpress image search endpoint
            result = self._make_image_search_request(search_params)
            
            # Parse and convert results to our format
            products = []
            if result.get('products'):
                for product_data in result['products']:
                    products.append(ProductResponse(
                        product_id=str(product_data.get('product_id', 'unknown')),
                        product_title=str(product_data.get('product_title', 'No title')),
                        product_url=str(product_data.get('product_detail_url', 
                                              product_data.get('product_url', 'No URL'))),
                        price=str(product_data.get('target_sale_price', '0.00')),
                        currency=str(product_data.get('target_sale_price_currency', self.config.currency)),
                        image_url=product_data.get('product_main_image_url'),
                        commission_rate=str(product_data.get('commission_rate', None)) if product_data.get('commission_rate') else None,
                        original_price=str(product_data.get('target_original_price', None)) if product_data.get('target_original_price') else None,
                        discount=str(product_data.get('discount', None)) if product_data.get('discount') else None,
                        evaluate_rate=str(product_data.get('evaluate_rate', None)) if product_data.get('evaluate_rate') else None,
                        orders_count=product_data.get('volume', None)
                    ))
            
            search_response = ProductSearchResponse(
                products=products,
                total_record_count=result.get('total_record_count', len(products)),
                current_page=search_params['page_no'],
                page_size=search_params['page_size']
            )
            
            logger.info(f"Successfully found {len(products)} products via image search")
            return {
                'search_result': search_response,
                'image_url': image_url,
                'search_method': 'native_aliexpress_api'
            }
            
        except Exception as e:
            logger.error(f"Failed to search products by image: {e}")
            raise APIError(f"Image search failed: {e}")
    
    def _make_image_search_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make direct API request to AliExpress image search endpoint.
        
        Uses the official aliexpress.affiliate.image.search API method.
        """
        import hashlib
        import hmac
        import time
        import json
        import requests
        from urllib.parse import quote
        
        # AliExpress API endpoint for image search
        api_url = "https://api-sg.aliexpress.com/sync"
        method = "aliexpress.affiliate.image.search"
        
        # Prepare API parameters
        api_params = {
            'method': method,
            'app_key': self.config.app_key,
            'timestamp': str(int(time.time() * 1000)),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'sha256',
            **params
        }
        
        # Generate signature
        signature = self._generate_api_signature(api_params, self.config.app_secret)
        api_params['sign'] = signature
        
        try:
            # Make the API request
            response = requests.post(api_url, data=api_params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for API errors
            if 'error_response' in result:
                error_info = result['error_response']
                error_msg = error_info.get('msg', 'Unknown API error')
                error_code = error_info.get('code', 'unknown')
                
                # Handle specific error cases
                if 'permission' in error_msg.lower() or error_code in ['27', '50']:
                    raise PermissionError(f"Image search requires special API permissions: {error_msg}")
                elif 'not found' in error_msg.lower() or error_code == '40':
                    raise ValidationError(f"Invalid image URL or image not accessible: {error_msg}")
                else:
                    raise APIError(f"AliExpress API error ({error_code}): {error_msg}")
            
            # Extract the actual response data
            if method.replace('.', '_') + '_response' in result:
                return result[method.replace('.', '_') + '_response']['result']
            else:
                return result
                
        except requests.RequestException as e:
            raise APIError(f"Network error during image search: {e}")
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response from AliExpress API: {e}")
    
    def _generate_api_signature(self, params: Dict[str, Any], app_secret: str) -> str:
        """Generate SHA256 signature for AliExpress API requests."""
        import hashlib
        import hmac
        
        # Sort parameters and create query string
        sorted_params = sorted(params.items())
        query_string = ''.join([f'{k}{v}' for k, v in sorted_params])
        
        # Create signature string
        sign_string = app_secret + query_string + app_secret
        
        # Generate SHA256 hash
        signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().upper()
        
        return signature

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
                'hot_products', 'orders', 'smart_match', 'image_search'
            ],
            'sdk_methods': [
                'get_parent_categories', 'get_child_categories', 'get_products',
                'get_products_details', 'get_affiliate_links', 'get_hotproducts',
                'get_order_list', 'smart_match_product', 'search_products_by_image'
            ],
            'notes': {
                'hot_products': 'Requires special API permissions',
                'orders': 'Requires affiliate account with order tracking permissions',
                'affiliate_links': 'Works with valid AliExpress product URLs',
                'image_search': 'Uses native AliExpress image search API - may require special permissions'
            }
        }