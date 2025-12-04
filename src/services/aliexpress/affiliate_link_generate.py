"""AliExpress Affiliate Link Generate API service module."""

from .base import RestApi

class AliexpressAffiliateLinkGenerateRequest(RestApi):
    """Service class for aliexpress.affiliate.link.generate API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app_signature = None
        self.promotion_link_type = None
        self.source_values = None
        self.tracking_id = None

    def getapiname(self):
        return "aliexpress.affiliate.link.generate"