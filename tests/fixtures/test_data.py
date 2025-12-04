"""Test data generators for testing."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import string


def generate_product_id() -> str:
    """Generate a random product ID."""
    return f"100500{random.randint(1000000000, 9999999999)}"


def generate_category_id() -> str:
    """Generate a random category ID."""
    return str(random.randint(100, 999))


def generate_product_data(
    product_id: str = None,
    title: str = None,
    price: float = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate product data for testing.
    
    Args:
        product_id: Optional product ID
        title: Optional product title
        price: Optional product price
        **kwargs: Additional product fields
    
    Returns:
        Dictionary with product data
    """
    product_id = product_id or generate_product_id()
    title = title or f"Test Product {random.randint(1, 1000)}"
    price = price or round(random.uniform(10.0, 500.0), 2)
    
    data = {
        "product_id": product_id,
        "product_title": title,
        "product_url": f"https://www.aliexpress.com/item/{product_id}.html",
        "price": price,
        "original_price": round(price * random.uniform(1.5, 3.0), 2),
        "currency": "USD",
        "image_url": f"https://example.com/images/{product_id}.jpg",
        "rating": round(random.uniform(4.0, 5.0), 1),
        "order_count": random.randint(100, 10000),
        "commission_rate": round(random.uniform(3.0, 15.0), 1)
    }
    
    data.update(kwargs)
    return data


def generate_category_data(
    category_id: str = None,
    name: str = None,
    parent_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate category data for testing.
    
    Args:
        category_id: Optional category ID
        name: Optional category name
        parent_id: Optional parent category ID
        **kwargs: Additional category fields
    
    Returns:
        Dictionary with category data
    """
    category_id = category_id or generate_category_id()
    name = name or f"Test Category {random.randint(1, 100)}"
    
    data = {
        "category_id": category_id,
        "category_name": name,
        "parent_category_id": parent_id
    }
    
    data.update(kwargs)
    return data


def generate_affiliate_link_data(
    original_url: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate affiliate link data for testing.
    
    Args:
        original_url: Optional original URL
        **kwargs: Additional link fields
    
    Returns:
        Dictionary with affiliate link data
    """
    product_id = generate_product_id()
    original_url = original_url or f"https://www.aliexpress.com/item/{product_id}.html"
    
    # Generate random affiliate code
    affiliate_code = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    data = {
        "original_url": original_url,
        "affiliate_url": f"https://s.click.aliexpress.com/e/_{affiliate_code}",
        "tracking_id": "test_tracking",
        "commission_rate": round(random.uniform(3.0, 15.0), 1)
    }
    
    data.update(kwargs)
    return data


def generate_search_request_data(
    keywords: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate search request data for testing.
    
    Args:
        keywords: Optional search keywords
        **kwargs: Additional search parameters
    
    Returns:
        Dictionary with search request data
    """
    keywords = keywords or f"test product {random.randint(1, 100)}"
    
    data = {
        "keywords": keywords,
        "page_size": random.randint(10, 50),
        "page_no": 1,
        "sort": random.choice(["SALE_PRICE_ASC", "SALE_PRICE_DESC", "LAST_VOLUME_ASC", "LAST_VOLUME_DESC"])
    }
    
    data.update(kwargs)
    return data


def generate_product_list(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate a list of product data for testing.
    
    Args:
        count: Number of products to generate
    
    Returns:
        List of product dictionaries
    """
    return [generate_product_data() for _ in range(count)]


def generate_category_list(count: int = 5, parent_id: str = None) -> List[Dict[str, Any]]:
    """
    Generate a list of category data for testing.
    
    Args:
        count: Number of categories to generate
        parent_id: Optional parent category ID for all categories
    
    Returns:
        List of category dictionaries
    """
    return [generate_category_data(parent_id=parent_id) for _ in range(count)]


def generate_cache_entry(
    key: str = None,
    value: Any = None,
    ttl: int = 3600
) -> Dict[str, Any]:
    """
    Generate cache entry data for testing.
    
    Args:
        key: Optional cache key
        value: Optional cache value
        ttl: Time to live in seconds
    
    Returns:
        Dictionary with cache entry data
    """
    key = key or f"test_key_{random.randint(1, 1000)}"
    value = value or {"test": "data"}
    
    now = datetime.utcnow()
    
    return {
        "key": key,
        "value": value,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=ttl)).isoformat(),
        "hit_count": 0
    }


def generate_api_response(
    success: bool = True,
    data: Any = None,
    error: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate API response data for testing.
    
    Args:
        success: Whether the response is successful
        data: Optional response data
        error: Optional error information
    
    Returns:
        Dictionary with API response data
    """
    response = {
        "success": success,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time_ms": random.randint(50, 500)
        }
    }
    
    if success:
        response["data"] = data or generate_product_list(5)
    else:
        response["error"] = error or {
            "code": "INTERNAL_ERROR",
            "message": "An error occurred",
            "details": {}
        }
    
    return response


# Predefined test data sets
SAMPLE_PRODUCTS = [
    generate_product_data(
        product_id="1005003091506814",
        title="Wireless Bluetooth Headphones",
        price=29.99
    ),
    generate_product_data(
        product_id="1005004567890123",
        title="Smart Watch Fitness Tracker",
        price=49.99
    ),
    generate_product_data(
        product_id="1005005678901234",
        title="USB-C Fast Charging Cable",
        price=9.99
    )
]

SAMPLE_CATEGORIES = [
    generate_category_data(category_id="123", name="Electronics"),
    generate_category_data(category_id="456", name="Fashion"),
    generate_category_data(category_id="789", name="Home & Garden")
]

SAMPLE_CHILD_CATEGORIES = [
    generate_category_data(category_id="789", name="Smartphones", parent_id="123"),
    generate_category_data(category_id="790", name="Laptops", parent_id="123"),
    generate_category_data(category_id="791", name="Headphones", parent_id="123")
]
