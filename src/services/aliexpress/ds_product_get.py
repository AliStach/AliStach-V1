"""AliExpress DS Product Get API service module."""

from .base import RestApi

class AliexpressDsProductGetRequest(RestApi):
    """Service class for aliexpress.ds.product.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.product_id = None
        self.target_currency = None
        self.target_language = None
        self.ship_to_country = None

    def getapiname(self):
        return "aliexpress.ds.product.get"