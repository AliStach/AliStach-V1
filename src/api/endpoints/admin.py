"""Admin endpoints for monitoring and security management."""

import os
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from ...middleware.security import get_security_manager, SecurityManager
from ...services.aliexpress_service import AliExpressService
from ...models.responses import ServiceResponse

router = APIRouter()

# Admin authentication
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'admin-secret-key-change-in-production')

def verify_admin_key(x_admin_key: Optional[str] = Header(None)) -> bool:
    """Verify admin API key."""
    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing admin API key. Include 'x-admin-key' header."
        )
    return True

def get_service() -> AliExpressService:
    """Dependency to get the AliExpress service instance."""
    from ..main import service_instance
    if service_instance is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return service_instance

@router.get("/admin/health")
async def admin_health_check(
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager),
    service: AliExpressService = Depends(get_service)
):
    """
    Admin-only health check with detailed system information.
    
    Requires: x-admin-key header
    """
    try:
        # Get security statistics
        security_stats = security.get_security_stats()
        
        # Get service information
        service_info = service.get_service_info()
        
        # System health data
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime": {
                "seconds": security_stats['uptime_seconds'],
                "human_readable": security_stats['uptime_human']
            },
            "api_statistics": {
                "total_requests": security_stats['total_requests'],
                "blocked_requests": security_stats['blocked_requests'],
                "rate_limited_requests": security_stats['rate_limited_requests'],
                "permission_errors": security_stats['permission_errors'],
                "success_rate": round(
                    (security_stats['total_requests'] - security_stats['blocked_requests'] - security_stats['rate_limited_requests']) 
                    / max(security_stats['total_requests'], 1) * 100, 2
                ) if security_stats['total_requests'] > 0 else 100
            },
            "security": {
                "blocked_ips_count": security_stats['blocked_ips_count'],
                "active_rate_limits": security_stats['active_rate_limits'],
                "recent_logs_count": security_stats['recent_logs_count']
            },
            "service_info": service_info,
            "last_failed_request": None  # Will be populated if we track this
        }
        
        # Find last failed request
        recent_logs = security.get_recent_logs(100)
        failed_logs = [log for log in recent_logs if log['response_status'] >= 400]
        if failed_logs:
            health_data["last_failed_request"] = {
                "timestamp": failed_logs[-1]['timestamp'],
                "status": failed_logs[-1]['response_status'],
                "path": failed_logs[-1]['path'],
                "error": failed_logs[-1].get('error', 'Unknown error')
            }
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=health_data
            ).to_dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Admin health check failed: {str(e)}"
            ).to_dict()
        )

@router.get("/admin/logs")
async def get_request_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of recent logs to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    client_ip: Optional[str] = Query(None, description="Filter by client IP"),
    status_code: Optional[int] = Query(None, description="Filter by status code"),
    use_audit_db: bool = Query(True, description="Use SQLite audit database"),
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager)
):
    """
    Get recent request logs for monitoring and debugging.
    
    Requires: x-admin-key header
    
    Uses SQLite audit database by default for persistent logging.
    """
    try:
        if use_audit_db:
            # Get logs from SQLite audit database
            logs = security.get_audit_logs(
                limit=limit,
                event_type=event_type,
                client_ip=client_ip,
                status_code=status_code
            )
        else:
            # Get logs from in-memory storage
            logs = security.get_recent_logs(limit)
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "logs": logs,
                    "total_returned": len(logs),
                    "limit": limit,
                    "source": "audit_database" if use_audit_db else "memory"
                },
                metadata={
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "filters": {
                        "event_type": event_type,
                        "client_ip": client_ip,
                        "status_code": status_code
                    }
                }
            ).to_dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to retrieve logs: {str(e)}"
            ).to_dict()
        )

@router.get("/admin/security/stats")
async def get_security_statistics(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager)
):
    """
    Get detailed security statistics and metrics from audit database.
    
    Requires: x-admin-key header
    """
    try:
        # Get in-memory stats
        memory_stats = security.get_security_stats()
        
        # Get audit database stats
        audit_stats = security.get_audit_statistics(days=days)
        
        # Combine stats
        combined_stats = {
            **memory_stats,
            "audit_database": audit_stats,
            "analysis_period_days": days
        }
        
        # Calculate additional metrics
        if memory_stats['total_requests'] > 0:
            combined_stats['block_rate'] = round(memory_stats['blocked_requests'] / memory_stats['total_requests'] * 100, 2)
            combined_stats['rate_limit_rate'] = round(memory_stats['rate_limited_requests'] / memory_stats['total_requests'] * 100, 2)
        else:
            combined_stats['block_rate'] = 0
            combined_stats['rate_limit_rate'] = 0
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=combined_stats
            ).to_dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get security stats: {str(e)}"
            ).to_dict()
        )

@router.post("/admin/security/block-ip")
async def block_ip_address(
    ip_address: str = Query(..., description="IP address to block"),
    reason: str = Query("Manual block via admin", description="Reason for blocking"),
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager)
):
    """
    Block an IP address manually.
    
    Requires: x-admin-key header
    """
    try:
        security.block_ip(ip_address, reason)
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "blocked_ip": ip_address,
                    "reason": reason,
                    "blocked_at": datetime.utcnow().isoformat() + "Z"
                }
            ).to_dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to block IP: {str(e)}"
            ).to_dict()
        )

@router.delete("/admin/security/unblock-ip")
async def unblock_ip_address(
    ip_address: str = Query(..., description="IP address to unblock"),
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager)
):
    """
    Unblock an IP address.
    
    Requires: x-admin-key header
    """
    try:
        if ip_address in security.blocked_ips:
            security.blocked_ips.remove(ip_address)
            
            return JSONResponse(
                content=ServiceResponse.success_response(
                    data={
                        "unblocked_ip": ip_address,
                        "unblocked_at": datetime.utcnow().isoformat() + "Z"
                    }
                ).to_dict()
            )
        else:
            return JSONResponse(
                status_code=404,
                content=ServiceResponse.error_response(
                    error=f"IP address {ip_address} is not currently blocked"
                ).to_dict()
            )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to unblock IP: {str(e)}"
            ).to_dict()
        )

@router.get("/admin/security/blocked-ips")
async def get_blocked_ips(
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager)
):
    """
    Get list of currently blocked IP addresses.
    
    Requires: x-admin-key header
    """
    try:
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "blocked_ips": list(security.blocked_ips),
                    "total_blocked": len(security.blocked_ips)
                }
            ).to_dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get blocked IPs: {str(e)}"
            ).to_dict()
        )

@router.post("/admin/security/clear-rate-limits")
async def clear_rate_limits(
    ip_address: Optional[str] = Query(None, description="Specific IP to clear (optional)"),
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager)
):
    """
    Clear rate limit counters for all IPs or a specific IP.
    
    Requires: x-admin-key header
    """
    try:
        if ip_address:
            if ip_address in security.rate_limit_storage:
                del security.rate_limit_storage[ip_address]
                message = f"Rate limits cleared for IP: {ip_address}"
            else:
                message = f"No rate limits found for IP: {ip_address}"
        else:
            security.rate_limit_storage.clear()
            message = "All rate limits cleared"
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "message": message,
                    "cleared_at": datetime.utcnow().isoformat() + "Z"
                }
            ).to_dict()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to clear rate limits: {str(e)}"
            ).to_dict()
        )