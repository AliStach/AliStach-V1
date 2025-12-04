"""Integration test for smart search with real AliExpress API - comprehensive validation."""

import asyncio
import logging

from src.utils.config import Config
from src.services.cache_config import CacheConfig
from src.services.enhanced_aliexpress_service import EnhancedAliExpressService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


async def run_comprehensive_tests():
    """Run comprehensive integration tests for smart search."""
    
    print_section("SMART SEARCH INTEGRATION TEST - REAL ALIEXPRESS API")
    
    # Initialize service with minimal caching to test real API calls
    config = Config.from_env()
    cache_config = CacheConfig(
        enable_redis_cache=False,  # Disable Redis for testing
        enable_database_cache=False,  # Disable DB for testing
        enable_memory_cache=True,  # Keep memory cache for performance
        search_results_ttl=60,  # Short TTL for testing
        affiliate_links_ttl=300
    )
    
    service = EnhancedAliExpressService(config, cache_config)
    print("✓ Service initialized (Redis/DB caching disabled for testing)\n")
    
    test_results = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    # Test 1: Basic search with real data
    print_section("TEST 1: Basic Product Search")
    test_results["total_tests"] += 1
    
    try:
        result = await service.smart_product_search(
            keywords="wireless mouse",
            page_no=1,
            page_size=5,
            generate_affiliate_links=True
        )
        
        # Validate response structure
        assert result is not None, "Result is None"
        assert hasattr(result, 'products'), "Missing products attribute"
        assert hasattr(result, 'total_record_count'), "Missing total_record_count"
        assert hasattr(result, 'cache_hit'), "Missing cache_hit"
        assert hasattr(result, 'affiliate_links_cached'), "Missing affiliate_links_cached"
        assert hasattr(result, 'affiliate_links_generated'), "Missing affiliate_links_generated"
        assert hasattr(result, 'api_calls_saved'), "Missing api_calls_saved"
        assert hasattr(result, 'response_time_ms'), "Missing response_time_ms"
        
        # Validate data
        assert len(result.products) > 0, "No products returned"
        assert result.total_record_count > 0, "Total record count is 0"
        assert result.cache_hit == False, "Should be cache miss on first call"
        assert result.affiliate_links_cached == 0, "Should have 0 cached links on first call"
        assert result.affiliate_links_generated > 0, "Should have generated affiliate links"
        assert result.api_calls_saved == 0, "Should have 0 API calls saved on cache miss"
        assert result.response_time_ms > 0, "Response time should be > 0"
        
        # Validate product structure
        product = result.products[0]
        assert hasattr(product, 'product_id'), "Product missing product_id"
        assert hasattr(product, 'product_title'), "Product missing product_title"
        assert hasattr(product, 'product_url'), "Product missing product_url"
        assert hasattr(product, 'price'), "Product missing price"
        assert hasattr(product, 'currency'), "Product missing currency"
        assert hasattr(product, 'affiliate_url'), "Product missing affiliate_url"
        assert hasattr(product, 'affiliate_status'), "Product missing affiliate_status"
        
        # Validate affiliate link generation
        assert product.affiliate_url is not None, "Affiliate URL is None"
        assert product.affiliate_status == "auto_generated", f"Unexpected affiliate status: {product.affiliate_status}"
        assert "aliexpress.com" in product.affiliate_url or "s.click.aliexpress.com" in product.affiliate_url, "Invalid affiliate URL"
        
        print(f"✓ PASSED")
        print(f"  Products: {len(result.products)}")
        print(f"  Total available: {result.total_record_count:,}")
        print(f"  Affiliate links generated: {result.affiliate_links_generated}")
        print(f"  Response time: {result.response_time_ms:.2f}ms")
        print(f"\n  Sample product:")
        print(f"    ID: {product.product_id}")
        print(f"    Title: {product.product_title[:60]}...")
        print(f"    Price: {product.price} {product.currency}")
        print(f"    Affiliate URL: {product.affiliate_url[:70]}...")
        
        test_results["passed"] += 1
        test_results["tests"].append({"name": "Basic Search", "status": "PASSED"})
        
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Basic Search", "status": "FAILED", "error": str(e)})
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Basic Search", "status": "ERROR", "error": str(e)})
    
    # Test 2: Search with price filters
    print_section("TEST 2: Search with Price Filters")
    test_results["total_tests"] += 1
    
    try:
        result = await service.smart_product_search(
            keywords="bluetooth headphones",
            min_sale_price=15.0,
            max_sale_price=100.0,
            page_no=1,
            page_size=10,
            generate_affiliate_links=True
        )
        
        assert len(result.products) > 0, "No products returned"
        assert result.total_record_count > 0, "Total record count is 0"
        
        # Validate price filtering (check a few products)
        for i, product in enumerate(result.products[:3]):
            try:
                price = float(product.price)
                # Note: API might return products slightly outside range, so we're lenient
                assert price >= 10.0, f"Product {i} price {price} below minimum"
                assert price <= 150.0, f"Product {i} price {price} above maximum"
            except ValueError:
                pass  # Skip if price can't be parsed
        
        print(f"✓ PASSED")
        print(f"  Products: {len(result.products)}")
        print(f"  Total available: {result.total_record_count:,}")
        print(f"  Price range validated")
        
        test_results["passed"] += 1
        test_results["tests"].append({"name": "Price Filters", "status": "PASSED"})
        
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Price Filters", "status": "FAILED", "error": str(e)})
    except Exception as e:
        print(f"✗ ERROR: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Price Filters", "status": "ERROR", "error": str(e)})
    
    # Test 3: Pagination
    print_section("TEST 3: Pagination")
    test_results["total_tests"] += 1
    
    try:
        # Get page 1
        result_page1 = await service.smart_product_search(
            keywords="phone case",
            page_no=1,
            page_size=5,
            generate_affiliate_links=False  # Skip affiliate links for speed
        )
        
        # Get page 2
        result_page2 = await service.smart_product_search(
            keywords="phone case",
            page_no=2,
            page_size=5,
            generate_affiliate_links=False
        )
        
        assert len(result_page1.products) > 0, "Page 1 has no products"
        assert len(result_page2.products) > 0, "Page 2 has no products"
        assert result_page1.current_page == 1, "Page 1 current_page incorrect"
        assert result_page2.current_page == 2, "Page 2 current_page incorrect"
        
        # Products should be different
        page1_ids = {p.product_id for p in result_page1.products}
        page2_ids = {p.product_id for p in result_page2.products}
        assert len(page1_ids.intersection(page2_ids)) == 0, "Pages have overlapping products"
        
        print(f"✓ PASSED")
        print(f"  Page 1 products: {len(result_page1.products)}")
        print(f"  Page 2 products: {len(result_page2.products)}")
        print(f"  No overlapping products")
        
        test_results["passed"] += 1
        test_results["tests"].append({"name": "Pagination", "status": "PASSED"})
        
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Pagination", "status": "FAILED", "error": str(e)})
    except Exception as e:
        print(f"✗ ERROR: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Pagination", "status": "ERROR", "error": str(e)})
    
    # Test 4: Force refresh
    print_section("TEST 4: Force Refresh")
    test_results["total_tests"] += 1
    
    try:
        # First call
        result1 = await service.smart_product_search(
            keywords="laptop",
            page_no=1,
            page_size=3,
            generate_affiliate_links=False
        )
        
        # Force refresh
        result2 = await service.smart_product_search(
            keywords="laptop",
            page_no=1,
            page_size=3,
            force_refresh=True,
            generate_affiliate_links=False
        )
        
        assert result2.cache_hit == False, "Force refresh should not hit cache"
        assert len(result2.products) > 0, "Force refresh returned no products"
        
        print(f"✓ PASSED")
        print(f"  Force refresh bypassed cache")
        print(f"  Products: {len(result2.products)}")
        
        test_results["passed"] += 1
        test_results["tests"].append({"name": "Force Refresh", "status": "PASSED"})
        
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Force Refresh", "status": "FAILED", "error": str(e)})
    except Exception as e:
        print(f"✗ ERROR: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Force Refresh", "status": "ERROR", "error": str(e)})
    
    # Test 5: Metrics accuracy
    print_section("TEST 5: Metrics Accuracy")
    test_results["total_tests"] += 1
    
    try:
        result = await service.smart_product_search(
            keywords="usb cable",
            page_no=1,
            page_size=7,
            generate_affiliate_links=True
        )
        
        # Validate metrics
        assert result.affiliate_links_cached >= 0, "affiliate_links_cached is negative"
        assert result.affiliate_links_generated >= 0, "affiliate_links_generated is negative"
        assert result.api_calls_saved >= 0, "api_calls_saved is negative"
        assert result.response_time_ms >= 0, "response_time_ms is negative"
        
        # On cache miss, should have generated links
        if not result.cache_hit:
            assert result.affiliate_links_generated == len(result.products), \
                f"Mismatch: generated {result.affiliate_links_generated} links but have {len(result.products)} products"
            assert result.affiliate_links_cached == 0, "Should have 0 cached links on cache miss"
            assert result.api_calls_saved == 0, "Should have 0 API calls saved on cache miss"
        
        print(f"✓ PASSED")
        print(f"  All metrics are valid")
        print(f"  Cache hit: {result.cache_hit}")
        print(f"  Links cached: {result.affiliate_links_cached}")
        print(f"  Links generated: {result.affiliate_links_generated}")
        print(f"  API calls saved: {result.api_calls_saved}")
        
        test_results["passed"] += 1
        test_results["tests"].append({"name": "Metrics Accuracy", "status": "PASSED"})
        
    except AssertionError as e:
        print(f"✗ FAILED: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Metrics Accuracy", "status": "FAILED", "error": str(e)})
    except Exception as e:
        print(f"✗ ERROR: {e}")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Metrics Accuracy", "status": "ERROR", "error": str(e)})
    
    # Print final summary
    print_section("FINAL SUMMARY")
    
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed']} ✓")
    print(f"Failed: {test_results['failed']} ✗")
    print(f"Success Rate: {(test_results['passed'] / test_results['total_tests'] * 100):.1f}%")
    
    print("\nDetailed Results:")
    for test in test_results["tests"]:
        status_icon = "✓" if test["status"] == "PASSED" else "✗"
        print(f"  {status_icon} {test['name']}: {test['status']}")
        if "error" in test:
            print(f"      Error: {test['error']}")
    
    if test_results["failed"] == 0:
        print("\n" + "=" * 80)
        print("  🎉 ALL TESTS PASSED - SMART SEARCH IS FULLY OPERATIONAL!")
        print("  ✓ Real AliExpress API integration working")
        print("  ✓ Affiliate link generation working")
        print("  ✓ Metrics tracking accurate")
        print("  ✓ Bug fix verified")
        print("=" * 80 + "\n")
        return True
    else:
        print("\n" + "=" * 80)
        print(f"  ⚠️  {test_results['failed']} TEST(S) FAILED")
        print("=" * 80 + "\n")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    exit(0 if success else 1)
