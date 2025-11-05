# AliExpress API Service Modules

This directory contains individual service modules for each AliExpress API endpoint, following the same structure and pattern used in the official SDK.

## Overview

Each service module is a separate class that handles a specific AliExpress API endpoint. This modular approach provides:

- **Clean separation of concerns** - Each API endpoint has its own dedicated class
- **Consistent interface** - All services extend the same base `RestApi` class
- **Easy parameter management** - Each service exposes its parameters as instance attributes
- **Flexible usage** - Services can be used directly or through the factory pattern

## Architecture

```
src/services/aliexpress/
├── base.py                           # Base RestApi class
├── factory.py                        # Service factory for easy instantiation
├── __init__.py                       # Module exports
├── README.md                         # This documentation
│
├── affiliate_*.py                    # Affiliate API services
├── ds_*.py                          # Dropshipping API services
└── solution_*.py                    # Solution API services
```

## Available Services

### Affiliate API Services

| Service Class | API Method | Description |
|---------------|------------|-------------|
| `AliexpressAffiliateProductQueryRequest` | `aliexpress.affiliate.product.query` | Search for affiliate products |
| `AliexpressAffiliateCategoryGetRequest` | `aliexpress.affiliate.category.get` | Get product categories |
| `AliexpressAffiliateLinkGenerateRequest` | `aliexpress.affiliate.link.generate` | Generate affiliate links |
| `AliexpressAffiliateHotproductQueryRequest` | `aliexpress.affiliate.hotproduct.query` | Get hot/trending products |
| `AliexpressAffiliateProductdetailGetRequest` | `aliexpress.affiliate.productdetail.get` | Get detailed product information |
| `AliexpressAffiliateOrderGetRequest` | `aliexpress.affiliate.order.get` | Get order information |
| `AliexpressAffiliateOrderListRequest` | `aliexpress.affiliate.order.list` | List orders |
| `AliexpressAffiliateFeaturedpromoProductsGetRequest` | `aliexpress.affiliate.featuredpromo.products.get` | Get featured promotion products |
| `AliexpressAffiliateFeaturedpromoGetRequest` | `aliexpress.affiliate.featuredpromo.get` | Get featured promotions |
| `AliexpressAffiliateImageSearchRequest` | `aliexpress.affiliate.image.search` | Search products by image |
| `AliexpressAffiliateProductSmartmatchRequest` | `aliexpress.affiliate.product.smartmatch` | Smart match products |

### Dropshipping API Services

| Service Class | API Method | Description |
|---------------|------------|-------------|
| `AliexpressDsProductGetRequest` | `aliexpress.ds.product.get` | Get dropshipping product details |
| `AliexpressDsRecommendFeedGetRequest` | `aliexpress.ds.recommend.feed.get` | Get recommended product feed |
| `AliexpressDsTradeOrderGetRequest` | `aliexpress.ds.trade.order.get` | Get dropshipping order details |

### Solution API Services

| Service Class | API Method | Description |
|---------------|------------|-------------|
| `AliexpressSolutionProductInfoGetRequest` | `aliexpress.solution.product.info.get` | Get solution product information |
| `AliexpressSolutionProductPostsGetRequest` | `aliexpress.solution.product.posts.get` | Get solution product posts |

## Usage Examples

### Method 1: Using the Service Factory (Recommended)

```python
from src.utils.config import Config
from src.services.aliexpress import AliExpressServiceFactory

# Load configuration
config = Config.from_env()

# Create factory
factory = AliExpressServiceFactory(config)

# Create and configure a product search service
product_service = factory.product_query(
    keywords="smartphone",
    page_size=20,
    sort="SALE_PRICE_ASC",
    target_currency="USD",
    target_language="EN"
)

# Execute the API call
result = product_service.execute()
print(result)
```

### Method 2: Using Services Directly

```python
from src.utils.config import Config
from src.services.aliexpress import AliexpressAffiliateProductQueryRequest

# Load configuration
config = Config.from_env()

# Create service instance
service = AliexpressAffiliateProductQueryRequest()
service.set_config(config)

# Set parameters
service.keywords = "laptop"
service.page_no = 1
service.page_size = 10
service.target_currency = "USD"
service.target_language = "EN"
service.sort = "SALE_PRICE_ASC"

# Execute the API call
result = service.execute()
print(result)
```

### Method 3: Category Service Example

```python
from src.utils.config import Config
from src.services.aliexpress import AliexpressAffiliateCategoryGetRequest

# Load configuration
config = Config.from_env()

# Create and configure category service
category_service = AliexpressAffiliateCategoryGetRequest()
category_service.set_config(config)

# Execute to get categories
result = category_service.execute()
print(result)
```

### Method 4: Link Generation Example

```python
from src.utils.config import Config
from src.services.aliexpress import AliexpressAffiliateLinkGenerateRequest

# Load configuration
config = Config.from_env()

# Create link generation service
link_service = AliexpressAffiliateLinkGenerateRequest()
link_service.set_config(config)

# Set parameters
link_service.source_values = "https://www.aliexpress.com/item/1005001234567890.html"
link_service.promotion_link_type = 0

# Execute to generate affiliate links
result = link_service.execute()
print(result)
```

### Method 5: Image Search Example

```python
from src.utils.config import Config
from src.services.aliexpress import AliexpressAffiliateImageSearchRequest

# Load configuration
config = Config.from_env()

# Create image search service
image_service = AliexpressAffiliateImageSearchRequest()
image_service.set_config(config)

# Set parameters
image_service.image_url = "https://example.com/product-image.jpg"
image_service.page_size = 20
image_service.target_currency = "USD"
image_service.target_language = "EN"

# Execute image search
result = image_service.execute()
print(result)
```

## Service Parameters

Each service class exposes its parameters as instance attributes. Here are some common parameters:

### Common Parameters
- `app_signature` - Application signature
- `tracking_id` - Affiliate tracking ID
- `target_currency` - Target currency (USD, EUR, etc.)
- `target_language` - Target language (EN, ES, etc.)

### Product Search Parameters
- `keywords` - Search keywords
- `category_ids` - Category IDs to filter by
- `page_no` - Page number (starting from 1)
- `page_size` - Number of results per page
- `sort` - Sort order (SALE_PRICE_ASC, SALE_PRICE_DESC, etc.)
- `max_sale_price` - Maximum price filter
- `min_sale_price` - Minimum price filter

### Link Generation Parameters
- `source_values` - Product URLs to convert
- `promotion_link_type` - Type of promotion link

### Image Search Parameters
- `image_url` - URL of the image to search with
- `category_ids` - Category filter for image search

## Error Handling

All services include comprehensive error handling:

```python
try:
    result = service.execute()
    # Handle successful response
    print("Success:", result)
except Exception as e:
    # Handle API errors
    print("Error:", str(e))
```

Common error types:
- **Network errors** - Connection issues, timeouts
- **API errors** - Invalid parameters, permission issues
- **Authentication errors** - Invalid credentials
- **Rate limiting** - Too many requests

## Configuration

Services require a `Config` object with the following settings:

```python
# Required configuration
config.app_key = "your_app_key"
config.app_secret = "your_app_secret" 
config.tracking_id = "your_tracking_id"

# Optional configuration
config.language = "EN"  # Default language
config.currency = "USD"  # Default currency
```

## Response Format

All services return JSON responses from the AliExpress API. The exact format depends on the specific API endpoint, but generally follows this structure:

```json
{
  "aliexpress_affiliate_product_query_response": {
    "result": {
      "products": [...],
      "total_record_count": 1000,
      "current_page": 1
    }
  }
}
```

## Best Practices

1. **Use the Factory Pattern** - The `AliExpressServiceFactory` provides a clean way to create and configure services
2. **Reuse Service Instances** - Create service instances once and reuse them for multiple calls
3. **Handle Errors Gracefully** - Always wrap API calls in try-catch blocks
4. **Respect Rate Limits** - Don't make too many concurrent requests
5. **Validate Parameters** - Check parameter values before making API calls

## Integration with Existing Service

These service modules complement the existing `AliExpressService` class:

- **High-level operations** - Use `AliExpressService` for common operations with built-in response parsing
- **Low-level operations** - Use individual service modules for direct API access and custom parameter handling
- **Batch operations** - Use service modules for batch processing with custom logic

## Testing

Run the demonstration script to test the service modules:

```bash
python scripts/demo_service_modules.py
```

This will show examples of:
- Creating services with the factory
- Using services directly
- Parameter configuration
- Error handling

## Contributing

When adding new service modules:

1. Follow the naming convention: `AliexpressApiMethodNameRequest`
2. Extend the `RestApi` base class
3. Implement the `getapiname()` method
4. Add all API parameters as instance attributes
5. Update the factory registry
6. Add documentation and examples