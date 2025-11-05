#!/usr/bin/env python3
"""
Simple test script to verify affiliate link generation without complex dependencies.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config, ConfigurationError
from src.services.aliexpress_service import AliExpressService, AliExpressServiceException


def test_affiliate_links():
    """Test that product search automatically generates affiliate links."""
    try:
        print("🔧 Loading configuration...")
        config = Config.from_env()
        config.validate()
        
        print(f"✅ Configuration loaded")
        print(f"   - App Key: {config.app_key}")
        print(f"   - Tracking ID: {config.tracking_id}")
        print()
        
        # Initialize AliExpress service
        print("🚀 Initializing AliExpress service...")
        service = AliExpressService(config)
        print("✅ Service initialized")
        print()
        
        # Test 1: Search for products with automatic affiliate link generation
        print("🔍 Test 1: Product Search with Automatic Affiliate Links")
        print("Searching for 'bluetooth headphones'...")
        
        result = service.search_products(
            keywords="bluetooth headphones",
            page_size=5,
            auto_generate_affiliate_links=True  # This should automatically convert URLs
        )
        
        print(f"📊 Found {len(result.products)} products")
        print()
        
        # Analyze URLs to verify they are affiliate links
        affiliate_count = 0
        direct_count = 0
        
        for i, product in enumerate(result.products, 1):
            url = product.product_url
            
            # Check if URL contains affiliate indicators
            is_affiliate = (
                's.click.aliexpress.com' in url or 
                'tracking_id' in url or 
                config.tracking_id in url or
                'pid=' in url or
                '/e/_' in url  # AliExpress short affiliate links
            )
            
            print(f"Product {i}: {product.product_title[:40]}...")
            print(f"   URL: {url[:80]}...")
            print(f"   Is Affiliate Link: {'✅ YES' if is_affiliate else '❌ NO'}")
            print(f"   Commission Rate: {product.commission_rate}")
            print()
            
            if is_affiliate:
                affiliate_count += 1
            else:
                direct_count += 1
        
        # Test 2: Test the affiliate link generation method directly
        print("🔗 Test 2: Direct Affiliate Link Generation")
        if result.products:
            # Get first product URL (should be original URL from API)
            test_urls = [result.products[0].product_url]
            
            try:
                affiliate_links = service.get_affiliate_links(test_urls)
                print(f"✅ Successfully generated {len(affiliate_links)} affiliate links")
                
                for link in affiliate_links:
                    print(f"   Original: {link.original_url[:60]}...")
                    print(f"   Affiliate: {link.affiliate_url[:60]}...")
                    print(f"   Tracking ID: {link.tracking_id}")
                    print()
            except Exception as e:
                print(f"❌ Affiliate link generation failed: {e}")
        
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
            return True
        elif affiliate_count > 0:
            print("⚠️  PARTIAL: Some URLs converted to affiliate links")
            print("💡 Check API permissions or network connectivity")
            return False
        else:
            print("❌ FAILURE: No affiliate links generated")
            print("💡 Check your AliExpress API credentials and affiliate account status")
            return False
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure you have set the following environment variables:")
        print("   - ALIEXPRESS_APP_KEY")
        print("   - ALIEXPRESS_APP_SECRET")
        print("   - ALIEXPRESS_TRACKING_ID")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🧪 SIMPLE AFFILIATE LINK VERIFICATION TEST")
    print("=" * 60)
    print("This test verifies that the AliExpress service can generate")
    print("affiliate links and that product search returns affiliate URLs.")
    print()
    
    success = test_affiliate_links()
    
    if success:
        print("\n🎉 All tests passed! Your affiliate link system is working correctly.")
        print("\n📋 Next Steps:")
        print("   1. Start the API server: python -m src.api.main")
        print("   2. Test the endpoint: POST /api/products/smart-search")
        print("   3. Verify all returned product_url fields are affiliate links")
        exit(0)
    else:
        print("\n❌ Tests failed. Please check your configuration and try again.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify your AliExpress API credentials are correct")
        print("   2. Check that your affiliate account is active")
        print("   3. Ensure you have proper API permissions")
        exit(1)


if __name__ == "__main__":
    main()