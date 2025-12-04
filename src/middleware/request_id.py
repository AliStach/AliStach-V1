"""Request ID middleware for request tracing."""

import uuid
import logging
from typing import Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from ..utils.logging_config import request_id_ctx, log_info, log_error

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.
    
    The request ID is:
    - Generated for each request
    - Added to response headers
    - Available in request state for logging
    - Used for distributed tracing
    - Stored in context variable for automatic inclusion in all logs
    """
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Process request and add request ID."""
        # Generate unique request ID or use existing from header
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Store in request state for access in endpoints
        request.state.request_id = request_id
        
        # Set in context variable for automatic logging
        token = request_id_ctx.set(request_id)
        
        try:
            # Log incoming request
            log_info(
                logger,
                "incoming_request",
                method=request.method,
                path=request.url.path,
                client_host=request.client.host if request.client else None
            )
            
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            # Log response
            log_info(
                logger,
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code
            )
            
            return response
        except Exception as e:
            # Log error
            log_error(
                logger,
                "request_failed",
                exc_info=True,
                method=request.method,
                path=request.url.path,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            raise
        finally:
            # Reset context variable
            request_id_ctx.reset(token)
