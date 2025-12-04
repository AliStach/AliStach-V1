# Data Flow Architecture

## Overview

This document describes how data flows through the AliExpress Affiliate API Service, from initial request to final response. Understanding these flows is essential for debugging, optimization, and extending the system.

## Request/Response Flow

### Standard API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Middleware
    participant Endpoint
    participant Service
    participant Cache
    participant AliExpressAPI
    
    Client->>Gateway: HTTP Request
    Gateway->>Middleware: Route Request
    Middleware->>Middleware: Generate Request ID
    Middleware->>Middleware: Apply Security Headers
    Middleware->>Middleware: Check Rate Limit
    
    alt Rate Limit Exceeded
        Middleware-->>Client: 429 Too Many Requests
    else Rate Limit OK
        Middleware->>Endpoint: Forward Request
        Endpoint->>Endpoint: Validate Input
        
        alt Validation Failed
            Endpoint-->>Client: 400 Bad Request
        else Validation OK
            Endpoint->>Service: Call Service Method
            Service->>Cache: Check Cache
            
            alt Cache Hit
                Cache-->>Service: Return Cached Data
                Service-->>Endpoint: Return Data
            else Cache Miss
                Service->>AliExpressAPI: API Request
                AliExpressAPI-->>Service: API Response
                Service->>Cache: Store in Cache
                Service-->>Endpoint: Return Data
            end
            
            Endpoint->>Endpoint: Format Response
            Endpoint-->>Client: 200 OK + Data
        end
    end
```

## Detailed Flow Descriptions

### 1. Product Search Flow

**Endpoint**: `POST /api/products/search`

```mermaid
graph LR
    A[Client Request] --> B[Rate Limiter]
    B --> C[Input Validation]
    C --> D[Service Layer]
    D --> E{Cache Check}
    E -->|Hit| F[Return Cached]
    E -->|Miss| G[AliExpress API]
    G --> H[Transform Response]
    H --> I[Update Cache]
    I --> J[Format Response]
    F --> J
    J --> K[Client Response]
```

**Steps**:
1. **Request Reception**: FastAPI receives POST request
2. **Middleware Processing**:
   - Generate unique request ID
   - Apply security headers
   - Check rate limits (60/min, 5/sec)
3. **Input Validation**:
   - Validate keywords (required, max 200 chars)
   - Validate page_size (1-50)
   - Validate price ranges
   - Sanitize search query
4. **Cache Lookup**:
   - Generate cache key from parameters
   - Check memory cache (fastest)
   - Check Redis cache (if configured)
   - Check database cache (persistent)
5. **API Call** (if cache miss):
   - Build AliExpress API request
   - Add authentication signature
   - Execute HTTP request with retry logic
   - Handle API errors
6. **Response Transformation**:
   - Parse API response
   - Transform to internal models
   - Validate response data
   - Calculate additional fields
7. **Cache Update**:
   - Store in memory cache (TTL: 30 min)
   - Store in Redis (TTL: 1 hour)
   - Store in database (TTL: 24 hours)
8. **Response Formatting**:
   - Wrap in ServiceResponse model
   - Add metadata (processing time, cache status)
   - Serialize to JSON
9. **Response Delivery**:
   - Add response headers
   - Return to client

### 2. Category Retrieval Flow

**Endpoint**: `GET /api/categories`

```mermaid
graph TD
    A[GET /api/categories] --> B{Cache Available?}
    B -->|Yes| C[Return from Cache]
    B -->|No| D[Call AliExpress API]
    D --> E[Parse Response]
    E --> F[Build Category Tree]
    F --> G[Cache Result]
    G --> H[Return to Client]
    C --> H
```

**Caching Strategy**:
- Categories change infrequently
- Long TTL: 24 hours in memory, 7 days in database
- Aggressive caching reduces API calls

### 3. Affiliate Link Generation Flow

**Endpoint**: `POST /api/affiliate/links`

```mermaid
graph LR
    A[Product URLs] --> B[Validate URLs]
    B --> C[Batch Processing]
    C --> D{Cache Check}
    D -->|Hit| E[Return Cached Links]
    D -->|Miss| F[Generate Links API]
    F --> G[Parse Response]
    G --> H[Cache Links]
    H --> I[Return Links]
    E --> I
```

**Batch Processing**:
- Maximum 20 URLs per request
- Parallel cache lookups
- Single API call for all uncached URLs
- Individual error handling per URL

## Caching Architecture

### Multi-Level Cache Strategy

```mermaid
graph TD
    Request[Incoming Request] --> L1{Memory Cache}
    L1 -->|Hit| Return[Return Data]
    L1 -->|Miss| L2{Redis Cache}
    L2 -->|Hit| UpdateL1[Update Memory]
    UpdateL1 --> Return
    L2 -->|Miss| L3{Database Cache}
    L3 -->|Hit| UpdateL2[Update Redis]
    UpdateL2 --> UpdateL1
    L3 -->|Miss| API[Call AliExpress API]
    API --> UpdateAll[Update All Caches]
    UpdateAll --> Return
```

### Cache Key Generation

```python
def generate_cache_key(operation: str, params: dict) -> str:
    """
    Generate deterministic cache key from operation and parameters.
    
    Example:
        operation = "product_search"
        params = {"keywords": "phone", "page_size": 10}
        key = "product_search:keywords=phone:page_size=10"
    """
    sorted_params = sorted(params.items())
    param_str = ":".join(f"{k}={v}" for k, v in sorted_params)
    return f"{operation}:{param_str}"
```

### Cache TTL Strategy

| Data Type | Memory TTL | Redis TTL | Database TTL | Rationale |
|-----------|-----------|-----------|--------------|-----------|
| Categories | 24 hours | 7 days | 30 days | Rarely changes |
| Products | 30 minutes | 1 hour | 24 hours | Prices change frequently |
| Affiliate Links | 2 hours | 6 hours | 7 days | Stable once generated |
| Hot Products | 15 minutes | 30 minutes | 2 hours | Very dynamic |

## Error Handling Flow

### Error Classification and Handling

```mermaid
graph TD
    Error[Error Occurs] --> Classify{Error Type}
    Classify -->|Transient| Retry[Retry Logic]
    Classify -->|Permanent| Fail[Fail Fast]
    Classify -->|Validation| Return400[Return 400]
    
    Retry --> Backoff[Exponential Backoff]
    Backoff --> Attempt{Retry Attempt}
    Attempt -->|Success| Success[Return Result]
    Attempt -->|Max Retries| Fail
    
    Fail --> Log[Log Error]
    Log --> Return500[Return 500]
    
    Return400 --> Client[Client Response]
    Return500 --> Client
    Success --> Client
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "retry_after": 60,
      "limit": "60 requests per minute"
    }
  },
  "metadata": {
    "request_id": "req_abc123",
    "timestamp": "2025-12-04T10:30:00Z"
  }
}
```

## Monitoring Data Flow

### Metrics Collection

```mermaid
graph LR
    Request[Request] --> Middleware[Middleware]
    Middleware --> Metrics1[Record Request]
    Middleware --> Service[Service Layer]
    Service --> Metrics2[Record API Call]
    Service --> Cache[Cache Layer]
    Cache --> Metrics3[Record Cache Hit/Miss]
    Service --> Response[Response]
    Response --> Metrics4[Record Response Time]
    
    Metrics1 --> DB[(Metrics DB)]
    Metrics2 --> DB
    Metrics3 --> DB
    Metrics4 --> DB
```

### Logged Events

1. **Request Events**:
   - Request received (method, path, IP)
   - Request ID assigned
   - Rate limit check result

2. **Processing Events**:
   - Input validation result
   - Cache lookup result
   - API call initiated
   - API call completed

3. **Response Events**:
   - Response prepared
   - Response sent
   - Total processing time

4. **Error Events**:
   - Error type and message
   - Stack trace
   - Request context

## Performance Optimization

### Request Optimization Strategies

1. **Parallel Processing**:
   ```python
   # Fetch multiple products in parallel
   async def get_multiple_products(product_ids: List[str]):
       tasks = [get_product(id) for id in product_ids]
       return await asyncio.gather(*tasks)
   ```

2. **Connection Pooling**:
   - Reuse HTTP connections to AliExpress API
   - Database connection pool (10 connections)
   - Redis connection pool (if used)

3. **Response Compression**:
   - GZip compression for responses > 1KB
   - Reduces bandwidth by 60-80%

4. **Lazy Loading**:
   - Load detailed data only when requested
   - Paginate large result sets

### Cache Warming

```python
# Warm cache with popular categories on startup
async def warm_cache():
    """Pre-populate cache with frequently accessed data."""
    await cache_service.get_categories()  # Cache all categories
    await cache_service.get_hot_products()  # Cache trending products
```

## Data Transformation Pipeline

### AliExpress API Response → Internal Model

```mermaid
graph LR
    A[API Response] --> B[Parse JSON]
    B --> C[Extract Data]
    C --> D[Validate Fields]
    D --> E[Transform Types]
    E --> F[Calculate Derived Fields]
    F --> G[Create Pydantic Model]
    G --> H[Validate Model]
    H --> I[Return Model]
```

**Example Transformation**:
```python
# AliExpress API Response
{
  "app_sale_price": "2999",  # Price in cents
  "original_price": "5999",
  "evaluate_rate": "98.5%"
}

# Transformed Internal Model
ProductResponse(
    price=29.99,  # Converted to dollars
    original_price=59.99,
    discount_percentage=50.0,  # Calculated
    rating=4.9,  # Converted from percentage
    rating_percentage=98.5
)
```

## Security Data Flow

### Request Security Pipeline

```mermaid
graph TD
    Request[Incoming Request] --> CORS{CORS Check}
    CORS -->|Fail| Reject1[403 Forbidden]
    CORS -->|Pass| RateLimit{Rate Limit}
    RateLimit -->|Exceed| Reject2[429 Too Many Requests]
    RateLimit -->|OK| Validate{Input Validation}
    Validate -->|Fail| Reject3[400 Bad Request]
    Validate -->|Pass| Sanitize[Sanitize Input]
    Sanitize --> Auth{Authentication}
    Auth -->|Fail| Reject4[401 Unauthorized]
    Auth -->|Pass| Process[Process Request]
    Process --> Response[Return Response]
```

### Data Sanitization

```python
def sanitize_search_query(query: str) -> str:
    """Remove potentially dangerous characters from search query."""
    # Remove SQL injection attempts
    query = re.sub(r'[<>\"\'%;()&+]', '', query)
    # Limit length
    query = query[:200]
    # Trim whitespace
    return query.strip()
```

## Related Documentation

- [Architecture Overview](overview.md) - High-level system architecture
- [Components](components.md) - Detailed component documentation
- [API Documentation](../api/) - API endpoint reference
- [Operations Guide](../operations/) - Monitoring and troubleshooting

---

*Last Updated: December 4, 2025*
