"""Response models for AliExpress API service."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class CategoryResponse:
    """Response model for category data."""
    
    category_id: str
    category_name: str
    parent_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProductResponse:
    """Response model for product data."""
    
    product_id: str
    product_title: str
    product_url: str
    price: str
    currency: str
    image_url: Optional[str] = None
    commission_rate: Optional[str] = None
    original_price: Optional[str] = None
    discount: Optional[str] = None
    evaluate_rate: Optional[str] = None
    orders_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProductDetailResponse:
    """Response model for detailed product information."""
    
    product_id: str
    product_title: str
    product_url: str
    price: str
    currency: str
    image_url: Optional[str] = None
    gallery_images: Optional[List[str]] = None
    description: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    shipping_info: Optional[Dict[str, Any]] = None
    seller_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class AffiliateLink:
    """Response model for affiliate link data."""
    
    original_url: str
    affiliate_url: str
    tracking_id: str
    commission_rate: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class HotProductResponse:
    """Response model for hot products."""
    
    products: List[ProductResponse]
    total_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'products': [product.to_dict() for product in self.products],
            'total_count': self.total_count
        }


@dataclass
class PromoProductResponse:
    """Response model for promotional products."""
    
    product_id: str
    product_title: str
    product_url: str
    promo_price: str
    original_price: str
    discount_rate: str
    promo_start_time: Optional[str] = None
    promo_end_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ShippingInfo:
    """Response model for shipping information."""
    
    product_id: str
    country: str
    shipping_methods: List[Dict[str, Any]]
    estimated_delivery_time: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ProductSearchResponse:
    """Response model for product search results."""
    
    products: List[ProductResponse]
    total_record_count: int
    current_page: int
    page_size: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'products': [product.to_dict() for product in self.products],
            'total_record_count': self.total_record_count,
            'current_page': self.current_page,
            'page_size': self.page_size
        }


@dataclass
class ServiceResponse:
    """Generic service response wrapper."""
    
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @classmethod
    def success_response(cls, data: Any, metadata: Optional[Dict[str, Any]] = None) -> 'ServiceResponse':
        """Create a successful response."""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'request_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error_response(cls, error: str, metadata: Optional[Dict[str, Any]] = None) -> 'ServiceResponse':
        """Create an error response."""
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'request_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
        return cls(success=False, error=error, metadata=metadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'success': self.success,
            'metadata': self.metadata or {}
        }
        
        if self.success and self.data is not None:
            # Handle different data types
            if hasattr(self.data, 'to_dict'):
                result['data'] = self.data.to_dict()
            elif isinstance(self.data, list):
                result['data'] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.data]
            else:
                result['data'] = self.data
        
        if not self.success and self.error:
            result['error'] = self.error
        
        return result