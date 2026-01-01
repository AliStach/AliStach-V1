"""Security middleware for AliExpress API proxy."""

import time
import logging
from typing import Optional, Dict, List, Tuple
from collections import defaultdict
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from ..models.responses import ServiceResponse
from .audit_logger import get_audit_logger

logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security manager for API protection."""
    
    def __init__(self, config=None):
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage = defaultdict(list)
        self.blocked_ips = set()
        
        # Load configuration
        if config:
            self.allowed_origins = [origin.strip() for origin in config.allowed_origins.split(',')]
            self.internal_api_key = config.internal_api_key
            self.max_requests_per_minute = config.max_requests_per_minute
            self.max_requests_per_second = config.max_requests_per_second
        else:
            # Default configuration
            self.allowed_origins = [
                "https://chat.openai.com",
                "https://chatgpt.com", 
                "https://platform.openai.com",
                "http://localhost:3000",  # Development
                "http://localhost:8000",  # Development
                "http://127.0.0.1:3000",  # Development
                "http://127.0.0.1:8000",  # Development
                "https://aliexpress-api-proxy.vercel.app",  # Production Vercel domain
            ]
            self.internal_api_key = "ALIINSIDER-2025"
            self.max_requests_per_minute = 60
            self.max_requests_per_second = 5
        
        # Request logging
        self.request_logs = []
        self.max_log_entries = 10000
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'rate_limited_requests': 0,
            'permission_errors': 0,
            'start_time': datetime.now()
        }
    
    def validate_origin(self, request: Request) -> bool:
        """Validate request origin against allowed origins."""
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        host = request.headers.get("host", "")
        user_agent = request.headers.get("user-agent", "").lower()
        internal_key = request.headers.get("x-internal-key")
        
        # Check if request has valid internal API key
        has_valid_key = internal_key == self.internal_api_key
        
        # Allow authenticated CLI tools and GPT based on User-Agent
        if has_valid_key:
            cli_tools = ["curl", "powershell", "invoke-restmethod", "python-httpx", "openai", "gpt"]
            if any(tool in user_agent for tool in cli_tools):
                return True
            
            # Allow missing/null/empty origin for authenticated requests
            if not origin or origin.lower() in ["null", ""]:
                return True
        
        # Allow requests without origin/referer for direct API access (curl, Postman, etc.)
        if not origin and not referer:
            return True
        
        # Always allow requests from the same host (self-origin)
        if origin:
            # Extract domain from origin (e.g., "https://example.com" -> "example.com")
            origin_domain = origin.replace("https://", "").replace("http://", "").split("/")[0]
            if origin_domain == host:
                return True
        
        # Check origin against allowed list
        if origin:
            for allowed in self.allowed_origins:
                if origin == allowed or origin.startswith(allowed):
                    return True
        
        # Check referer as fallback
        if referer:
            # Extract domain from referer
            referer_domain = referer.replace("https://", "").replace("http://", "").split("/")[0]
            if referer_domain == host:
                return True
            
            for allowed in self.allowed_origins:
                if referer.startswith(allowed):
                    return True
        
        return False
    
    def validate_internal_key(self, request: Request) -> bool:
        """Validate internal API key header."""
        internal_key = request.headers.get("x-internal-key")
        return internal_key == self.internal_api_key
    
    def check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """Check if client IP is within rate limits."""
        now = time.time()
        
        # Clean old entries
        self.rate_limit_storage[client_ip] = [
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if now - timestamp < 60  # Keep last minute
        ]
        
        requests_last_minute = len(self.rate_limit_storage[client_ip])
        requests_last_second = len([
            timestamp for timestamp in self.rate_limit_storage[client_ip]
            if now - timestamp < 1
        ])
        
        # Check limits
        if requests_last_second >= self.max_requests_per_second:
            return False, f"Rate limit exceeded: {requests_last_second} requests in last second (max: {self.max_requests_per_second})"
        
        if requests_last_minute >= self.max_requests_per_minute:
            return False, f"Rate limit exceeded: {requests_last_minute} requests in last minute (max: {self.max_requests_per_minute})"
        
        # Add current request
        self.rate_limit_storage[client_ip].append(now)
        return True, None
    
    def is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked."""
        return client_ip in self.blocked_ips
    
    def block_ip(self, client_ip: str, reason: str = "Security violation"):
        """Block an IP address."""
        self.blocked_ips.add(client_ip)
        logger.warning(f"Blocked IP {client_ip}: {reason}")
        
        # Log security event to audit database
        try:
            get_audit_logger().log_event(
                event_type="ip_blocked",
                client_ip=client_ip,
                security_event=reason,
                metadata={'action': 'block_ip', 'reason': reason}
            )
        except Exception as e:
            logger.warning(f"Failed to log IP block event: {e}")
    
    def log_request(self, request: Request, response_status: int, duration: float, error: Optional[str] = None):
        """Log request for monitoring and audit."""
        client_ip = self.get_client_ip(request)
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'client_ip': client_ip,
            'method': request.method,
            'path': str(request.url.path),
            'query_params': dict(request.query_params),
            'user_agent': request.headers.get('user-agent', ''),
            'origin': request.headers.get('origin', ''),
            'referer': request.headers.get('referer', ''),
            'response_status': response_status,
            'duration_ms': round(duration * 1000, 2),
            'error': error
        }
        
        # Add to logs (in production, send to logging service)
        self.request_logs.append(log_entry)
        
        # Keep only recent logs
        if len(self.request_logs) > self.max_log_entries:
            self.request_logs = self.request_logs[-self.max_log_entries:]
        
        # Log to SQLite audit database
        event_type = "request"
        security_event = None
        
        if response_status == 403:
            event_type = "blocked_request"
            security_event = error or "Unauthorized access attempt"
        elif response_status == 429:
            event_type = "rate_limited"
            security_event = "Rate limit exceeded"
        elif response_status >= 500:
            event_type = "server_error"
        elif error:
            event_type = "error"
            security_event = error
        
        # Log to audit database
        try:
            get_audit_logger().log_event(
                event_type=event_type,
                client_ip=client_ip,
                method=request.method,
                path=str(request.url.path),
                status_code=response_status,
                user_agent=request.headers.get('user-agent'),
                origin=request.headers.get('origin'),
                referer=request.headers.get('referer'),
                error_message=error,
                duration_ms=round(duration * 1000, 2),
                security_event=security_event,
                metadata={
                    'query_params': dict(request.query_params),
                    'has_internal_key': bool(request.headers.get('x-internal-key')),
                    'has_admin_key': bool(request.headers.get('x-admin-key'))
                }
            )
        except Exception as e:
            logger.warning(f"Failed to write audit log: {e}")
        
        # Update statistics
        self.stats['total_requests'] += 1
        if response_status == 429:
            self.stats['rate_limited_requests'] += 1
        elif response_status == 403:
            self.stats['blocked_requests'] += 1
        elif response_status == 403 and error and 'permission' in error.lower():
            self.stats['permission_errors'] += 1
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else 'unknown'
    
    def get_security_stats(self) -> Dict:
        """Get security statistics."""
        uptime = datetime.utcnow() - self.stats['start_time']
        
        return {
            **self.stats,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime),
            'blocked_ips_count': len(self.blocked_ips),
            'active_rate_limits': len(self.rate_limit_storage),
            'recent_logs_count': len(self.request_logs)
        }
    
    def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent request logs."""
        return self.request_logs[-limit:]
    
    def get_audit_logs(self, limit: int = 100, **filters) -> List[Dict]:
        """Get audit logs from SQLite database."""
        try:
            return get_audit_logger().get_recent_events(limit=limit, **filters)
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []
    
    def get_audit_statistics(self, days: int = 7) -> Dict:
        """Get security statistics from audit database."""
        try:
            return get_audit_logger().get_security_statistics(days=days)
        except Exception as e:
            logger.error(f"Failed to get audit statistics: {e}")
            return {}

# Global security manager instance (lazy initialization to prevent import-time failures)
_security_manager_instance = None

def get_security_manager(config=None) -> SecurityManager:
    """Get or create the global security manager instance."""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = SecurityManager(config)
    return _security_manager_instance

async def security_middleware(request: Request, call_next) -> JSONResponse:
    """Security middleware for all requests."""
    import os
    
    # TEMPORARY: Skip all security checks for debugging
    return await call_next(request)
    
    # Internal CLI bypass - must be at the very top before any other checks
    INTERNAL_CLI_KEY = os.getenv("INTERNAL_API_KEY", "DISABLED")
    if (
        request.headers.get("x-internal-key") == INTERNAL_CLI_KEY
        and INTERNAL_CLI_KEY != "DISABLED"
    ):
        return await call_next(request)  # allow trusted CLI access
    
    start_time = time.time()
    security_mgr = get_security_manager()
    client_ip = security_mgr.get_client_ip(request)
    
    try:
        # Skip security checks for health, docs, and root endpoints
        if request.url.path in ['/', '/health', '/docs', '/redoc', '/openapi.json', '/openapi-gpt.json', '/system/info', '/security/info', '/debug/env']:
            response = await call_next(request)
            duration = time.time() - start_time
            security_mgr.log_request(request, response.status_code, duration)
            return response
        
        # Check if IP is blocked
        if security_mgr.is_ip_blocked(client_ip):
            security_mgr.stats['blocked_requests'] += 1
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ServiceResponse.error_response(
                    error="IP address is blocked due to security violations"
                ).to_dict()
            )
        
        # Validate origin (CORS protection)
        if not security_mgr.validate_origin(request):
            logger.warning(f"Blocked request from unauthorized origin: {request.headers.get('origin', 'unknown')} (IP: {client_ip})")
            security_mgr.stats['blocked_requests'] += 1
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ServiceResponse.error_response(
                    error="Unauthorized origin. This API is restricted to authorized domains."
                ).to_dict()
            )
        
        # Validate internal API key for API endpoints
        if request.url.path.startswith('/api/'):
            if not security_mgr.validate_internal_key(request):
                logger.warning(f"Blocked request without valid internal key from IP: {client_ip}") 
                security_mgr.stats['blocked_requests'] += 1
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content=ServiceResponse.error_response(
                        error="Missing or invalid internal API key. Include 'x-internal-key' header."
                    ).to_dict()
                )
        
        # Check rate limits
        rate_limit_ok, rate_limit_error = security_mgr.check_rate_limit(client_ip)
        if not rate_limit_ok:
            logger.warning(f"Rate limit exceeded for IP: {client_ip} - {rate_limit_error}")
            security_mgr.stats['rate_limited_requests'] += 1
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=ServiceResponse.error_response(
                    error=rate_limit_error
                ).to_dict(),
                headers={"Retry-After": "60"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Log successful request
        duration = time.time() - start_time
        security_mgr.log_request(request, response.status_code, duration)
        
        return response
        
    except Exception as e:
        # Log error
        duration = time.time() - start_time
        security_mgr.log_request(request, 500, duration, str(e))
        
        # Return error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ServiceResponse.error_response(
                error="Internal server error"
            ).to_dict()
        )

