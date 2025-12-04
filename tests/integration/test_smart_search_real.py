"""Test smart search with real AliExpress API."""

import asyncio
import logging
from src.utils.config import Config
from src.services.cache_config import CacheConfig
from src.services.enhanced_aliexpress_service import EnhancedAliExpressService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_smart_search():
    """Test smart search with real API."""
    print("\n" + "=" * 80)
    print("  TESTING SMART SEARCH WITH REAL ALIEXPRESS API")
    print("=" * 80 + "\n")
    
    # Initialize service
    config = Config.from_env()
    cache_config = CacheConfig.from_env()
    
    # Disable caching for this test to ensure fresh API calls
    cache_config.enable_redis_cache = False
    cache_config.enable_database_cache = False
    cache_config.enable_memory_cache = False
    
    service = EnhancedAliExpressService(config, cache_config)
    
    print("✓ Service initialized\n")
    
    # Test 1: Basic smart search
    print("TEST 1: Basic smart search (keywords='phone')")
    print("-" * 80)
    
    try:
        result = await service.smart_product_search(
            keywords="phone",
            page_no=1,
            page_size=5,
            generate_affiliate_links=True
        )
        
        print(f"✓ SUCCESS")
        print(f"  - Products returned: {len(result.products)}")
        print(f"  - Total available: {result.total_record_count}")
        print(f"  - Cache hit: {result.cache_hit}")
        print(f"  - Affiliate links cached: {result.affiliate_links_cached}")
        print(f"  - Affiliate links generated: {result.affiliate_links_generated}")
        print(f"  - API calls saved: {result.api_calls_saved}")
        print(f"  - Response time: {result.response_time_ms:.2f}ms")
        
        if result.products:
            print(f"\n  Sample product:")
            product = result.products[0]
            print(f"    - ID: {product.product_id}")
            print(f"    - Title: {product.product_title[:60]}...")
            print(f"    - Price: {product.price} {product.currency}")
            print(f"    - URL: {product.product_url[:80]}...")
            print(f"    - Affiliate URL: {product.affiliate_url[:80] if product.affiliate_url else 'None'}...")
            print(f"    - Affiliate Status: {product.affiliate_status}")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n")
    
    # Test 2: Smart search with filters
    print("TEST 2: Smart search with price filter")
    print("-" * 80)
    
    try:
        result = await service.smart_product_search(
            keywords="headphones",
            min_sale_price=10.0,
            max_sale_price=50.0,
            page_no=1,
            page_size=3,
            generate_affiliate_links=True
        )
        
        print(f"✓ SUCCESS")
        print(f"  - Products returned: {len(result.products)}")
        print(f"  - Total available: {result.total_record_count}")
        print(f"  - Cache hit: {result.cache_hit}")
        print(f"  - Response time: {result.response_time_ms:.2f}ms")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n")
    
    # Test 3: Force refresh
    print("TEST 3: Force refresh (bypass cache)")
    print("-" * 80)
    
    try:
        result = await service.smart_product_search(
            keywords="phone",
            page_no=1,
            page_size=3,
            force_refresh=True,
            generate_affiliate_links=True
        )
        
        print(f"✓ SUCCESS")
        print(f"  - Products returned: {len(result.products)}")
        print(f"  - Cache hit: {result.cache_hit} (should be False)")
        print(f"  - Response time: {result.response_time_ms:.2f}ms")
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("  ALL TESTS PASSED - SMART SEARCH IS WORKING WITH REAL API!")
    print("=" * 80 + "\n")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_smart_search())
    exit(0 if success else 1)
