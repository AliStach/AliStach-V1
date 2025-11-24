"""Enhanced AliExpress service with automatic mock mode fallback."""

import logging
from typing import List, Optional
from .aliexpress_service import AliExpressService, AliExpressServiceException
from .mock_data_service import MockDataService
from ..models.responses import (
    CategoryResponse, ProductResponse, ProductSearchResponse, 
    ProductDetailResponse, AffiliateLink
)

logger = logging.getLogger(__name__)


class AliExpressServiceWithMock(AliExpressService):
    """Enhanced AliExpress service that automatically falls back to mock data."""
    
    def get_parent_categories(self) -> List[CategoryResponse]:
        """Get all parent categories - with mock fallback."""
        if self.mock_mode:
            logger.info("Fetching parent categories from MOCK DATA")
            mock_categories = MockDataService.get_parent_categories()
            return [
                CategoryResponse(
                    category_id=cat["category_id"],
                    category_name=cat["category_name"]
                )
                for cat in mock_categories
            ]
        
        try:
            return super().get_parent_categories()
        except AliExpressServiceException:
            logger.warning("Falling back to mock data for parent categories")
            self.mock_mode = True
            return self.get_parent_categories()
    
    def get_child_categories(self, parent_id: str) -> List[CategoryResponse]:
        """Get child categories - with mock fallback."""
        if self.mock_mode:
            logger.info(f"Fetching child categories for parent_id={parent_id} from MOCK DATA")
            mock_categories = MockDataService.get_child_categories(parent_id)
            return [
                CategoryResponse(
                    category_id=cat["category_id"],
                    category_name=cat["category_name"],
                    parent_id=parent_id
                )
                for cat in mock_categories
            ]
        
        try:
            return super().get_child_categories(parent_id)
        except AliExpressServiceException:
            logger.warning(f"Falling back to mock data for child categories (parent_id={parent_id})")
            self.mock_mode = True
            return self.get_child_categories(parent_id)
    
    def search_products(self, 
                       keywords: Optional[str] = None,
                       category_ids: Optional[str] = None,
                       page_no: int = 1,
                       page_size: int = 20,
                       sort: Optional[str] = None,
                       auto_generate_affiliate_links: bool = True,
                       **kwargs) -> ProductSearchResponse:
        """Search products - with mock fallback."""
        if self.mock_mode:
            logger.info(f"Searching products from MOCK DATA: keywords='{keywords}'")
            mock_result = MockDataService.search_products(
                keywords=keywords,
                category_id=category_ids,
                page_no=page_no,
                page_size=page_size,
                sort=sort
            )
            
            # Convert to ProductResponse objects
            products = [
                ProductResponse(
                    product_id=p["product_id"],
                    product_title=p["product_title"],
                    product_url=p["product_url"],
                    image_url=p["product_main_image_url"],
                    price=p["sale_price"],
                    original_price=p["original_price"],
                    currency=p["target_sale_price_currency"],
                    commission_rate=p["commission_rate"],
                    orders_count=p["orders"],
                    evaluate_rate=p["evaluate_rate"],
                    discount=p.get("discount")
                )
                for p in mock_result["products"]
            ]
            
            return ProductSearchResponse(
                products=products,
                total_record_count=mock_result["total_record_count"],
                current_page=mock_result["current_page_no"],
                page_size=len(products)
            )
        
        try:
            return super().search_products(
                keywords=keywords,
                category_ids=category_ids,
                page_no=page_no,
                page_size=page_size,
                sort=sort,
                auto_generate_affiliate_links=auto_generate_affiliate_links,
                **kwargs
            )
        except AliExpressServiceException:
            logger.warning("Falling back to mock data for product search")
            self.mock_mode = True
            return self.search_products(
                keywords=keywords,
                category_ids=category_ids,
                page_no=page_no,
                page_size=page_size,
                sort=sort,
                auto_generate_affiliate_links=auto_generate_affiliate_links,
                **kwargs
            )
    
    def get_products_details(self, product_ids: List[str]) -> List[ProductDetailResponse]:
        """Get product details - with mock fallback."""
        if self.mock_mode:
            logger.info(f"Fetching product details from MOCK DATA for {len(product_ids)} products")
            mock_details = MockDataService.get_product_details(product_ids)
            
            return [
                ProductDetailResponse(
                    product_id=p["product_id"],
                    product_title=p["product_title"],
                    product_url=p["product_url"],
                    image_url=p["product_main_image_url"],
                    price=p["sale_price"],
                    currency=p["target_sale_price_currency"],
                    description=p.get("product_description", ""),
                    specifications=p.get("specifications", []),
                    shipping_info=p.get("shipping_info", {}),
                    seller_info=p.get("seller_info", {}),
                    gallery_images=p.get("product_small_image_urls", [])
                )
                for p in mock_details
            ]
        
        try:
            return super().get_products_details(product_ids)
        except AliExpressServiceException:
            logger.warning("Falling back to mock data for product details")
            self.mock_mode = True
            return self.get_products_details(product_ids)
    
    def get_affiliate_links(self, urls: List[str]) -> List[AffiliateLink]:
        """Generate affiliate links - with mock fallback."""
        if self.mock_mode:
            logger.info(f"Generating MOCK affiliate links for {len(urls)} URLs")
            mock_links = MockDataService.generate_affiliate_links(urls)
            
            return [
                AffiliateLink(
                    original_url=link["source_value"],
                    affiliate_url=link["promotion_link"],
                    tracking_id=link["tracking_id"]
                )
                for link in mock_links
            ]
        
        try:
            return super().get_affiliate_links(urls)
        except AliExpressServiceException:
            logger.warning("Falling back to mock data for affiliate links")
            self.mock_mode = True
            return self.get_affiliate_links(urls)
    
    def get_hotproducts(self,
                       keywords: Optional[str] = None,
                       max_sale_price: Optional[float] = None,
                       sort: Optional[str] = None,
                       page_size: int = 20) -> ProductSearchResponse:
        """Get hot products - with mock fallback."""
        if self.mock_mode:
            logger.info(f"Fetching hot products from MOCK DATA: keywords='{keywords}'")
            mock_result = MockDataService.get_hot_products(
                keywords=keywords,
                max_price=max_sale_price,
                page_size=page_size
            )
            
            products = [
                ProductResponse(
                    product_id=p["product_id"],
                    product_title=p["product_title"],
                    product_url=p["product_url"],
                    image_url=p["product_main_image_url"],
                    price=p["sale_price"],
                    original_price=p["original_price"],
                    currency=p["target_sale_price_currency"],
                    commission_rate=p["commission_rate"],
                    orders_count=p["orders"],
                    evaluate_rate=p["evaluate_rate"],
                    discount=p.get("discount")
                )
                for p in mock_result["products"]
            ]
            
            return ProductSearchResponse(
                products=products,
                total_record_count=mock_result["total_record_count"],
                current_page=mock_result["current_page_no"],
                page_size=len(products)
            )
        
        try:
            return super().get_hotproducts(
                keywords=keywords,
                max_sale_price=max_sale_price,
                sort=sort,
                page_size=page_size
            )
        except AliExpressServiceException:
            logger.warning("Falling back to mock data for hot products")
            self.mock_mode = True
            return self.get_hotproducts(
                keywords=keywords,
                max_sale_price=max_sale_price,
                sort=sort,
                page_size=page_size
            )
    
    def get_service_info(self) -> dict:
        """Get service information including mock mode status."""
        info = super().get_service_info()
        info["mock_mode"] = self.mock_mode
        info["mock_mode_reason"] = "Using simulated data for testing" if self.mock_mode else "Using real AliExpress API"
        return info
