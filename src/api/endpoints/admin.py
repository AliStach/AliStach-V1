"""Admin endpoints for monitoring and security management."""

import os
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from ...middleware.security import get_security_manager, SecurityManager
from ...services.aliexpress_service import AliExpressService
from ...services.monitoring_service import get_monitoring_service, MonitoringService
from ...models.responses import ServiceResponse

router: APIRouter = APIRouter()

# Admin authentication
ADMIN_API_KEY: str = os.getenv('ADMIN_API_KEY', 'admin-secret-key-change-in-production')

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
    from ..main import get_service as main_get_service
    return main_get_service()

@router.get("/admin/health")
async def admin_health_check(
    _: bool = Depends(verify_admin_key),
    security: SecurityManager = Depends(get_security_manager),
    service: AliExpressService = Depends(get_service)
) -> JSONResponse:
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
) -> JSONResponse:
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
) -> JSONResponse:
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
) -> JSONResponse:
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
) -> JSONResponse:
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
) -> JSONResponse:
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
) -> JSONResponse:
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

# ============================================================================
# Monitoring and Metrics Endpoints
# ============================================================================

@router.get("/admin/monitoring/metrics")
async def get_monitoring_metrics(
    _: bool = Depends(verify_admin_key),
    monitoring: MonitoringService = Depends(get_monitoring_service)
) -> JSONResponse:
    """
    Get comprehensive performance metrics and statistics.
    
    Requires: x-admin-key header
    
    Returns:
        - Service uptime
        - Request statistics (total, success rate, error rate)
        - API call statistics
        - Cache performance (hit rate)
        - Response time statistics (avg, min, max, percentiles)
        - Error breakdown by type
        - Endpoint usage statistics
    """
    try:
        stats = monitoring.get_stats()
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=stats,
                metadata={
                    "description": "System performance metrics and statistics",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get monitoring metrics: {str(e)}"
            ).to_dict()
        )

@router.get("/admin/monitoring/recent-requests")
async def get_recent_requests(
    _: bool = Depends(verify_admin_key),
    limit: int = Query(100, ge=1, le=1000, description="Number of recent requests to return"),
    monitoring: MonitoringService = Depends(get_monitoring_service)
) -> JSONResponse:
    """
    Get recent request metrics for debugging and analysis.
    
    Requires: x-admin-key header
    
    Args:
        limit: Maximum number of recent requests to return (1-1000)
    
    Returns:
        List of recent request metrics with:
        - Endpoint
        - Response time
        - Cache hit status
        - API calls made
        - Status code
        - Error type (if any)
        - Request ID
        - Timestamp
    """
    try:
        recent_requests = monitoring.get_recent_requests(limit=limit)
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "requests": recent_requests,
                    "count": len(recent_requests),
                    "limit": limit
                },
                metadata={
                    "description": "Recent request metrics",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get recent requests: {str(e)}"
            ).to_dict()
        )

@router.get("/admin/monitoring/slow-requests")
async def get_slow_requests(
    _: bool = Depends(verify_admin_key),
    threshold_ms: Optional[float] = Query(None, description="Custom threshold in milliseconds"),
    monitoring: MonitoringService = Depends(get_monitoring_service)
) -> JSONResponse:
    """
    Get requests that exceeded the slow request threshold.
    
    Requires: x-admin-key header
    
    Args:
        threshold_ms: Optional custom threshold (uses default 3000ms if not provided)
    
    Returns:
        List of slow requests with full metrics
    """
    try:
        slow_requests = monitoring.get_slow_requests(threshold_ms=threshold_ms)
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={
                    "slow_requests": slow_requests,
                    "count": len(slow_requests),
                    "threshold_ms": threshold_ms or monitoring.slow_request_threshold_ms
                },
                metadata={
                    "description": "Slow request metrics",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get slow requests: {str(e)}"
            ).to_dict()
        )

@router.post("/admin/monitoring/reset")
async def reset_monitoring_stats(
    _: bool = Depends(verify_admin_key),
    monitoring: MonitoringService = Depends(get_monitoring_service)
) -> JSONResponse:
    """
    Reset all monitoring statistics.
    
    Requires: x-admin-key header
    
    Warning: This will clear all accumulated metrics and statistics.
    Use with caution in production.
    """
    try:
        monitoring.reset_stats()
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data={"message": "Monitoring statistics reset successfully"},
                metadata={
                    "timestamp": datetime.utcnow().isoformat()
                }
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to reset monitoring stats: {str(e)}"
            ).to_dict()
        )

@router.get("/admin/monitoring/health")
async def get_monitoring_health(
    _: bool = Depends(verify_admin_key),
    monitoring: MonitoringService = Depends(get_monitoring_service)
) -> JSONResponse:
    """
    Get monitoring service health and status.
    
    Requires: x-admin-key header
    
    Returns:
        - Buffer utilization
        - Service uptime
        - Basic statistics
    """
    try:
        stats = monitoring.get_stats()
        
        health_data = {
            "status": "healthy",
            "uptime": stats['service']['uptime_human'],
            "buffer_utilization": {
                "current": len(monitoring.metrics_buffer),
                "max": monitoring.buffer_size,
                "percentage": round((len(monitoring.metrics_buffer) / monitoring.buffer_size) * 100, 2)
            },
            "metrics_tracked": {
                "total_requests": stats['requests']['total'],
                "total_api_calls": stats['api_calls']['total'],
                "cache_hit_rate": stats['cache']['hit_rate']
            }
        }
        
        return JSONResponse(
            content=ServiceResponse.success_response(
                data=health_data,
                metadata={
                    "timestamp": datetime.utcnow().isoformat()
                }
            ).to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ServiceResponse.error_response(
                error=f"Failed to get monitoring health: {str(e)}"
            ).to_dict()
        )
