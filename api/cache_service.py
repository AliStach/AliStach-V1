"""
Redis-based caching service for AliExpress API responses.
Optimized for Vercel serverless environment with connection pooling.
"""

import os
import json
import time
import hashlib
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

# Try to import Redis - fallback to in-memory cache if not available
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    REDIS_AVAILABLE = False
    logging.warning(f"Redis not available - using in-memory cache: {e}")

logger = logging.getLogger(__name__)

class CacheService:
    """
    High-performance caching service with Redis backend and in-memory fallback.
    Optimized for serverless environments with intelligent connection management.
    """
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL')
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.cache_ttl = int(os.getenv('CACHE_TTL', '3600'))  # 1 hour default
        self.max_memory_items = 100  # Limit memory cache size
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'errors': 0,
            'redis_connected': False
        }
        
        logger.info(f"Cache service initialized - Redis available: {REDIS_AVAILABLE}, TTL: {self.cache_ttl}s")
    
    async def connect_redis(self) -> bool:
        """Connect to Redis with error handling."""
        if not REDIS_AVAILABLE or not self.redis_url:
            return False
        
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            self.stats['redis_connected'] = True
            logger.info("Redis connection established successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
            self.stats['redis_connected'] = False
            return False
    
    def _generate_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate a consistent cache key from parameters."""
        # Sort parameters for consistent key generation
        sorted_params = sorted(params.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        param_hash = hashlib.md5(param_string.encode()).hexdigest()
        return f"aliexpress:{prefix}:{param_hash}"
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data with Redis primary and memory fallback."""
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    cached_data = await self.redis_client.get(key)
                    if cached_data:
                        data = json.loads(cached_data)
                        # Check if data is still valid
                        if self._is_cache_valid(data):
                            self.stats['hits'] += 1
                            logger.debug(f"Redis cache hit for key: {key}")
                            return data['content']
                except Exception as e:
                    logger.warning(f"Redis get error: {e}")
                    self.stats['errors'] += 1
            
            # Fallback to memory cache
            if key in self.memory_cache:
                data = self.memory_cache[key]
                if self._is_cache_valid(data):
                    self.stats['hits'] += 1
                    logger.debug(f"Memory cache hit for key: {key}")
                    return data['content']
                else:
                    # Remove expired data
                    del self.memory_cache[key]
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.stats['errors'] += 1
            return None
    
    async def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set cached data with Redis primary and memory fallback."""
        try:
            ttl = ttl or self.cache_ttl
            cache_data = {
                'content': data,
                'timestamp': time.time(),
                'ttl': ttl
            }
            
            # Try Redis first
            if self.redis_client:
                try:
                    await self.redis_client.setex(
                        key, 
                        ttl, 
                        json.dumps(cache_data)
                    )
                    self.stats['sets'] += 1
                    logger.debug(f"Data cached in Redis for key: {key}")
                    return True
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")
                    self.stats['errors'] += 1
            
            # Fallback to memory cache
            self._cleanup_memory_cache()
            self.memory_cache[key] = cache_data
            self.stats['sets'] += 1
            logger.debug(f"Data cached in memory for key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self.stats['errors'] += 1
            return False
    
    def _is_cache_valid(self, cache_data: Dict[str, Any]) -> bool:
        """Check if cached data is still valid."""
        try:
            timestamp = cache_data.get('timestamp', 0)
            ttl = cache_data.get('ttl', self.cache_ttl)
            return (time.time() - timestamp) < ttl
        except:
            return False
    
    def _cleanup_memory_cache(self):
        """Clean up expired items and limit memory cache size."""
        try:
            # Remove expired items
            current_time = time.time()
            expired_keys = []
            
            for key, data in self.memory_cache.items():
                if not self._is_cache_valid(data):
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            # Limit cache size (remove oldest items)
            if len(self.memory_cache) > self.max_memory_items:
                # Sort by timestamp and remove oldest
                sorted_items = sorted(
                    self.memory_cache.items(),
                    key=lambda x: x[1].get('timestamp', 0)
                )
                
                items_to_remove = len(self.memory_cache) - self.max_memory_items
                for i in range(items_to_remove):
                    key = sorted_items[i][0]
                    del self.memory_cache[key]
                    
        except Exception as e:
            logger.error(f"Memory cache cleanup error: {e}")
    
    async def cache_product_search(self, params: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Cache product search results."""
        key = self._generate_cache_key("products", params)
        await self.set(key, data)
        return key
    
    async def get_cached_product_search(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached product search results."""
        key = self._generate_cache_key("products", params)
        return await self.get(key)
    
    async def cache_categories(self, data: List[Dict[str, Any]]) -> str:
        """Cache category data."""
        key = self._generate_cache_key("categories", {})
        await self.set(key, {"categories": data}, ttl=7200)  # 2 hours for categories
        return key
    
    async def get_cached_categories(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached category data."""
        key = self._generate_cache_key("categories", {})
        cached = await self.get(key)
        return cached.get("categories") if cached else None
    
    async def cache_affiliate_links(self, urls: List[str], links: List[Dict[str, Any]]) -> str:
        """Cache affiliate links."""
        key = self._generate_cache_key("affiliate", {"urls": sorted(urls)})
        await self.set(key, {"links": links}, ttl=1800)  # 30 minutes for affiliate links
        return key
    
    async def get_cached_affiliate_links(self, urls: List[str]) -> Optional[List[Dict[str, Any]]]:
        """Get cached affiliate links."""
        key = self._generate_cache_key("affiliate", {"urls": sorted(urls)})
        cached = await self.get(key)
        return cached.get("links") if cached else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_stats': {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'errors': self.stats['errors'],
                'hit_rate_percent': round(hit_rate, 2),
                'total_requests': total_requests
            },
            'cache_config': {
                'redis_available': REDIS_AVAILABLE,
                'redis_connected': self.stats['redis_connected'],
                'redis_url_configured': bool(self.redis_url),
                'default_ttl': self.cache_ttl,
                'memory_cache_size': len(self.memory_cache),
                'max_memory_items': self.max_memory_items
            },
            'performance_impact': {
                'estimated_api_calls_saved': self.stats['hits'],
                'cache_efficiency': 'high' if hit_rate > 70 else 'medium' if hit_rate > 40 else 'low'
            }
        }
    
    async def clear_cache(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern."""
        cleared = 0
        
        try:
            # Clear Redis cache
            if self.redis_client:
                if pattern:
                    keys = await self.redis_client.keys(f"aliexpress:{pattern}:*")
                    if keys:
                        cleared += await self.redis_client.delete(*keys)
                else:
                    keys = await self.redis_client.keys("aliexpress:*")
                    if keys:
                        cleared += await self.redis_client.delete(*keys)
            
            # Clear memory cache
            if pattern:
                keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                    cleared += 1
            else:
                cleared += len(self.memory_cache)
                self.memory_cache.clear()
            
            logger.info(f"Cleared {cleared} cache entries")
            return cleared
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

# Global cache instance
cache_service = CacheService()