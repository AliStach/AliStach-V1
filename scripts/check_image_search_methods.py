#!/usr/bin/env python3
"""
Script to check available image search methods in the AliExpress SDK.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    from aliexpress_api import AliexpressApi
    import inspect
    
    print("🔍 Checking AliExpress SDK for image search methods...")
    print("=" * 60)
    
    # Get all methods from AliexpressApi
    api_methods = [method for method in dir(AliexpressApi) if not method.startswith('_')]
    
    print(f"📋 Total API methods available: {len(api_methods)}")
    print()
    
    # Look for image-related methods
    image_methods = [method for method in api_methods if 'image' in method.lower()]
    
    if image_methods:
        print("🖼️  Image-related methods found:")
        for method in image_methods:
            print(f"   - {method}")
    else:
        print("❌ No image-related methods found in SDK")
    
    print()
    
    # Look for search-related methods
    search_methods = [method for method in api_methods if 'search' in method.lower()]
    
    if search_methods:
        print("🔍 Search-related methods found:")
        for method in search_methods:
            print(f"   - {method}")
    
    print()
    
    # Print all available methods for reference
    print("📚 All available methods:")
    for i, method in enumerate(api_methods, 1):
        print(f"   {i:2d}. {method}")
    
    print()
    print("🔧 Checking method signatures...")
    
    # Try to get method signatures for key methods
    key_methods = ['get_products', 'get_affiliate_links', 'get_hotproducts']
    
    for method_name in key_methods:
        if hasattr(AliexpressApi, method_name):
            method = getattr(AliexpressApi, method_name)
            try:
                sig = inspect.signature(method)
                print(f"   {method_name}{sig}")
            except Exception as e:
                print(f"   {method_name}: Could not get signature - {e}")
    
    print()
    print("✅ SDK inspection complete!")
    
except ImportError as e:
    print(f"❌ Failed to import AliExpress SDK: {e}")
    print("💡 Install with: pip install python-aliexpress-api")
except Exception as e:
    print(f"❌ Error during SDK inspection: {e}")