"""AliExpress Affiliate Product Query API service module."""

from typing import Optional
from .base import RestApi

class AliexpressAffiliateProductQueryRequest(RestApi):
    """Service class for aliexpress.affiliate.product.query API."""
    
    def __init__(self, domain: str = "api-sg.aliexpress.com", port: int = 80) -> None:
        RestApi.__init__(self, domain, port)
        self.app_signature: Optional[str] = None
        self.category_ids: Optional[str] = None
        self.delivery_days: Optional[int] = None
        self.fields: Optional[str] = None
        self.keywords: Optional[str] = None
        self.max_sale_price: Optional[int] = None
        self.min_sale_price: Optional[int] = None
        self.page_no: Optional[int] = None
        self.page_size: Optional[int] = None
        self.platform_product_type: Optional[str] = None
        self.ship_to_country: Optional[str] = None
        self.sort: Optional[str] = None
        self.target_currency: Optional[str] = None
        self.target_language: Optional[str] = None
        self.tracking_id: Optional[str] = None

    def getapiname(self) -> str:
        return "aliexpress.affiliate.product.query"