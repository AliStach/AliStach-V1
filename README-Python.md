# AliExpress Affiliate API - Production Ready 🚀

A comprehensive, production-grade Python service for the AliExpress Affiliate API using the official [python-aliexpress-api](https://github.com/sergioteula/python-aliexpress-api) SDK. This service provides both a programmatic interface and a full-featured REST API with 15+ endpoints for accessing AliExpress affiliate data.

## 🚀 Features

- **🔗 Official SDK Integration**: Uses the official python-aliexpress-api library
- **🏗️ Clean Architecture**: Modular design with services, models, and utilities
- **⚡ FastAPI REST API**: Production-ready API with 15+ endpoints and automatic documentation
- **🔐 Secure Configuration**: Environment-based credential management with python-dotenv
- **🛡️ Comprehensive Error Handling**: Structured error responses and detailed logging
- **📝 Type Safety**: Full type hints and Pydantic models throughout
- **🌐 Real AliExpress Data**: Connects to live AliExpress Affiliate API
- **📊 Advanced Filtering**: Price ranges, categories, sorting, and pagination
- **🔗 Affiliate Link Generation**: Convert product URLs to trackable affiliate links
- **🔥 Hot Products**: Access trending products (with permissions)
- **📦 Product Details**: Detailed product information and specifications
- **📈 Order Tracking**: Monitor affiliate orders and commissions (with permissions)

## 📋 Requirements

- Python 3.8+
- AliExpress Affiliate API credentials (App Key, App Secret)
- pip or conda for package management

## 🛠️ Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd aliexpress-python-refactor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Copy the example file
   cp .env.python.example .env
   
   # Edit .env with your AliExpress credentials
   ALIEXPRESS_APP_KEY=your_app_key_here
   ALIEXPRESS_APP_SECRET=your_app_secret_here
   ALIEXPRESS_TRACKING_ID=gpt_chat
   ```

## 🔧 Configuration

The service uses environment variables for configuration. Create a `.env` file with:

```env
# Required
ALIEXPRESS_APP_KEY=your_app_key_here
ALIEXPRESS_APP_SECRET=your_app_secret_here

# Optional (with defaults)
ALIEXPRESS_TRACKING_ID=gpt_chat
ALIEXPRESS_LANGUAGE=EN
ALIEXPRESS_CURRENCY=USD
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### API Permissions & Requirements

Some endpoints require special AliExpress API permissions:

| Feature | Permission Level | How to Enable |
|---------|------------------|---------------|
| **Basic Search** | Standard | ✅ Available with basic affiliate account |
| **Categories** | Standard | ✅ Available with basic affiliate account |
| **Affiliate Links** | Standard | ✅ Available with basic affiliate account |
| **Product Details** | Standard | ✅ Available with basic affiliate account |
| **Hot Products** | Advanced | ❌ Contact AliExpress for special permissions |
| **Order Tracking** | Advanced | ❌ Requires affiliate account with commission tracking |
| **Smart Match** | Advanced | ❌ Requires advanced API access + device_id |

### Supported Languages and Currencies

**Languages**: EN, RU, PT, ES, FR, ID, IT, TH, JA, AR, VI, TR, DE, HE, KO, NL, PL, MX, CL, IN

**Currencies**: USD, GBP, CAD, EUR, UAH, MXN, TRY, RUB, BRL, AUD, INR, JPY, IDR, SEK, KRW

## 🎯 Quick Start

### 1. Test with Demo Script

Run the demo script to verify your setup:

```bash
python scripts/demo.py
```

Expected output:
```
🔧 Loading configuration...
✅ Configuration loaded successfully
   - App Key: 520934
   - Language: EN
   - Currency: USD
   - Tracking ID: gpt_chat

🚀 Initializing AliExpress service...
✅ AliExpress service initialized successfully

📂 Parent Categories:

ID: 2 | Name: Food
ID: 3 | Name: Apparel & Accessories
ID: 6 | Name: Home Appliances
...

📁 Child Categories of Food:
  ↳ ID: 101 | Name: Beverages
  ↳ ID: 102 | Name: Snacks
...

✅ Demo completed successfully! Found 40 parent categories.
```

### 2. Start the FastAPI Server

```bash
python -m src.api.main
```

The server will start at `http://localhost:8000`

### 3. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all categories
curl http://localhost:8000/api/categories

# Get child categories
curl http://localhost:8000/api/categories/3/children

# Search products
curl -X POST http://localhost:8000/api/products/search \
  -H "Content-Type: application/json" \
  -d '{"keywords": "wireless headphones", "page_size": 10}'
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| **System** |
| GET | `/health` | Service health check and status |
| GET | `/docs` | Interactive API documentation |
| **Categories** |
| GET | `/api/categories` | Get all parent categories |
| GET | `/api/categories/{id}/children` | Get child categories |
| **Products** |
| GET/POST | `/api/products/search` | Basic product search |
| GET/POST | `/api/products` | Enhanced search with price filters |
| GET | `/api/products/details/{id}` | Single product details |
| POST | `/api/products/details` | Bulk product details (up to 20) |
| GET/POST | `/api/products/hot` | Hot/trending products* |
| **Affiliate** |
| GET | `/api/affiliate/link` | Generate single affiliate link |
| POST | `/api/affiliate/links` | Generate multiple affiliate links |
| GET | `/api/smart-match` | Smart product URL matching |
| GET | `/api/orders` | Get affiliate orders* |

*Requires special AliExpress API permissions

### Example Responses

**Categories Response:**
```json
{
  "success": true,
  "data": [
    {
      "category_id": "2",
      "category_name": "Food",
      "parent_id": null
    }
  ],
  "metadata": {
    "total_count": 40,
    "request_id": "uuid",
    "timestamp": "2025-11-02T10:35:42Z"
  }
}
```

**Product Search Response:**
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "product_id": "123456",
        "product_title": "Wireless Bluetooth Headphones",
        "product_url": "https://...",
        "price": "29.99",
        "currency": "USD"
      }
    ],
    "total_record_count": 1500,
    "current_page": 1,
    "page_size": 20
  }
}
```

## 💻 Programmatic Usage

### Using the Service Class

```python
from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService

# Load configuration
config = Config.from_env()
service = AliExpressService(config)

# Get categories
categories = service.get_parent_categories()
for category in categories:
    print(f"ID: {category.category_id}, Name: {category.category_name}")

# Search products
results = service.search_products(
    keywords="wireless headphones",
    page_size=10
)
print(f"Found {len(results.products)} products")
```

### Error Handling

```python
from src.services.aliexpress_service import AliExpressServiceException

try:
    categories = service.get_parent_categories()
except AliExpressServiceException as e:
    print(f"Service error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🏗️ Project Structure

```
src/
├── __init__.py
├── api/                    # FastAPI application
│   ├── main.py            # Main FastAPI app
│   └── endpoints/         # API route handlers
│       └── categories.py
├── services/              # Business logic
│   └── aliexpress_service.py
├── models/                # Data models
│   └── responses.py
└── utils/                 # Utilities
    ├── config.py          # Configuration management
    └── response_formatter.py

scripts/
└── demo.py               # Demo script

tests/                    # Test suite
├── unit/
├── integration/
└── fixtures/
```

## 🧪 Testing

### Run Demo Script
```bash
python scripts/demo.py
```

### Test API Endpoints
```bash
# Install httpx for testing
pip install httpx

# Create a simple test script
python -c "
import httpx
response = httpx.get('http://localhost:8000/health')
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the project root directory
   cd /path/to/project
   python scripts/demo.py
   ```

2. **Missing Environment Variables**
   ```bash
   # Check your .env file exists and has the required variables
   cat .env
   ```

3. **API Connection Issues**
   ```bash
   # Test your credentials with the demo script first
   python scripts/demo.py
   ```

4. **Port Already in Use**
   ```bash
   # Change the port in .env file
   API_PORT=8001
   ```

### Logging

The service includes comprehensive logging. Check the console output for detailed information about API calls and errors.

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Use environment variables for all sensitive configuration
- The service includes input validation and error handling
- Consider adding authentication for production use

## 📈 Performance

- The service uses the official SDK's connection pooling
- Responses include timing metadata
- Consider implementing caching for frequently accessed data
- Rate limiting is handled by the AliExpress API

## 🚀 Deployment

### Docker Deployment

```bash
# Build and run with Docker
docker build -t aliexpress-api .
docker run -p 8000:8000 --env-file .env aliexpress-api

# Or use docker-compose
docker-compose up -d
```

### Render Deployment

1. Connect your GitHub repository to Render
2. Use the provided `render.yaml` configuration
3. Set environment variables in Render dashboard:
   - `ALIEXPRESS_APP_KEY`
   - `ALIEXPRESS_APP_SECRET`
4. Deploy automatically

### Vercel Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set environment variables
vercel env add ALIEXPRESS_APP_KEY
vercel env add ALIEXPRESS_APP_SECRET
```

### Manual Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ALIEXPRESS_APP_KEY="your_key"
export ALIEXPRESS_APP_SECRET="your_secret"

# Run production server
python -m src.api.main
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [python-aliexpress-api](https://github.com/sergioteula/python-aliexpress-api) - Official AliExpress API SDK
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation using Python type hints