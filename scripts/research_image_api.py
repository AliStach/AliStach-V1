#!/usr/bin/env python3
"""
Research script to check AliExpress API documentation for image search endpoints.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    from aliexpress_api import AliexpressApi
    from src.utils.config import Config
    
    print("🔍 Researching AliExpress Image Search API Endpoints...")
    print("=" * 60)
    
    # Load configuration
    config = Config.from_env()
    
    # Initialize API
    api = AliexpressApi(
        key=config.app_key,
        secret=config.app_secret,
        language="EN",
        currency="USD",
        tracking_id=config.tracking_id
    )
    
    print("✅ API initialized successfully")
    print(f"   App Key: {config.app_key}")
    print(f"   Tracking ID: {config.tracking_id}")
    print()
    
    # Check if the API object has any internal methods we can access
    print("🔧 Checking internal API structure...")
    
    # Look at the API object's attributes
    api_attrs = [attr for attr in dir(api) if not attr.startswith('_')]
    print(f"📋 API object attributes: {len(api_attrs)}")
    
    for attr in api_attrs:
        attr_obj = getattr(api, attr)
        if callable(attr_obj):
            print(f"   📞 {attr}() - callable method")
        else:
            print(f"   📄 {attr} - {type(attr_obj).__name__}")
    
    print()
    
    # Check if we can access the base URL or make custom requests
    if hasattr(api, 'base_url') or hasattr(api, '_base_url'):
        base_url = getattr(api, 'base_url', getattr(api, '_base_url', 'Unknown'))
        print(f"🌐 Base URL: {base_url}")
    
    # Check for request methods
    if hasattr(api, '_make_request') or hasattr(api, 'make_request'):
        print("✅ Found request method - we can make custom API calls")
    
    print()
    print("📚 Known AliExpress Image Search Endpoints (from documentation):")
    print("   1. aliexpress.affiliate.image.search")
    print("   2. aliexpress.affiliate.image.recommend") 
    print("   3. aliexpress.affiliate.image.query")
    print("   4. aliexpress.affiliate.product.smartmatch")
    print()
    
    # Try to access smart_match_product to see its parameters
    print("🔍 Analyzing smart_match_product method...")
    try:
        import inspect
        sig = inspect.signature(api.smart_match_product)
        print(f"   Signature: smart_match_product{sig}")
        
        # Check the source code if possible
        try:
            source = inspect.getsource(api.smart_match_product)
            print("   📝 Method source available - checking for image support...")
            if 'image' in source.lower():
                print("   ✅ Found 'image' references in smart_match_product")
            else:
                print("   ❌ No 'image' references in smart_match_product")
        except:
            print("   ❌ Cannot access method source code")
            
    except Exception as e:
        print(f"   ❌ Error analyzing smart_match_product: {e}")
    
    print()
    print("🧪 Testing smart_match_product with image URL...")
    
    # Test with a sample image URL
    test_image_url = "https://ae01.alicdn.com/kf/H8c9c8f5c5d5a4c5b9a5c5d5a4c5b9a5c/Wireless-Bluetooth-Headphones.jpg"
    
    try:
        # Try different parameter combinations
        test_params = [
            {"product_url": test_image_url},
            {"image_url": test_image_url},
            {"url": test_image_url},
            {"product_url": test_image_url, "device_id": "test_device"},
        ]
        
        for i, params in enumerate(test_params, 1):
            try:
                print(f"   Test {i}: {params}")
                result = api.smart_match_product(**params)
                print(f"   ✅ Success! Result type: {type(result)}")
                if hasattr(result, '__dict__'):
                    print(f"   📊 Result attributes: {list(result.__dict__.keys())}")
                break
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
    except Exception as e:
        print(f"   ❌ All tests failed: {e}")
    
    print()
    print("✅ Research complete!")
    
except Exception as e:
    print(f"❌ Research failed: {e}")
    import traceback
    traceback.print_exc()