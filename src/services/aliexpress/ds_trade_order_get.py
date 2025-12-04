"""AliExpress DS Trade Order Get API service module."""

from .base import RestApi

class AliexpressDsTradeOrderGetRequest(RestApi):
    """Service class for aliexpress.ds.trade.order.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.order_id = None

    def getapiname(self):
        return "aliexpress.ds.trade.order.get"