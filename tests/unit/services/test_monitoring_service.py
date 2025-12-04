"""Unit tests for MonitoringService."""

import pytest
from datetime import datetime
from src.services.monitoring_service import (
    MonitoringService,
    PerformanceMetrics,
    AggregatedStats,
    get_monitoring_service,
    reset_monitoring_service
)


class TestPerformanceMetrics:
    """Test PerformanceMetrics dataclass."""
    
    def test_create_metrics(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            endpoint="/api/products/smart-search",
            response_time_ms=1234.56,
            cache_hit=True,
            api_calls_made=0,
            timestamp=datetime.utcnow(),
            request_id="test-123"
        )
        
        assert metrics.endpoint == "/api/products/smart-search"
        assert metrics.response_time_ms == 1234.56
        assert metrics.cache_hit is True
        assert metrics.status_code == 200
    
    def test_to_dict(self):
        """Test metrics serialization."""
        now = datetime.utcnow()
        metrics = PerformanceMetrics(
            endpoint="/test",
            response_time_ms=100.0,
            cache_hit=False,
            api_calls_made=1,
            timestamp=now,
            request_id="req-1"
        )
        
        result = metrics.to_dict()
        
        assert result['endpoint'] == "/test"
        assert result['response_time_ms'] == 100.0
        assert result['cache_hit'] is False
        assert result['request_id'] == "req-1"


class TestAggregatedStats:
    """Test AggregatedStats dataclass."""
    
    def test_initial_stats(self):
        """Test initial statistics."""
        stats = AggregatedStats()
        
        assert stats.total_requests == 0
        assert stats.avg_response_time == 0.0
        assert stats.cache_hit_rate == 0.0
        assert stats.success_rate == 100.0
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        stats = AggregatedStats()
        stats.cache_hits = 70
        stats.cache_misses = 30
        
        assert stats.cache_hit_rate == 70.0
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = AggregatedStats()
        stats.total_requests = 100
        stats.successful_requests = 95
        stats.failed_requests = 5
        
        assert stats.success_rate == 95.0
        assert stats.error_rate == 5.0


class TestMonitoringService:
    """Test MonitoringService class."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create monitoring service for testing."""
        return MonitoringService(buffer_size=100, slow_request_threshold_ms=1000)
    
    def test_initialization(self, monitoring_service):
        """Test service initialization."""
        assert monitoring_service.buffer_size == 100
        assert monitoring_service.slow_request_threshold_ms == 1000
        assert len(monitoring_service.metrics_buffer) == 0
    
    def test_record_request(self, monitoring_service):
        """Test recording a request."""
        metrics = PerformanceMetrics(
            endpoint="/test",
            response_time_ms=500.0,
            cache_hit=True,
            api_calls_made=0,
            timestamp=datetime.utcnow(),
            request_id="req-1"
        )
        
        monitoring_service.record_request(metrics)
        
        assert len(monitoring_service.metrics_buffer) == 1
        assert monitoring_service.stats.total_requests == 1
        assert monitoring_service.stats.successful_requests == 1
        assert monitoring_service.stats.cache_hits == 1
    
    def test_record_failed_request(self, monitoring_service):
        """Test recording a failed request."""
        metrics = PerformanceMetrics(
            endpoint="/test",
            response_time_ms=500.0,
            cache_hit=False,
            api_calls_made=1,
            timestamp=datetime.utcnow(),
            request_id="req-1",
            status_code=500,
            error_type="APIError"
        )
        
        monitoring_service.record_request(metrics)
        
        assert monitoring_service.stats.failed_requests == 1
        assert monitoring_service.stats.errors_by_type["APIError"] == 1
    
    def test_get_stats(self, monitoring_service):
        """Test getting statistics."""
        # Record some requests
        for i in range(10):
            metrics = PerformanceMetrics(
                endpoint="/test",
                response_time_ms=100.0 * (i + 1),
                cache_hit=i % 2 == 0,
                api_calls_made=1,
                timestamp=datetime.utcnow(),
                request_id=f"req-{i}"
            )
            monitoring_service.record_request(metrics)
        
        stats = monitoring_service.get_stats()
        
        assert stats['requests']['total'] == 10
        assert stats['cache']['hits'] == 5
        assert stats['cache']['misses'] == 5
        assert stats['cache']['hit_rate'] == 50.0
    
    def test_get_recent_requests(self, monitoring_service):
        """Test getting recent requests."""
        # Record requests
        for i in range(5):
            metrics = PerformanceMetrics(
                endpoint="/test",
                response_time_ms=100.0,
                cache_hit=True,
                api_calls_made=0,
                timestamp=datetime.utcnow(),
                request_id=f"req-{i}"
            )
            monitoring_service.record_request(metrics)
        
        recent = monitoring_service.get_recent_requests(limit=3)
        
        assert len(recent) == 3
    
    def test_get_slow_requests(self, monitoring_service):
        """Test getting slow requests."""
        # Record fast and slow requests
        for i in range(5):
            metrics = PerformanceMetrics(
                endpoint="/test",
                response_time_ms=500.0 if i < 3 else 2000.0,
                cache_hit=True,
                api_calls_made=0,
                timestamp=datetime.utcnow(),
                request_id=f"req-{i}"
            )
            monitoring_service.record_request(metrics)
        
        slow = monitoring_service.get_slow_requests()
        
        assert len(slow) == 2  # 2 requests > 1000ms
    
    def test_reset_stats(self, monitoring_service):
        """Test resetting statistics."""
        # Record some requests
        metrics = PerformanceMetrics(
            endpoint="/test",
            response_time_ms=100.0,
            cache_hit=True,
            api_calls_made=0,
            timestamp=datetime.utcnow(),
            request_id="req-1"
        )
        monitoring_service.record_request(metrics)
        
        assert monitoring_service.stats.total_requests == 1
        
        # Reset
        monitoring_service.reset_stats()
        
        assert monitoring_service.stats.total_requests == 0
        assert len(monitoring_service.metrics_buffer) == 0
    
    def test_buffer_size_limit(self, monitoring_service):
        """Test that buffer respects size limit."""
        # Record more than buffer size
        for i in range(150):
            metrics = PerformanceMetrics(
                endpoint="/test",
                response_time_ms=100.0,
                cache_hit=True,
                api_calls_made=0,
                timestamp=datetime.utcnow(),
                request_id=f"req-{i}"
            )
            monitoring_service.record_request(metrics)
        
        # Buffer should be limited to 100
        assert len(monitoring_service.metrics_buffer) == 100


class TestGlobalMonitoringService:
    """Test global monitoring service singleton."""
    
    def test_get_monitoring_service(self):
        """Test getting global monitoring service."""
        reset_monitoring_service()
        
        service1 = get_monitoring_service()
        service2 = get_monitoring_service()
        
        assert service1 is service2  # Same instance
    
    def test_reset_monitoring_service(self):
        """Test resetting global monitoring service."""
        service1 = get_monitoring_service()
        reset_monitoring_service()
        service2 = get_monitoring_service()
        
        assert service1 is not service2  # Different instances
