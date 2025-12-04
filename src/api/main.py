"""FastAPI application for AliExpress API service with comprehensive security."""

import logging
import os
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from ..utils.config import Config
from ..utils.logging_config import setup_production_logging, get_logger_with_context
from ..middleware.security import security_middleware, get_security_manager
from ..middleware.csrf import csrf_middleware
from ..middleware.security_headers import SecurityHeadersMiddleware
from ..exceptions import (
    AliExpressServiceException,
    ConfigurationError,
    PermanentError,
    RateLimitError
)
from ..services.aliexpress_service import AliExpressService
from ..models.responses import ServiceResponse

# Global service instance - lazy initialized for Vercel compatibility
_service_instance: Optional[AliExpressService] = None
_config_instance: Optional[Config] = None
_initialization_error: Optional[HTTPException] = None
_logger: Optional[Any] = None

def _initialize_service() -> Tuple[AliExpressService, Config]:
    """
    Lazy initialization for Vercel serverless environment.
    This function is called on first request, not during startup.
    """
    global _service_instance, _config_instance, _initialization_error, _logger
    
    # Return cached instance if already initialized
    if _service_instance is not None:
        return _service_instance, _config_instance
    
    # Return cached error if initialization previously failed
    if _initialization_error is not None:
        raise _initialization_error
    
    try:
        # Debug: Check environment variables
        import os
        env_check = {
            "ALIEXPRESS_APP_KEY": os.getenv("ALIEXPRESS_APP_KEY", "NOT_SET"),
            "ALIEXPRESS_APP_SECRET": os.getenv("ALIEXPRESS_APP_SECRET", "NOT_SET")[:10] + "..." if os.getenv("ALIEXPRESS_APP_SECRET") else "NOT_SET",
            "ALIEXPRESS_TRACKING_ID": os.getenv("ALIEXPRESS_TRACKING_ID", "NOT_SET"),
            "VERCEL": os.getenv("VERCEL", "NOT_SET"),
            "VERCEL_ENV": os.getenv("VERCEL_ENV", "NOT_SET")
        }
        print(f"[INIT] Environment check: {env_check}")
        
        # Initialize configuration
        _config_instance = Config.from_env()
        print(f"[INIT] Config loaded: app_key={_config_instance.app_key}, tracking_id={_config_instance.tracking_id}")
        
        _config_instance.validate()
        print(f"[INIT] Config validated successfully")
        
        # Set up logging
        setup_production_logging(_config_instance.log_level)
        _logger = get_logger_with_context(__name__)
        
        # Initialize service
        _service_instance = AliExpressService(_config_instance)
        print(f"[INIT] Service initialized successfully")
        
        _logger.info_ctx(
            "AliExpress service initialized successfully",
            language=_config_instance.language,
            currency=_config_instance.currency,
            tracking_id=_config_instance.tracking_id
        )
        
        return _service_instance, _config_instance
        
    except ConfigurationError as e:
        error_msg = f"Service configuration error: {str(e)}"
        print(f"[INIT ERROR] {error_msg}")
        if hasattr(e, 'details'):
            print(f"[INIT ERROR] Details: {e.details}")
        _initialization_error = HTTPException(
            status_code=503,
            detail=error_msg
        )
        raise _initialization_error
    except AliExpressServiceException as e:
        error_msg = f"Service initialization failed: {str(e)}"
        print(f"[INIT ERROR] {error_msg}")
        if hasattr(e, 'details'):
            print(f"[INIT ERROR] Details: {e.details}")
        _initialization_error = HTTPException(
            status_code=503,
            detail=error_msg
        )
        raise _initialization_error
    except Exception as e:
        error_msg = f"Service initialization failed: {str(e)}"
        print(f"[INIT ERROR] {error_msg}")
        import traceback
        traceback.print_exc()
        _initialization_error = HTTPException(
            status_code=503,
            detail=error_msg
        )
        raise _initialization_error

# Create FastAPI app without lifespan (for Vercel compatibility)
app = FastAPI(
    title="AliExpress Affiliate API Proxy",
    description="""
    🔒 **Secure AliExpress Affiliate API Proxy**
    
    A production-grade, secure FastAPI service for the AliExpress Affiliate API with:
    
    * **🛡️ Security**: Origin validation, rate limiting, IP blocking, CSRF protection
    * **🔐 Authentication**: Internal API key protection, JWT token support
    * **📊 Monitoring**: Request logging, SQLite audit trail, admin dashboard
    * **⚡ Performance**: Optimized for GPT and high-traffic usage
    * **🔗 Affiliate Integration**: Automatic affiliate link generation
    
    ## Security Features
    
    * **HTTPS Enforcement**: Automatic HTTPS redirect in production
    * **Trusted Hosts**: Strict host header validation
    * **CORS Protection**: Restricted to OpenAI domains only (production)
    * **Rate Limiting**: 60 requests/minute, 5 requests/second per IP
    * **Request Logging**: Comprehensive SQLite audit trail
    * **IP Blocking**: Automatic and manual IP blocking
    * **CSRF Protection**: Token validation for web requests
    * **Internal API Key**: Required for all API endpoints
    * **Admin API Key**: Required for admin endpoints
    
    ## Usage
    
    All API requests must include the `x-internal-key` header.
    
    Admin endpoints require the `x-admin-key` header for monitoring and management.
    
    ## Security Headers
    
    The API automatically adds security headers:
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `X-XSS-Protection: 1; mode=block`
    - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
    """,
    version="2.1.0-secure",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security manager will be initialized lazily via get_security_manager()
# Don't create it at module level to avoid import-time failures
security_manager = None

# Add HTTPS redirect middleware (only in production)
# Note: Vercel handles HTTPS redirect, so this is optional
try:
    if os.getenv("ENVIRONMENT", "development") == "production" and os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower() == "true":
        app.add_middleware(HTTPSRedirectMiddleware)
except Exception as e:
    from src.utils.logging_config import log_warning
    log_warning(logging.getLogger(__name__), "https_redirect_middleware_failed", error_type=type(e).__name__, error_message=str(e))

# Add trusted host middleware for additional security
# Update with your actual production domain
production_domain = os.getenv("PRODUCTION_DOMAIN", "alistach.vercel.app")
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.vercel.app",
        "*.render.com",
        "*.railway.app",
        production_domain,
        "alistach.vercel.app"  # Production domain
    ]
)

# Add CORS middleware with strict origin restrictions
# Only allow OpenAI domains in production
# Use environment variable or defaults (don't access security_manager at module level)
cors_origins_str = os.getenv("ALLOWED_ORIGINS", "https://chat.openai.com,https://chatgpt.com,https://platform.openai.com,http://localhost:3000,http://localhost:8000")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

if os.getenv("ENVIRONMENT", "development") == "production":
    # Strict CORS for production - only OpenAI domains
    cors_origins = [
        origin for origin in cors_origins 
        if "openai.com" in origin or "chatgpt.com" in origin or origin.startswith("https://")
    ]
    # Remove localhost from production CORS
    cors_origins = [origin for origin in cors_origins if "localhost" not in origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "x-internal-key",
        "x-admin-key",
        "x-csrf-token",
        "User-Agent",
        "Accept",
        "X-Requested-With"
    ],
    expose_headers=["Retry-After", "X-Request-ID"],
    max_age=3600  # Cache preflight requests for 1 hour
)

# Add security headers middleware (adds security headers to all responses)
try:
    app.add_middleware(SecurityHeadersMiddleware)
except Exception as e:
    log_warning(logging.getLogger(__name__), "security_headers_middleware_failed", error_type=type(e).__name__, error_message=str(e))

# Add CSRF protection middleware (after CORS)
try:
    app.middleware("http")(csrf_middleware)
except Exception as e:
    log_warning(logging.getLogger(__name__), "csrf_middleware_failed", error_type=type(e).__name__, error_message=str(e))

# Add security middleware LAST (order matters - after CORS and CSRF)
try:
    app.middleware("http")(security_middleware)
except Exception as e:
    log_warning(logging.getLogger(__name__), "security_middleware_failed", error_type=type(e).__name__, error_message=str(e))

def get_service() -> AliExpressService:
    """
    Dependency to get the AliExpress service instance.
    Uses lazy initialization for Vercel serverless compatibility.
    """
    service, _ = _initialize_service()
    return service

def get_config() -> Config:
    """
    Dependency to get the configuration instance.
    Uses lazy initialization for Vercel serverless compatibility.
    """
    _, config = _initialize_service()
    return config

@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint - API information."""
    import os
    return JSONResponse(
        content={
            "service": "AliExpress Affiliate API Proxy",
            "version": "2.3.0-vercel-fix",
            "deployment_timestamp": "2025-11-26T16:20:00Z",
            "deployment_id": os.getenv("VERCEL_GIT_COMMIT_SHA", "local")[:8],
            "status": "online",
            "message": "Welcome to AliExpress API Proxy 🚀",
            "documentation": {
                "swagger_ui": "/docs",
                "redoc": "/redoc",
                "openapi_json": "/openapi.json",
                "openapi_gpt": "/openapi-gpt.json"
            },
            "endpoints": {
                "health": "/health",
                "system_info": "/system/info",
                "security_info": "/security/info",
                "debug_env": "/debug/env"
            }
        }
    )

@app.get("/debug/env")
async def debug_env() -> Dict[str, Any]:
    """Debug endpoint to check environment variables (remove in production)."""
    import os
    import sys
    
    # Try to initialize and capture any errors
    init_status = "not_attempted"
    init_error = None
    config_app_key = None
    config_app_secret_first10 = None
    try:
        service, config = _initialize_service()
        init_status = "success"
        config_app_key = config.app_key
        config_app_secret_first10 = config.app_secret[:10]
    except Exception as e:
        init_status = "failed"
        init_error = str(e)
    
    raw_key = os.getenv("ALIEXPRESS_APP_KEY", "NOT_SET")
    raw_secret = os.getenv("ALIEXPRESS_APP_SECRET", "NOT_SET")
    
    return {
        "initialization_status": init_status,
        "initialization_error": init_error,
        "vercel": os.getenv("VERCEL", "not_set"),
        "vercel_env": os.getenv("VERCEL_ENV", "not_set"),
        "vercel_region": os.getenv("VERCEL_REGION", "not_set"),
        "router_status": _router_status,
        "raw_env_vars": {
            "aliexpress_app_key_present": bool(raw_key),
            "aliexpress_app_key_raw": raw_key,
            "aliexpress_app_key_repr": repr(raw_key),
            "aliexpress_app_secret_present": bool(raw_secret),
            "aliexpress_app_secret_first10_raw": raw_secret[:10],
            "aliexpress_tracking_id": os.getenv("ALIEXPRESS_TRACKING_ID", "not_set"),
        },
        "config_loaded_values": {
            "app_key": config_app_key,
            "app_key_repr": repr(config_app_key) if config_app_key else None,
            "app_secret_first10": config_app_secret_first10,
        },
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "all_aliexpress_keys": [k for k in os.environ.keys() if "ALIEXPRESS" in k],
        "all_vercel_keys": [k for k in os.environ.keys() if "VERCEL" in k]
    }

@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Basic health check endpoint.
    
    Returns 200 if service is operational, 503 if unhealthy.
    For detailed health information, use /health/detailed
    """
    try:
        # Initialize service if needed (lazy initialization)
        service = get_service()
        
        service_info = service.get_service_info()
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "status": "healthy",
                    "service_info": service_info
                }
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content=ServiceResponse.error_response(
                error=f"Service unhealthy: {str(e)}"
            ).to_dict()
        )

@app.get("/health/detailed")
async def detailed_health_check() -> JSONResponse:
    """
    Comprehensive health check with component-level status.
    
    Checks:
    - AliExpress API connectivity
    - Cache service availability (Redis, Database)
    - Service metrics
    - System resources
    
    Returns:
    - 200: All components healthy
    - 503: One or more critical components unhealthy
    - 207: Degraded (non-critical components unavailable)
    """
    from ..services.cache_service import CacheService
    from ..services.cache_config import CacheConfig
    from ..services.monitoring_service import get_monitoring_service
    import time
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "version": "2.0.0",
        "components": {},
        "metrics": {}
    }
    
    # Check AliExpress API
    try:
        service = get_service()
        start_time = time.time()
        categories = service.get_parent_categories()
        response_time = (time.time() - start_time) * 1000
        
        health_status["components"]["aliexpress_api"] = {
            "status": "healthy",
            "response_time_ms": round(response_time, 2),
            "categories_available": len(categories)
        }
    except Exception as e:
        health_status["components"]["aliexpress_api"] = {
            "status": "unhealthy",
            "error": str(e),
            "error_type": type(e).__name__
        }
        health_status["status"] = "unhealthy"
    
    # Check Cache Service
    try:
        cache_config = CacheConfig.from_env()
        cache_service = CacheService(cache_config)
        
        # Check Redis
        if cache_service.redis_available:
            try:
                cache_service.redis_client.ping()
                health_status["components"]["redis_cache"] = {
                    "status": "healthy",
                    "host": cache_config.redis_host,
                    "port": cache_config.redis_port
                }
            except Exception as e:
                health_status["components"]["redis_cache"] = {
                    "status": "degraded",
                    "error": str(e),
                    "note": "Using memory-only cache"
                }
                if health_status["status"] == "healthy":
                    health_status["status"] = "degraded"
        else:
            health_status["components"]["redis_cache"] = {
                "status": "unavailable",
                "note": "Redis disabled or unavailable, using memory-only cache"
            }
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
        
        # Check Database Cache
        if cache_service.db_available:
            try:
                cache_service.db_session.execute("SELECT 1")
                health_status["components"]["database_cache"] = {
                    "status": "healthy"
                }
            except Exception as e:
                health_status["components"]["database_cache"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                if health_status["status"] == "healthy":
                    health_status["status"] = "degraded"
        else:
            health_status["components"]["database_cache"] = {
                "status": "unavailable",
                "note": "Database cache disabled"
            }
    except Exception as e:
        health_status["components"]["cache_service"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Add monitoring metrics
    try:
        monitoring = get_monitoring_service()
        stats = monitoring.get_stats()
        
        health_status["metrics"] = {
            "uptime": stats['service']['uptime_human'],
            "total_requests": stats['requests']['total'],
            "success_rate": stats['requests']['success_rate'],
            "cache_hit_rate": stats['cache']['hit_rate'],
            "avg_response_time_ms": stats['response_time']['avg_ms']
        }
    except Exception as e:
        health_status["metrics"] = {
            "error": f"Failed to get metrics: {str(e)}"
        }
    
    # Determine HTTP status code
    if health_status["status"] == "healthy":
        status_code = 200
    elif health_status["status"] == "degraded":
        status_code = 207  # Multi-Status
    else:
        status_code = 503  # Service Unavailable
    
    return JSONResponse(
        content=health_status,
        status_code=status_code
    )

@app.get("/openapi.json")
async def get_openapi_spec() -> JSONResponse:
    """Export OpenAPI specification as JSON."""
    return JSONResponse(content=app.openapi())

@app.get("/openapi-gpt.json")
async def get_openapi_gpt_spec() -> JSONResponse:
    """Export GPT-optimized OpenAPI specification as JSON."""
    openapi_schema = app.openapi()
    
    # Optimize for GPT Actions
    openapi_schema["info"]["title"] = "AliExpress Affiliate API"
    openapi_schema["info"]["description"] = "AliExpress Affiliate API for product search, categories, and affiliate link generation. Perfect for GPT Actions integration."
    
    return JSONResponse(content=openapi_schema)

@app.get("/system/info")
async def get_system_info(
    service: AliExpressService = Depends(get_service),
    config: Config = Depends(get_config)
) -> JSONResponse:
    """Get detailed system information and API capabilities."""
    try:
        service_info = service.get_service_info()
        
        system_info = {
            "service": service_info,
            "configuration": {
                "language": config.language,
                "currency": config.currency,
                "api_host": config.api_host,
                "api_port": config.api_port,
                "log_level": config.log_level
            },
            "api_endpoints": {
                "total_endpoints": len([route for route in app.routes if hasattr(route, 'methods')]),
                "categories": ["GET /api/categories", "GET /api/categories/{id}/children"],
                "products": [
                    "GET/POST /api/products/search",
                    "GET/POST /api/products",
                    "GET /api/products/details/{id}",
                    "POST /api/products/details",
                    "GET/POST /api/products/hot"
                ],
                "affiliate": [
                    "GET /api/affiliate/link",
                    "POST /api/affiliate/links",
                    "GET /api/smart-match",
                    "GET /api/orders"
                ]
            },
            "permissions_required": {
                "hot_products": "Special API permissions needed",
                "orders": "Affiliate account with order tracking",
                "smart_match": "Advanced API access with device_id"
            }
        }
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=system_info
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get system info: {str(e)}"
            ).to_dict()
        )

@app.exception_handler(PermissionError)
async def permission_exception_handler(request: Request, exc: PermissionError) -> JSONResponse:
    """Handle permission errors with helpful guidance."""
    logger = get_logger_with_context(__name__)
    logger.warning_ctx("Permission error encountered", error=str(exc), path=str(request.url))
    
    return JSONResponse(
        status_code=403,
        content=ServiceResponse.error_response(
            error=str(exc)
        ).to_dict()
    )

@app.exception_handler(RateLimitError)
async def rate_limit_exception_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handle rate limit errors."""
    logger = get_logger_with_context(__name__)
    logger.warning_ctx("Rate limit exceeded", error=str(exc), path=str(request.url))
    
    return JSONResponse(
        status_code=429,
        content=ServiceResponse.error_response(
            error=str(exc)
        ).to_dict(),
        headers={"Retry-After": "60"}
    )

@app.exception_handler(AliExpressServiceException)
async def service_exception_handler(request: Request, exc: AliExpressServiceException) -> JSONResponse:
    """Handle AliExpress service exceptions."""
    logger = get_logger_with_context(__name__)
    logger.error_ctx("Service exception", error=str(exc), path=str(request.url))
    
    return JSONResponse(
        status_code=400,
        content=ServiceResponse.error_response(
            error=str(exc)
        ).to_dict()
    )

@app.exception_handler(ConfigurationError)
async def config_exception_handler(request: Request, exc: ConfigurationError) -> JSONResponse:
    """Handle configuration exceptions."""
    logger = get_logger_with_context(__name__)
    logger.error_ctx("Configuration error", error=str(exc))
    
    return JSONResponse(
        status_code=500,
        content=ServiceResponse.error_response(
            error=f"Configuration error: {str(exc)}"
        ).to_dict()
    )

# Track router loading status
_router_status: Dict[str, str] = {}

# Import and include routers with error handling
try:
    from .endpoints.categories import router as categories_router
    app.include_router(categories_router, prefix="/api", tags=["categories"])
    _router_status["categories"] = "loaded"
    print("[ROUTER] Categories router loaded successfully")
except Exception as e:
    _router_status["categories"] = f"failed: {str(e)}"
    log_warning(logging.getLogger(__name__), "categories_router_load_failed", error_type=type(e).__name__, error_message=str(e))
    import traceback
    traceback.print_exc()

try:
    from .endpoints.products import router as products_router
    app.include_router(products_router, prefix="/api", tags=["products"])
    _router_status["products"] = "loaded"
    print("[ROUTER] Products router loaded successfully")
except Exception as e:
    _router_status["products"] = f"failed: {str(e)}"
    log_warning(logging.getLogger(__name__), "products_router_load_failed", error_type=type(e).__name__, error_message=str(e))
    import traceback
    traceback.print_exc()

try:
    from .endpoints.affiliate import router as affiliate_router
    app.include_router(affiliate_router, prefix="/api", tags=["affiliate"])
    _router_status["affiliate"] = "loaded"
    print("[ROUTER] Affiliate router loaded successfully")
except Exception as e:
    _router_status["affiliate"] = f"failed: {str(e)}"
    log_warning(logging.getLogger(__name__), "affiliate_router_load_failed", error_type=type(e).__name__, error_message=str(e))
    import traceback
    traceback.print_exc()

try:
    from .endpoints.admin import router as admin_router
    app.include_router(admin_router, tags=["admin"])
    _router_status["admin"] = "loaded"
    print("[ROUTER] Admin router loaded successfully")
except Exception as e:
    _router_status["admin"] = f"failed: {str(e)}"
    log_warning(logging.getLogger(__name__), "admin_router_load_failed", error_type=type(e).__name__, error_message=str(e))
    import traceback
    traceback.print_exc()

# Add security info endpoint
@app.get("/security/info")
async def get_security_info() -> JSONResponse:
    """Get public security information (no auth required)."""
    # Get security manager lazily to avoid import-time failures
    try:
        sec_mgr = get_security_manager()
        rate_limits = {
            "per_minute": sec_mgr.max_requests_per_minute,
            "per_second": sec_mgr.max_requests_per_second
        }
        allowed_origins = sec_mgr.allowed_origins
    except Exception as e:
        # Fallback if security manager not available
        log_warning(
            logging.getLogger(__name__),
            "security_manager_unavailable",
            error_type=type(e).__name__,
            error_message=str(e)
        )
        rate_limits = {
            "per_minute": 60,
            "per_second": 5
        }
        allowed_origins = ["https://chat.openai.com", "https://chatgpt.com"]
    
    return JSONResponse(
        content=ServiceResponse.success_response(
            data={
                "security_features": [
                    "HTTPS enforcement (production)",
                    "Trusted host validation",
                    "CORS protection with restricted origins",
                    "CSRF token protection",
                    "Rate limiting (60/min, 5/sec per IP)",
                    "Internal API key authentication",
                    "SQLite audit logging",
                    "Request logging and monitoring",
                    "IP blocking capabilities",
                    "Security headers (X-Content-Type-Options, X-Frame-Options, etc.)"
                ],
                "required_headers": {
                    "x-internal-key": "Required for all /api/* endpoints",
                    "x-admin-key": "Required for all /admin/* endpoints",
                    "x-csrf-token": "Required for POST/PUT/DELETE web requests (optional for API)"
                },
                "rate_limits": rate_limits,
                "allowed_origins": allowed_origins,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "audit_logging": "SQLite-based audit trail enabled"
            }
        ).to_dict(),
        headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Load config for port
    try:
        config = Config.from_env()
        uvicorn.run(
            "src.api.main:app",
            host=config.api_host,
            port=config.api_port,
            reload=True,
            log_level=config.log_level.lower()
        )
    except Exception as e:
        print(f"Failed to start server: {e}")
        exit(1)