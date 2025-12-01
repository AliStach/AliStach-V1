"""Affiliate endpoints for AliExpress API."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ...services.aliexpress_service import AliExpressService, AliExpressServiceException
from ...models.responses import ServiceResponse


router = APIRouter()


class AffiliateLinksRequest(BaseModel):
    """Request model for affiliate link generation."""
    urls: List[str] = Field(..., min_length=1, max_length=50)


def get_service() -> AliExpressService:
    """Dependency to get the AliExpress service instance."""
    from ..main import get_service as main_get_service
    return main_get_service()


@router.post("/affiliate/links")
async def generate_affiliate_links(
    request: AffiliateLinksRequest,
    service: AliExpressService = Depends(get_service)
):
    """
    Generate affiliate links for given product URLs.
    """
    try:
        results = service.get_affiliate_links(request.urls)
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=[result.to_dict() for result in results],
                metadata={
                    "requested_count": len(request.urls),
                    "generated_count": len(results),
                    "tracking_id": service.config.tracking_id
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


@router.get("/affiliate/link")
async def generate_affiliate_link_single(
    url: str = Query(..., description="Product URL to convert to affiliate link"),
    service: AliExpressService = Depends(get_service)
):
    """
    Generate affiliate link for a single product URL.
    """
    try:
        results = service.get_affiliate_links([url])
        
        if not results:
            return JSONResponse(
                status_code=404,
                content=ServiceResponse.error_response(
                    error="Could not generate affiliate link for the provided URL"
                ).to_dict()
            )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=results[0].to_dict(),
                metadata={
                    "original_url": url,
                    "tracking_id": service.config.tracking_id
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


@router.get("/orders")
async def get_orders(
    start_time: Optional[str] = Query(None, description="Start time for order search (YYYY-MM-DD)"),
    end_time: Optional[str] = Query(None, description="End time for order search (YYYY-MM-DD)"),
    page_no: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=50, description="Number of results per page"),
    service: AliExpressService = Depends(get_service)
):
    """
    Get order list (requires special affiliate permissions).
    Defaults to last 7 days if no date range specified.
    """
    try:
        # Default to last 7 days if not specified
        from datetime import datetime, timedelta
        if not start_time:
            start_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if not end_time:
            end_time = datetime.now().strftime("%Y-%m-%d")
        
        result = service.get_order_list(
            start_time=start_time,
            end_time=end_time,
            page_no=page_no,
            page_size=page_size
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result,
                metadata={
                    "search_params": {
                        "start_time": start_time,
                        "end_time": end_time,
                        "page_no": page_no,
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


@router.get("/smart-match")
async def smart_match_product(
    product_url: str = Query(..., description="Product URL to match"),
    target_language: Optional[str] = Query(None, description="Target language code"),
    target_currency: Optional[str] = Query(None, description="Target currency code"),
    device_id: Optional[str] = Query("alistach-smartmatch-001", description="Device ID for tracking"),
    service: AliExpressService = Depends(get_service)
):
    """
    Smart match product by URL to get standardized product information.
    Uses default device_id for better data quality.
    """
    try:
        result = service.smart_match_product(
            product_url=product_url,
            target_language=target_language,
            target_currency=target_currency,
            device_id=device_id
        )
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=result,
                metadata={
                    "original_url": product_url,
                    "target_language": target_language,
                    "target_currency": target_currency,
                    "device_id": device_id
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