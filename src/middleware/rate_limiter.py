"""Enhanced rate limiter with token bucket algorithm."""

import time
import logging
from collections import deque
from dataclasses import dataclass
from ..utils.logging_config import log_info, log_warning

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    rate_per_second: float = 5.0  # Tokens per second
    burst_size: int = 10  # Maximum burst capacity
    rate_per_minute: int = 60  # Maximum requests per minute
    
    def __post_init__(self):
        """Validate configuration."""
        if self.rate_per_second <= 0:
            raise ValueError("rate_per_second must be positive")
        if self.burst_size <= 0:
            raise ValueError("burst_size must be positive")
        if self.rate_per_minute <= 0:
            raise ValueError("rate_per_minute must be positive")

class TokenBucket:
    """
    Token bucket implementation for rate limiting.
    
    The token bucket algorithm allows for burst traffic while maintaining
    an average rate limit. Tokens are added at a constant rate, and each
    request consumes one token.
    """
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.
        
        Args:
            rate: Tokens added per second
            capacity: Maximum token capacity (burst size)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        now = time.time()
        
        # Refill tokens based on time elapsed
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
        
        # Try to consume tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def get_retry_after(self) -> float:
        """
        Calculate seconds until next token available.
        
        Returns:
            Seconds to wait
        """
        if self.tokens >= 1:
            return 0.0
        
        tokens_needed = 1 - self.tokens
        return tokens_needed / self.rate

class SlidingWindowCounter:
    """
    Sliding window counter for per-minute rate limiting.
    
    Maintains a sliding window of timestamps to enforce per-minute limits.
    """
    
    def __init__(self, limit: int, window_seconds: int = 60):
        """
        Initialize sliding window counter.
        
        Args:
            limit: Maximum requests in window
            window_seconds: Window size in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.timestamps = deque()
    
    def is_allowed(self) -> bool:
        """
        Check if request is allowed within the window.
        
        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        cutoff = now - self.window_seconds
        
        # Remove old timestamps
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        
        # Check if under limit
        if len(self.timestamps) < self.limit:
            self.timestamps.append(now)
            return True
        
        return False
    
    def get_retry_after(self) -> float:
        """
        Calculate seconds until oldest request expires.
        
        Returns:
            Seconds to wait
        """
        if not self.timestamps:
            return 0.0
        
        now = time.time()
        oldest = self.timestamps[0]
        wait_time = self.window_seconds - (now - oldest)
        
        return max(0.0, wait_time)

class EnhancedRateLimiter:
    """
    Enhanced rate limiter with token bucket and sliding window.
    
    Combines:
    - Token bucket for per-second rate limiting with burst support
    - Sliding window for per-minute rate limiting
    - Per-IP tracking
    - Metrics collection
    """
    
    def __init__(self, config: RateLimitConfig = None):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        
        # Per-IP rate limiters
        self.token_buckets: dict[str, TokenBucket] = {}
        self.sliding_windows: dict[str, SlidingWindowCounter] = {}
        
        # Metrics
        self.metrics = {
            'total_requests': 0,
            'allowed_requests': 0,
            'blocked_requests': 0,
            'unique_ips': 0
        }
        
        # Cleanup tracking
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5 minutes
        
        log_info(
            logger,
            "rate_limiter_initialized",
            rate_per_second=self.config.rate_per_second,
            burst_size=self.config.burst_size,
            rate_per_minute=self.config.rate_per_minute
        )
    
    def is_allowed(self, client_id: str) -> tuple[bool, float]:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier (usually IP address)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        self.metrics['total_requests'] += 1
        
        # Periodic cleanup of old entries
        self._cleanup_if_needed()
        
        # Get or create token bucket for this client
        if client_id not in self.token_buckets:
            self.token_buckets[client_id] = TokenBucket(
                self.config.rate_per_second,
                self.config.burst_size
            )
            self.sliding_windows[client_id] = SlidingWindowCounter(
                self.config.rate_per_minute
            )
            self.metrics['unique_ips'] += 1
        
        token_bucket = self.token_buckets[client_id]
        sliding_window = self.sliding_windows[client_id]
        
        # Check both rate limiters
        token_allowed = token_bucket.consume()
        window_allowed = sliding_window.is_allowed()
        
        if token_allowed and window_allowed:
            self.metrics['allowed_requests'] += 1
            return True, 0.0
        
        # Rate limited - calculate retry-after
        self.metrics['blocked_requests'] += 1
        
        retry_after = max(
            token_bucket.get_retry_after() if not token_allowed else 0.0,
            sliding_window.get_retry_after() if not window_allowed else 0.0
        )
        
        log_warning(
            logger,
            "rate_limit_exceeded",
            client_id=client_id,
            retry_after=retry_after,
            token_limited=not token_allowed,
            window_limited=not window_allowed
        )
        
        return False, retry_after
    
    def get_status(self, client_id: str) -> dict[str, any]:
        """
        Get rate limit status for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Dictionary with rate limit status
        """
        if client_id not in self.token_buckets:
            return {
                'tokens_available': self.config.burst_size,
                'requests_in_window': 0,
                'limit_per_second': self.config.rate_per_second,
                'limit_per_minute': self.config.rate_per_minute
            }
        
        token_bucket = self.token_buckets[client_id]
        sliding_window = self.sliding_windows[client_id]
        
        # Update tokens
        now = time.time()
        elapsed = now - token_bucket.last_update
        current_tokens = min(
            token_bucket.capacity,
            token_bucket.tokens + elapsed * token_bucket.rate
        )
        
        return {
            'tokens_available': int(current_tokens),
            'requests_in_window': len(sliding_window.timestamps),
            'limit_per_second': self.config.rate_per_second,
            'limit_per_minute': self.config.rate_per_minute,
            'burst_capacity': self.config.burst_size
        }
    
    def get_metrics(self) -> dict[str, any]:
        """
        Get rate limiter metrics.
        
        Returns:
            Dictionary with metrics
        """
        return {
            **self.metrics,
            'block_rate': round(
                (self.metrics['blocked_requests'] / self.metrics['total_requests'] * 100)
                if self.metrics['total_requests'] > 0 else 0,
                2
            )
        }
    
    def reset_client(self, client_id: str) -> None:
        """
        Reset rate limits for a specific client.
        
        Args:
            client_id: Client identifier to reset
        """
        if client_id in self.token_buckets:
            del self.token_buckets[client_id]
            del self.sliding_windows[client_id]
            log_info(logger, "rate_limits_reset", client_id=client_id)
    
    def _cleanup_if_needed(self) -> None:
        """Cleanup old entries periodically."""
        now = time.time()
        
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # Remove inactive clients (no activity in last 5 minutes)
        inactive_threshold = now - 300
        inactive_clients = []
        
        for client_id, token_bucket in self.token_buckets.items():
            if token_bucket.last_update < inactive_threshold:
                inactive_clients.append(client_id)
        
        for client_id in inactive_clients:
            del self.token_buckets[client_id]
            del self.sliding_windows[client_id]
        
        if inactive_clients:
            log_info(
                logger,
                "rate_limiter_cleanup_completed",
                inactive_clients_removed=len(inactive_clients)
            )
        
        self.last_cleanup = now

# Global rate limiter instance
_rate_limiter: EnhancedRateLimiter = None

def get_rate_limiter() -> EnhancedRateLimiter:
    """
    Get or create global rate limiter instance.
    
    Returns:
        EnhancedRateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = EnhancedRateLimiter()
    return _rate_limiter

def reset_rate_limiter() -> None:
    """Reset global rate limiter (useful for testing)."""
    global _rate_limiter
    _rate_limiter = None
