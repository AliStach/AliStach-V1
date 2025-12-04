"""AliExpress Solution Product Info Get API service module."""

from .base import RestApi

class AliexpressSolutionProductInfoGetRequest(RestApi):
    """Service class for aliexpress.solution.product.info.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.product_id = None
        self.ship_to_country = None
        self.target_currency = None
        self.target_language = None

    def getapiname(self):
        return "aliexpress.solution.product.info.get"