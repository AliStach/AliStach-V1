"""AliExpress Affiliate Product Detail Get API service module."""

from .base import RestApi

class AliexpressAffiliateProductdetailGetRequest(RestApi):
    """Service class for aliexpress.affiliate.productdetail.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app_signature = None
        self.country = None
        self.fields = None
        self.product_ids = None
        self.target_currency = None
        self.target_language = None
        self.tracking_id = None

    def getapiname(self):
        return "aliexpress.affiliate.productdetail.get"