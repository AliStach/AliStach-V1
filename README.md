# AliExpress API Proxy Service

A Python-based API proxy service for the AliExpress Open Platform API. Built with FastAPI and designed for serverless deployment.

> **Recently Modernized (v2.0)**: Enterprise-grade architecture with type coverage, error handling, and production deployment support.

## Deployment

### Vercel (Primary)
- **Platform**: Vercel Serverless Functions
- **Runtime**: Python 3.11
- **Status**: Production Ready

### Render (Alternative)  
- **Platform**: Render.com Web Service
- **Runtime**: Python 3.11 + Gunicorn + Uvicorn
- **Status**: Deployment Ready

## Quick Start

```bash
# Clone and setup
git clone https://github.com/AliStach/AliStach-V1.git
cd AliStach-V1
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start API server
python -m src.api.main
```

## Features

- **Modern Python** - Type hints, modular architecture
- **FastAPI Integration** - REST API with OpenAPI documentation  
- **Security** - Rate limiting, CORS, input validation
- **Retry Logic** - Automatic retry with exponential backoff
- **Logging** - Structured logging with performance metrics
- **Testing** - Unit and integration tests with pytest
- **Serverless Ready** - Optimized for serverless deployment

## API Operations

| Operation | Description | Status |
|-----------|-------------|--------|
| **Categories** | Get parent/child categories | ✅ Available |
| **Product Search** | Search with filters | ✅ Available |
| **Product Details** | Get detailed product info | ✅ Available |
| **Link Generation** | Generate tracking links | ✅ Available |
| **Hot Products** | Get trending products | ⚠️ Requires permissions |
| **Orders** | Order tracking | ⚠️ Requires permissions |
| **Smart Match** | URL matching | ⚠️ Requires permissions |
| **Image Search** | Search by image | ⚠️ Requires permissions |

### Service Modules

#### Core API Services
| Service Module | API Method | Status |
|----------------|------------|--------|
| `AliexpressAffiliateProductQueryRequest` | `aliexpress.affiliate.product.query` | ✅ Available |
| `AliexpressAffiliateCategoryGetRequest` | `aliexpress.affiliate.category.get` | ✅ Available |
| `AliexpressAffiliateLinkGenerateRequest` | `aliexpress.affiliate.link.generate` | ✅ Available |
| `AliexpressAffiliateProductdetailGetRequest` | `aliexpress.affiliate.productdetail.get` | ✅ Available |
| `AliexpressDsProductGetRequest` | `aliexpress.ds.product.get` | ✅ Available |
| `AliexpressDsRecommendFeedGetRequest` | `aliexpress.ds.recommend.feed.get` | ✅ Available |
| `AliexpressSolutionProductInfoGetRequest` | `aliexpress.solution.product.info.get` | ✅ Available |
| `AliexpressSolutionProductPostsGetRequest` | `aliexpress.solution.product.posts.get` | ✅ Available |

#### Extended Services (Requires Permissions)
| Service Module | API Method | Status |
|----------------|------------|--------|
| `AliexpressAffiliateHotproductQueryRequest` | `aliexpress.affiliate.hotproduct.query` | ⚠️ Permissions Required |
| `AliexpressAffiliateOrderGetRequest` | `aliexpress.affiliate.order.get` | ⚠️ Permissions Required |
| `AliexpressAffiliateImageSearchRequest` | `aliexpress.affiliate.image.search` | ⚠️ Permissions Required |
| `AliexpressAffiliateProductSmartmatchRequest` | `aliexpress.affiliate.product.smartmatch` | ⚠️ Permissions Required |

## Configuration

### Required Environment Variables
```bash
ALIEXPRESS_APP_KEY=your_app_key_here
ALIEXPRESS_APP_SECRET=your_app_secret_here
```

### Optional Configuration
```bash
ALIEXPRESS_TRACKING_ID=default_id    # Tracking identifier
ALIEXPRESS_LANGUAGE=EN               # API language
ALIEXPRESS_CURRENCY=USD              # Currency code

# Server Settings
API_HOST=0.0.0.0                     # Server host
API_PORT=8000                        # Server port
LOG_LEVEL=INFO                       # Logging level

# Security Settings
ADMIN_API_KEY=your_admin_key         # Admin access
INTERNAL_API_KEY=your_internal_key   # Internal access
MAX_REQUESTS_PER_MINUTE=60           # Rate limiting
ALLOWED_ORIGINS=https://example.com  # CORS origins
```

## Usage Examples

### High-Level Service

```python
from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService

# Initialize service
config = Config.from_env()
service = AliExpressService(config)

# Get categories
categories = service.get_parent_categories()
for category in categories:
    print(f"{category.category_id}: {category.category_name}")

# Search products
results = service.search_products(
    keywords="electronics",
    page_size=10
)

for product in results.products:
    print(f"{product.product_title} - ${product.price}")

# Generate links
urls = [product.product_url for product in results.products[:3]]
links = service.get_affiliate_links(urls)

for link in links:
    print(f"Generated: {link.affiliate_url}")
```

### Service Factory

```python
from src.utils.config import Config
from src.services.aliexpress import AliExpressServiceFactory

# Create factory
config = Config.from_env()
factory = AliExpressServiceFactory(config)

# List available services
services = factory.get_available_services()
for service_name, description in services.items():
    print(f"{service_name}: {description}")

# Create product search service
product_service = factory.product_query(
    keywords="electronics",
    page_size=20,
    sort="SALE_PRICE_ASC",
    target_currency="USD",
    target_language="EN"
)

# Execute API call
result = product_service.execute()
print(result)

# Create category service
category_service = factory.category_get()
categories_result = category_service.execute()

# Create link generation service
link_service = factory.link_generate(
    source_values="https://www.aliexpress.com/item/1005001234567890.html",
    promotion_link_type=0
)
links_result = link_service.execute()
```

### Direct Service Module Usage

```python
from src.utils.config import Config
from src.services.aliexpress import (
    AliexpressAffiliateProductQueryRequest,
    AliexpressAffiliateCategoryGetRequest,
    AliexpressAffiliateImageSearchRequest
)

# Load configuration
config = Config.from_env()

# Create product search service
product_service = AliexpressAffiliateProductQueryRequest()
product_service.set_config(config)

# Set parameters
product_service.keywords = "electronics"
product_service.category_ids = "509,3"
product_service.page_no = 1
product_service.page_size = 50
product_service.min_sale_price = 10000
product_service.max_sale_price = 50000
product_service.sort = "SALE_PRICE_ASC"
product_service.ship_to_country = "US"
product_service.target_currency = "USD"
product_service.target_language = "EN"

# Execute API call
result = product_service.execute()

# Create image search service
image_service = AliexpressAffiliateImageSearchRequest()
image_service.set_config(config)
image_service.image_url = "https://example.com/image.jpg"
image_service.page_size = 20

# Execute image search
image_result = image_service.execute()
```

### FastAPI Server

```bash
# Start the server
python -m src.api.main

# Available at:
# - API: http://localhost:8000/api/
# - Documentation: http://localhost:8000/docs
# - Health check: http://localhost:8000/health
```

### API Endpoints

```bash
# Categories
GET /api/categories
GET /api/categories/{parent_id}/children

# Product search
POST /api/products/search
{
  "keywords": "electronics",
  "page_size": 10,
  "sort": "SALE_PRICE_ASC"
}

# Enhanced search
POST /api/products
{
  "keywords": "electronics",
  "max_sale_price": 500.0,
  "min_sale_price": 100.0,
  "category_id": "509"
}

# Link generation
POST /api/affiliate/links
{
  "urls": ["https://www.aliexpress.com/item/123.html"]
}
```

## 🏗️ **Project Structure**

```
├── .github/                     # GitHub workflows (CI/CD)
├── docs/                        # Comprehensive documentation
│   ├── architecture/           # System architecture docs
│   ├── api/                    # API documentation
│   ├── deployment/             # Deployment guides
│   ├── operations/             # Operations & monitoring
│   └── development/            # Development guidelines
├── src/                         # Source code
│   ├── api/                    # FastAPI application
│   │   ├── endpoints/         # API route handlers
│   │   └── main.py            # Application entry point
│   ├── middleware/             # Request/response middleware
│   │   ├── rate_limiter.py    # Rate limiting
│   │   ├── security_headers.py # Security headers
│   │   └── request_id.py      # Request ID tracking
│   ├── services/               # Business logic layer
│   │   ├── aliexpress/        # AliExpress SDK modules
│   │   ├── aliexpress_service.py # High-level service
│   │   ├── cache_service.py   # Caching logic
│   │   └── monitoring_service.py # Metrics & monitoring
│   ├── models/                 # Data models (Pydantic)
│   ├── utils/                  # Utility functions
│   │   ├── config.py          # Configuration management
│   │   ├── logging_config.py  # Logging setup
│   │   └── validators.py      # Input validators
│   └── exceptions.py           # Custom exception hierarchy
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests (mirrors src/)
│   │   ├── api/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── integration/            # Integration tests
│   ├── e2e/                    # End-to-end tests
│   └── fixtures/               # Test fixtures
├── scripts/                     # Utility scripts
├── archive/                     # Historical files
└── api/                         # Vercel serverless functions
```

📖 **[Complete Documentation Index](docs/README.md)**

## Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Verbose output
python -m pytest -v
```

## Deployment

### Vercel
```bash
# Deploy to Vercel
vercel --prod
```

### Render
```bash
# Deploy using render.yaml
git push origin main
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .env

EXPOSE 8000
CMD ["python", "-m", "src.api.main"]
```

### Local Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Security

- **Rate Limiting**: 60 requests/minute, 5 requests/second per IP
- **CORS Protection**: Configurable origin restrictions
- **Input Validation**: Request validation
- **Error Handling**: Secure error responses
- **API Key Authentication**: Optional key protection
- **Request Logging**: Audit trail
- **IP Blocking**: Manual and automatic blocking

## Monitoring

```bash
# Health check
GET /health

# System info
GET /system/info

# Security info
GET /security/info
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests: `python -m pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## API Documentation

- **AliExpress Open Platform**: [https://open.aliexpress.com/](https://open.aliexpress.com/)
- **API Documentation**: [https://developers.aliexpress.com/en/doc.htm](https://developers.aliexpress.com/en/doc.htm)
- **Python SDK**: [https://github.com/sergioteula/python-aliexpress-api](https://github.com/sergioteula/python-aliexpress-api)
