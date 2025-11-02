"""Product endpoints for AliExpress API."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ...services.aliexpress_service import AliExpressService, AliExpressServiceException
from ...models.responses import ServiceResponse


router = APIRouter()


class ProductSearchRequest(BaseModel):
    """Request model for product search."""
    keywords: Optional[str] = None
    category_ids: Optional[str] = None
    page_no: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)
    sort: Optional[str] = None


class ProductsRequest(BaseModel):
    """Request model for enhanced product search."""
    keywords: Optional[str] = None
    max_sale_price: Optional[float] = Field(default=None, ge=0)
    min_sale_price: Optional[float] = Field(default=None, ge=0)
    category_id: Optional[str] = None
    page_no: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)
    sort: Optional[str] = None


class HotProductsRequest(BaseModel):
    """Request model for hot products."""
    keywords: Optional[str] = None
    max_sale_price: Optional[float] = Field(default=None, ge=0)
    sort: Optional[str] = None
    page_size: int = Field(default=20, ge=1, le=50)


def get_service() -> AliExpressService:
    """Dependency to get the AliExpress service instance."""
    from ..main import service_instance
    if service_instance is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return service_instance


@router.post("/products/search")
async def search_products(
    request: ProductSearchRequest,
    service: AliExpressService = Depends(get_service)
):
    """
    Search for products using various criteria.
    
    Args:
        request: Product search parameters including keywords, categories, pagination
        
    Returns a list of products matching the search criteria.
    """
    try:
        result = service.search_products(
            keywords=request.keywords,
            category_ids=request.category_ids,
            page_no=request.page_no,
            page_size=request.page_size,
            sort=request.sort
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result.to_dict(),
                metadata={
                    "search_params": request.dict(exclude_none=True)
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


@router.get("/products/search")
async def search_products_get(
    keywords: Optional[str] = Query(None, description="Search keywords"),
    category_ids: Optional[str] = Query(None, description="Comma-separated category IDs"),
    page_no: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Number of results per page"),
    sort: Optional[str] = Query(None, description="Sort order"),
    service: AliExpressService = Depends(get_service)
):
    """
    Search for products using GET method with query parameters.
    
    This is an alternative to the POST method for simpler integrations.
    """
    try:
        result = service.search_products(
            keywords=keywords,
            category_ids=category_ids,
            page_no=page_no,
            page_size=page_size,
            sort=sort
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result.to_dict(),
                metadata={
                    "search_params": {
                        "keywords": keywords,
                        "category_ids": category_ids,
                        "page_no": page_no,
                        "page_size": page_size,
                        "sort": sort
                    }
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


@router.post("/products")
async def get_products(
    request: ProductsRequest,
    service: AliExpressService = Depends(get_service)
):
    """
    Get products with enhanced filtering options including price range.
    
    This endpoint provides more advanced filtering capabilities than the basic search.
    """
    try:
        result = service.get_products(
            keywords=request.keywords,
            max_sale_price=request.max_sale_price,
            min_sale_price=request.min_sale_price,
            category_id=request.category_id,
            page_no=request.page_no,
            page_size=request.page_size,
            sort=request.sort
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result.to_dict(),
                metadata={
                    "search_params": request.dict(exclude_none=True)
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


@router.get("/products")
async def get_products_get(
    keywords: Optional[str] = Query(None, description="Search keywords"),
    max_sale_price: Optional[float] = Query(None, ge=0, description="Maximum sale price"),
    min_sale_price: Optional[float] = Query(None, ge=0, description="Minimum sale price"),
    category_id: Optional[str] = Query(None, description="Category ID"),
    page_no: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Number of results per page"),
    sort: Optional[str] = Query(None, description="Sort order"),
    service: AliExpressService = Depends(get_service)
):
    """
    Get products with enhanced filtering using GET method.
    """
    try:
        result = service.get_products(
            keywords=keywords,
            max_sale_price=max_sale_price,
            min_sale_price=min_sale_price,
            category_id=category_id,
            page_no=page_no,
            page_size=page_size,
            sort=sort
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result.to_dict(),
                metadata={
                    "search_params": {
                        "keywords": keywords,
                        "max_sale_price": max_sale_price,
                        "min_sale_price": min_sale_price,
                        "category_id": category_id,
                        "page_no": page_no,
                        "page_size": page_size,
                        "sort": sort
                    }
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


@router.get("/products/details/{product_id}")
async def get_product_details_single(
    product_id: str,
    service: AliExpressService = Depends(get_service)
):
    """
    Get detailed information for a single product.
    """
    try:
        results = service.get_products_details([product_id])
        
        if not results:
            return JSONResponse(
                status_code=404,
                content=ServiceResponse.error_response(
                    error=f"Product {product_id} not found"
                ).to_dict()
            )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=results[0].to_dict(),
                metadata={
                    "product_id": product_id
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


class ProductDetailsRequest(BaseModel):
    """Request model for product details."""
    product_ids: List[str] = Field(..., min_items=1, max_items=20)


@router.post("/products/details")
async def get_products_details_bulk(
    request: ProductDetailsRequest,
    service: AliExpressService = Depends(get_service)
):
    """
    Get detailed information for multiple products (up to 20).
    """
    try:
        results = service.get_products_details(request.product_ids)
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=[result.to_dict() for result in results],
                metadata={
                    "requested_count": len(request.product_ids),
                    "returned_count": len(results)
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


@router.post("/products/hot")
async def get_hot_products(
    request: HotProductsRequest,
    service: AliExpressService = Depends(get_service)
):
    """
    Get hot/trending products.
    """
    try:
        result = service.get_hotproducts(
            keywords=request.keywords,
            max_sale_price=request.max_sale_price,
            sort=request.sort,
            page_size=request.page_size
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result.to_dict(),
                metadata={
                    "search_params": request.dict(exclude_none=True)
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


@router.get("/products/hot")
async def get_hot_products_get(
    keywords: Optional[str] = Query(None, description="Search keywords"),
    max_sale_price: Optional[float] = Query(None, ge=0, description="Maximum sale price"),
    sort: Optional[str] = Query(None, description="Sort order"),
    page_size: int = Query(20, ge=1, le=50, description="Number of results per page"),
    service: AliExpressService = Depends(get_service)
):
    """
    Get hot/trending products using GET method.
    """
    try:
        result = service.get_hotproducts(
            keywords=keywords,
            max_sale_price=max_sale_price,
            sort=sort,
            page_size=page_size
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result.to_dict(),
                metadata={
                    "search_params": {
                        "keywords": keywords,
                        "max_sale_price": max_sale_price,
                        "sort": sort,
                        "page_size": page_size
                    }
                }
            ).to_dict()
        )
    except AliExpressServiceException as e:
        return JSONResponse(
            status_code=400,
            content=ServiceResponse.error_response(
                error=str(e)
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Internal server error: {str(e)}"
            ).to_dict()
        )


