"""AliExpress DS Recommend Feed Get API service module."""

from .base import RestApi


class AliexpressDsRecommendFeedGetRequest(RestApi):
    """Service class for aliexpress.ds.recommend.feed.get API."""
    
    def __init__(self, domain="api-sg.aliexpress.com", port=80):
        RestApi.__init__(self, domain, port)
        self.category_id = None
        self.country = None
        self.feed_name = None
        self.page_no = None
        self.page_size = None
        self.sort = None
        self.target_currency = None
        self.target_language = None

    def getapiname(self):
        return "aliexpress.ds.recommend.feed.get"