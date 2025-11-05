"""AliExpress Affiliate Order Get API service module."""

from .base import RestApi


class AliexpressAffiliateOrderGetRequest(RestApi):
    """Service class for aliexpress.affiliate.order.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.app_signature = None
        self.end_time = None
        self.fields = None
        self.locale_site = None
        self.page_no = None
        self.page_size = None
        self.start_time = None
        self.status = None
        self.tracking_id = None

    def getapiname(self):
        return "aliexpress.affiliate.order.get"