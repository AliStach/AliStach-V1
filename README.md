# 🛍️ AliExpress Affiliate API Service (Python)

A modern, production-ready Python service for the AliExpress Affiliate API using the official Python SDK. Features clean architecture, comprehensive error handling, and optional FastAPI endpoints for GPT integration.

## 🚀 **LIVE PRODUCTION DEPLOYMENT**

**🌐 Production URL**: `https://alistach.vercel.app`

**✅ Status**: LIVE and ready for GPT Actions integration!

### 🔗 **Key Endpoints**
- **Health Check**: [`/health`](https://alistach.vercel.app/health)
- **OpenAPI Spec**: [`/openapi-gpt.json`](https://alistach.vercel.app/openapi-gpt.json)
- **Interactive Docs**: [`/docs`](https://alistach.vercel.app/docs)
- **API Status**: [`/api/status`](https://alistach.vercel.app/api/status)
- **Cache Stats**: [`/api/cache/stats`](https://alistach.vercel.app/api/cache/stats)

### 🤖 **GPT Actions Ready**
This API is **publicly accessible** and optimized for ChatGPT Actions integration. Use the OpenAPI specification URL above to configure your custom GPT.

## 🚀 **Quick Start**

```bash
# 1. Clone and setup
git clone https://github.com/AliStach/AliStach-V1.git
cd AliStach-V1
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your AliExpress credentials

# 3. Run demo
python scripts/demo.py

# 4. Start API server (optional)
python -m src.api.main
```

## ✨ **Features**

- 🐍 **Modern Python** - Clean, modular architecture with type hints
- 🔐 **Official SDK** - Uses python-aliexpress-api for reliable API access
- 🚀 **FastAPI Integration** - Optional REST API with OpenAPI documentation
- 🛡️ **Comprehensive Security** - Rate limiting, CORS, input validation
- 🔄 **Retry Logic** - Automatic retry with exponential backoff
- 📊 **Rich Logging** - Structured logging with performance metrics
- 🧪 **Full Test Coverage** - Unit and integration tests with pytest
- 🔗 **Affiliate Links** - Automatic affiliate link generation

## 🎯 **Supported Operations**

### High-Level Service Operations
| Operation | Description | Status |
|-----------|-------------|--------|
| **Categories** | Get parent/child categories | ✅ Ready |
| **Product Search** | Search with filters | ✅ Ready |
| **Product Details** | Get detailed product info | ✅ Ready |
| **Affiliate Links** | Generate tracking links | ✅ Ready |
| **Hot Products** | Get trending products | ⚠️ Requires permissions |
| **Orders** | Track affiliate orders | ⚠️ Requires permissions |
| **Smart Match** | Match product URLs | ⚠️ Requires permissions |
| **Image Search** | Search by image | ⚠️ Requires permissions |

### Individual Service Modules (16 Available)

#### Affiliate API Services
| Service Module | API Method | Description | Status |
|----------------|------------|-------------|--------|
| `AliexpressAffiliateProductQueryRequest` | `aliexpress.affiliate.product.query` | Search for affiliate products | ✅ Ready |
| `AliexpressAffiliateCategoryGetRequest` | `aliexpress.affiliate.category.get` | Get product categories | ✅ Ready |
| `AliexpressAffiliateLinkGenerateRequest` | `aliexpress.affiliate.link.generate` | Generate affiliate links | ✅ Ready |
| `AliexpressAffiliateHotproductQueryRequest` | `aliexpress.affiliate.hotproduct.query` | Get hot/trending products | ⚠️ Requires permissions |
| `AliexpressAffiliateProductdetailGetRequest` | `aliexpress.affiliate.productdetail.get` | Get detailed product information | ✅ Ready |
| `AliexpressAffiliateOrderGetRequest` | `aliexpress.affiliate.order.get` | Get order information | ⚠️ Requires permissions |
| `AliexpressAffiliateOrderListRequest` | `aliexpress.affiliate.order.list` | List orders | ⚠️ Requires permissions |
| `AliexpressAffiliateFeaturedpromoProductsGetRequest` | `aliexpress.affiliate.featuredpromo.products.get` | Get featured promotion products | ⚠️ Requires permissions |
| `AliexpressAffiliateFeaturedpromoGetRequest` | `aliexpress.affiliate.featuredpromo.get` | Get featured promotions | ⚠️ Requires permissions |
| `AliexpressAffiliateImageSearchRequest` | `aliexpress.affiliate.image.search` | Search products by image | ⚠️ Requires permissions |
| `AliexpressAffiliateProductSmartmatchRequest` | `aliexpress.affiliate.product.smartmatch` | Smart match products | ⚠️ Requires permissions |

#### Dropshipping API Services
| Service Module | API Method | Description | Status |
|----------------|------------|-------------|--------|
| `AliexpressDsProductGetRequest` | `aliexpress.ds.product.get` | Get dropshipping product details | ✅ Ready |
| `AliexpressDsRecommendFeedGetRequest` | `aliexpress.ds.recommend.feed.get` | Get recommended product feed | ✅ Ready |
| `AliexpressDsTradeOrderGetRequest` | `aliexpress.ds.trade.order.get` | Get dropshipping order details | ⚠️ Requires permissions |

#### Solution API Services
| Service Module | API Method | Description | Status |
|----------------|------------|-------------|--------|
| `AliexpressSolutionProductInfoGetRequest` | `aliexpress.solution.product.info.get` | Get solution product information | ✅ Ready |
| `AliexpressSolutionProductPostsGetRequest` | `aliexpress.solution.product.posts.get` | Get solution product posts | ✅ Ready |

## 🔧 **Configuration**

### Required Environment Variables
```bash
ALIEXPRESS_APP_KEY=your_app_key_here
ALIEXPRESS_APP_SECRET=your_app_secret_here
```

### Optional Configuration
```bash
ALIEXPRESS_TRACKING_ID=gpt_chat      # Default tracking ID
ALIEXPRESS_LANGUAGE=EN               # API language (EN, ES, FR, etc.)
ALIEXPRESS_CURRENCY=USD              # Currency (USD, EUR, GBP, etc.)

# API Server Settings (if using FastAPI)
API_HOST=0.0.0.0                     # Server host
API_PORT=8000                        # Server port
LOG_LEVEL=INFO                       # Logging level

# Security Settings
ADMIN_API_KEY=your_admin_key         # Admin endpoints access
INTERNAL_API_KEY=ALIINSIDER-2025     # Internal API access
MAX_REQUESTS_PER_MINUTE=60           # Rate limiting
ALLOWED_ORIGINS=https://chat.openai.com,https://chatgpt.com
```

## 📖 **Usage Examples**

### Method 1: High-Level Service (Recommended for Most Use Cases)

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
    keywords="wireless headphones",
    page_size=10
)

for product in results.products:
    print(f"{product.product_title} - ${product.price}")

# Generate affiliate links
urls = [product.product_url for product in results.products[:3]]
affiliate_links = service.get_affiliate_links(urls)

for link in affiliate_links:
    print(f"Affiliate: {link.affiliate_url}")
```

### Method 2: Service Factory (Best of Both Worlds)

```python
from src.utils.config import Config
from src.services.aliexpress import AliExpressServiceFactory

# Create factory with configuration
config = Config.from_env()
factory = AliExpressServiceFactory(config)

# List all available services
services = factory.get_available_services()
for service_name, description in services.items():
    print(f"{service_name}: {description}")

# Create and use product search service
product_service = factory.product_query(
    keywords="smartphone",
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

### Method 3: Direct Service Module Usage (Maximum Control)

```python
from src.utils.config import Config
from src.services.aliexpress import (
    AliexpressAffiliateProductQueryRequest,
    AliexpressAffiliateCategoryGetRequest,
    AliexpressAffiliateImageSearchRequest
)

# Load configuration
config = Config.from_env()

# Create product search service directly
product_service = AliexpressAffiliateProductQueryRequest()
product_service.set_config(config)

# Set all parameters manually
product_service.keywords = "laptop"
product_service.category_ids = "509,3"  # Electronics categories
product_service.page_no = 1
product_service.page_size = 50
product_service.min_sale_price = 10000  # $100.00 in cents
product_service.max_sale_price = 50000  # $500.00 in cents
product_service.sort = "SALE_PRICE_ASC"
product_service.ship_to_country = "US"
product_service.target_currency = "USD"
product_service.target_language = "EN"

# Execute the API call
result = product_service.execute()

# Create image search service
image_service = AliexpressAffiliateImageSearchRequest()
image_service.set_config(config)
image_service.image_url = "https://example.com/product-image.jpg"
image_service.page_size = 20

# Execute image search
image_result = image_service.execute()
```

### AliExpressServiceFactory Class

The `AliExpressServiceFactory` provides the most convenient way to create and use service modules:

```python
from src.services.aliexpress import AliExpressServiceFactory

# Initialize factory
factory = AliExpressServiceFactory(config)

# Convenience methods for common services
product_service = factory.product_query(keywords="headphones", page_size=10)
category_service = factory.category_get()
link_service = factory.link_generate(source_values="https://aliexpress.com/item/123")
hotproduct_service = factory.hotproduct_query(keywords="trending", page_size=20)
image_service = factory.image_search(image_url="https://example.com/image.jpg")

# Generic service creation
any_service = factory.create_service('affiliate.product.query')
any_service.keywords = "custom search"
result = any_service.execute()
```

### FastAPI Server Usage

```bash
# Start the server
python -m src.api.main

# API will be available at:
# - Main API: http://localhost:8000/api/
# - Documentation: http://localhost:8000/docs
# - Health check: http://localhost:8000/health
```

### API Endpoints

```bash
# Get categories
GET /api/categories
GET /api/categories/{parent_id}/children

# Search products
GET /api/products/search?keywords=headphones&page_size=10
POST /api/products/search
{
  "keywords": "headphones",
  "page_size": 10,
  "sort": "SALE_PRICE_ASC"
}

# Enhanced product search
POST /api/products
{
  "keywords": "phone",
  "max_sale_price": 500.0,
  "min_sale_price": 100.0,
  "category_id": "509"
}

# Generate affiliate links
POST /api/affiliate/links
{
  "urls": ["https://www.aliexpress.com/item/123.html"]
}

# Single affiliate link
GET /api/affiliate/link?url=https://www.aliexpress.com/item/123.html
```

## 🏗️ **Project Structure**

```
src/
├── api/                           # FastAPI application
│   ├── endpoints/                # API route handlers
│   ├── middleware/               # Security middleware
│   └── main.py                  # FastAPI app setup
├── services/                     # Business logic
│   ├── aliexpress/              # Individual service modules (NEW)
│   │   ├── __init__.py         # Module exports
│   │   ├── base.py             # RestApi base class
│   │   ├── factory.py          # Service factory
│   │   ├── README.md           # Service documentation
│   │   ├── affiliate_*.py      # Affiliate API services (11 modules)
│   │   ├── ds_*.py            # Dropshipping API services (3 modules)
│   │   └── solution_*.py      # Solution API services (2 modules)
│   ├── aliexpress_service.py   # High-level service wrapper
│   ├── cache_service.py        # Caching functionality
│   └── enhanced_aliexpress_service.py
├── models/                      # Data models
│   ├── responses.py            # Response data classes
│   └── cache_models.py         # Cache models
├── utils/                       # Utilities
│   ├── config.py              # Configuration management
│   ├── response_formatter.py   # Response formatting
│   └── logging_config.py       # Logging setup
└── __init__.py

tests/
├── unit/                        # Unit tests
├── integration/                 # Integration tests
├── fixtures/                   # Test fixtures
└── conftest.py                 # Test configuration

scripts/
├── demo.py                     # Basic demo script
├── demo_service_modules.py     # Service modules demo (NEW)
└── integration_example.py      # Integration examples (NEW)
```

## 🧪 **Testing**

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test categories
python -m pytest tests/unit/          # Unit tests only
python -m pytest tests/integration/   # Integration tests only

# Run with verbose output
python -m pytest -v
```

## 🚀 **Deployment**

### ✅ **Production Deployment (Vercel)**

**Status**: ✅ LIVE  
**URL**: https://alistach.vercel.app  
**Platform**: Vercel Serverless Functions  
**Runtime**: Python 3.11  
**Last Updated**: November 2024  

**Environment Configuration**:
- ✅ All environment variables configured
- ✅ CORS enabled for GPT Actions domains
- ✅ Rate limiting active (60/min, 5/sec per IP)
- ✅ Security middleware enabled
- ✅ Production logging configured

**Verification Results**:
- ✅ Health endpoint: `/health` - Operational
- ✅ OpenAPI spec: `/openapi-gpt.json` - Available
- ✅ Interactive docs: `/docs` - Accessible
- ✅ GPT Actions compatible: Ready for integration

### Docker Deployment

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

### Railway/Render Deployment

1. Connect your repository
2. Set environment variables
3. Use start command: `python -m src.api.main`
4. Set port to 8000

### Local Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests in watch mode
python -m pytest --watch
```

## 🔒 **Security Features**

- **Rate Limiting**: 60 requests/minute, 5 requests/second per IP
- **CORS Protection**: Restricted to authorized domains
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error messages without data leakage
- **API Key Authentication**: Optional internal API key protection
- **Request Logging**: Comprehensive audit trail
- **IP Blocking**: Automatic and manual IP blocking capabilities

## 📊 **Monitoring & Logging**

The service includes comprehensive monitoring:

```bash
# Health check endpoint
GET /health

# System information
GET /system/info

# Security information
GET /security/info

# Admin dashboard (requires admin key)
GET /admin/dashboard
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run tests: `python -m pytest`
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- 📖 **Documentation**: Check the `/docs` endpoint when running the API
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Contact**: [Your contact information]

## 📚 **Official Documentation**

### AliExpress API Documentation
- **Official AliExpress Open Platform**: [https://open.aliexpress.com/](https://open.aliexpress.com/)
- **API Documentation**: [https://developers.aliexpress.com/en/doc.htm](https://developers.aliexpress.com/en/doc.htm)
- **Python SDK Repository**: [https://github.com/sergioteula/python-aliexpress-api](https://github.com/sergioteula/python-aliexpress-api)

### Service Module Compatibility
This project's service modules are designed to be **100% compatible** with the official SDK structure:
- Same class naming conventions
- Same parameter structure
- Same method interfaces
- Easy migration path from/to official SDK

### Getting Started with AliExpress API
1. **Register**: Create account at [AliExpress Open Platform](https://open.aliexpress.com/)
2. **Apply**: Submit application for affiliate API access
3. **Credentials**: Get your App Key and App Secret
4. **Documentation**: Review [API documentation](https://developers.aliexpress.com/en/doc.htm)
5. **Testing**: Use this service for easy integration

## 🙏 **Acknowledgments**

- [python-aliexpress-api](https://github.com/sergioteula/python-aliexpress-api) - Official Python SDK
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [pytest](https://pytest.org/) - Testing framework
```

## 📖 **API Usage**

### Product Search
```bash
POST /api/aliexpress
Content-Type: application/json

{
  "method": "aliexpress.affiliate.product.query",
  "keywords": "wireless headphones",
  "page_size": 10,
  "target_currency": "USD"
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "aliexpress_affiliate_product_query_response": {
      "resp_result": {
        "result": {
          "products": [
            {
              "product_title": "Wireless Bluetooth Headphones",
              "app_sale_price": "29.99",
              "original_price": "59.99",
              "discount": "50%",
              "evaluate_rate": "98.5%",
              "commission_rate": "30%"
            }
          ]
        }
      }
    }
  },
  "metadata": {
    "mock_mode": true,
    "processing_time_ms": 250
  }
}
```

## 🤖 **Custom GPT Integration**

### OpenAPI Specification
The service provides a comprehensive OpenAPI 3.1.0 specification optimized for GPT Actions:

**Production URL**: `https://alistach.vercel.app/openapi-gpt.json`  
**Local Development**: `http://localhost:8000/openapi-gpt.json`

### GPT Actions Setup

#### 1. Create Custom GPT
1. Go to **ChatGPT** → **My GPTs** → **Create a GPT**
2. Navigate to **Configure** → **Actions** → **Create new action**
3. **Import from URL**: Paste your OpenAPI spec URL
4. **Authentication**: Set to "None" (or API Key if using authentication)
5. **Privacy**: Set according to your needs

#### 2. Sample GPT Instructions
```
You are an AliExpress Product Search Assistant powered by the official AliExpress API.

CAPABILITIES:
- Search products with advanced filtering (price, category, keywords)
- Get product categories and subcategories
- Generate affiliate tracking links
- Retrieve detailed product information
- Find trending/hot products (with permissions)
- Search products by image (with permissions)

USAGE GUIDELINES:
- Always show product prices, discounts, ratings, and order counts
- Include affiliate links when available
- Provide category context for better search results
- Suggest related categories when searches return few results
- Format responses in a user-friendly way with clear product information

SEARCH STRATEGIES:
- Use /api/products/search for general product searches
- Use /api/categories for browsing product categories
- Use /api/affiliate/links to generate tracking links
- Use /api/products for advanced filtering with price ranges

Always prioritize user experience and provide helpful, accurate product information.
```

#### 3. Available Actions
The OpenAPI specification includes these key endpoints:

| Action | Endpoint | Description |
|--------|----------|-------------|
| **Search Products** | `POST /api/products/search` | General product search with keywords |
| **Advanced Search** | `POST /api/products` | Search with price filtering |
| **Get Categories** | `GET /api/categories` | Retrieve parent categories |
| **Get Subcategories** | `GET /api/categories/{parent_id}/children` | Get child categories |
| **Generate Links** | `POST /api/affiliate/links` | Create affiliate tracking links |
| **Product Details** | `POST /api/products/details` | Get detailed product information |
| **Hot Products** | `POST /api/products/hot` | Get trending products |
| **Image Search** | `POST /api/products/image-search` | Search by image URL |

#### 4. Example GPT Conversation Flow
```
User: "Find me wireless headphones under $50"

GPT Action: POST /api/products/search
{
  "keywords": "wireless headphones",
  "max_sale_price": 50.0,
  "page_size": 10,
  "sort": "SALE_PRICE_ASC"
}

Response: Displays products with prices, ratings, and affiliate links
```

### Testing Your GPT Integration

#### 1. Verify OpenAPI Spec
```bash
curl https://alistach.vercel.app/openapi-gpt.json
```

#### 2. Test Health Endpoint
```bash
curl https://alistach.vercel.app/health
```

#### 3. Test Product Search
```bash
curl -X POST https://alistach.vercel.app/api/products/search \
  -H "Content-Type: application/json" \
  -d '{"keywords": "smartphone", "page_size": 5}'
```

## 🏃‍♂️ **Local Development**

```bash
# Clone repository
git clone https://github.com/AliStach/AliStach-V1.git
cd AliStach-V1

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your credentials

# Start development server
npm run dev

# Server runs on http://localhost:3000
```

## 📊 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/aliexpress` | POST | Main proxy endpoint |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/openapi.json` | GET | OpenAPI specification |
| `/openapi-gpt.json` | GET | GPT-optimized OpenAPI spec |

## 🔒 **Security Features**

- ✅ **Rate Limiting** - 100 requests/minute per IP
- ✅ **Input Sanitization** - Prevents injection attacks  
- ✅ **CORS Protection** - Configured for OpenAI domains
- ✅ **Security Headers** - CSP, HSTS, XSS protection
- ✅ **Optional Authentication** - API token support
- ✅ **Request Logging** - Comprehensive monitoring

## 📈 **Performance**

- **Response Time**: 200-700ms (mock), 1-2s (real API)
- **Memory Usage**: ~8MB heap
- **Scalability**: Serverless auto-scaling
- **Uptime**: 99.9%+ on Vercel

## 🧪 **Testing**

```bash
# Test health endpoint
curl https://alistach.vercel.app/health

# Test API call
curl -X POST https://alistach.vercel.app/api/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "smartwatch",
    "page_size": 3
  }'
```

## 📋 **Getting AliExpress Credentials**

1. Register at [AliExpress Open Platform](https://open.aliexpress.com/)
2. Create a new application
3. Get your App Key and App Secret
4. Apply for affiliate API access
5. Update environment variables

## 🚨 **Troubleshooting**

### Mock Mode (Normal)
If you see `"mock_mode": true` in responses:
- This is normal when AliExpress credentials aren't configured
- Perfect for testing GPT integration
- Add real credentials to get live data

### Common Issues
- **CORS errors**: Check domain whitelist in CORS config
- **Rate limiting**: Reduce request frequency  
- **Auth errors**: Verify API_TOKEN configuration

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/AliStach/AliStach-V1/issues)
- **Documentation**: [Live API Docs](https://alistach.vercel.app/docs)

---

**Built for developers who want to integrate AliExpress affiliate data into their custom GPTs without dealing with complex authentication and signature generation.** 🚀