"""FastAPI application for AliExpress API service."""

import logging
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from ..utils.config import Config, ConfigurationError
from ..utils.logging_config import setup_production_logging, get_logger_with_context
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


# Create FastAPI app
app = FastAPI(
    title="AliExpress API Service",
    description="A comprehensive FastAPI service for the AliExpress Affiliate API using the official Python SDK. "
                "Supports product search, details, affiliate links, hot products, promotions, and more.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(categories_router, prefix="/api", tags=["categories"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(affiliate_router, prefix="/api", tags=["affiliate"])


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