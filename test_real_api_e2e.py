"""
Strict End-to-End Test of Real AliExpress API
Tests live endpoints through our proxy.
Reports only actual results - no assumptions, no fixes, no fallbacks.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Set up logging to capture everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import after setting environment
from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(endpoint, success, data=None, error=None):
    """Print test result."""
    status = "✓ SUCCESS" if success else "✗ FAILED"
    print(f"\n{status}: {endpoint}")
    
    if success and data:
        print(f"\nRaw Response Data:")
        print(json.dumps(data, indent=2, default=str))
    elif error:
        print(f"\nError Details:")
        print(f"  Type: {type(error).__name__}")
        print(f"  Message: {str(error)}")


def test_categories(service):
    """Test categories endpoint."""
    print_section("TEST 1: Categories Endpoint")
    
    try:
        logger.info("Calling get_parent_categories()...")
        categories = service.get_parent_categories()
        
        # Convert to dict for display
        data = {
            "total_categories": len(categories),
            "categories": [
                {
                    "category_id": cat.category_id,
                    "category_name": cat.category_name
                }
                for cat in categories[:5]  # Show first 5
            ]
        }
        
        print_result("GET /api/categories", True, data)
        return True, categories
        
    except Exception as e:
        print_result("GET /api/categories", False, error=e)
        logger.exception("Categories test failed")
        return False, None


def test_child_categories(service, parent_id="3"):
    """Test child categories endpoint."""
    print_section(f"TEST 2: Child Categories Endpoint (parent_id={parent_id})")
    
    try:
        logger.info(f"Calling get_child_categories(parent_id={parent_id})...")
        categories = service.get_child_categories(parent_id)
        
        # Convert to dict for display
        data = {
            "parent_id": parent_id,
            "total_child_categories": len(categories),
            "child_categories": [
                {
                    "category_id": cat.category_id,
                    "category_name": cat.category_name,
                    "parent_id": cat.parent_id
                }
                for cat in categories[:5]  # Show first 5
            ]
        }
        
        print_result(f"GET /api/categories/{parent_id}/children", True, data)
        return True, categories
        
    except Exception as e:
        print_result(f"GET /api/categories/{parent_id}/children", False, error=e)
        logger.exception("Child categories test failed")
        return False, None


def test_product_search(service, keywords="phone"):
    """Test product search endpoint."""
    print_section(f"TEST 3: Product Search Endpoint (keywords='{keywords}')")
    
    try:
        logger.info(f"Calling search_products(keywords='{keywords}')...")
        result = service.search_products(
            keywords=keywords,
            page_no=1,
            page_size=5,
            auto_generate_affiliate_links=False  # Test without affiliate links first
        )
        
        # Convert to dict for display
        data = {
            "total_record_count": result.total_record_count,
            "current_page": result.current_page,
            "page_size": result.page_size,
            "products_returned": len(result.products),
            "sample_products": [
                {
                    "product_id": p.product_id,
                    "product_title": p.product_title[:50] + "..." if len(p.product_title) > 50 else p.product_title,
                    "price": p.price,
                    "currency": p.currency,
                    "product_url": p.product_url[:80] + "..." if len(p.product_url) > 80 else p.product_url,
                    "commission_rate": p.commission_rate
                }
                for p in result.products[:3]  # Show first 3
            ]
        }
        
        print_result("GET /api/products/search", True, data)
        return True, result
        
    except Exception as e:
        print_result("GET /api/products/search", False, error=e)
        logger.exception("Product search test failed")
        return False, None


def test_product_details(service, product_ids):
    """Test product details endpoint."""
    print_section(f"TEST 4: Product Details Endpoint")
    
    if not product_ids:
        print("⚠ SKIPPED: No product IDs available from search")
        return False, None
    
    # Use first product ID
    test_ids = [product_ids[0]]
    
    try:
        logger.info(f"Calling get_products_details(product_ids={test_ids})...")
        details = service.get_products_details(test_ids)
        
        # Convert to dict for display
        data = {
            "requested_ids": test_ids,
            "products_returned": len(details),
            "product_details": [
                {
                    "product_id": p.product_id,
                    "product_title": p.product_title[:50] + "..." if len(p.product_title) > 50 else p.product_title,
                    "price": p.price,
                    "currency": p.currency,
                    "has_description": p.description is not None,
                    "has_gallery_images": p.gallery_images is not None and len(p.gallery_images) > 0,
                    "has_specifications": p.specifications is not None,
                    "has_shipping_info": p.shipping_info is not None,
                    "has_seller_info": p.seller_info is not None
                }
                for p in details
            ]
        }
        
        print_result("POST /api/products/details", True, data)
        return True, details
        
    except Exception as e:
        print_result("POST /api/products/details", False, error=e)
        logger.exception("Product details test failed")
        return False, None


def test_affiliate_links(service, product_urls):
    """Test affiliate link generator endpoint."""
    print_section(f"TEST 5: Affiliate Link Generator Endpoint")
    
    if not product_urls:
        print("⚠ SKIPPED: No product URLs available from search")
        return False, None
    
    # Use first product URL
    test_urls = [product_urls[0]]
    
    try:
        logger.info(f"Calling get_affiliate_links(urls={test_urls})...")
        links = service.get_affiliate_links(test_urls)
        
        # Convert to dict for display
        data = {
            "requested_urls": test_urls,
            "links_generated": len(links),
            "affiliate_links": [
                {
                    "original_url": link.original_url[:80] + "..." if len(link.original_url) > 80 else link.original_url,
                    "affiliate_url": link.affiliate_url[:80] + "..." if len(link.affiliate_url) > 80 else link.affiliate_url,
                    "tracking_id": link.tracking_id,
                    "commission_rate": link.commission_rate
                }
                for link in links
            ]
        }
        
        print_result("POST /api/affiliate/links", True, data)
        return True, links
        
    except Exception as e:
        print_result("POST /api/affiliate/links", False, error=e)
        logger.exception("Affiliate links test failed")
        return False, None


def main():
    """Run all end-to-end tests."""
    print("\n" + "=" * 80)
    print("  STRICT END-TO-END TEST: Real AliExpress API")
    print("  Testing live endpoints through our proxy")
    print("  No assumptions, no fixes, no fallbacks")
    print("=" * 80)
    
    # Display configuration
    print("\nConfiguration:")
    print(f"  ALIEXPRESS_APP_KEY: {os.getenv('ALIEXPRESS_APP_KEY', 'not set')[:10]}...")
    print(f"  ALIEXPRESS_APP_SECRET: {'set' if os.getenv('ALIEXPRESS_APP_SECRET') else 'not set'}")
    print(f"  ALIEXPRESS_TRACKING_ID: {os.getenv('ALIEXPRESS_TRACKING_ID', 'not set')}")
    
    # Initialize service
    try:
        print("\nInitializing AliExpress service...")
        config = Config.from_env()
        service = AliExpressService(config)
        print("✓ Service initialized with REAL API\n")
            
    except Exception as e:
        print(f"\n✗ FAILED to initialize service: {e}")
        logger.exception("Service initialization failed")
        return
    
    # Track results
    results = {
        "categories": False,
        "child_categories": False,
        "product_search": False,
        "product_details": False,
        "affiliate_links": False
    }
    
    # Test 1: Categories
    success, categories = test_categories(service)
    results["categories"] = success
    
    # Test 2: Child Categories (use first parent category if available)
    parent_id = "3"  # Default to category 3 (Apparel & Accessories)
    if success and categories and len(categories) > 0:
        parent_id = categories[0].category_id
    
    success, child_cats = test_child_categories(service, parent_id)
    results["child_categories"] = success
    
    # Test 3: Product Search
    success, search_result = test_product_search(service, "phone")
    results["product_search"] = success
    
    # Collect product IDs and URLs for subsequent tests
    product_ids = []
    product_urls = []
    if success and search_result and search_result.products:
        product_ids = [p.product_id for p in search_result.products]
        product_urls = [p.product_url for p in search_result.products]
    
    # Test 4: Product Details
    success, details = test_product_details(service, product_ids)
    results["product_details"] = success
    
    # Test 5: Affiliate Links
    success, links = test_affiliate_links(service, product_urls)
    results["affiliate_links"] = success
    
    # Final Summary
    print_section("FINAL SUMMARY")
    
    print("Endpoint Test Results:")
    for endpoint, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {endpoint}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    print("\n✓ Tests ran against REAL AliExpress API")
    
    print("\n" + "=" * 80)
    print(f"  Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
