"""AliExpress Affiliate Image Search API service module."""

from .base import RestApi


class AliexpressAffiliateImageSearchRequest(RestApi):
    """Service class for aliexpress.affiliate.image.search API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app_signature = None
        self.category_ids = None
        self.fields = None
        self.image_url = None
        self.max_sale_price = None
        self.min_sale_price = None
        self.page_no = None
        self.page_size = None
        self.sort = None
        self.target_currency = None
        self.target_language = None
        self.tracking_id = None

    def getapiname(self):
        return "aliexpress.affiliate.image.search"