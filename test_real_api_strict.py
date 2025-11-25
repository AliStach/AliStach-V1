"""Strict test of real AliExpress API."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from aliexpress_api import AliexpressApi, models

def test_real_api():
    """Test the real AliExpress API directly without any wrappers."""
    print("="*80)
    print("STRICT REAL API TEST - NO MOCK MODE")
    print("="*80)
    
    # Load config
    config = Config.from_env()
    
    print(f"\n📋 Configuration:")
    print(f"   APP_KEY: {config.app_key}")
    print(f"   APP_SECRET: {'*' * (len(config.app_secret) - 4)}{config.app_secret[-4:]}")
    print(f"   TRACKING_ID: {config.tracking_id}")
    print(f"   LANGUAGE: {config.language}")
    print(f"   CURRENCY: {config.currency}")
    
    # Initialize API directly
    print(f"\n🔌 Initializing AliExpress API client...")
    try:
        api = AliexpressApi(
            key=config.app_key,
            secret=config.app_secret,
            language=getattr(models.Language, config.language),
            currency=getattr(models.Currency, config.currency),
            tracking_id=config.tracking_id
        )
        print("   ✅ API client initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    
    # Test 1: Get Parent Categories
    print(f"\n{'='*80}")
    print("TEST 1: Get Parent Categories (REAL API CALL)")
    print(f"{'='*80}")
    try:
        print("   Making API call...")
        categories = api.get_parent_categories()
        
        if categories:
            print(f"   ✅ SUCCESS! Retrieved {len(categories)} categories")
            print(f"\n   🎉 REAL DATA CONFIRMED - Not mock mode!")
            print(f"\n   Sample categories:")
            for i, cat in enumerate(categories[:5], 1):
                print(f"   {i}. {cat.category_name} (ID: {cat.category_id})")
            return True
        else:
            print(f"   ⚠️  API call succeeded but returned no data")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ API CALL FAILED")
        print(f"   Error: {error_msg}")
        
        # Analyze the error
        print(f"\n   🔍 Error Analysis:")
        if "signature" in error_msg.lower():
            print(f"   ❌ SIGNATURE ERROR")
            print(f"      → APP_SECRET is incorrect or doesn't match APP_KEY")
            print(f"      → Credentials may be from wrong environment (test vs production)")
            print(f"      → Check for extra spaces or formatting issues")
        elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
            print(f"   ❌ INVALID KEY ERROR")
            print(f"      → APP_KEY is incorrect or not approved")
            print(f"      → API access may not be fully activated")
        elif "permission" in error_msg.lower():
            print(f"   ⚠️  PERMISSION ERROR")
            print(f"      → API access pending or restricted")
            print(f"      → Specific endpoint may require additional permissions")
        else:
            print(f"   ❌ UNKNOWN ERROR")
            print(f"      → {error_msg}")
        
        return False
    
    # Test 2: Search Products
    print(f"\n{'='*80}")
    print("TEST 2: Search Products (REAL API CALL)")
    print(f"{'='*80}")
    try:
        print("   Making API call...")
        products = api.get_products(keywords="phone", page_size=3)
        
        if products and hasattr(products, 'products') and products.products:
            print(f"   ✅ SUCCESS! Found {len(products.products)} products")
            print(f"\n   🎉 REAL DATA CONFIRMED - Not mock mode!")
            print(f"\n   Sample products:")
            for i, product in enumerate(products.products[:3], 1):
                title = getattr(product, 'product_title', 'No title')
                price = getattr(product, 'target_sale_price', 'N/A')
                print(f"   {i}. {title[:60]}")
                print(f"      Price: ${price}")
            return True
        else:
            print(f"   ⚠️  API call succeeded but returned no products")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ API CALL FAILED")
        print(f"   Error: {error_msg}")
        return False
    
    # Test 3: Generate Affiliate Link
    print(f"\n{'='*80}")
    print("TEST 3: Generate Affiliate Link (REAL API CALL)")
    print(f"{'='*80}")
    try:
        print("   Making API call...")
        test_url = "https://www.aliexpress.com/item/1005006265991420.html"
        links = api.get_affiliate_links([test_url])
        
        if links:
            print(f"   ✅ SUCCESS! Generated {len(links)} affiliate link(s)")
            print(f"\n   🎉 REAL DATA CONFIRMED - Not mock mode!")
            for i, link in enumerate(links, 1):
                promo_link = getattr(link, 'promotion_link', 'N/A')
                print(f"   {i}. Affiliate Link: {promo_link[:70]}...")
            return True
        else:
            print(f"   ⚠️  API call succeeded but returned no links")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ API CALL FAILED")
        print(f"   Error: {error_msg}")
        return False

if __name__ == "__main__":
    print("\n⚠️  WARNING: This test will ONLY use real API calls")
    print("   Mock mode is DISABLED")
    print("   Any failures indicate actual API issues\n")
    
    success = test_real_api()
    
    print(f"\n{'='*80}")
    print("FINAL VERDICT")
    print(f"{'='*80}")
    
    if success:
        print("\n✅ ALIEXPRESS API IS WORKING WITH REAL DATA")
        print("   Your credentials are valid and approved!")
        print("   The API is returning genuine AliExpress data.")
    else:
        print("\n❌ ALIEXPRESS API IS NOT WORKING")
        print("   The credentials are still invalid or not approved.")
        print("   Please verify your APP_KEY and APP_SECRET.")
        print("\n   Next steps:")
        print("   1. Log in to https://portals.aliexpress.com/")
        print("   2. Verify your application is approved")
        print("   3. Copy the correct production credentials")
        print("   4. Update the .env file")
        print("   5. Run this test again")
    
    print(f"{'='*80}\n")
    
    sys.exit(0 if success else 1)
