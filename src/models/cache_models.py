"""Database models for persistent caching layer."""

from sqlalchemy import Column, String, DateTime, Text, Float, Integer, Boolean, JSON, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

Base = declarative_base()


class CachedProduct(Base):
    """
    Cached product information with metadata.
    
    COMPLIANCE: This stores product metadata from AliExpress API responses
    for performance optimization. Data is refreshed according to TTL policies.
    """
    __tablename__ = 'cached_products'
    
    # Primary product data
    product_id = Column(String(50), primary_key=True)
    product_title = Column(String(500))
    product_url = Column(Text)
    price = Column(Float)
    original_price = Column(Float)
    currency = Column(String(10))
    commission_rate = Column(Float)
    image_url = Column(Text)
    
    # Additional metadata
    category_id = Column(String(50))
    seller_id = Column(String(50))
    evaluate_rate = Column(Float)
    orders_count = Column(Integer)
    discount = Column(Float)
    
    # Cache metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime)
    last_accessed = Column(DateTime, default=func.now())
    access_count = Column(Integer, default=1)
    
    # Data freshness tracking
    price_updated_at = Column(DateTime, default=func.now())
    metadata_updated_at = Column(DateTime, default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_expires', 'expires_at'),
        Index('idx_product_category', 'category_id'),
        Index('idx_product_price_updated', 'price_updated_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'product_id': self.product_id,
            'product_title': self.product_title,
            'product_url': self.product_url,
            'price': str(self.price) if self.price else '0.00',
            'original_price': str(self.original_price) if self.original_price else None,
            'currency': self.currency,
            'commission_rate': str(self.commission_rate) if self.commission_rate else None,
            'image_url': self.image_url,
            'category_id': self.category_id,
            'evaluate_rate': str(self.evaluate_rate) if self.evaluate_rate else None,
            'orders_count': self.orders_count,
            'discount': str(self.discount) if self.discount else None
        }
    
    def is_price_stale(self, price_ttl_seconds: int) -> bool:
        """Check if price data needs refresh."""
        if not self.price_updated_at:
            return True
        return datetime.utcnow() - self.price_updated_at > timedelta(seconds=price_ttl_seconds)


class CachedAffiliateLink(Base):
    """
    Cached affiliate links from our own authorized affiliate account.
    
    COMPLIANCE: These are OUR OWN affiliate links generated through our 
    authorized AliExpress affiliate account. Storing and reusing our own 
    affiliate links is fully legal and required for performance optimization.
    The links contain our tracking ID and generate commissions for our account.
    """
    __tablename__ = 'cached_affiliate_links'
    
    # Link data
    original_url = Column(Text, primary_key=True)
    affiliate_url = Column(Text, nullable=False)
    tracking_id = Column(String(100), nullable=False)
    commission_rate = Column(Float)
    
    # Cache metadata
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, default=func.now())
    usage_count = Column(Integer, default=1)  # Track reuse for analytics
    
    # Performance tracking
    generation_time_ms = Column(Float)  # Time taken to generate
    
    # Indexes
    __table_args__ = (
        Index('idx_affiliate_expires', 'expires_at'),
        Index('idx_affiliate_tracking', 'tracking_id'),
        Index('idx_affiliate_last_used', 'last_used'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'original_url': self.original_url,
            'affiliate_url': self.affiliate_url,
            'tracking_id': self.tracking_id,
            'commission_rate': str(self.commission_rate) if self.commission_rate else None
        }
    
    def is_expired(self) -> bool:
        """Check if affiliate link has expired."""
        return datetime.utcnow() > self.expires_at
    
    def update_usage(self):
        """Update usage statistics."""
        self.last_used = datetime.utcnow()
        self.usage_count += 1


class CachedSearchResult(Base):
    """
    Cached search result sets for performance optimization.
    
    COMPLIANCE: Caches search result metadata and product IDs to avoid
    redundant API calls for identical search queries.
    """
    __tablename__ = 'cached_search_results'
    
    # Search identification
    search_hash = Column(String(64), primary_key=True)  # SHA256 of search params
    search_params = Column(JSON)  # Original search parameters
    
    # Result data
    product_ids = Column(JSON)  # List of product IDs in results
    total_record_count = Column(Integer)
    
    # Cache metadata
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=func.now())
    hit_count = Column(Integer, default=1)
    
    # Performance tracking
    api_response_time_ms = Column(Float)
    
    # Indexes
    __table_args__ = (
        Index('idx_search_expires', 'expires_at'),
        Index('idx_search_accessed', 'last_accessed'),
    )
    
    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.utcnow()
        self.hit_count += 1


class CacheAnalytics(Base):
    """
    Cache performance analytics and API call savings tracking.
    """
    __tablename__ = 'cache_analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=func.now())
    
    # API call savings
    search_api_calls_saved = Column(Integer, default=0)
    affiliate_api_calls_saved = Column(Integer, default=0)
    product_detail_calls_saved = Column(Integer, default=0)
    total_api_calls_saved = Column(Integer, default=0)
    
    # Cache performance
    cache_hit_rate = Column(Float)  # Percentage
    average_response_time_ms = Column(Float)
    
    # Storage usage
    cached_products_count = Column(Integer, default=0)
    cached_affiliate_links_count = Column(Integer, default=0)
    cached_searches_count = Column(Integer, default=0)
    
    # Cost savings (estimated)
    estimated_cost_savings_usd = Column(Float, default=0.0)
    
    __table_args__ = (
        Index('idx_analytics_date', 'date'),
    )


class CachedCategory(Base):
    """
    Cached category information (very stable data).
    """
    __tablename__ = 'cached_categories'
    
    category_id = Column(String(50), primary_key=True)
    category_name = Column(String(200), nullable=False)
    parent_id = Column(String(50))
    level = Column(Integer, default=0)  # 0 = parent, 1 = child, etc.
    
    # Cache metadata
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    __table_args__ = (
        Index('idx_category_parent', 'parent_id'),
        Index('idx_category_level', 'level'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'category_id': self.category_id,
            'category_name': self.category_name,
            'parent_id': self.parent_id
        }