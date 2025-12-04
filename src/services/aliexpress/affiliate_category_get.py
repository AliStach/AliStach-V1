"""AliExpress Affiliate Category Get API service module."""

from .base import RestApi

class AliexpressAffiliateCategoryGetRequest(RestApi):
    """Service class for aliexpress.affiliate.category.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app_signature = None
        self.tracking_id = None

    def getapiname(self):
        return "aliexpress.affiliate.category.get"