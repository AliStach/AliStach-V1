"""CSRF protection middleware for FastAPI."""

import secrets
import logging
from typing import Optional, List, Callable, Awaitable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.responses import Response
from ..models.responses import ServiceResponse

logger = logging.getLogger(__name__)

class CSRFProtection:
    """CSRF token validation for POST/PUT/DELETE requests."""
    
    def __init__(self, secret_key: Optional[str] = None):
        """Initialize CSRF protection."""
        self.secret_key: str = secret_key or secrets.token_urlsafe(32)
        self.exempt_paths: List[str] = [
            '/health',
            '/docs',
            '/redoc',
            '/openapi.json',
            '/openapi-gpt.json'
        ]
    
    def is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection."""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    def validate_csrf_token(self, request: Request) -> bool:
        """Validate CSRF token in request."""
        # Skip CSRF for GET, HEAD, OPTIONS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Skip CSRF for exempt paths
        if self.is_exempt(request.url.path):
            return True
        
        # For API endpoints, CSRF is optional if using API keys
        # This is a simplified implementation - in production, use proper CSRF tokens
        # For API-only services, API key authentication may be sufficient
        
        # Check for API key (if present, skip CSRF)
        if request.headers.get('x-internal-key') or request.headers.get('x-admin-key'):
            return True
        
        # For web forms, require CSRF token
        csrf_token = request.headers.get('x-csrf-token')
        if not csrf_token:
            logger.warning(f"Missing CSRF token for {request.method} {request.url.path}")
            return False
        
        # In production, validate against session token
        # For now, we'll allow requests with API keys
        return True

# Global CSRF protection instance (lazy initialization for Vercel compatibility)
_csrf_protection_instance: Optional[CSRFProtection] = None

def get_csrf_protection() -> CSRFProtection:
    """Get or create the global CSRF protection instance."""
    global _csrf_protection_instance
    if _csrf_protection_instance is None:
        _csrf_protection_instance = CSRFProtection()
    return _csrf_protection_instance

async def csrf_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """CSRF protection middleware."""
    # Skip CSRF for API endpoints (they use API keys)
    if request.url.path.startswith('/api/') or request.url.path.startswith('/admin/'):
        return await call_next(request)
    
    # Validate CSRF for other POST/PUT/DELETE requests
    csrf_protection = get_csrf_protection()
    if not csrf_protection.validate_csrf_token(request):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ServiceResponse.error_response(
                error="CSRF token validation failed"
            ).to_dict()
        )
    
    return await call_next(request)

