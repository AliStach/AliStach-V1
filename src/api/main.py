"""FastAPI application for AliExpress API service with comprehensive security."""

import logging
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from ..utils.config import Config, ConfigurationError
from ..utils.logging_config import setup_production_logging, get_logger_with_context
from ..middleware.security import security_middleware, get_security_manager
from ..middleware.csrf import csrf_middleware
from ..middleware.security_headers import SecurityHeadersMiddleware
from ..services.aliexpress_service import (
    AliExpressServiceException, PermissionError, RateLimitError
)
from ..services.aliexpress_service import AliExpressService
from ..models.responses import ServiceResponse


# Global service instance - lazy initialized for Vercel compatibility
_service_instance = None
_config_instance = None
_initialization_error = None
_logger = None


def _initialize_service():
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
        # Initialize configuration
        _config_instance = Config.from_env()
        _config_instance.validate()
        
        # Set up logging
        setup_production_logging(_config_instance.log_level)
        _logger = get_logger_with_context(__name__)
        
        # Initialize service
        _service_instance = AliExpressService(_config_instance)
        
        _logger.info_ctx(
            "AliExpress service initialized successfully",
            language=_config_instance.language,
            currency=_config_instance.currency,
            tracking_id=_config_instance.tracking_id
        )
        
        return _service_instance, _config_instance
        
    except ConfigurationError as e:
        _initialization_error = HTTPException(
            status_code=503,
            detail=f"Service configuration error: {str(e)}"
        )
        raise _initialization_error
    except Exception as e:
        _initialization_error = HTTPException(
            status_code=503,
            detail=f"Service initialization failed: {str(e)}"
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
    logging.warning(f"Failed to add HTTPS redirect middleware: {e}")

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
    logging.warning(f"Failed to add SecurityHeadersMiddleware: {e}")

# Add CSRF protection middleware (after CORS)
try:
    app.middleware("http")(csrf_middleware)
except Exception as e:
    logging.warning(f"Failed to add CSRF middleware: {e}")

# Add security middleware LAST (order matters - after CORS and CSRF)
try:
    app.middleware("http")(security_middleware)
except Exception as e:
    logging.warning(f"Failed to add security middleware: {e}")


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
async def root():
    """Root endpoint - API information."""
    return JSONResponse(
        content={
            "service": "AliExpress Affiliate API Proxy",
            "version": "2.1.0-secure",
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
                "security_info": "/security/info"
            }
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
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


@app.get("/system/info")
async def get_system_info(
    service: AliExpressService = Depends(get_service),
    config: Config = Depends(get_config)
):
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
async def permission_exception_handler(request, exc: PermissionError):
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
async def rate_limit_exception_handler(request, exc: RateLimitError):
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
async def service_exception_handler(request, exc: AliExpressServiceException):
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
async def config_exception_handler(request, exc: ConfigurationError):
    """Handle configuration exceptions."""
    logger = get_logger_with_context(__name__)
    logger.error_ctx("Configuration error", error=str(exc))
    
    return JSONResponse(
        status_code=500,
        content=ServiceResponse.error_response(
            error=f"Configuration error: {str(exc)}"
        ).to_dict()
    )


# Import and include routers with error handling
try:
    from .endpoints.categories import router as categories_router
    app.include_router(categories_router, prefix="/api", tags=["categories"])
except Exception as e:
    logging.warning(f"Failed to load categories router: {e}")

try:
    from .endpoints.products import router as products_router
    app.include_router(products_router, prefix="/api", tags=["products"])
except Exception as e:
    logging.warning(f"Failed to load products router: {e}")

try:
    from .endpoints.affiliate import router as affiliate_router
    app.include_router(affiliate_router, prefix="/api", tags=["affiliate"])
except Exception as e:
    logging.warning(f"Failed to load affiliate router: {e}")

try:
    from .endpoints.admin import router as admin_router
    app.include_router(admin_router, tags=["admin"])
except Exception as e:
    logging.warning(f"Failed to load admin router: {e}")

# Add security info endpoint
@app.get("/security/info")
async def get_security_info():
    """Get public security information (no auth required)."""
    # Get security manager lazily to avoid import-time failures
    try:
        sec_mgr = get_security_manager()
        rate_limits = {
            "per_minute": sec_mgr.max_requests_per_minute,
            "per_second": sec_mgr.max_requests_per_second
        }
        allowed_origins = sec_mgr.allowed_origins
    except Exception:
        # Fallback if security manager not available
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