"""Models module for AliExpress API service.

This module contains all data models including:
- Response models for API endpoints
- Cache models for persistent storage
"""

from typing import TYPE_CHECKING

from src.models.responses import (
    CategoryResponse,
    ProductResponse,
    ProductDetailResponse,
    AffiliateLink,
    HotProductResponse,
    PromoProductResponse,
    ShippingInfo,
    ProductSearchResponse,
    ImageSearchResponse,
    ServiceResponse,
)

from src.models.cache_models import (
    Base,
    CachedProduct,
    CachedAffiliateLink,
    CachedSearchResult,
    CacheAnalytics,
    CachedCategory,
)

__all__ = [
    # Response models
    "CategoryResponse",
    "ProductResponse",
    "ProductDetailResponse",
    "AffiliateLink",
    "HotProductResponse",
    "PromoProductResponse",
    "ShippingInfo",
    "ProductSearchResponse",
    "ImageSearchResponse",
    "ServiceResponse",
    # Cache models
    "Base",
    "CachedProduct",
    "CachedAffiliateLink",
    "CachedSearchResult",
    "CacheAnalytics",
    "CachedCategory",
]