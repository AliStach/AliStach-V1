"""Response formatting utilities for AliExpress API service."""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..models.responses import CategoryResponse, ProductResponse

def format_categories_response(categories: List[CategoryResponse]) -> Dict[str, Any]:
    """Format a list of categories for API response."""
    return {
        'categories': [category.to_dict() for category in categories],
        'total_count': len(categories)
    }

def format_products_response(products: List[ProductResponse], 
                           total_count: Optional[int] = None,
                           page_no: int = 1,
                           page_size: int = 20) -> Dict[str, Any]:
    """Format a list of products for API response."""
    return {
        'products': [product.to_dict() for product in products],
        'total_record_count': total_count or len(products),
        'current_page': page_no,
        'page_size': page_size,
        'total_pages': ((total_count or len(products)) + page_size - 1) // page_size
    }

def format_error_response(error_message: str, 
                         error_code: Optional[str] = None,
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format an error response."""
    error_data: Dict[str, Any] = {
        'message': error_message
    }
    
    if error_code:
        error_data['code'] = error_code
    
    if details:
        error_data['details'] = details
    
    return error_data

def to_json_string(data: Any, indent: int = 2) -> str:
    """Convert data to formatted JSON string."""
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

def add_response_metadata(data: Dict[str, Any], 
                         processing_time_ms: Optional[float] = None,
                         additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Add metadata to response data."""
    metadata: Dict[str, Any] = {
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if processing_time_ms is not None:
        metadata['processing_time_ms'] = round(processing_time_ms, 2)
    
    if additional_metadata:
        metadata.update(additional_metadata)
    
    data['metadata'] = metadata
    return data