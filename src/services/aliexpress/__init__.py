"""AliExpress API service modules."""

from .base import RestApi
from .factory import AliExpressServiceFactory

# Affiliate API modules
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

# Dropshipping API modules
from .ds_product_get import AliexpressDsProductGetRequest
from .ds_recommend_feed_get import AliexpressDsRecommendFeedGetRequest
from .ds_trade_order_get import AliexpressDsTradeOrderGetRequest

# Solution API modules
from .solution_product_info_get import AliexpressSolutionProductInfoGetRequest
from .solution_product_posts_get import AliexpressSolutionProductPostsGetRequest

__all__ = [
    'RestApi',
    'AliExpressServiceFactory',
    # Affiliate API
    'AliexpressAffiliateProductQueryRequest',
    'AliexpressAffiliateCategoryGetRequest', 
    'AliexpressAffiliateLinkGenerateRequest',
    'AliexpressAffiliateHotproductQueryRequest',
    'AliexpressAffiliateProductdetailGetRequest',
    'AliexpressAffiliateOrderGetRequest',
    'AliexpressAffiliateOrderListRequest',
    'AliexpressAffiliateFeaturedpromoProductsGetRequest',
    'AliexpressAffiliateFeaturedpromoGetRequest',
    'AliexpressAffiliateImageSearchRequest',
    'AliexpressAffiliateProductSmartmatchRequest',
    # Dropshipping API
    'AliexpressDsProductGetRequest',
    'AliexpressDsRecommendFeedGetRequest',
    'AliexpressDsTradeOrderGetRequest',
    # Solution API
    'AliexpressSolutionProductInfoGetRequest',
    'AliexpressSolutionProductPostsGetRequest',
]