"""Multi-level caching service for optimal API call reduction."""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import redis
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .cache_config import CacheConfig
from ..models.cache_models import (
    Base, CachedProduct, CachedAffiliateLink, CachedSearchResult, 
    CacheAnalytics, CachedCategory
)
from ..models.responses import ProductResponse, AffiliateLink

logger = logging.getLogger(__name__)


class CacheService:
    """
    Multi-level caching service with memory, Redis, and database layers.
    
    COMPLIANCE NOTE: This service caches our own affiliate links and product
    data for performance optimization. All affiliate links stored are from our
    authorized affiliate account, making local storage fully legal and compliant.
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        
        # L1 Cache: Memory (fastest, limited size)
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_timestamps: Dict[str, datetime] = {}
        
        # L2 Cache: Redis (fast, shared across instances)
        self.redis_client = None
        if config.enable_redis_cache:
            try:
                self.redis_client = redis.Redis(
                    host=config.redis_host,
                    port=config.redis_port,
                    db=config.redis_db,
                    password=config.redis_password if config.redis_password else None,
                    decode_responses=True,
                    socket_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis cache initialization failed: {e}")
                self.redis_client = None
        
        # L3 Cache: Database (persistent, unlimited size)
        self.db_session = None
        if config.enable_database_cache:
            try:
                self.engine = create_engine(config.database_url, echo=False)
                Base.metadata.create_all(self.engine)
                SessionLocal = sessionmaker(bind=self.engine)
                self.db_session = SessionLocal()
                logger.info("Database cache initialized successfully")
            except Exception as e:
                logger.error(f"Database cache initialization failed: {e}")
                self.db_session = None
        
        # Performance tracking
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'api_calls_saved': 0
        }
    
    def generate_cache_key(self, operation: str, **params) -> str:
        """Generate consistent cache keys for operations."""
        # Sort parameters for consistent hashing
        sorted_params = sorted(params.items())
        param_string = json.dumps(sorted_params, sort_keys=True, default=str)
        key_data = f"{operation}:{param_string}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    # === PRODUCT CACHING ===
    
    async def get_cached_products(self, product_ids: List[str]) -> Tuple[List[ProductResponse], List[str]]:
        """
        Get cached products, return found products and missing product IDs.
        
        Returns:
            Tuple of (found_products, missing_product_ids)
        """
        found_products = []
        missing_ids = []
        
        for product_id in product_ids:
            cached_product = await self._get_cached_product(product_id)
            if cached_product:
                found_products.append(cached_product)
                self.cache_stats['hits'] += 1
            else:
                missing_ids.append(product_id)
                self.cache_stats['misses'] += 1
        
        logger.info(f"Product cache: {len(found_products)} hits, {len(missing_ids)} misses")
        return found_products, missing_ids
    
    async def _get_cached_product(self, product_id: str) -> Optional[ProductResponse]:
        """Get single cached product from multi-level cache."""
        
        # L1: Memory cache
        if self.config.enable_memory_cache:
            memory_key = f"product:{product_id}"
            if memory_key in self.memory_cache:
                timestamp = self.memory_cache_timestamps.get(memory_key)
                if timestamp and datetime.utcnow() - timestamp < timedelta(minutes=5):  # 5min memory TTL
                    return self.memory_cache[memory_key]
                else:
                    # Expired, remove from memory
                    self.memory_cache.pop(memory_key, None)
                    self.memory_cache_timestamps.pop(memory_key, None)
        
        # L2: Redis cache
        if self.redis_client:
            try:
                redis_key = f"product:{product_id}"
                cached_data = self.redis_client.get(redis_key)
                if cached_data:
                    product_dict = json.loads(cached_data)
                    product = ProductResponse(**product_dict)
                    
                    # Store in memory cache
                    if self.config.enable_memory_cache:
                        self.memory_cache[f"product:{product_id}"] = product
                        self.memory_cache_timestamps[f"product:{product_id}"] = datetime.utcnow()
                    
                    return product
            except Exception as e:
                logger.warning(f"Redis cache error for product {product_id}: {e}")
        
        # L3: Database cache
        if self.db_session:
            try:
                cached_product = self.db_session.query(CachedProduct)\
                    .filter(CachedProduct.product_id == product_id)\
                    .filter(CachedProduct.expires_at > datetime.utcnow())\
                    .first()
                
                if cached_product:
                    # Update access statistics
                    cached_product.last_accessed = datetime.utcnow()
                    cached_product.access_count += 1
                    self.db_session.commit()
                    
                    # Convert to ProductResponse
                    product = ProductResponse(**cached_product.to_dict())
                    
                    # Store in upper cache levels
                    await self._store_product_in_cache(product)
                    
                    return product
            except SQLAlchemyError as e:
                logger.error(f"Database cache error for product {product_id}: {e}")
        
        return None
    
    async def cache_products(self, products: List[ProductResponse], ttl_seconds: int = None):
        """Cache multiple products in all cache levels."""
        if not ttl_seconds:
            ttl_seconds = self.config.product_metadata_ttl
        
        for product in products:
            await self._store_product_in_cache(product, ttl_seconds)
    
    async def _store_product_in_cache(self, product: ProductResponse, ttl_seconds: int = None):
        """Store product in all available cache levels."""
        if not ttl_seconds:
            ttl_seconds = self.config.product_metadata_ttl
        
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # L1: Memory cache (with size limit)
        if self.config.enable_memory_cache and len(self.memory_cache) < 1000:  # Limit memory usage
            memory_key = f"product:{product.product_id}"
            self.memory_cache[memory_key] = product
            self.memory_cache_timestamps[memory_key] = datetime.utcnow()
        
        # L2: Redis cache
        if self.redis_client:
            try:
                redis_key = f"product:{product.product_id}"
                self.redis_client.setex(
                    redis_key,
                    ttl_seconds,
                    json.dumps(product.to_dict())
                )
            except Exception as e:
                logger.warning(f"Failed to cache product {product.product_id} in Redis: {e}")
        
        # L3: Database cache
        if self.db_session:
            try:
                cached_product = CachedProduct(
                    product_id=product.product_id,
                    product_title=product.product_title,
                    product_url=product.product_url,
                    price=float(product.price) if product.price else 0.0,
                    original_price=float(product.original_price) if product.original_price else None,
                    currency=product.currency,
                    commission_rate=float(product.commission_rate) if product.commission_rate else None,
                    image_url=product.image_url,
                    evaluate_rate=float(product.evaluate_rate) if product.evaluate_rate else None,
                    orders_count=product.orders_count,
                    discount=float(product.discount) if product.discount else None,
                    expires_at=expires_at,
                    price_updated_at=datetime.utcnow(),
                    metadata_updated_at=datetime.utcnow()
                )
                
                # Use merge to handle duplicates
                self.db_session.merge(cached_product)
                self.db_session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Failed to cache product {product.product_id} in database: {e}")
                self.db_session.rollback()
    
    # === AFFILIATE LINK CACHING ===
    
    async def get_cached_affiliate_links(self, urls: List[str]) -> Tuple[List[AffiliateLink], List[str]]:
        """
        Get cached affiliate links for URLs.
        
        COMPLIANCE: These are our own authorized affiliate links. Caching and
        reusing them is legal and required for performance optimization.
        
        Returns:
            Tuple of (found_links, missing_urls)
        """
        found_links = []
        missing_urls = []
        
        for url in urls:
            cached_link = await self._get_cached_affiliate_link(url)
            if cached_link and not cached_link.is_expired():
                found_links.append(cached_link)
                self.cache_stats['hits'] += 1
                self.cache_stats['api_calls_saved'] += 1  # Each cached link saves an API call
            else:
                missing_urls.append(url)
                self.cache_stats['misses'] += 1
        
        logger.info(f"Affiliate cache: {len(found_links)} hits, {len(missing_urls)} misses")
        return found_links, missing_urls
    
    async def _get_cached_affiliate_link(self, url: str) -> Optional[AffiliateLink]:
        """Get cached affiliate link from multi-level cache."""
        
        # Generate URL hash for consistent caching
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # L2: Redis cache (skip memory for affiliate links due to size)
        if self.redis_client:
            try:
                redis_key = f"affiliate:{url_hash}"
                cached_data = self.redis_client.get(redis_key)
                if cached_data:
                    link_dict = json.loads(cached_data)
                    return AffiliateLink(**link_dict)
            except Exception as e:
                logger.warning(f"Redis cache error for affiliate link: {e}")
        
        # L3: Database cache
        if self.db_session:
            try:
                cached_link = self.db_session.query(CachedAffiliateLink)\
                    .filter(CachedAffiliateLink.original_url == url)\
                    .filter(CachedAffiliateLink.expires_at > datetime.utcnow())\
                    .first()
                
                if cached_link:
                    # Update usage statistics
                    cached_link.update_usage()
                    self.db_session.commit()
                    
                    # Convert to AffiliateLink
                    affiliate_link = AffiliateLink(**cached_link.to_dict())
                    
                    # Store in Redis for faster access
                    if self.redis_client:
                        try:
                            redis_key = f"affiliate:{url_hash}"
                            remaining_ttl = int((cached_link.expires_at - datetime.utcnow()).total_seconds())
                            if remaining_ttl > 0:
                                self.redis_client.setex(
                                    redis_key,
                                    remaining_ttl,
                                    json.dumps(affiliate_link.to_dict())
                                )
                        except Exception as e:
                            logger.warning(f"Failed to cache affiliate link in Redis: {e}")
                    
                    return affiliate_link
            except SQLAlchemyError as e:
                logger.error(f"Database cache error for affiliate link: {e}")
        
        return None
    
    async def cache_affiliate_links(self, affiliate_links: List[AffiliateLink], ttl_seconds: int = None):
        """
        Cache affiliate links with appropriate TTL.
        
        COMPLIANCE: These are our own affiliate links from our authorized account.
        Caching them locally is legal and required for performance optimization.
        """
        if not ttl_seconds:
            ttl_seconds = self.config.affiliate_links_ttl
        
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        for link in affiliate_links:
            await self._store_affiliate_link_in_cache(link, expires_at, ttl_seconds)
    
    async def _store_affiliate_link_in_cache(self, link: AffiliateLink, expires_at: datetime, ttl_seconds: int):
        """Store affiliate link in cache levels."""
        url_hash = hashlib.md5(link.original_url.encode()).hexdigest()
        
        # L2: Redis cache
        if self.redis_client:
            try:
                redis_key = f"affiliate:{url_hash}"
                self.redis_client.setex(
                    redis_key,
                    ttl_seconds,
                    json.dumps(link.to_dict())
                )
            except Exception as e:
                logger.warning(f"Failed to cache affiliate link in Redis: {e}")
        
        # L3: Database cache
        if self.db_session:
            try:
                cached_link = CachedAffiliateLink(
                    original_url=link.original_url,
                    affiliate_url=link.affiliate_url,
                    tracking_id=link.tracking_id,
                    commission_rate=float(link.commission_rate) if link.commission_rate else None,
                    expires_at=expires_at
                )
                
                self.db_session.merge(cached_link)
                self.db_session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Failed to cache affiliate link in database: {e}")
                self.db_session.rollback()
    
    # === SEARCH RESULT CACHING ===
    
    async def get_cached_search_result(self, search_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached search result if available."""
        search_key = self.generate_cache_key("search", **search_params)
        
        # Check database cache
        if self.db_session:
            try:
                cached_search = self.db_session.query(CachedSearchResult)\
                    .filter(CachedSearchResult.search_hash == search_key)\
                    .filter(CachedSearchResult.expires_at > datetime.utcnow())\
                    .first()
                
                if cached_search:
                    # Update access statistics
                    cached_search.update_access()
                    self.db_session.commit()
                    
                    # Get cached products for this search
                    product_ids = cached_search.product_ids
                    cached_products, _ = await self.get_cached_products(product_ids)
                    
                    if cached_products:
                        self.cache_stats['hits'] += 1
                        self.cache_stats['api_calls_saved'] += 1  # Saved a search API call
                        
                        return {
                            'products': cached_products,
                            'total_record_count': cached_search.total_record_count,
                            'cached': True,
                            'cached_at': cached_search.created_at
                        }
            except SQLAlchemyError as e:
                logger.error(f"Database error getting cached search: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    async def cache_search_result(self, search_params: Dict[str, Any], products: List[ProductResponse], total_count: int):
        """Cache search result for future use."""
        search_key = self.generate_cache_key("search", **search_params)
        product_ids = [p.product_id for p in products]
        
        # Cache the products first
        await self.cache_products(products)
        
        # Cache the search result
        if self.db_session:
            try:
                expires_at = datetime.utcnow() + timedelta(seconds=self.config.search_results_ttl)
                
                cached_search = CachedSearchResult(
                    search_hash=search_key,
                    search_params=search_params,
                    product_ids=product_ids,
                    total_record_count=total_count,
                    expires_at=expires_at
                )
                
                self.db_session.merge(cached_search)
                self.db_session.commit()
                
                logger.info(f"Cached search result with {len(products)} products")
            except SQLAlchemyError as e:
                logger.error(f"Failed to cache search result: {e}")
                self.db_session.rollback()
    
    # === CACHE MAINTENANCE ===
    
    async def cleanup_expired_cache(self):
        """Remove expired cache entries."""
        if not self.db_session:
            return
        
        try:
            current_time = datetime.utcnow()
            
            # Clean expired products
            expired_products = self.db_session.query(CachedProduct)\
                .filter(CachedProduct.expires_at < current_time)\
                .delete()
            
            # Clean expired affiliate links
            expired_links = self.db_session.query(CachedAffiliateLink)\
                .filter(CachedAffiliateLink.expires_at < current_time)\
                .delete()
            
            # Clean expired search results
            expired_searches = self.db_session.query(CachedSearchResult)\
                .filter(CachedSearchResult.expires_at < current_time)\
                .delete()
            
            self.db_session.commit()
            
            logger.info(f"Cache cleanup: removed {expired_products} products, "
                       f"{expired_links} affiliate links, {expired_searches} searches")
            
        except SQLAlchemyError as e:
            logger.error(f"Cache cleanup failed: {e}")
            self.db_session.rollback()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_stats['hits'],
            'cache_misses': self.cache_stats['misses'],
            'hit_rate_percentage': round(hit_rate, 2),
            'api_calls_saved': self.cache_stats['api_calls_saved'],
            'total_requests': total_requests
        }
    
    def __del__(self):
        """Cleanup resources."""
        if self.db_session:
            self.db_session.close()
        if self.redis_client:
            self.redis_client.close()