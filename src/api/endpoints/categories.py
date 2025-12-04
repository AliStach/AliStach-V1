"""Category endpoints for AliExpress API."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from ...services.aliexpress_service import AliExpressService, AliExpressServiceException
from ...models.responses import ServiceResponse

router: APIRouter = APIRouter()

def get_service() -> AliExpressService:
    """Dependency to get the AliExpress service instance."""
    from ..main import get_service as main_get_service
    return main_get_service()

@router.get("/categories")
async def get_categories(service: AliExpressService = Depends(get_service)) -> JSONResponse:
    """
    Get all parent categories from AliExpress.
    
    Returns a list of parent categories with their IDs and names.
    """
    try:
        categories = service.get_parent_categories()
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=[category.to_dict() for category in categories],
                metadata={"total_count": len(categories)}
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

@router.get("/categories/{parent_id}/children")
async def get_child_categories(
    parent_id: str,
    service: AliExpressService = Depends(get_service)
) -> JSONResponse:
    """
    Get child categories for a specific parent category.
    
    Args:
        parent_id: The ID of the parent category
        
    Returns a list of child categories under the specified parent.
    """
    try:
        if not parent_id or not parent_id.strip():
            return JSONResponse(
                status_code=400,
                content=ServiceResponse.error_response(
                    error="parent_id cannot be empty"
                ).to_dict()
            )
        
        categories = service.get_child_categories(parent_id)
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=[category.to_dict() for category in categories],
                metadata={
                    "parent_id": parent_id,
                    "total_count": len(categories)
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