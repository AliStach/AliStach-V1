"""Monitoring and metrics collection service for production observability."""

import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Any, Dict, Deque, List
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single request."""
    endpoint: str
    response_time_ms: float
    cache_hit: bool
    api_calls_made: int
    timestamp: datetime
    request_id: str
    status_code: int = 200
    error_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'endpoint': self.endpoint,
            'response_time_ms': self.response_time_ms,
            'cache_hit': self.cache_hit,
            'api_calls_made': self.api_calls_made,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id,
            'status_code': self.status_code,
            'error_type': self.error_type
        }

@dataclass
class AggregatedStats:
    """Aggregated statistics over a time window."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Response time statistics
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    # Error tracking
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Endpoint statistics
    requests_by_endpoint: Dict[str, int] = field(default_factory=dict)
    
    @property
    def avg_response_time(self) -> float:
        """Calculate average response time."""
        if self.total_requests == 0:
            return 0.0
        return self.total_response_time / self.total_requests
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return (self.cache_hits / total_cache_requests) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        return 100.0 - self.success_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': round(self.success_rate, 2),
            'error_rate': round(self.error_rate, 2),
            'total_api_calls': self.total_api_calls,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_rate': round(self.cache_hit_rate, 2),
            'response_time': {
                'avg_ms': round(self.avg_response_time, 2),
                'min_ms': round(self.min_response_time, 2) if self.min_response_time != float('inf') else 0,
                'max_ms': round(self.max_response_time, 2)
            },
            'errors_by_type': self.errors_by_type,
            'requests_by_endpoint': self.requests_by_endpoint
        }

class MonitoringService:
    """
    Centralized monitoring and metrics collection service.
    
    Tracks performance metrics, aggregates statistics, and provides
    observability into system behavior for production operations.
    """
    
    def __init__(self, buffer_size: int = 1000, slow_request_threshold_ms: float = 3000) -> None:
        """
        Initialize monitoring service.
        
        Args:
            buffer_size: Maximum number of recent metrics to keep in memory
            slow_request_threshold_ms: Threshold for logging slow requests
        """
        self.buffer_size: int = buffer_size
        self.slow_request_threshold_ms: float = slow_request_threshold_ms
        
        # Recent metrics buffer (circular buffer)
        self.metrics_buffer: Deque[PerformanceMetrics] = deque(maxlen=buffer_size)
        
        # Aggregated statistics
        self.stats: AggregatedStats = AggregatedStats()
        
        # Service start time
        self.start_time: datetime = datetime.utcnow()
        
        # Percentile tracking (for p50, p95, p99)
        self.response_times: Deque[float] = deque(maxlen=buffer_size)
        
        logger.info(f"Monitoring service initialized with buffer_size={buffer_size}, slow_threshold={slow_request_threshold_ms}ms")
    
    def record_request(self, metrics: PerformanceMetrics) -> None:
        """
        Record request metrics and update aggregated statistics.
        
        Args:
            metrics: Performance metrics for the request
        """
        # Add to buffer
        self.metrics_buffer.append(metrics)
        self.response_times.append(metrics.response_time_ms)
        
        # Update aggregated stats
        self.stats.total_requests += 1
        
        if metrics.status_code < 400:
            self.stats.successful_requests += 1
        else:
            self.stats.failed_requests += 1
            
            # Track error types
            if metrics.error_type:
                self.stats.errors_by_type[metrics.error_type] = \
                    self.stats.errors_by_type.get(metrics.error_type, 0) + 1
        
        # Update API call stats
        self.stats.total_api_calls += metrics.api_calls_made
        
        # Update cache stats
        if metrics.cache_hit:
            self.stats.cache_hits += 1
        else:
            self.stats.cache_misses += 1
        
        # Update response time stats
        self.stats.total_response_time += metrics.response_time_ms
        self.stats.min_response_time = min(self.stats.min_response_time, metrics.response_time_ms)
        self.stats.max_response_time = max(self.stats.max_response_time, metrics.response_time_ms)
        
        # Update endpoint stats
        self.stats.requests_by_endpoint[metrics.endpoint] = \
            self.stats.requests_by_endpoint.get(metrics.endpoint, 0) + 1
        
        # Log slow requests
        if metrics.response_time_ms > self.slow_request_threshold_ms:
            logger.warning(
                f"Slow request detected: {metrics.endpoint}",
                extra={
                    'request_id': metrics.request_id,
                    'endpoint': metrics.endpoint,
                    'response_time_ms': metrics.response_time_ms,
                    'cache_hit': metrics.cache_hit,
                    'api_calls_made': metrics.api_calls_made
                }
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current aggregated statistics.
        
        Returns:
            Dictionary containing all statistics
        """
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        # Calculate percentiles
        percentiles = self._calculate_percentiles()
        
        return {
            'service': {
                'uptime_seconds': round(uptime_seconds, 2),
                'uptime_human': self._format_uptime(uptime_seconds),
                'start_time': self.start_time.isoformat()
            },
            'requests': {
                'total': self.stats.total_requests,
                'successful': self.stats.successful_requests,
                'failed': self.stats.failed_requests,
                'success_rate': round(self.stats.success_rate, 2),
                'error_rate': round(self.stats.error_rate, 2),
                'requests_per_second': round(self.stats.total_requests / uptime_seconds, 2) if uptime_seconds > 0 else 0
            },
            'api_calls': {
                'total': self.stats.total_api_calls,
                'calls_per_request': round(self.stats.total_api_calls / self.stats.total_requests, 2) if self.stats.total_requests > 0 else 0
            },
            'cache': {
                'hits': self.stats.cache_hits,
                'misses': self.stats.cache_misses,
                'hit_rate': round(self.stats.cache_hit_rate, 2)
            },
            'response_time': {
                'avg_ms': round(self.stats.avg_response_time, 2),
                'min_ms': round(self.stats.min_response_time, 2) if self.stats.min_response_time != float('inf') else 0,
                'max_ms': round(self.stats.max_response_time, 2),
                'p50_ms': round(percentiles['p50'], 2),
                'p95_ms': round(percentiles['p95'], 2),
                'p99_ms': round(percentiles['p99'], 2)
            },
            'errors': {
                'by_type': self.stats.errors_by_type,
                'total': self.stats.failed_requests
            },
            'endpoints': {
                'by_endpoint': self.stats.requests_by_endpoint,
                'total_endpoints': len(self.stats.requests_by_endpoint)
            },
            'buffer': {
                'size': len(self.metrics_buffer),
                'max_size': self.buffer_size
            }
        }
    
    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent request metrics.
        
        Args:
            limit: Maximum number of recent requests to return
            
        Returns:
            List of recent request metrics
        """
        recent = list(self.metrics_buffer)[-limit:]
        return [m.to_dict() for m in recent]
    
    def get_slow_requests(self, threshold_ms: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get requests that exceeded the slow request threshold.
        
        Args:
            threshold_ms: Optional custom threshold (uses default if not provided)
            
        Returns:
            List of slow request metrics
        """
        threshold = threshold_ms or self.slow_request_threshold_ms
        slow_requests = [
            m for m in self.metrics_buffer
            if m.response_time_ms > threshold
        ]
        return [m.to_dict() for m in slow_requests]
    
    def reset_stats(self) -> None:
        """Reset all statistics (useful for testing or periodic resets)."""
        self.stats = AggregatedStats()
        self.metrics_buffer.clear()
        self.response_times.clear()
        self.start_time = datetime.utcnow()
        logger.info("Monitoring statistics reset")
    
    def _calculate_percentiles(self) -> Dict[str, float]:
        """
        Calculate response time percentiles.
        
        Returns:
            Dictionary with p50, p95, p99 percentiles
        """
        if not self.response_times:
            return {'p50': 0.0, 'p95': 0.0, 'p99': 0.0}
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        return {
            'p50': sorted_times[int(n * 0.50)] if n > 0 else 0.0,
            'p95': sorted_times[int(n * 0.95)] if n > 0 else 0.0,
            'p99': sorted_times[int(n * 0.99)] if n > 0 else 0.0
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Format uptime in human-readable format.
        
        Args:
            seconds: Uptime in seconds
            
        Returns:
            Formatted uptime string
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)

# Global monitoring service instance
_monitoring_service: Optional[MonitoringService] = None

def get_monitoring_service() -> MonitoringService:
    """
    Get or create the global monitoring service instance.
    
    Returns:
        MonitoringService instance
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service

def reset_monitoring_service() -> None:
    """Reset the global monitoring service (useful for testing)."""
    global _monitoring_service
    _monitoring_service = None
