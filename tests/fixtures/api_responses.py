"""Mock API response fixtures for testing."""

from typing import Dict, List, Any


def mock_category_response() -> Dict[str, Any]:
    """Mock AliExpress category API response."""
    return {
        "aliexpress_affiliate_category_get_response": {
            "resp_result": {
                "result": {
                    "categories": [
                        {
                            "category_id": "123",
                            "category_name": "Electronics",
                            "parent_category_id": None
                        },
                        {
                            "category_id": "456",
                            "category_name": "Fashion",
                            "parent_category_id": None
                        }
                    ]
                },
                "resp_code": "200",
                "resp_msg": "success"
            }
        }
    }


def mock_child_category_response(parent_id: str = "123") -> Dict[str, Any]:
    """Mock AliExpress child category API response."""
    return {
        "aliexpress_affiliate_category_get_response": {
            "resp_result": {
                "result": {
                    "categories": [
                        {
                            "category_id": "789",
                            "category_name": "Smartphones",
                            "parent_category_id": parent_id
                        },
                        {
                            "category_id": "790",
                            "category_name": "Laptops",
                            "parent_category_id": parent_id
                        }
                    ]
                },
                "resp_code": "200",
                "resp_msg": "success"
            }
        }
    }


def mock_product_search_response() -> Dict[str, Any]:
    """Mock AliExpress product search API response."""
    return {
        "aliexpress_affiliate_product_query_response": {
            "resp_result": {
                "result": {
                    "products": [
                        {
                            "product_id": "1005003091506814",
                            "product_title": "Wireless Bluetooth Headphones",
                            "product_detail_url": "https://www.aliexpress.com/item/1005003091506814.html",
                            "target_sale_price": "29.99",
                            "target_sale_price_currency": "USD",
                            "target_original_price": "59.99",
                            "product_main_image_url": "https://example.com/image.jpg",
                            "evaluate_rate": "98.5",
                            "30days_total_sold_quantity": "1000",
                            "commission_rate": "5.0"
                        },
                        {
                            "product_id": "1005004567890123",
                            "product_title": "Smart Watch Fitness Tracker",
                            "product_detail_url": "https://www.aliexpress.com/item/1005004567890123.html",
                            "target_sale_price": "49.99",
                            "target_sale_price_currency": "USD",
                            "target_original_price": "99.99",
                            "product_main_image_url": "https://example.com/watch.jpg",
                            "evaluate_rate": "97.0",
                            "30days_total_sold_quantity": "500",
                            "commission_rate": "8.0"
                        }
                    ],
                    "total_record_count": 2
                },
                "resp_code": "200",
                "resp_msg": "success"
            }
        }
    }


def mock_product_details_response() -> Dict[str, Any]:
    """Mock AliExpress product details API response."""
    return {
        "aliexpress_affiliate_productdetail_get_response": {
            "resp_result": {
                "result": {
                    "products": [
                        {
                            "product_id": "1005003091506814",
                            "product_title": "Wireless Bluetooth Headphones",
                            "product_detail_url": "https://www.aliexpress.com/item/1005003091506814.html",
                            "target_sale_price": "29.99",
                            "target_sale_price_currency": "USD",
                            "target_original_price": "59.99",
                            "product_main_image_url": "https://example.com/image.jpg",
                            "product_video_url": "https://example.com/video.mp4",
                            "evaluate_rate": "98.5",
                            "30days_total_sold_quantity": "1000",
                            "commission_rate": "5.0",
                            "shop_id": "12345",
                            "shop_url": "https://www.aliexpress.com/store/12345"
                        }
                    ]
                },
                "resp_code": "200",
                "resp_msg": "success"
            }
        }
    }


def mock_affiliate_links_response() -> Dict[str, Any]:
    """Mock AliExpress affiliate link generation API response."""
    return {
        "aliexpress_affiliate_link_generate_response": {
            "resp_result": {
                "result": {
                    "promotion_links": [
                        {
                            "source_value": "https://www.aliexpress.com/item/1005003091506814.html",
                            "promotion_link": "https://s.click.aliexpress.com/e/_test_affiliate_link_1",
                            "tracking_id": "test_tracking"
                        },
                        {
                            "source_value": "https://www.aliexpress.com/item/1005004567890123.html",
                            "promotion_link": "https://s.click.aliexpress.com/e/_test_affiliate_link_2",
                            "tracking_id": "test_tracking"
                        }
                    ]
                },
                "resp_code": "200",
                "resp_msg": "success"
            }
        }
    }


def mock_hot_products_response() -> Dict[str, Any]:
    """Mock AliExpress hot products API response."""
    return {
        "aliexpress_affiliate_hotproduct_query_response": {
            "resp_result": {
                "result": {
                    "products": [
                        {
                            "product_id": "1005005678901234",
                            "product_title": "Trending Wireless Earbuds",
                            "product_detail_url": "https://www.aliexpress.com/item/1005005678901234.html",
                            "target_sale_price": "19.99",
                            "target_sale_price_currency": "USD",
                            "target_original_price": "39.99",
                            "product_main_image_url": "https://example.com/earbuds.jpg",
                            "evaluate_rate": "99.0",
                            "30days_total_sold_quantity": "5000",
                            "commission_rate": "10.0"
                        }
                    ],
                    "total_record_count": 1
                },
                "resp_code": "200",
                "resp_msg": "success"
            }
        }
    }


def mock_error_response(error_code: str = "500", error_msg: str = "Internal error") -> Dict[str, Any]:
    """Mock AliExpress API error response."""
    return {
        "error_response": {
            "code": error_code,
            "msg": error_msg,
            "sub_code": "isv.invalid-parameter",
            "sub_msg": "Invalid parameter"
        }
    }


def mock_rate_limit_response() -> Dict[str, Any]:
    """Mock AliExpress API rate limit response."""
    return mock_error_response(
        error_code="429",
        error_msg="Rate limit exceeded. Please try again later."
    )


def mock_permission_error_response() -> Dict[str, Any]:
    """Mock AliExpress API permission error response."""
    return mock_error_response(
        error_code="403",
        error_msg="App does not have permission to access this resource"
    )
