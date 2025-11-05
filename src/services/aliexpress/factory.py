"""Factory class for creating AliExpress API service instances."""

from typing import Dict, Type, Any
from ...utils.config import Config
from .base import RestApi

# Import all service classes
from .affiliate_product_query import AliexpressAffiliateProductQueryRequest
from .affiliate_category_get import AliexpressAffiliateCategoryGetRequest
from .affiliate_link_generate import AliexpressAffiliateLinkGenerateRequest
from .affiliate_hotproduct_query import AliexpressAffiliateHotproductQueryRequest
from .affiliate_productdetail_get import AliexpressAffiliateProductdetailGetRequest
from .affiliate_order_get import AliexpressAffiliateOrderGetRequest
from .affiliate_order_list import AliexpressAffiliateOrderListRequest
from .affiliate_featuredpromo_products_get import AliexpressAffiliateFeaturedpromoProductsGetRequest
from .affiliate_featuredpromo_get import AliexpressAffiliateFeaturedpromoGetRequest
from .affiliate_image_search import AliexpressAffiliateImageSearchRequest
from .affiliate_product_smartmatch import AliexpressAffiliateProductSmartmatchRequest
from .ds_product_get import AliexpressDsProductGetRequest
from .ds_recommend_feed_get import AliexpressDsRecommendFeedGetRequest
from .ds_trade_order_get import AliexpressDsTradeOrderGetRequest
from .solution_product_info_get import AliexpressSolutionProductInfoGetRequest
from .solution_product_posts_get import AliexpressSolutionProductPostsGetRequest


class AliExpressServiceFactory:
    """Factory for creating AliExpress API service instances."""
    
    # Registry of available service classes
    _services: Dict[str, Type[RestApi]] = {
        # Affiliate API services
        'affiliate.product.query': AliexpressAffiliateProductQueryRequest,
        'affiliate.category.get': AliexpressAffiliateCategoryGetRequest,
        'affiliate.link.generate': AliexpressAffiliateLinkGenerateRequest,
        'affiliate.hotproduct.query': AliexpressAffiliateHotproductQueryRequest,
        'affiliate.productdetail.get': AliexpressAffiliateProductdetailGetRequest,
        'affiliate.order.get': AliexpressAffiliateOrderGetRequest,
        'affiliate.order.list': AliexpressAffiliateOrderListRequest,
        'affiliate.featuredpromo.products.get': AliexpressAffiliateFeaturedpromoProductsGetRequest,
        'affiliate.featuredpromo.get': AliexpressAffiliateFeaturedpromoGetRequest,
        'affiliate.image.search': AliexpressAffiliateImageSearchRequest,
        'affiliate.product.smartmatch': AliexpressAffiliateProductSmartmatchRequest,
        
        # Dropshipping API services
        'ds.product.get': AliexpressDsProductGetRequest,
        'ds.recommend.feed.get': AliexpressDsRecommendFeedGetRequest,
        'ds.trade.order.get': AliexpressDsTradeOrderGetRequest,
        
        # Solution API services
        'solution.product.info.get': AliexpressSolutionProductInfoGetRequest,
        'solution.product.posts.get': AliexpressSolutionProductPostsGetRequest,
    }
    
    def __init__(self, config: Config):
        """Initialize the factory with configuration."""
        self.config = config
    
    def create_service(self, service_name: str, **kwargs) -> RestApi:
        """
        Create a service instance by name.
        
        Args:
            service_name: The service name (e.g., 'affiliate.product.query')
            **kwargs: Additional parameters to pass to the service constructor
            
        Returns:
            Configured service instance
            
        Raises:
            ValueError: If service_name is not found
        """
        if service_name not in self._services:
            available_services = list(self._services.keys())
            raise ValueError(f"Unknown service '{service_name}'. Available services: {available_services}")
        
        service_class = self._services[service_name]
        service_instance = service_class(**kwargs)
        service_instance.set_config(self.config)
        
        return service_instance
    
    def get_available_services(self) -> Dict[str, str]:
        """Get a list of all available services with their descriptions."""
        return {
            # Affiliate API
            'affiliate.product.query': 'Search for affiliate products',
            'affiliate.category.get': 'Get product categories',
            'affiliate.link.generate': 'Generate affiliate links',
            'affiliate.hotproduct.query': 'Get hot/trending products',
            'affiliate.productdetail.get': 'Get detailed product information',
            'affiliate.order.get': 'Get order information',
            'affiliate.order.list': 'List orders',
            'affiliate.featuredpromo.products.get': 'Get featured promotion products',
            'affiliate.featuredpromo.get': 'Get featured promotions',
            'affiliate.image.search': 'Search products by image',
            'affiliate.product.smartmatch': 'Smart match products',
            
            # Dropshipping API
            'ds.product.get': 'Get dropshipping product details',
            'ds.recommend.feed.get': 'Get recommended product feed',
            'ds.trade.order.get': 'Get dropshipping order details',
            
            # Solution API
            'solution.product.info.get': 'Get solution product information',
            'solution.product.posts.get': 'Get solution product posts',
        }
    
    # Convenience methods for commonly used services
    def product_query(self, **params) -> AliexpressAffiliateProductQueryRequest:
        """Create a product query service instance."""
        service = self.create_service('affiliate.product.query')
        for key, value in params.items():
            if hasattr(service, key):
                setattr(service, key, value)
        return service
    
    def category_get(self, **params) -> AliexpressAffiliateCategoryGetRequest:
        """Create a category get service instance."""
        service = self.create_service('affiliate.category.get')
        for key, value in params.items():
            if hasattr(service, key):
                setattr(service, key, value)
        return service
    
    def link_generate(self, **params) -> AliexpressAffiliateLinkGenerateRequest:
        """Create a link generate service instance."""
        service = self.create_service('affiliate.link.generate')
        for key, value in params.items():
            if hasattr(service, key):
                setattr(service, key, value)
        return service
    
    def hotproduct_query(self, **params) -> AliexpressAffiliateHotproductQueryRequest:
        """Create a hot product query service instance."""
        service = self.create_service('affiliate.hotproduct.query')
        for key, value in params.items():
            if hasattr(service, key):
                setattr(service, key, value)
        return service
    
    def image_search(self, **params) -> AliexpressAffiliateImageSearchRequest:
        """Create an image search service instance."""
        service = self.create_service('affiliate.image.search')
        for key, value in params.items():
            if hasattr(service, key):
                setattr(service, key, value)
        return service