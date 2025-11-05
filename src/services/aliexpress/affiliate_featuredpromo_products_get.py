"""AliExpress Affiliate Featured Promo Products Get API service module."""

from .base import RestApi


class AliexpressAffiliateFeaturedpromoProductsGetRequest(RestApi):
    """Service class for aliexpress.affiliate.featuredpromo.products.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app_signature = None
        self.category_id = None
        self.country = None
        self.fields = None
        self.page_no = None
        self.page_size = None
        self.promotion_end_time = None
        self.promotion_name = None
        self.promotion_start_time = None
        self.sort = None
        self.target_currency = None
        self.target_language = None
        self.tracking_id = None

    def getapiname(self):
        return "aliexpress.affiliate.featuredpromo.products.get"