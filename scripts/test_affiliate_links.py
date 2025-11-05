#!/usr/bin/env python3
"""
Test script to verify that all returned product URLs are affiliate links.
"""

import sys
import os
import asyncio

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config, ConfigurationError
from src.services.enhanced_aliexpress_service import EnhancedAliExpressService
from src.services.cache_config import CacheConfig


async def test_affiliate_links():
    """Test that all product URLs are affiliate links."""
    try:
        print("🔧 Loading configuration...")
        config = Config.from_env()
        config.validate()
        cache_config = CacheConfig.from_env()
        
        print(f"✅ Configuration loaded")
        print(f"   - Tracking ID: {config.tracking_id}")
        print()
        
        # Initialize Enhanced AliExpress service
        print("🚀 Initializing Enhanced AliExpress service...")
        enhanced_service = EnhancedAliExpressService(config, cache_config)
        print("✅ Service initialized")
        print()
        
        # Test 1: Search for products and check URLs
        print("🔍 Test 1: Product Search with Automatic Affiliate Links")
        result = await enhanced_service.smart_product_search(
            keywords="bluetooth headphones",
            page_size=5,
            generate_affiliate_links=True
        )
        
        print(f"📊 Found {len(result.products)} products")
        print()
        
        # Analyze URLs to verify they are affiliate links
        affiliate_count = 0
        direct_count = 0
        
        for i, product in enumerate(result.products, 1):
            url = product.product_url
            is_affiliate = 's.click.aliexpress.com' in url or 'tracking_id' in url or config.tracking_id in url
            
            print(f"Product {i}: {product.product_title[:40]}...")
            print(f"   URL: {url[:80]}...")
            print(f"   Is Affiliate Link: {'✅ YES' if is_affiliate else '❌ NO'}")
            print(f"   Status: {product.affiliate_status}")
            print()
            
            if is_affiliate:
                affiliate_count += 1
            else:
                direct_count += 1
        
        # Summary
        print("=" * 60)
        print("📊 AFFILIATE LINK VERIFICATION RESULTS")
        print("=" * 60)
        print(f"✅ Affiliate Links: {affiliate_count}")
        print(f"❌ Direct Links: {direct_count}")
        print(f"📈 Conversion Rate: {(affiliate_count / len(result.products) * 100):.1f}%")
        print()
        
        if affiliate_count == len(result.products):
            print("🎉 SUCCESS: All product URLs are affiliate links!")
            print("🔗 No further conversion needed - URLs are ready to use")
        elif affiliate_count > 0:
            print("⚠️  PARTIAL: Some URLs converted to affiliate links")
            print("💡 Check API permissions or network connectivity")
        else:
            print("❌ FAILURE: No affiliate links generated")
            print("💡 Check your AliExpress API credentials and affiliate account status")
        
        print()
        print("🔧 Performance Metrics:")
        print(f"   - Cache Hit: {result.cache_hit}")
        print(f"   - Response Time: {result.response_time_ms:.2f}ms")
        print(f"   - Affiliate Links Generated: {result.affiliate_links_generated}")
        
        return affiliate_count == len(result.products)
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure you have set the following environment variables:")
        print("   - ALIEXPRESS_APP_KEY")
        print("   - ALIEXPRESS_APP_SECRET")
        print("   - ALIEXPRESS_TRACKING_ID")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 AFFILIATE LINK VERIFICATION TEST")
    print("=" * 60)
    print("This test verifies that all product URLs returned by the API")
    print("are automatically converted to affiliate links with your tracking ID.")
    print()
    
    success = asyncio.run(test_affiliate_links())
    
    if success:
        print("\n🎉 All tests passed! Your affiliate link system is working correctly.")
        exit(0)
    else:
        print("\n❌ Tests failed. Please check your configuration and try again.")
        exit(1)


if __name__ == "__main__":
    main()