"""AliExpress Affiliate Product Smart Match API service module."""

from .base import RestApi


class AliexpressAffiliateProductSmartmatchRequest(RestApi):
    """Service class for aliexpress.affiliate.product.smartmatch API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app = None
        self.app_signature = None
        self.country = None
        self.device = None
        self.device_id = None
        self.fields = None
        self.keywords = None
        self.page_no = None
        self.product_id = None
        self.site = None
        self.target_currency = None
        self.target_language = None
        self.tracking_id = None
        self.user = None

    def getapiname(self):
        return "aliexpress.affiliate.product.smartmatch"