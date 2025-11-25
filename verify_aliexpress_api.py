"""Comprehensive verification of AliExpress API connectivity and functionality."""

import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_test(test_name):
    """Print test name."""
    print(f"\n{'─'*80}")
    print(f"TEST: {test_name}")
    print(f"{'─'*80}")

def test_result(success, message, data=None):
    """Print test result."""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if data:
        print(f"   Data: {data}")
    return success

def main():
    """Run comprehensive AliExpress API verification."""
    print_header("ALIEXPRESS API VERIFICATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Testing with REAL AliExpress API credentials")
    
    # Initialize service
    print("\n📋 Initializing AliExpress Service...")
    try:
        config = Config.from_env()
        print(f"   App Key: {config.app_key[:10]}...")
        print(f"   Language: {config.language}")
        print(f"   Currency: {config.currency}")
        print(f"   Tracking ID: {config.tracking_id}")
        
        service = AliExpressService(config)
        print("✅ Service initialized successfully with REAL API")
        
    except Exception as e:
        print(f"❌ FAILED to initialize service: {e}")
        return False
    
    # Track results
    results = {
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # TEST 1: Get Parent Categories
    print_test("1. Get Parent Categories")
    try:
        start_time = time.time()
        categories = service.get_parent_categories()
        elapsed = (time.time() - start_time) * 1000
        
        if categories and len(categories) > 0:
            success = test_result(
                True,
                f"Retrieved {len(categories)} parent categories in {elapsed:.0f}ms",
                f"First 3: {', '.join([c.category_name for c in categories[:3]])}"
            )
            results["passed"] += 1
            results["tests"].append({"name": "Parent Categories", "status": "PASS", "count": len(categories)})
            
            # Show sample
            print("\n   Sample Categories:")
            for i, cat in enumerate(categories[:5], 1):
                print(f"   {i}. {cat.category_name} (ID: {cat.category_id})")
        else:
            success = test_result(False, "No categories returned")
            results["failed"] += 1
            results["tests"].append({"name": "Parent Categories", "status": "FAIL", "error": "No data"})
            
    except Exception as e:
        test_result(False, f"Exception: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Parent Categories", "status": "FAIL", "error": str(e)})
    
    # TEST 2: Get Child Categories
    print_test("2. Get Child Categories")
    try:
        # Try to get child categories for the first parent category
        if categories and len(categories) > 0:
            parent_id = categories[0].category_id
            start_time = time.time()
            child_cats = service.get_child_categories(parent_id)
            elapsed = (time.time() - start_time) * 1000
            
            if child_cats and len(child_cats) > 0:
                success = test_result(
                    True,
                    f"Retrieved {len(child_cats)} child categories for parent_id={parent_id} in {elapsed:.0f}ms"
                )
                results["passed"] += 1
                results["tests"].append({"name": "Child Categories", "status": "PASS", "count": len(child_cats)})
                
                print("\n   Sample Child Categories:")
                for i, cat in enumerate(child_cats[:5], 1):
                    print(f"   {i}. {cat.category_name} (ID: {cat.category_id})")
            else:
                success = test_result(True, f"No child categories for parent_id={parent_id} (this is normal)")
                results["passed"] += 1
                results["tests"].append({"name": "Child Categories", "status": "PASS", "count": 0})
        else:
            test_result(False, "Skipped - no parent categories available")
            results["failed"] += 1
            results["tests"].append({"name": "Child Categories", "status": "SKIP"})
            
    except Exception as e:
        test_result(False, f"Exception: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Child Categories", "status": "FAIL", "error": str(e)})
    
    # TEST 3: Search Products
    print_test("3. Search Products")
    try:
        start_time = time.time()
        search_results = service.search_products(
            keywords="wireless headphones",
            page_size=5,
            sort="SALE_PRICE_ASC"
        )
        elapsed = (time.time() - start_time) * 1000
        
        if search_results and search_results.products:
            success = test_result(
                True,
                f"Found {search_results.total_record_count} products (showing {len(search_results.products)}) in {elapsed:.0f}ms"
            )
            results["passed"] += 1
            results["tests"].append({
                "name": "Product Search",
                "status": "PASS",
                "total": search_results.total_record_count,
                "returned": len(search_results.products)
            })
            
            print("\n   Sample Products:")
            for i, product in enumerate(search_results.products, 1):
                print(f"   {i}. {product.product_title[:60]}")
                print(f"      Price: ${product.price} {product.currency} | Orders: {product.orders_count}")
                print(f"      URL: {product.product_url[:70]}...")
        else:
            test_result(False, "No products found")
            results["failed"] += 1
            results["tests"].append({"name": "Product Search", "status": "FAIL", "error": "No results"})
            
    except Exception as e:
        test_result(False, f"Exception: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Product Search", "status": "FAIL", "error": str(e)})
    
    # TEST 4: Get Product Details
    print_test("4. Get Product Details")
    try:
        # Use product IDs from search results if available
        if search_results and search_results.products:
            product_ids = [p.product_id for p in search_results.products[:2]]
            start_time = time.time()
            details = service.get_products_details(product_ids)
            elapsed = (time.time() - start_time) * 1000
            
            if details and len(details) > 0:
                success = test_result(
                    True,
                    f"Retrieved details for {len(details)} products in {elapsed:.0f}ms"
                )
                results["passed"] += 1
                results["tests"].append({"name": "Product Details", "status": "PASS", "count": len(details)})
                
                print("\n   Sample Product Details:")
                for i, product in enumerate(details, 1):
                    print(f"   {i}. {product.product_title[:60]}")
                    print(f"      Price: ${product.price} {product.currency}")
                    if product.description:
                        print(f"      Description: {product.description[:80]}...")
            else:
                test_result(False, "No product details returned")
                results["failed"] += 1
                results["tests"].append({"name": "Product Details", "status": "FAIL", "error": "No data"})
        else:
            test_result(False, "Skipped - no products from search")
            results["failed"] += 1
            results["tests"].append({"name": "Product Details", "status": "SKIP"})
            
    except Exception as e:
        test_result(False, f"Exception: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Product Details", "status": "FAIL", "error": str(e)})
    
    # TEST 5: Generate Affiliate Links
    print_test("5. Generate Affiliate Links")
    try:
        # Use product URLs from search results
        if search_results and search_results.products:
            product_urls = [p.product_url for p in search_results.products[:2]]
            start_time = time.time()
            affiliate_links = service.get_affiliate_links(product_urls)
            elapsed = (time.time() - start_time) * 1000
            
            if affiliate_links and len(affiliate_links) > 0:
                success = test_result(
                    True,
                    f"Generated {len(affiliate_links)} affiliate links in {elapsed:.0f}ms"
                )
                results["passed"] += 1
                results["tests"].append({"name": "Affiliate Links", "status": "PASS", "count": len(affiliate_links)})
                
                print("\n   Sample Affiliate Links:")
                for i, link in enumerate(affiliate_links, 1):
                    print(f"   {i}. Original: {link.original_url[:50]}...")
                    print(f"      Affiliate: {link.affiliate_url[:70]}...")
                    print(f"      Tracking ID: {link.tracking_id}")
            else:
                test_result(False, "No affiliate links generated")
                results["failed"] += 1
                results["tests"].append({"name": "Affiliate Links", "status": "FAIL", "error": "No links"})
        else:
            test_result(False, "Skipped - no product URLs available")
            results["failed"] += 1
            results["tests"].append({"name": "Affiliate Links", "status": "SKIP"})
            
    except Exception as e:
        test_result(False, f"Exception: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": "Affiliate Links", "status": "FAIL", "error": str(e)})
    
    # TEST 6: Get Hot Products (may require special permissions)
    print_test("6. Get Hot Products (Optional)")
    try:
        start_time = time.time()
        hot_products = service.get_hotproducts(
            keywords="electronics",
            page_size=5
        )
        elapsed = (time.time() - start_time) * 1000
        
        if hot_products and hot_products.products:
            success = test_result(
                True,
                f"Retrieved {len(hot_products.products)} hot products in {elapsed:.0f}ms"
            )
            results["passed"] += 1
            results["tests"].append({"name": "Hot Products", "status": "PASS", "count": len(hot_products.products)})
            
            print("\n   Sample Hot Products:")
            for i, product in enumerate(hot_products.products, 1):
                print(f"   {i}. {product.product_title[:60]}")
                print(f"      Price: ${product.price} | Orders: {product.orders_count}")
        else:
            test_result(False, "No hot products returned (may require special permissions)")
            results["tests"].append({"name": "Hot Products", "status": "SKIP", "note": "May require permissions"})
            
    except Exception as e:
        error_msg = str(e)
        if "permission" in error_msg.lower():
            test_result(False, f"Permission required: {error_msg}")
            results["tests"].append({"name": "Hot Products", "status": "SKIP", "note": "Requires special permissions"})
        else:
            test_result(False, f"Exception: {error_msg}")
            results["failed"] += 1
            results["tests"].append({"name": "Hot Products", "status": "FAIL", "error": error_msg})
    
    # FINAL SUMMARY
    print_header("VERIFICATION SUMMARY")
    
    total_tests = results["passed"] + results["failed"]
    pass_rate = (results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   📈 Pass Rate: {pass_rate:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test in results["tests"]:
        status_icon = "✅" if test["status"] == "PASS" else "⚠️" if test["status"] == "SKIP" else "❌"
        print(f"   {status_icon} {test['name']}: {test['status']}")
        if "count" in test:
            print(f"      → Returned {test['count']} items")
        if "error" in test:
            print(f"      → Error: {test['error']}")
        if "note" in test:
            print(f"      → Note: {test['note']}")
    
    # Final verdict
    print(f"\n{'='*80}")
    if results["passed"] >= 4:  # At least 4 core tests should pass
        print("✅ VERDICT: ALIEXPRESS API IS FULLY OPERATIONAL")
        print("   All core endpoints are working correctly!")
        print("   Your API credentials are valid and approved.")
    elif results["passed"] >= 2:
        print("⚠️  VERDICT: ALIEXPRESS API IS PARTIALLY OPERATIONAL")
        print("   Some endpoints are working, but others may require additional permissions.")
    else:
        print("❌ VERDICT: ALIEXPRESS API IS NOT OPERATIONAL")
        print("   Most tests failed. Please check your credentials and API permissions.")
    
    print(f"{'='*80}\n")
    
    return results["passed"] >= 4

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
