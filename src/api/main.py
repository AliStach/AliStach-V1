"""FastAPI application for AliExpress API service with comprehensive security."""

import logging
import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from ..utils.config import Config, ConfigurationError
from ..utils.logging_config import setup_production_logging, get_logger_with_context
from ..middleware.security import security_middleware, get_security_manager
from ..services.aliexpress_service import (
    AliExpressService, AliExpressServiceException, PermissionError, RateLimitError
)
from ..models.responses import ServiceResponse


# Global service instance
service_instance = None
config_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global service_instance, config_instance
    
    try:
        # Initialize configuration and service on startup
        config_instance = Config.from_env()
        config_instance.validate()
        
        # Set up production logging
        setup_production_logging(config_instance.log_level)
        logger = get_logger_with_context(__name__)
        
        service_instance = AliExpressService(config_instance)
        logger.info_ctx(
            "AliExpress service initialized successfully",
            language=config_instance.language,
            currency=config_instance.currency,
            tracking_id=config_instance.tracking_id
        )
        yield
    except Exception as e:
        logger = get_logger_with_context(__name__)
        logger.error_ctx("Failed to initialize service", error=str(e))
        raise
    finally:
        # Cleanup on shutdown
        service_instance = None
        config_instance = None
        logger = get_logger_with_context(__name__)
        logger.info("Service shutdown complete")


# Create FastAPI app with security configuration
app = FastAPI(
    title="AliExpress Affiliate API Proxy",
    description="""
    🔒 **Secure AliExpress Affiliate API Proxy**
    
    A production-grade, secure FastAPI service for the AliExpress Affiliate API with:
    
    * **🛡️ Security**: Origin validation, rate limiting, IP blocking
    * **🔐 Authentication**: Internal API key protection
    * **📊 Monitoring**: Request logging and admin dashboard
    * **⚡ Performance**: Optimized for GPT and high-traffic usage
    * **🔗 Affiliate Integration**: Automatic affiliate link generation
    
    ## Security Features
    
    * **CORS Protection**: Restricted to authorized domains
    * **Rate Limiting**: 60 requests/minute, 5 requests/second per IP
    * **Request Logging**: Comprehensive audit trail
    * **IP Blocking**: Automatic and manual IP blocking
    * **Internal API Key**: Required for all API endpoints
    
    ## Usage
    
    All API requests must include the `x-internal-key` header with value `ALIINSIDER-2025`.
    
    Admin endpoints require the `x-admin-key` header for monitoring and management.
    """,
    version="2.0.0-secure",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware FIRST (order matters)
app.middleware("http")(security_middleware)

# Add trusted host middleware for additional security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.vercel.app",
        "*.render.com",
        "*.railway.app",
        "your-domain.com"  # Replace with your actual domain
    ]
)

# Add CORS middleware with restricted origins
security_manager = get_security_manager()
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_manager.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization", 
        "x-internal-key",
        "x-admin-key",
        "User-Agent",
        "Accept"
    ],
    expose_headers=["Retry-After"]
)


def get_service() -> AliExpressService:
    """Dependency to get the AliExpress service instance."""
    if service_instance is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return service_instance


def get_config() -> Config:
    """Dependency to get the configuration instance."""
    if config_instance is None:
        raise HTTPException(status_code=503, detail="Configuration not loaded")
    return config_instance


@app.get("/health")
async def health_check(
    service: AliExpressService = Depends(get_service),
    config: Config = Depends(get_config)
):
    """Health check endpoint."""
    try:
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


# Import and include routers
from .endpoints.categories import router as categories_router
from .endpoints.products import router as products_router
from .endpoints.affiliate import router as affiliate_router
from .endpoints.admin import router as admin_router

app.include_router(categories_router, prefix="/api", tags=["categories"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(affiliate_router, prefix="/api", tags=["affiliate"])
app.include_router(admin_router, tags=["admin"])

# Add security info endpoint
@app.get("/security/info")
async def get_security_info():
    """Get public security information (no auth required)."""
    return JSONResponse(
        content=ServiceResponse.success_response(
            data={
                "security_features": [
                    "CORS protection with restricted origins",
                    "Rate limiting (60/min, 5/sec per IP)",
                    "Internal API key authentication",
                    "Request logging and monitoring",
                    "IP blocking capabilities"
                ],
                "required_headers": {
                    "x-internal-key": "Required for all /api/* endpoints"
                },
                "rate_limits": {
                    "per_minute": security_manager.max_requests_per_minute,
                    "per_second": security_manager.max_requests_per_second
                },
                "allowed_origins": security_manager.allowed_origins
            }
        ).to_dict()
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