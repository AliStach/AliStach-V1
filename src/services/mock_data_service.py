"""Mock data service for testing and development without real AliExpress credentials."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import random


class MockDataService:
    """Provides realistic mock data for AliExpress API responses."""
    
    # Mock categories data
    PARENT_CATEGORIES = [
        {"category_id": "1", "category_name": "Apparel & Accessories"},
        {"category_id": "2", "category_name": "Automobiles & Motorcycles"},
        {"category_id": "3", "category_name": "Beauty & Health"},
        {"category_id": "4", "category_name": "Computer & Office"},
        {"category_id": "5", "category_name": "Consumer Electronics"},
        {"category_id": "6", "category_name": "Home & Garden"},
        {"category_id": "7", "category_name": "Jewelry & Watches"},
        {"category_id": "8", "category_name": "Luggage & Bags"},
        {"category_id": "9", "category_name": "Mother & Kids"},
        {"category_id": "10", "category_name": "Phones & Telecommunications"},
        {"category_id": "11", "category_name": "Shoes"},
        {"category_id": "12", "category_name": "Sports & Entertainment"},
        {"category_id": "13", "category_name": "Toys & Hobbies"},
        {"category_id": "14", "category_name": "Home Improvement"},
        {"category_id": "15", "category_name": "Lights & Lighting"},
    ]
    
    CHILD_CATEGORIES = {
        "5": [  # Consumer Electronics
            {"category_id": "5001", "category_name": "Headphones & Earphones", "parent_category_id": "5"},
            {"category_id": "5002", "category_name": "Smart Watches", "parent_category_id": "5"},
            {"category_id": "5003", "category_name": "Portable Audio & Video", "parent_category_id": "5"},
            {"category_id": "5004", "category_name": "Camera & Photo", "parent_category_id": "5"},
            {"category_id": "5005", "category_name": "Home Audio & Video", "parent_category_id": "5"},
        ],
        "10": [  # Phones & Telecommunications
            {"category_id": "10001", "category_name": "Mobile Phones", "parent_category_id": "10"},
            {"category_id": "10002", "category_name": "Phone Cases", "parent_category_id": "10"},
            {"category_id": "10003", "category_name": "Phone Cables", "parent_category_id": "10"},
            {"category_id": "10004", "category_name": "Power Banks", "parent_category_id": "10"},
            {"category_id": "10005", "category_name": "Phone Holders & Stands", "parent_category_id": "10"},
        ],
        "4": [  # Computer & Office
            {"category_id": "4001", "category_name": "Laptops", "parent_category_id": "4"},
            {"category_id": "4002", "category_name": "Computer Peripherals", "parent_category_id": "4"},
            {"category_id": "4003", "category_name": "Office Electronics", "parent_category_id": "4"},
            {"category_id": "4004", "category_name": "Tablet Accessories", "parent_category_id": "4"},
        ],
    }
    
    # Mock product templates
    PRODUCT_TEMPLATES = [
        {
            "title_template": "Wireless Bluetooth {adjective} Headphones",
            "category_id": "5001",
            "adjectives": ["Premium", "Sport", "Gaming", "Studio", "Noise Cancelling"],
            "price_range": (19.99, 89.99),
            "commission_rate": "8%",
        },
        {
            "title_template": "{adjective} Smart Watch Fitness Tracker",
            "category_id": "5002",
            "adjectives": ["Pro", "Ultra", "Sport", "Health", "Advanced"],
            "price_range": (29.99, 199.99),
            "commission_rate": "10%",
        },
        {
            "title_template": "{adjective} Smartphone {storage}GB",
            "category_id": "10001",
            "adjectives": ["5G", "Pro", "Max", "Ultra", "Plus"],
            "storage": ["128", "256", "512"],
            "price_range": (199.99, 899.99),
            "commission_rate": "5%",
        },
        {
            "title_template": "USB-C {adjective} Fast Charging Cable",
            "category_id": "10003",
            "adjectives": ["Braided", "Magnetic", "LED", "Premium", "Heavy Duty"],
            "price_range": (4.99, 19.99),
            "commission_rate": "15%",
        },
        {
            "title_template": "{capacity}mAh Power Bank {adjective}",
            "category_id": "10004",
            "capacity": ["10000", "20000", "30000", "50000"],
            "adjectives": ["Fast Charge", "Solar", "Wireless", "Compact", "Ultra Slim"],
            "price_range": (15.99, 49.99),
            "commission_rate": "12%",
        },
    ]
    
    @classmethod
    def get_parent_categories(cls) -> List[Dict[str, Any]]:
        """Get mock parent categories."""
        return cls.PARENT_CATEGORIES.copy()
    
    @classmethod
    def get_child_categories(cls, parent_id: str) -> List[Dict[str, Any]]:
        """Get mock child categories for a parent."""
        return cls.CHILD_CATEGORIES.get(parent_id, []).copy()
    
    @classmethod
    def generate_product(cls, template: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Generate a single mock product from a template."""
        # Generate title
        title = template["title_template"]
        if "{adjective}" in title:
            adjective = random.choice(template["adjectives"])
            title = title.replace("{adjective}", adjective)
        if "{storage}" in title:
            storage = random.choice(template.get("storage", ["128"]))
            title = title.replace("{storage}", storage)
        if "{capacity}" in title:
            capacity = random.choice(template.get("capacity", ["10000"]))
            title = title.replace("{capacity}", capacity)
        
        # Generate prices
        min_price, max_price = template["price_range"]
        original_price = round(random.uniform(min_price * 1.5, max_price * 2), 2)
        sale_price = round(random.uniform(min_price, max_price), 2)
        discount = round((1 - sale_price / original_price) * 100)
        
        # Generate ratings and orders
        evaluate_rate = round(random.uniform(92.0, 99.9), 1)
        orders = random.randint(100, 50000)
        
        # Generate product ID
        product_id = f"100500{random.randint(1000000000, 9999999999)}"
        
        return {
            "product_id": product_id,
            "product_title": title,
            "product_main_image_url": f"https://ae01.alicdn.com/kf/{product_id}.jpg",
            "product_video_url": f"https://video.aliexpress-media.com/{product_id}.mp4" if random.random() > 0.7 else None,
            "product_small_image_urls": [
                f"https://ae01.alicdn.com/kf/{product_id}_{i}.jpg" for i in range(1, 5)
            ],
            "product_url": f"https://www.aliexpress.com/item/{product_id}.html",
            "sale_price": str(sale_price),
            "original_price": str(original_price),
            "discount": f"{discount}%",
            "target_sale_price": str(sale_price),
            "target_original_price": str(original_price),
            "target_sale_price_currency": "USD",
            "evaluate_rate": f"{evaluate_rate}%",
            "orders": orders,
            "commission_rate": template["commission_rate"],
            "shop_id": f"shop_{random.randint(100000, 999999)}",
            "shop_url": f"https://www.aliexpress.com/store/{random.randint(100000, 999999)}",
            "platform_product_type": "TMALL" if random.random() > 0.5 else "ALIEXPRESS",
            "relevant_market_commission_rate": template["commission_rate"],
            "category_id": template["category_id"],
        }
    
    @classmethod
    def search_products(
        cls,
        keywords: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page_no: int = 1,
        page_size: int = 20,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate mock product search results."""
        # Filter templates based on criteria
        templates = cls.PRODUCT_TEMPLATES.copy()
        
        if category_id:
            templates = [t for t in templates if t["category_id"] == category_id]
        
        if min_price or max_price:
            filtered = []
            for t in templates:
                t_min, t_max = t["price_range"]
                if min_price and t_max < min_price:
                    continue
                if max_price and t_min > max_price:
                    continue
                filtered.append(t)
            templates = filtered
        
        # Generate products
        num_products = min(page_size, len(templates) * 3)
        products = []
        
        for i in range(num_products):
            template = random.choice(templates)
            product = cls.generate_product(template, i)
            products.append(product)
        
        # Sort if requested
        if sort == "SALE_PRICE_ASC":
            products.sort(key=lambda p: float(p["sale_price"]))
        elif sort == "SALE_PRICE_DESC":
            products.sort(key=lambda p: float(p["sale_price"]), reverse=True)
        elif sort == "LAST_VOLUME_ASC":
            products.sort(key=lambda p: p["orders"])
        elif sort == "LAST_VOLUME_DESC":
            products.sort(key=lambda p: p["orders"], reverse=True)
        
        # Pagination
        total_results = len(products) * 10  # Simulate more results
        start_idx = (page_no - 1) * page_size
        end_idx = start_idx + page_size
        page_products = products[start_idx:end_idx] if start_idx < len(products) else []
        
        return {
            "current_page_no": page_no,
            "current_record_count": len(page_products),
            "total_record_count": total_results,
            "total_page_no": (total_results + page_size - 1) // page_size,
            "products": page_products
        }
    
    @classmethod
    def get_product_details(cls, product_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate mock product details."""
        details = []
        
        for product_id in product_ids:
            # Use a template to generate consistent data
            template = random.choice(cls.PRODUCT_TEMPLATES)
            product = cls.generate_product(template, 0)
            product["product_id"] = product_id
            
            # Add detailed information
            product.update({
                "product_description": f"High quality {product['product_title']} with excellent features and performance.",
                "shipping_info": {
                    "free_shipping": random.random() > 0.3,
                    "estimated_delivery_days": random.randint(7, 30),
                    "ship_from_country": random.choice(["CN", "US", "ES", "RU"]),
                },
                "seller_info": {
                    "seller_id": f"seller_{random.randint(100000, 999999)}",
                    "seller_name": f"Official Store {random.randint(1, 100)}",
                    "positive_feedback_rate": f"{random.uniform(95.0, 99.9):.1f}%",
                },
                "specifications": [
                    {"name": "Brand", "value": random.choice(["Generic", "OEM", "Brand Name"])},
                    {"name": "Material", "value": random.choice(["Plastic", "Metal", "Silicone", "Mixed"])},
                    {"name": "Color", "value": random.choice(["Black", "White", "Blue", "Red", "Silver"])},
                ],
            })
            
            details.append(product)
        
        return details
    
    @classmethod
    def generate_affiliate_links(cls, urls: List[str]) -> List[Dict[str, Any]]:
        """Generate mock affiliate links."""
        links = []
        
        for url in urls:
            # Extract product ID if possible
            product_id = url.split("/")[-1].replace(".html", "") if "/" in url else "mock_product"
            
            links.append({
                "promotion_link": f"https://s.click.aliexpress.com/e/_mock_{random.randint(100000, 999999)}",
                "source_value": url,
                "tracking_id": "gpt_chat",
                "product_id": product_id,
            })
        
        return links
    
    @classmethod
    def get_hot_products(
        cls,
        keywords: Optional[str] = None,
        max_price: Optional[float] = None,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Generate mock hot products."""
        # Hot products are just high-order products
        result = cls.search_products(
            keywords=keywords,
            max_price=max_price,
            page_size=page_size,
            sort="LAST_VOLUME_DESC"
        )
        
        # Mark as hot products
        for product in result["products"]:
            product["is_hot"] = True
            product["hot_rank"] = random.randint(1, 100)
        
        return result
    
    @classmethod
    def smart_match_product(cls, product_url: str) -> Dict[str, Any]:
        """Generate mock smart match result."""
        # Generate a product based on URL
        template = random.choice(cls.PRODUCT_TEMPLATES)
        product = cls.generate_product(template, 0)
        
        return {
            "matched_product": product,
            "confidence_score": random.uniform(0.85, 0.99),
            "original_url": product_url,
            "matched_url": product["product_url"],
        }
    
    @classmethod
    def get_orders(
        cls,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Generate mock order data."""
        orders = []
        
        for i in range(min(page_size, 5)):  # Generate fewer mock orders
            order_id = f"ORD{random.randint(100000000, 999999999)}"
            product_template = random.choice(cls.PRODUCT_TEMPLATES)
            
            orders.append({
                "order_id": order_id,
                "product_title": product_template["title_template"].replace("{adjective}", "Premium"),
                "order_amount": round(random.uniform(20.0, 200.0), 2),
                "commission_amount": round(random.uniform(2.0, 20.0), 2),
                "commission_rate": product_template["commission_rate"],
                "order_status": random.choice(["Paid", "Shipped", "Completed", "Refunded"]),
                "order_time": datetime.now().isoformat(),
                "tracking_id": "gpt_chat",
            })
        
        return {
            "orders": orders,
            "current_page_no": page_no,
            "total_record_count": len(orders) * 3,  # Simulate more orders
            "total_page_no": 3,
        }
