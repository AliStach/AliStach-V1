"""Unit tests for EnhancedRateLimiter."""

import pytest
import time
from src.middleware.rate_limiter import (
    RateLimitConfig,
    TokenBucket,
    SlidingWindowCounter,
    EnhancedRateLimiter,
    get_rate_limiter,
    reset_rate_limiter
)


class TestRateLimitConfig:
    """Test RateLimitConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = RateLimitConfig()
        
        assert config.rate_per_second == 5.0
        assert config.burst_size == 10
        assert config.rate_per_minute == 60
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = RateLimitConfig(
            rate_per_second=10.0,
            burst_size=20,
            rate_per_minute=120
        )
        
        assert config.rate_per_second == 10.0
        assert config.burst_size == 20
        assert config.rate_per_minute == 120
    
    def test_invalid_config(self):
        """Test invalid configuration raises error."""
        with pytest.raises(ValueError):
            RateLimitConfig(rate_per_second=0)
        
        with pytest.raises(ValueError):
            RateLimitConfig(burst_size=-1)


class TestTokenBucket:
    """Test TokenBucket class."""
    
    def test_initialization(self):
        """Test token bucket initialization."""
        bucket = TokenBucket(rate=5.0, capacity=10)
        
        assert bucket.rate == 5.0
        assert bucket.capacity == 10
        assert bucket.tokens == 10.0
    
    def test_consume_tokens(self):
        """Test consuming tokens."""
        bucket = TokenBucket(rate=5.0, capacity=10)
        
        assert bucket.consume(1) is True
        assert bucket.tokens == 9.0
        
        assert bucket.consume(5) is True
        assert bucket.tokens == 4.0
    
    def test_consume_insufficient_tokens(self):
        """Test consuming when insufficient tokens."""
        bucket = TokenBucket(rate=5.0, capacity=10)
        
        assert bucket.consume(11) is False
        assert bucket.tokens == 10.0  # No tokens consumed
    
    def test_token_refill(self):
        """Test token refill over time."""
        bucket = TokenBucket(rate=10.0, capacity=10)
        
        # Consume all tokens
        bucket.consume(10)
        assert bucket.tokens == 0.0
        
        # Wait for refill
        time.sleep(0.5)
        
        # Should have ~5 tokens (10 tokens/sec * 0.5 sec)
        assert bucket.consume(1) is True
    
    def test_get_retry_after(self):
        """Test retry-after calculation."""
        bucket = TokenBucket(rate=10.0, capacity=10)
        
        # Consume all tokens
        bucket.consume(10)
        
        retry_after = bucket.get_retry_after()
        
        # Should need ~0.1 seconds for 1 token at 10 tokens/sec
        assert 0.05 <= retry_after <= 0.15


class TestSlidingWindowCounter:
    """Test SlidingWindowCounter class."""
    
    def test_initialization(self):
        """Test sliding window initialization."""
        window = SlidingWindowCounter(limit=10, window_seconds=60)
        
        assert window.limit == 10
        assert window.window_seconds == 60
        assert len(window.timestamps) == 0
    
    def test_is_allowed(self):
        """Test request allowance."""
        window = SlidingWindowCounter(limit=5, window_seconds=60)
        
        # First 5 requests should be allowed
        for i in range(5):
            assert window.is_allowed() is True
        
        # 6th request should be blocked
        assert window.is_allowed() is False
    
    def test_window_expiration(self):
        """Test that old requests expire."""
        window = SlidingWindowCounter(limit=2, window_seconds=1)
        
        # Use up limit
        assert window.is_allowed() is True
        assert window.is_allowed() is True
        assert window.is_allowed() is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        assert window.is_allowed() is True
    
    def test_get_retry_after(self):
        """Test retry-after calculation."""
        window = SlidingWindowCounter(limit=2, window_seconds=2)
        
        # Use up limit
        window.is_allowed()
        window.is_allowed()
        
        retry_after = window.get_retry_after()
        
        # Should be close to window_seconds
        assert 0 <= retry_after <= 2.1


class TestEnhancedRateLimiter:
    """Test EnhancedRateLimiter class."""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter for testing."""
        config = RateLimitConfig(
            rate_per_second=10.0,
            burst_size=20,
            rate_per_minute=100
        )
        return EnhancedRateLimiter(config)
    
    def test_initialization(self, rate_limiter):
        """Test rate limiter initialization."""
        assert rate_limiter.config.rate_per_second == 10.0
        assert rate_limiter.metrics['total_requests'] == 0
    
    def test_is_allowed_first_request(self, rate_limiter):
        """Test first request is allowed."""
        is_allowed, retry_after = rate_limiter.is_allowed("client-1")
        
        assert is_allowed is True
        assert retry_after == 0.0
        assert rate_limiter.metrics['allowed_requests'] == 1
    
    def test_is_allowed_multiple_clients(self, rate_limiter):
        """Test multiple clients tracked separately."""
        # Client 1
        is_allowed, _ = rate_limiter.is_allowed("client-1")
        assert is_allowed is True
        
        # Client 2
        is_allowed, _ = rate_limiter.is_allowed("client-2")
        assert is_allowed is True
        
        assert rate_limiter.metrics['unique_ips'] == 2
    
    def test_rate_limiting_burst(self, rate_limiter):
        """Test burst rate limiting."""
        client_id = "client-1"
        
        # Should allow burst_size requests
        for i in range(20):
            is_allowed, _ = rate_limiter.is_allowed(client_id)
            assert is_allowed is True
        
        # Next request should be rate limited
        is_allowed, retry_after = rate_limiter.is_allowed(client_id)
        assert is_allowed is False
        assert retry_after > 0
    
    def test_get_status(self, rate_limiter):
        """Test getting rate limit status."""
        client_id = "client-1"
        
        # Make some requests
        for i in range(5):
            rate_limiter.is_allowed(client_id)
        
        status = rate_limiter.get_status(client_id)
        
        assert 'tokens_available' in status
        assert 'requests_in_window' in status
        assert status['requests_in_window'] == 5
    
    def test_get_metrics(self, rate_limiter):
        """Test getting metrics."""
        # Make some requests
        for i in range(10):
            rate_limiter.is_allowed(f"client-{i}")
        
        metrics = rate_limiter.get_metrics()
        
        assert metrics['total_requests'] == 10
        assert metrics['allowed_requests'] == 10
        assert metrics['blocked_requests'] == 0
    
    def test_reset_client(self, rate_limiter):
        """Test resetting client rate limits."""
        client_id = "client-1"
        
        # Use up some tokens
        for i in range(10):
            rate_limiter.is_allowed(client_id)
        
        # Reset
        rate_limiter.reset_client(client_id)
        
        # Should have full tokens again
        status = rate_limiter.get_status(client_id)
        assert status['tokens_available'] == rate_limiter.config.burst_size


class TestGlobalRateLimiter:
    """Test global rate limiter singleton."""
    
    def test_get_rate_limiter(self):
        """Test getting global rate limiter."""
        reset_rate_limiter()
        
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        
        assert limiter1 is limiter2
    
    def test_reset_rate_limiter(self):
        """Test resetting global rate limiter."""
        limiter1 = get_rate_limiter()
        reset_rate_limiter()
        limiter2 = get_rate_limiter()
        
        assert limiter1 is not limiter2
