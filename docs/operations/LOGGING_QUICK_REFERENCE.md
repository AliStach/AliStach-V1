# Logging Quick Reference

## Import
```python
from ..utils.logging_config import log_info, log_warning, log_error, log_debug
import logging

logger = logging.getLogger(__name__)
```

## Basic Usage

### INFO - Successful Operations
```python
log_info(logger, "operation_completed", operation="search", result_count=20)
```

### WARNING - Recoverable Issues
```python
log_warning(logger, "cache_miss", cache_key="product:123", fallback="api_call")
```

### ERROR - Failures
```python
log_error(logger, "api_call_failed", exc_info=True, 
          error_type=type(e).__name__, error_message=str(e))
```

### DEBUG - Detailed Diagnostics
```python
log_debug(logger, "cache_lookup", cache_key="product:123", cache_layer="redis")
```

## Common Patterns

### Operation Start/End
```python
log_info(logger, "operation_started", operation="search", keywords=keywords)
# ... do work ...
log_info(logger, "operation_completed", operation="search", duration_seconds=0.45)
```

### Error Handling
```python
try:
    result = risky_operation()
except SpecificError as e:
    log_error(logger, "operation_failed", exc_info=True,
              operation="risky_operation",
              error_type=type(e).__name__,
              error_message=str(e))
    raise
```

### Performance Tracking
```python
start_time = time.time()
result = expensive_operation()
duration = time.time() - start_time
log_info(logger, "operation_completed", 
         operation="expensive_operation",
         duration_seconds=duration,
         result_size=len(result))
```

## Standard Field Names

| Field | Usage | Example |
|-------|-------|---------|
| `operation` | Operation name | `"search_products"` |
| `duration_seconds` | Time taken | `0.45` |
| `error_type` | Exception class | `"RateLimitError"` |
| `error_message` | Error description | `"Rate limit exceeded"` |
| `client_id` | Client identifier | `"192.168.1.1"` |
| `cache_key` | Cache key | `"product:12345"` |
| `product_id` | Product ID | `"12345"` |
| `status_code` | HTTP status | `200` |
| `method` | HTTP method | `"POST"` |
| `path` | URL path | `"/api/products"` |
| `retry_attempt` | Retry number | `2` |
| `cache_hits` | Cache hits | `15` |
| `cache_misses` | Cache misses | `5` |

## Message Naming

Use snake_case event names (past tense):
- ✅ `operation_completed`
- ✅ `cache_miss`
- ✅ `api_call_failed`
- ❌ `Success`
- ❌ `Error occurred`
- ❌ `Processing...`

## Don'ts

❌ **Don't format strings**
```python
log_info(logger, f"Found {count} results")  # BAD
```

✅ **Do use structured fields**
```python
log_info(logger, "search_completed", result_count=count)  # GOOD
```

❌ **Don't log sensitive data**
```python
log_info(logger, "user_login", password=password)  # BAD
```

✅ **Do sanitize sensitive data**
```python
log_info(logger, "user_login", user_id=user_id)  # GOOD
```

## Request IDs

Request IDs are automatically included in all logs within a request context. No manual action needed!

```python
# Request ID automatically included
log_info(logger, "processing_request", user_id=user_id)
# Output includes: "request_id": "abc-123-def-456"
```

## Testing

```python
from testfixtures import LogCapture

def test_logging():
    with LogCapture() as logs:
        log_info(logger, "test_event", value=42)
        logs.check(('module.name', 'INFO', 'test_event'))
```

## Configuration

Set log level via environment variable:
```bash
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
export LOG_FORMAT=json  # json, console
```

## Full Documentation

See `docs/LOGGING_STANDARDS.md` for complete documentation.
