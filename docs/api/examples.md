# API Usage Examples

## Product Search

### Basic Search
```bash
curl -X POST https://alistach.vercel.app/api/products/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "wireless headphones",
    "page_size": 10
  }'
```

### Advanced Search with Filters
```bash
curl -X POST https://alistach.vercel.app/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "smartphone",
    "min_sale_price": 100.0,
    "max_sale_price": 500.0,
    "category_id": "509",
    "sort": "SALE_PRICE_ASC",
    "page_size": 20
  }'
```

## Categories

### Get Parent Categories
```bash
curl https://alistach.vercel.app/api/categories
```

### Get Child Categories
```bash
curl https://alistach.vercel.app/api/categories/509/children
```

## Affiliate Links

### Generate Multiple Links
```bash
curl -X POST https://alistach.vercel.app/api/affiliate/links \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.aliexpress.com/item/1005001234567890.html",
      "https://www.aliexpress.com/item/1005009876543210.html"
    ]
  }'
```

### Generate Single Link
```bash
curl "https://alistach.vercel.app/api/affiliate/link?url=https://www.aliexpress.com/item/1005001234567890.html"
```

## Python Examples

### Using requests library
```python
import requests

# Search products
response = requests.post(
    "https://alistach.vercel.app/api/products/search",
    json={
        "keywords": "laptop",
        "page_size": 10
    }
)

products = response.json()
for product in products["data"]["products"]:
    print(f"{product['product_title']} - ${product['price']}")
```

### Using the service directly
```python
from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService

config = Config.from_env()
service = AliExpressService(config)

# Search products
results = service.search_products(keywords="headphones", page_size=10)
for product in results.products:
    print(f"{product.product_title} - ${product.price}")
```

---

*Last Updated: December 4, 2025*
