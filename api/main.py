"""Enhanced FastAPI application for Vercel deployment with real AliExpress API integration and caching."""

import os
import logging
import asyncio
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .cache_service import cache_service

# Try to import AliExpress API - fallback to mock if not available
try:
    from aliexpress_api import AliexpressApi, models
    ALIEXPRESS_SDK_AVAILABLE = True
except ImportError:
    ALIEXPRESS_SDK_AVAILABLE = False
    logging.warning("AliExpress SDK not available - running in mock mode")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Configuration class with real API detection
class Config:
    def __init__(self):
        self.app_key = os.getenv('ALIEXPRESS_APP_KEY', 'demo-key')
        self.app_secret = os.getenv('ALIEXPRESS_APP_SECRET', 'demo-secret')
        self.tracking_id = os.getenv('ALIEXPRESS_TRACKING_ID', 'gpt_chat')
        self.language = os.getenv('ALIEXPRESS_LANGUAGE', 'EN')
        self.currency = os.getenv('ALIEXPRESS_CURRENCY', 'USD')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.admin_api_key = os.getenv('ADMIN_API_KEY', 'admin-key')
        self.internal_api_key = os.getenv('INTERNAL_API_KEY', 'ALIINSIDER-2025')
        self.allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://chat.openai.com,https://chatgpt.com').split(',')
        self.environment = os.getenv('ENVIRONMENT', 'production')
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Auto-detect real credentials and disable mock mode accordingly
        self.has_real_credentials = (
            self.app_key and self.app_key != 'demo-key' and
            self.app_secret and self.app_secret != 'demo-secret' and
            ALIEXPRESS_SDK_AVAILABLE
        )
        
        # Override mock mode based on credential availability
        manual_mock = os.getenv('MOCK_MODE', 'auto').lower()
        if manual_mock == 'auto':
            self.mock_mode = not self.has_real_credentials
        else:
            self.mock_mode = manual_mock == 'true'
        
        logger.info(f"Configuration initialized - Real credentials: {self.has_real_credentials}, Mock mode: {self.mock_mode}")

# AliExpress API Service class
class AliExpressService:
    def __init__(self, config: Config):
        self.config = config
        self.api = None
        
        if config.has_real_credentials and not config.mock_mode:
            try:
                self.api = AliexpressApi(
                    key=config.app_key,
                    secret=config.app_secret,
                    language=getattr(models.Language, config.language, models.Language.EN),
                    currency=getattr(models.Currency, config.currency, models.Currency.USD),
                    tracking_id=config.tracking_id
                )
                logger.info("AliExpress API initialized successfully with real credentials")
            except Exception as e:
                logger.error(f"Failed to initialize AliExpress API: {e}")
                self.api = None
    
    async def search_products(self, keywords: str, page_size: int = 10, page_no: int = 1, 
                            sort: str = "SALE_PRICE_ASC", min_sale_price: float = None, 
                            max_sale_price: float = None, use_cache: bool = True) -> Dict[str, Any]:
        """Search for products using real API or mock data with intelligent caching."""
        
        # Create cache parameters
        cache_params = {
            'keywords': keywords,
            'page_size': page_size,
            'page_no': page_no,
            'sort': sort,
            'min_sale_price': min_sale_price,
            'max_sale_price': max_sale_price,
            'mock_mode': self.config.mock_mode
        }
        
        # Try cache first if enabled
        if use_cache:
            cached_result = await cache_service.get_cached_product_search(cache_params)
            if cached_result:
                logger.debug("Returning cached product search results")
                cached_result['cache_hit'] = True
                return cached_result
        
        # Get fresh data
        if self.api and not self.config.mock_mode:
            result = await self._search_products_real(keywords, page_size, page_no, sort, min_sale_price, max_sale_price)
        else:
            result = self._search_products_mock(keywords, page_size, page_no, sort, min_sale_price, max_sale_price)
        
        result['cache_hit'] = False
        
        # Cache the result
        if use_cache:
            await cache_service.cache_product_search(cache_params, result)
        
        return result
    
    async def _search_products_real(self, keywords: str, page_size: int, page_no: int, 
                                  sort: str, min_sale_price: float, max_sale_price: float) -> Dict[str, Any]:
        """Real AliExpress API product search."""
        try:
            # Prepare search parameters
            search_params = {
                'keywords': keywords,
                'page_no': page_no,
                'page_size': min(page_size, 50),  # AliExpress limit
                'sort': sort
            }
            
            if min_sale_price is not None:
                search_params['min_sale_price'] = int(min_sale_price * 100)  # Convert to cents
            if max_sale_price is not None:
                search_params['max_sale_price'] = int(max_sale_price * 100)  # Convert to cents
            
            # Execute API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self.api.get_products(**search_params))
            
            # Process real API response
            products = []
            if hasattr(result, 'products') and result.products:
                for product in result.products:
                    products.append({
                        "product_id": str(getattr(product, 'product_id', 'unknown')),
                        "product_title": str(getattr(product, 'product_title', 'No title')),
                        "product_url": str(getattr(product, 'product_detail_url', 
                                                 getattr(product, 'product_url', 'No URL'))),
                        "app_sale_price": str(getattr(product, 'target_sale_price', '0.00')),
                        "original_price": str(getattr(product, 'target_original_price', '0.00')),
                        "discount": str(getattr(product, 'discount', '0%')),
                        "evaluate_rate": str(getattr(product, 'evaluate_rate', '0%')),
                        "commission_rate": str(getattr(product, 'commission_rate', '0%')),
                        "product_main_image_url": getattr(product, 'product_main_image_url', None),
                        "shop_id": str(getattr(product, 'shop_id', 'unknown')),
                        "shop_url": getattr(product, 'shop_url', None)
                    })
            
            total_results = getattr(result, 'total_record_count', len(products))
            
            return {
                "products": products,
                "total_results": total_results,
                "current_page": page_no,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"Real API search failed: {e}")
            # Fallback to mock on API failure
            return self._search_products_mock(keywords, page_size, page_no, sort, min_sale_price, max_sale_price)
    
    def _search_products_mock(self, keywords: str, page_size: int, page_no: int, 
                            sort: str, min_sale_price: float, max_sale_price: float) -> Dict[str, Any]:
        """Mock product search for testing and fallback."""
        mock_products = [
            {
                "product_id": "1005001234567890",
                "product_title": f"Mock Product for '{keywords}'",
                "product_url": "https://www.aliexpress.com/item/1005001234567890.html",
                "app_sale_price": "29.99",
                "original_price": "59.99",
                "discount": "50%",
                "evaluate_rate": "98.5%",
                "commission_rate": "30%",
                "product_main_image_url": "https://ae01.alicdn.com/kf/mock-image.jpg",
                "shop_id": "123456",
                "shop_url": "https://www.aliexpress.com/store/123456"
            }
        ]
        
        return {
            "products": mock_products,
            "total_results": len(mock_products),
            "current_page": page_no,
            "page_size": page_size
        }
    
    async def get_categories(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get product categories using real API or mock data with caching."""
        
        # Try cache first
        if use_cache:
            cached_categories = await cache_service.get_cached_categories()
            if cached_categories:
                logger.debug("Returning cached categories")
                return {
                    'categories': cached_categories,
                    'cache_hit': True
                }
        
        # Get fresh data
        if self.api and not self.config.mock_mode:
            categories = await self._get_categories_real()
        else:
            categories = self._get_categories_mock()
        
        # Cache the result
        if use_cache:
            await cache_service.cache_categories(categories)
        
        return {
            'categories': categories,
            'cache_hit': False
        }
    
    async def _get_categories_real(self) -> List[Dict[str, Any]]:
        """Real AliExpress API category retrieval."""
        try:
            loop = asyncio.get_event_loop()
            categories = await loop.run_in_executor(None, self.api.get_parent_categories)
            
            result = []
            if categories:
                for category in categories:
                    result.append({
                        "category_id": str(getattr(category, 'category_id', 'unknown')),
                        "category_name": str(getattr(category, 'category_name', 'Unknown Category'))
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Real API categories failed: {e}")
            return self._get_categories_mock()
    
    def _get_categories_mock(self) -> List[Dict[str, Any]]:
        """Mock categories for testing and fallback."""
        return [
            {"category_id": "3", "category_name": "Electronics"},
            {"category_id": "1420", "category_name": "Automobiles & Motorcycles"},
            {"category_id": "1501", "category_name": "Home & Garden"},
            {"category_id": "509", "category_name": "Cellphones & Telecommunications"},
            {"category_id": "322", "category_name": "Consumer Electronics"}
        ]
    
    async def generate_affiliate_links(self, urls: List[str], use_cache: bool = True) -> Dict[str, Any]:
        """Generate affiliate links using real API or mock data with caching."""
        
        # Try cache first
        if use_cache:
            cached_links = await cache_service.get_cached_affiliate_links(urls)
            if cached_links:
                logger.debug("Returning cached affiliate links")
                return {
                    'links': cached_links,
                    'cache_hit': True
                }
        
        # Get fresh data
        if self.api and not self.config.mock_mode:
            links = await self._generate_affiliate_links_real(urls)
        else:
            links = self._generate_affiliate_links_mock(urls)
        
        # Cache the result
        if use_cache:
            await cache_service.cache_affiliate_links(urls, links)
        
        return {
            'links': links,
            'cache_hit': False
        }
    
    async def _generate_affiliate_links_real(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Real AliExpress API affiliate link generation."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: self.api.get_affiliate_links(urls))
            
            affiliate_links = []
            if hasattr(result, 'promotion_links') and result.promotion_links:
                for link_data in result.promotion_links:
                    affiliate_links.append({
                        "original_url": str(getattr(link_data, 'source_value', '')),
                        "affiliate_url": str(getattr(link_data, 'promotion_link', '')),
                        "commission_rate": str(getattr(link_data, 'commission_rate', '0%'))
                    })
            
            return affiliate_links
            
        except Exception as e:
            logger.error(f"Real API affiliate links failed: {e}")
            return self._generate_affiliate_links_mock(urls)
    
    def _generate_affiliate_links_mock(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Mock affiliate links for testing and fallback."""
        mock_links = []
        for url in urls:
            mock_links.append({
                "original_url": url,
                "affiliate_url": f"{url}?aff_trace_key=mock_affiliate_key",
                "commission_rate": "5.0%"
            })
        return mock_links

# Initialize config and service
config = Config()
aliexpress_service = AliExpressService(config)

# Initialize cache service
async def startup_event():
    """Initialize cache connection on startup."""
    await cache_service.connect_redis()

# Create FastAPI app
app = FastAPI(
    title="AliExpress Affiliate API",
    description="AliExpress Affiliate API for product search, categories, and affiliate link generation. Perfect for GPT Actions integration with intelligent caching.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add startup event
app.add_event_handler("startup", startup_event)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins + ["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Response models
class HealthResponse(BaseModel):
    status: str
    environment: str
    mock_mode: bool
    service_info: Dict[str, Any]

class ProductSearchRequest(BaseModel):
    keywords: str
    page_size: Optional[int] = 10
    page_no: Optional[int] = 1
    sort: Optional[str] = "SALE_PRICE_ASC"
    min_sale_price: Optional[float] = None
    max_sale_price: Optional[float] = None

class ProductSearchResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        service_info = {
            "app_key_configured": bool(config.app_key and config.app_key != 'demo-key'),
            "app_secret_configured": bool(config.app_secret and config.app_secret != 'demo-secret'),
            "tracking_id": config.tracking_id,
            "language": config.language,
            "currency": config.currency,
            "environment": config.environment,
            "debug": config.debug,
            "mock_mode": config.mock_mode,
            "has_real_credentials": config.has_real_credentials,
            "sdk_available": ALIEXPRESS_SDK_AVAILABLE,
            "api_integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock"
        }
        
        return HealthResponse(
            status="healthy",
            environment=config.environment,
            mock_mode=config.mock_mode,
            service_info=service_info
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# OpenAPI spec endpoints
@app.get("/openapi.json")
async def get_openapi_spec():
    """Export OpenAPI specification as JSON."""
    return JSONResponse(content=app.openapi())

@app.get("/openapi-gpt.json")
async def get_openapi_gpt_spec():
    """Export GPT-optimized OpenAPI specification as JSON."""
    openapi_schema = app.openapi()
    
    # Optimize for GPT Actions
    openapi_schema["info"]["title"] = "AliExpress Affiliate API"
    openapi_schema["info"]["description"] = "AliExpress Affiliate API for product search, categories, and affiliate link generation. Perfect for GPT Actions integration."
    
    return JSONResponse(content=openapi_schema)

# Enhanced product search endpoint with real API integration
@app.post("/api/products/search", response_model=ProductSearchResponse)
async def search_products(request: ProductSearchRequest):
    """Search for products using real AliExpress API or mock data."""
    start_time = time.time()
    
    try:
        # Use the service to search products (automatically handles real/mock and caching)
        response_data = await aliexpress_service.search_products(
            keywords=request.keywords,
            page_size=request.page_size,
            page_no=request.page_no,
            sort=request.sort,
            min_sale_price=request.min_sale_price,
            max_sale_price=request.max_sale_price,
            use_cache=True
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        metadata = {
            "mock_mode": config.mock_mode,
            "processing_time_ms": processing_time,
            "api_version": "1.1.0",
            "api_integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
            "cache_hit": response_data.get('cache_hit', False),
            "cache_enabled": True,
            "search_params": {
                "keywords": request.keywords,
                "page_size": request.page_size,
                "sort": request.sort,
                "min_sale_price": request.min_sale_price,
                "max_sale_price": request.max_sale_price
            }
        }
        
        return ProductSearchResponse(
            success=True,
            data=response_data,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Product search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Enhanced categories endpoint with real API integration
@app.get("/api/categories")
async def get_categories():
    """Get product categories using real AliExpress API or mock data."""
    try:
        result = await aliexpress_service.get_categories(use_cache=True)
        categories = result['categories']
        
        return {
            "success": True,
            "data": {"categories": categories},
            "metadata": {
                "mock_mode": config.mock_mode,
                "api_integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
                "cache_hit": result.get('cache_hit', False),
                "cache_enabled": True,
                "total_categories": len(categories)
            }
        }
    except Exception as e:
        logger.error(f"Categories retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Categories failed: {str(e)}")

# Enhanced affiliate links endpoint with real API integration
@app.post("/api/affiliate/links")
async def generate_affiliate_links(urls: Dict[str, list]):
    """Generate affiliate links using real AliExpress API or mock data."""
    try:
        url_list = urls.get("urls", [])
        if not url_list:
            raise HTTPException(status_code=400, detail="No URLs provided")
        
        if len(url_list) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 URLs allowed per request")
        
        result = await aliexpress_service.generate_affiliate_links(url_list, use_cache=True)
        affiliate_links = result['links']
        
        return {
            "success": True,
            "data": {"affiliate_links": affiliate_links},
            "metadata": {
                "mock_mode": config.mock_mode,
                "api_integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
                "cache_hit": result.get('cache_hit', False),
                "cache_enabled": True,
                "processed_urls": len(url_list),
                "generated_links": len(affiliate_links)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Affiliate links generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Affiliate links failed: {str(e)}")

# System info endpoint
@app.get("/system/info")
async def get_system_info():
    """Get system information."""
    return {
        "success": True,
        "data": {
            "service": "AliExpress Affiliate API",
            "version": "1.0.0",
            "environment": config.environment,
            "mock_mode": config.mock_mode,
            "api_integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
            "has_real_credentials": config.has_real_credentials,
            "sdk_available": ALIEXPRESS_SDK_AVAILABLE,
            "configuration": {
                "language": config.language,
                "currency": config.currency,
                "tracking_id": config.tracking_id
            },
            "endpoints": {
                "health": "/health",
                "openapi": "/openapi-gpt.json",
                "docs": "/docs",
                "search": "/api/products/search",
                "categories": "/api/categories",
                "affiliate": "/api/affiliate/links"
            }
        }
    }

# Additional endpoints for enhanced functionality

@app.get("/api/products")
async def get_products(
    keywords: Optional[str] = None,
    page_size: int = 10,
    page_no: int = 1,
    sort: str = "SALE_PRICE_ASC",
    min_sale_price: Optional[float] = None,
    max_sale_price: Optional[float] = None
):
    """Get products using query parameters (alternative to POST)."""
    request = ProductSearchRequest(
        keywords=keywords or "",
        page_size=page_size,
        page_no=page_no,
        sort=sort,
        min_sale_price=min_sale_price,
        max_sale_price=max_sale_price
    )
    return await search_products(request)

@app.get("/api/affiliate/link")
async def generate_single_affiliate_link(url: str):
    """Generate a single affiliate link."""
    return await generate_affiliate_links({"urls": [url]})

@app.get("/api/status")
async def get_api_status():
    """Get detailed API status and capabilities."""
    cache_stats = cache_service.get_stats()
    
    return {
        "success": True,
        "data": {
            "api_status": "operational",
            "integration_mode": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
            "capabilities": {
                "product_search": True,
                "categories": True,
                "affiliate_links": True,
                "real_api_integration": config.has_real_credentials and ALIEXPRESS_SDK_AVAILABLE,
                "mock_fallback": True,
                "intelligent_caching": True,
                "redis_caching": cache_stats['cache_config']['redis_connected'],
                "memory_fallback": True
            },
            "performance": {
                "async_support": True,
                "concurrent_requests": True,
                "error_recovery": True,
                "caching_enabled": True,
                "cache_hit_rate": f"{cache_stats['cache_stats']['hit_rate_percent']}%"
            },
            "cache_performance": cache_stats
        },
        "metadata": {
            "timestamp": int(time.time()),
            "version": "1.1.0",
            "environment": config.environment
        }
    }

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get detailed cache performance statistics."""
    return {
        "success": True,
        "data": cache_service.get_stats(),
        "metadata": {
            "timestamp": int(time.time()),
            "description": "Cache performance and optimization statistics"
        }
    }

@app.post("/api/cache/clear")
async def clear_cache(pattern: Optional[str] = None):
    """Clear cache entries (admin function)."""
    try:
        cleared_count = await cache_service.clear_cache(pattern)
        return {
            "success": True,
            "data": {
                "cleared_entries": cleared_count,
                "pattern": pattern or "all"
            },
            "metadata": {
                "timestamp": int(time.time()),
                "operation": "cache_clear"
            }
        }
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@app.post("/api/products/search/no-cache")
async def search_products_no_cache(request: ProductSearchRequest):
    """Search for products bypassing cache (for testing)."""
    start_time = time.time()
    
    try:
        # Force fresh data by disabling cache
        response_data = await aliexpress_service.search_products(
            keywords=request.keywords,
            page_size=request.page_size,
            page_no=request.page_no,
            sort=request.sort,
            min_sale_price=request.min_sale_price,
            max_sale_price=request.max_sale_price,
            use_cache=False
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        metadata = {
            "mock_mode": config.mock_mode,
            "processing_time_ms": processing_time,
            "api_version": "1.1.0",
            "api_integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
            "cache_bypassed": True,
            "fresh_data": True,
            "search_params": {
                "keywords": request.keywords,
                "page_size": request.page_size,
                "sort": request.sort,
                "min_sale_price": request.min_sale_price,
                "max_sale_price": request.max_sale_price
            }
        }
        
        return ProductSearchResponse(
            success=True,
            data=response_data,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Product search (no cache) failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AliExpress Affiliate API",
        "version": "1.1.0",
        "status": "operational",
        "integration": "real" if (config.has_real_credentials and not config.mock_mode) else "mock",
        "caching": "enabled",
        "docs": "/docs",
        "openapi": "/openapi-gpt.json",
        "health": "/health",
        "endpoints": {
            "product_search": "/api/products/search",
            "product_search_no_cache": "/api/products/search/no-cache",
            "categories": "/api/categories",
            "affiliate_links": "/api/affiliate/links",
            "status": "/api/status",
            "cache_stats": "/api/cache/stats",
            "cache_clear": "/api/cache/clear"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)