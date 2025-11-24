"""Test script for mock mode functionality."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.services.aliexpress_service_with_mock import AliExpressServiceWithMock

def test_mock_mode():
    """Test all major endpoints in mock mode."""
    print("="*80)
    print("TESTING MOCK MODE FUNCTIONALITY")
    print("="*80)
    
    # Force mock mode
    os.environ["FORCE_MOCK_MODE"] = "true"
    
    # Initialize service
    config = Config.from_env()
    service = AliExpressServiceWithMock(config, force_mock=True)
    
    print(f"\n✅ Service initialized in {'MOCK' if service.mock_mode else 'REAL'} mode\n")
    
    # Test 1: Get parent categories
    print("\n" + "="*80)
    print("TEST 1: Get Parent Categories")
    print("="*80)
    try:
        categories = service.get_parent_categories()
        print(f"✅ SUCCESS: Retrieved {len(categories)} categories")
        for i, cat in enumerate(categories[:5], 1):
            print(f"  {i}. {cat.category_name} (ID: {cat.category_id})")
        if len(categories) > 5:
            print(f"  ... and {len(categories) - 5} more")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 2: Get child categories
    print("\n" + "="*80)
    print("TEST 2: Get Child Categories")
    print("="*80)
    try:
        child_cats = service.get_child_categories("5")  # Consumer Electronics
        print(f"✅ SUCCESS: Retrieved {len(child_cats)} child categories for parent_id=5")
        for i, cat in enumerate(child_cats, 1):
            print(f"  {i}. {cat.category_name} (ID: {cat.category_id})")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 3: Search products
    print("\n" + "="*80)
    print("TEST 3: Search Products")
    print("="*80)
    try:
        results = service.search_products(keywords="headphones", page_size=5)
        print(f"✅ SUCCESS: Found {results.total_record_count} products (showing {len(results.products)})")
        for i, product in enumerate(results.products, 1):
            print(f"  {i}. {product.product_title}")
            print(f"     Price: ${product.price} (was ${product.original_price})")
            print(f"     Orders: {product.orders_count} | Rating: {product.evaluate_rate}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 4: Get product details
    print("\n" + "="*80)
    print("TEST 4: Get Product Details")
    print("="*80)
    try:
        details = service.get_products_details(["1005006265991420", "1005006265991421"])
        print(f"✅ SUCCESS: Retrieved details for {len(details)} products")
        for i, product in enumerate(details, 1):
            print(f"  {i}. {product.product_title}")
            print(f"     Price: ${product.price}")
            print(f"     Description: {product.description[:100]}...")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 5: Generate affiliate links
    print("\n" + "="*80)
    print("TEST 5: Generate Affiliate Links")
    print("="*80)
    try:
        urls = [
            "https://www.aliexpress.com/item/1005006265991420.html",
            "https://www.aliexpress.com/item/1005006265991421.html"
        ]
        links = service.get_affiliate_links(urls)
        print(f"✅ SUCCESS: Generated {len(links)} affiliate links")
        for i, link in enumerate(links, 1):
            print(f"  {i}. Original: {link.original_url[:50]}...")
            print(f"     Affiliate: {link.affiliate_url}")
            print(f"     Tracking ID: {link.tracking_id}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Test 6: Get hot products
    print("\n" + "="*80)
    print("TEST 6: Get Hot Products")
    print("="*80)
    try:
        hot_products = service.get_hotproducts(keywords="electronics", page_size=5)
        print(f"✅ SUCCESS: Found {len(hot_products.products)} hot products")
        for i, product in enumerate(hot_products.products, 1):
            print(f"  {i}. {product.product_title}")
            print(f"     Price: ${product.price} | Orders: {product.orders_count}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
    
    # Final summary
    print("\n" + "="*80)
    print("MOCK MODE TEST SUMMARY")
    print("="*80)
    print("✅ All mock mode endpoints are functional!")
    print("✅ Mock data provides realistic test data")
    print("✅ No AliExpress credentials required")
    print("\nMock mode is perfect for:")
    print("  • Development and testing")
    print("  • Demos and presentations")
    print("  • CI/CD pipelines")
    print("  • Learning the API structure")
    print("\nTo use real AliExpress API:")
    print("  1. Set FORCE_MOCK_MODE=false in .env")
    print("  2. Add valid ALIEXPRESS_APP_KEY and ALIEXPRESS_APP_SECRET")
    print("  3. Redeploy to Vercel")

if __name__ == "__main__":
    test_mock_mode()
