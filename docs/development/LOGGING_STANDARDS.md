# Logging Standards

## Overview

This document describes the standardized logging approach used throughout the AliExpress Affiliate API Service. All modules follow consistent patterns for structured logging with automatic request ID propagation.

## Key Principles

1. **Structured Logging**: All log messages use JSON format with consistent field names
2. **Request ID Propagation**: Every log entry automatically includes the request ID for tracing
3. **Consistent Field Names**: Standard field names across all modules
4. **Appropriate Log Levels**: DEBUG, INFO, WARNING, ERROR used consistently
5. **Context-Rich Messages**: All logs include relevant context as structured fields

## Log Levels

### DEBUG
- Detailed diagnostic information
- Use for development and troubleshooting
- Not typically enabled in production

### INFO
- General informational messages
- Successful operations
- System state changes
- Performance metrics

### WARNING
- Potentially harmful situations
- Recoverable errors
- Fallback behaviors
- Configuration issues

### ERROR
- Error events that might still allow the application to continue
- Failed operations
- Unrecoverable errors
- Exception details

## Standard Logging Functions

### Import Statement
```python
from ..utils.logging_config import log_info, log_warning, log_error, log_debug

logger = logging.getLogger(__name__)
```

### Usage Examples

#### INFO Level
```python
log_info(
    logger,
    "operation_completed",
    operation="search_products",
    duration_seconds=0.45,
    result_count=20
)
```

#### WARNING Level
```python
log_warning(
    logger,
    "cache_miss",
    cache_key="products:search:headphones",
    fallback_action="api_call"
)
```

#### ERROR Level
```python
log_error(
    logger,
    "api_call_failed",
    exc_info=True,  # Include exception traceback
    service="aliexpress",
    method="product.query",
    error_type="RateLimitError",
    error_message="Rate limit exceeded"
)
```

#### DEBUG Level
```python
log_debug(
    logger,
    "cache_lookup",
    cache_key="product:12345",
    cache_layer="redis"
)
```

## Standard Field Names

### Common Fields (Automatically Included)
- `timestamp`: ISO 8601 timestamp in UTC
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `logger`: Logger name (module path)
- `message`: Log message (use snake_case event names)
- `module`: Python module name
- `function`: Function name
- `line`: Line number
- `request_id`: Unique request identifier (automatically included)

### Context Fields (Add as needed)
- `operation`: Name of the operation being performed
- `duration_seconds`: Operation duration
- `error_type`: Exception class name
- `error_message`: Error description
- `client_id`: Client identifier (IP, user ID, etc.)
- `cache_key`: Cache key being accessed
- `product_id`: Product identifier
- `search_query`: Search keywords
- `status_code`: HTTP status code
- `method`: HTTP method or API method
- `path`: URL path
- `retry_attempt`: Retry attempt number
- `max_attempts`: Maximum retry attempts

## Request ID Propagation

Request IDs are automatically propagated through the application using context variables:

```python
from ..utils.logging_config import request_id_ctx

# Set request ID (done automatically by RequestIDMiddleware)
token = request_id_ctx.set(request_id)

try:
    # All logs within this context will include the request_id
    log_info(logger, "processing_request", user_id=user_id)
finally:
    # Reset context
    request_id_ctx.reset(token)
```

## Message Naming Conventions

Use snake_case event names that describe what happened:

### Good Examples
- `operation_completed`
- `cache_miss`
- `api_call_failed`
- `rate_limit_exceeded`
- `database_connection_established`
- `user_authenticated`

### Bad Examples
- `Success` (too vague)
- `Error occurred` (not descriptive)
- `Processing...` (not an event)
- `API Call` (not past tense)

## Migration Guide

### Before (Old Style)
```python
logger.info(f"Searching products with keywords='{keywords}'")
logger.warning(f"Redis connection failed: {e}")
logger.error(
    "API call failed",
    extra={
        'extra_fields': {
            'error': str(e),
            'operation': 'search'
        }
    }
)
```

### After (New Style)
```python
log_info(
    logger,
    "product_search_initiated",
    keywords=keywords,
    page_size=page_size
)

log_warning(
    logger,
    "redis_connection_failed",
    error_type=type(e).__name__,
    error_message=str(e)
)

log_error(
    logger,
    "api_call_failed",
    exc_info=True,
    operation="search",
    error_type=type(e).__name__,
    error_message=str(e)
)
```

## Log Output Format

### Development (Console)
```
2024-01-15T10:30:45.123Z [INFO] product_search_initiated keywords=headphones page_size=20 request_id=abc-123
```

### Production (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "src.services.aliexpress_service",
  "message": "product_search_initiated",
  "module": "aliexpress_service",
  "function": "search_products",
  "line": 245,
  "request_id": "abc-123-def-456",
  "keywords": "headphones",
  "page_size": 20
}
```

## Performance Considerations

1. **Avoid String Formatting**: Don't format strings before logging
   ```python
   # Bad
   log_info(logger, f"Found {len(results)} results")
   
   # Good
   log_info(logger, "search_completed", result_count=len(results))
   ```

2. **Use Appropriate Levels**: Don't log DEBUG messages at INFO level

3. **Limit Log Volume**: Don't log inside tight loops

4. **Lazy Evaluation**: Context fields are only evaluated if the log level is enabled

## Testing Logging

### Capturing Logs in Tests
```python
import logging
from testfixtures import LogCapture

def test_logging():
    with LogCapture() as log_capture:
        # Your code that logs
        log_info(logger, "test_event", value=42)
        
        # Assert log was created
        log_capture.check(
            ('module.name', 'INFO', 'test_event')
        )
```

## Monitoring and Alerting

### Log Aggregation
- All logs are output to stdout in JSON format
- Use log aggregation tools (CloudWatch, Datadog, ELK) to collect and analyze
- Request IDs enable distributed tracing

### Alert Conditions
- ERROR level logs should trigger alerts
- High WARNING volume may indicate issues
- Track specific error types for targeted alerts

## Best Practices

1. **Always include context**: Add relevant fields to every log
2. **Use consistent field names**: Follow the standard field names
3. **Log at appropriate levels**: Don't overuse ERROR or INFO
4. **Include error details**: Always log error_type and error_message
5. **Use exc_info for exceptions**: Set `exc_info=True` for ERROR logs with exceptions
6. **Avoid sensitive data**: Never log passwords, API keys, or PII
7. **Use structured fields**: Don't embed data in message strings
8. **Keep messages concise**: Use snake_case event names
9. **Test your logging**: Verify logs are created correctly
10. **Monitor log volume**: Excessive logging can impact performance

## Configuration

### Environment Variables
- `LOG_LEVEL`: Set log level (DEBUG, INFO, WARNING, ERROR)
- `LOG_FORMAT`: Set format (json, console)

### Setup in Application
```python
from src.utils.logging_config import setup_production_logging

# Initialize logging
setup_production_logging(log_level="INFO")
```

## Troubleshooting

### Request ID Not Appearing
- Ensure RequestIDMiddleware is installed
- Check that request_id_ctx is being set
- Verify logging_config is imported correctly

### Logs Not Structured
- Confirm JSONFormatter is being used
- Check that extra_fields are being passed correctly
- Verify log handlers are configured

### Performance Issues
- Reduce log level in production
- Avoid logging in hot paths
- Use sampling for high-volume events

## References

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Structured Logging Best Practices](https://www.structlog.org/)
- [12-Factor App Logs](https://12factor.net/logs)
