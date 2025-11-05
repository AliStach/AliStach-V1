#!/usr/bin/env python3
"""
Script to check available AliExpress API methods for image search functionality.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    from aliexpress_api import AliexpressApi
    print("✅ AliExpress API SDK is available")
    
    # Check available methods
    api_methods = [method for method in dir(AliexpressApi) if not method.startswith('_')]
    print(f"📋 Available API methods ({len(api_methods)}):")
    
    image_related_methods = []
    for method in api_methods:
        if 'image' in method.lower():
            image_related_methods.append(method)
            print(f"  🖼️  {method}")
    
    if not image_related_methods:
        print("  ⚠️  No image-related methods found in SDK")
        print("  📝 Available methods:")
        for method in sorted(api_methods):
            print(f"     - {method}")
    
    # Check if we can inspect the SDK source or documentation
    try:
        import inspect
        api_source = inspect.getsource(AliexpressApi)
        if 'image' in api_source.lower():
            print("\n🔍 Found image-related code in SDK source")
        else:
            print("\n❌ No image search functionality found in current SDK")
    except:
        print("\n⚠️  Could not inspect SDK source code")
        
except ImportError as e:
    print(f"❌ AliExpress API SDK not available: {e}")
    print("💡 Install with: pip install python-aliexpress-api")

# Check official AliExpress API documentation references
print("\n📚 Official AliExpress API Image Search Endpoints:")
print("   - aliexpress.affiliate.image.search")
print("   - aliexpress.affiliate.image.recommend") 
print("   - aliexpress.affiliate.image.query")
print("   - aliexpress.affiliate.smartmatch")

print("\n🔗 Documentation URLs to check:")
print("   - https://developers.aliexpress.com/en/doc.htm")
print("   - https://portals.aliexpress.com/")
print("   - https://open.aliexpress.com/")