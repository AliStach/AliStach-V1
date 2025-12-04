"""AliExpress Solution Product Posts Get API service module."""

from .base import RestApi

class AliexpressSolutionProductPostsGetRequest(RestApi):
    """Service class for aliexpress.solution.product.posts.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.category_id = None
        self.keywords = None
        self.max_sale_price = None
        self.min_sale_price = None
        self.page_no = None
        self.page_size = None
        self.ship_to_country = None
        self.sort = None
        self.target_currency = None
        self.target_language = None

    def getapiname(self):
        return "aliexpress.solution.product.posts.get"