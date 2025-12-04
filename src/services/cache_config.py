"""Cache configuration for optimal API call reduction."""

from dataclasses import dataclass
from typing import ClassVar
import os

@dataclass
class CacheConfig:
    """
    Configuration for multi-level caching system.
    
    COMPLIANCE NOTE: All cached affiliate links are from our own authorized 
    affiliate account. Storing and reusing our own affiliate links is fully 
    legal and required for performance optimization under AliExpress Affiliate 
    Program Terms.
    """
    
    # Cache TTL (Time To Live) settings - optimized for compliance and performance
    product_metadata_ttl: int = 86400      # 24 hours - stable product info
    affiliate_links_ttl: int = 2592000      # 30 days - OUR OWN affiliate links (legal to cache)
    search_results_ttl: int = 3600          # 1 hour - search result sets
    price_stock_ttl: int = 1800             # 30 minutes - price/stock (frequent updates)
    categories_ttl: int = 604800            # 7 days - very stable category data
    hot_products_ttl: int = 1800            # 30 minutes - trending data changes fast
    
    # Cache size limits
    max_cached_products: int = 100000       # Maximum products in cache
    max_cached_searches: int = 10000        # Maximum search results cached
    max_cached_affiliate_links: int = 50000 # Maximum affiliate links cached
    
    # Performance settings
    batch_affiliate_generation: bool = True  # Batch affiliate link generation
    max_affiliate_batch_size: int = 50      # AliExpress API limit
    enable_memory_cache: bool = True        # L1 cache (fastest)
    enable_redis_cache: bool = True         # L2 cache (fast, shared)
    enable_database_cache: bool = True      # L3 cache (persistent)
    
    # Cleanup and maintenance
    cleanup_interval_seconds: int = 3600    # Cleanup every hour
    cache_hit_tracking: bool = True         # Track cache performance
    
    # Redis configuration
    redis_host: str = os.getenv('REDIS_HOST', 'localhost')
    redis_port: int = int(os.getenv('REDIS_PORT', '6379'))
    redis_db: int = int(os.getenv('REDIS_DB', '0'))
    redis_password: str = os.getenv('REDIS_PASSWORD', '')
    
    # Database configuration
    database_url: str = os.getenv('CACHE_DATABASE_URL', 'sqlite:///cache.db')
    
    @classmethod
    def from_env(cls) -> 'CacheConfig':
        """Load cache configuration from environment variables."""
        return cls(
            product_metadata_ttl=int(os.getenv('CACHE_PRODUCT_TTL', '86400')),
            affiliate_links_ttl=int(os.getenv('CACHE_AFFILIATE_TTL', '2592000')),
            search_results_ttl=int(os.getenv('CACHE_SEARCH_TTL', '3600')),
            price_stock_ttl=int(os.getenv('CACHE_PRICE_TTL', '1800')),
            enable_redis_cache=os.getenv('ENABLE_REDIS_CACHE', 'true').lower() == 'true',
            enable_database_cache=os.getenv('ENABLE_DB_CACHE', 'true').lower() == 'true'
        )
    
    def get_ttl_for_data_type(self, data_type: str) -> int:
        """Get appropriate TTL for different data types."""
        ttl_map = {
            'product_metadata': self.product_metadata_ttl,
            'affiliate_links': self.affiliate_links_ttl,
            'search_results': self.search_results_ttl,
            'price_stock': self.price_stock_ttl,
            'categories': self.categories_ttl,
            'hot_products': self.hot_products_ttl
        }
        return ttl_map.get(data_type, 3600)  # Default 1 hour