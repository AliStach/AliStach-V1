"""Multi-level caching service for optimal API call reduction."""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List, Tuple
import redis
from cachetools import LRUCache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .cache_config import CacheConfig
from ..models.cache_models import (
    Base, CachedProduct, CachedAffiliateLink, CachedSearchResult
)
from ..models.responses import ProductResponse, AffiliateLink
from ..exceptions import CacheError, AliExpressServiceException
from ..utils.logging_config import log_info, log_warning, log_error

logger = logging.getLogger(__name__)

class CacheService:
    """
    Multi-level caching service with memory, Redis, and database layers.
    
    COMPLIANCE NOTE: This service caches our own affiliate links and product
    data for performance optimization. All affiliate links stored are from our
    authorized affiliate account, making local storage fully legal and compliant.
    """
    
    def __init__(self, config: CacheConfig) -> None:
        self.config: CacheConfig = config
        
        # L1 Cache: Memory (fastest, limited size with LRU eviction)
        # Using LRUCache for automatic eviction of least recently used items
        self.memory_cache: LRUCache = LRUCache(maxsize=1000)
        self.memory_cache_timestamps: Dict[str, datetime] = {}
        
        # L2 Cache: Redis (fast, shared across instances)
        self.redis_client: Optional[redis.Redis] = None
        self.redis_available: bool = False
        if config.enable_redis_cache:
            self.redis_available = self._init_redis_with_fallback()
        else:
            log_info(logger, "redis_cache_disabled")
        
        # L3 Cache: Database (persistent, unlimited size)
        self.db_session: Optional[Session] = None
        self.db_available: bool = False
        if config.enable_database_cache:
            self.db_available = self._init_database_with_fallback()
        else:
            log_info(logger, "database_cache_disabled")
        
        # Performance tracking
        self.cache_stats: Dict[str, int] = {
            'hits': 0,
            'misses': 0,
            'api_calls_saved': 0,
            'redis_hits': 0,
            'memory_hits': 0,
            'db_hits': 0
        }
        
        # Log final cache configuration
        cache_layers = []
        if config.enable_memory_cache:
            cache_layers.append("Memory")
        if self.redis_available:
            cache_layers.append("Redis")
        if self.db_available:
            cache_layers.append("Database")
        
        log_info(
            logger,
            "cache_service_initialized",
            cache_layers=cache_layers,
            memory_enabled=config.enable_memory_cache,
            redis_enabled=self.redis_available,
            database_enabled=self.db_available
        )
    
    def _init_redis_with_fallback(self) -> bool:
        """
        Initialize Redis with graceful fallback.
        
        Returns:
            True if Redis is available, False otherwise
        """
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password if self.config.redis_password else None,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            log_info(
                logger,
                "redis_cache_initialized",
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db
            )
            return True
        except redis.ConnectionError as e:
            log_warning(
                logger,
                "redis_connection_failed",
                host=self.config.redis_host,
                port=self.config.redis_port,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            self.redis_client = None
            return False
        except redis.TimeoutError as e:
            log_warning(
                logger,
                "redis_connection_timeout",
                host=self.config.redis_host,
                port=self.config.redis_port,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            self.redis_client = None
            return False
        except Exception as e:
            log_error(
                logger,
                "redis_initialization_error",
                exc_info=True,
                host=self.config.redis_host,
                port=self.config.redis_port,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            self.redis_client = None
            return False
    
    def _init_database_with_fallback(self) -> bool:
        """
        Initialize database cache with graceful fallback.
        
        Returns:
            True if database is available, False otherwise
        """
        try:
            self.engine = create_engine(self.config.database_url, echo=False)
            Base.metadata.create_all(self.engine)
            SessionLocal = sessionmaker(bind=self.engine)
            self.db_session = SessionLocal()
            # Test connection
            self.db_session.execute("SELECT 1")
            log_info(
                logger,
                "database_cache_initialized",
                database_url=self.config.database_url.split('@')[-1]  # Log without credentials
            )
            return True
        except SQLAlchemyError as e:
            log_warning(
                logger,
                "database_cache_initialization_failed",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            self.db_session = None
            return False
        except Exception as e:
            log_error(
                logger,
                "database_initialization_error",
                exc_info=True,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            self.db_session = None
            return False
    
    def generate_cache_key(self, operation: str, **params: Any) -> str:
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
        
        log_info(
            logger,
            "product_cache_lookup_completed",
            cache_hits=len(found_products),
            cache_misses=len(missing_ids)
        )
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
        if self.redis_available and self.redis_client:
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
                    
                    self.cache_stats['redis_hits'] += 1
                    return product
            except redis.ConnectionError as e:
                log_warning(
                    logger,
                    "redis_connection_lost",
                    product_id=product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                self.redis_available = False
            except json.JSONDecodeError as e:
                log_error(
                    logger,
                    "redis_decode_error",
                    product_id=product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            except Exception as e:
                log_error(
                    logger,
                    "redis_cache_error",
                    exc_info=True,
                    product_id=product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
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
                log_error(
                    logger,
                    "database_cache_retrieval_error",
                    product_id=product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                # Rollback the transaction
                try:
                    self.db_session.rollback()
                except Exception as rollback_error:
                    log_error(
                        logger,
                        "database_rollback_failed",
                        error_type=type(rollback_error).__name__,
                        error_message=str(rollback_error)
                    )
            except Exception as e:
                log_error(
                    logger,
                    "database_cache_error",
                    exc_info=True,
                    product_id=product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
        return None
    
    async def cache_products(self, products: List[ProductResponse], ttl_seconds: Optional[int] = None) -> None:
        """Cache multiple products in all cache levels."""
        if not ttl_seconds:
            ttl_seconds = self.config.product_metadata_ttl
        
        for product in products:
            await self._store_product_in_cache(product, ttl_seconds)
    
    async def _store_product_in_cache(self, product: ProductResponse, ttl_seconds: Optional[int] = None) -> None:
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
                log_warning(
                    logger,
                    "redis_cache_store_failed",
                    product_id=product.product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
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
                log_error(
                    logger,
                    "database_cache_store_failed",
                    product_id=product.product_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
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
        
        log_info(
            logger,
            "affiliate_cache_lookup_completed",
            cache_hits=len(found_links),
            cache_misses=len(missing_urls)
        )
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
                log_warning(
                    logger,
                    "redis_affiliate_cache_error",
                    url_hash=url_hash,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
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
                            log_warning(
                                logger,
                                "redis_affiliate_store_failed",
                                url_hash=url_hash,
                                error_type=type(e).__name__,
                                error_message=str(e)
                            )
                    
                    return affiliate_link
            except SQLAlchemyError as e:
                log_error(
                    logger,
                    "database_affiliate_cache_error",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
        return None
    
    async def cache_affiliate_links(self, affiliate_links: List[AffiliateLink], ttl_seconds: Optional[int] = None) -> None:
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
    
    async def _store_affiliate_link_in_cache(self, link: AffiliateLink, expires_at: datetime, ttl_seconds: int) -> None:
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
                log_warning(
                    logger,
                    "redis_affiliate_store_failed",
                    url_hash=url_hash,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
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
                log_error(
                    logger,
                    "database_affiliate_store_failed",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
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
                log_error(
                    logger,
                    "database_search_cache_error",
                    search_key=search_key,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
        
        self.cache_stats['misses'] += 1
        return None
    
    async def cache_search_result(self, search_params: Dict[str, Any], products: List[ProductResponse], total_count: int) -> None:
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
                
                log_info(
                    logger,
                    "search_result_cached",
                    product_count=len(products),
                    search_key=search_key
                )
            except SQLAlchemyError as e:
                log_error(
                    logger,
                    "search_cache_store_failed",
                    search_key=search_key,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                self.db_session.rollback()
    
    # === CACHE MAINTENANCE ===
    
    async def cleanup_expired_cache(self) -> None:
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
            
            log_info(
                logger,
                "cache_cleanup_completed",
                expired_products=expired_products,
                expired_links=expired_links,
                expired_searches=expired_searches
            )
            
        except SQLAlchemyError as e:
            log_error(
                logger,
                "cache_cleanup_failed",
                error_type=type(e).__name__,
                error_message=str(e)
            )
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
    
    def __del__(self) -> None:
        """Cleanup resources."""
        if self.db_session:
            self.db_session.close()
        if self.redis_client:
            self.redis_client.close()