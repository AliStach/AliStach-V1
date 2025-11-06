"""Simplified FastAPI application for Vercel deployment."""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration class
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
        self.mock_mode = os.getenv('MOCK_MODE', 'true').lower() == 'true'

# Initialize config
config = Config()

# Create FastAPI app
app = FastAPI(
    title="AliExpress Affiliate API",
    description="AliExpress Affiliate API for product search, categories, and affiliate link generation. Perfect for GPT Actions integration.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
            "mock_mode": config.mock_mode
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

# Mock product search endpoint
@app.post("/api/products/search", response_model=ProductSearchResponse)
async def search_products(request: ProductSearchRequest):
    """Search for products (mock implementation for now)."""
    try:
        # Mock response data
        mock_products = [
            {
                "product_id": "1005001234567890",
                "product_title": f"Mock Product for '{request.keywords}'",
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
        
        response_data = {
            "products": mock_products,
            "total_results": len(mock_products),
            "current_page": request.page_no,
            "page_size": request.page_size
        }
        
        metadata = {
            "mock_mode": config.mock_mode,
            "processing_time_ms": 250,
            "api_version": "1.0.0",
            "search_params": {
                "keywords": request.keywords,
                "page_size": request.page_size,
                "sort": request.sort
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

# Categories endpoint
@app.get("/api/categories")
async def get_categories():
    """Get product categories (mock implementation)."""
    mock_categories = [
        {"category_id": "3", "category_name": "Electronics"},
        {"category_id": "1420", "category_name": "Automobiles & Motorcycles"},
        {"category_id": "1501", "category_name": "Home & Garden"},
        {"category_id": "509", "category_name": "Cellphones & Telecommunications"},
        {"category_id": "322", "category_name": "Consumer Electronics"}
    ]
    
    return {
        "success": True,
        "data": {"categories": mock_categories},
        "metadata": {"mock_mode": config.mock_mode}
    }

# Affiliate links endpoint
@app.post("/api/affiliate/links")
async def generate_affiliate_links(urls: Dict[str, list]):
    """Generate affiliate links (mock implementation)."""
    mock_links = []
    for url in urls.get("urls", []):
        mock_links.append({
            "original_url": url,
            "affiliate_url": f"{url}?aff_trace_key=mock_affiliate_key",
            "commission_rate": "5.0%"
        })
    
    return {
        "success": True,
        "data": {"affiliate_links": mock_links},
        "metadata": {"mock_mode": config.mock_mode}
    }

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

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AliExpress Affiliate API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "openapi": "/openapi-gpt.json",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)