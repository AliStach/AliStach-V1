#!/usr/bin/env python3
"""
Check available methods in the AliExpress SDK.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
from aliexpress_api import AliexpressApi, models

def main():
    """Check available SDK methods."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Initialize API
        api = AliexpressApi(
            key=config.app_key,
            secret=config.app_secret,
            language=getattr(models.Language, config.language),
            currency=getattr(models.Currency, config.currency),
            tracking_id=config.tracking_id
        )
        
        print("🔍 Available AliExpress SDK Methods:")
        print("=" * 50)
        
        methods = [method for method in dir(api) if not method.startswith('_')]
        
        for method in sorted(methods):
            print(f"  - {method}")
        
        print(f"\n📊 Total methods: {len(methods)}")
        
        # Test a few key methods
        print("\n🧪 Testing key methods:")
        
        try:
            categories = api.get_parent_categories()
            print(f"✅ get_parent_categories: {len(categories)} categories")
        except Exception as e:
            print(f"❌ get_parent_categories: {e}")
        
        try:
            products = api.get_products(keywords="test", page_size=1)
            print(f"✅ get_products: Works")
        except Exception as e:
            print(f"❌ get_products: {e}")
        
        # Check if hotproducts method exists
        if hasattr(api, 'get_hotproducts'):
            try:
                hot = api.get_hotproducts(keywords="test", page_size=1)
                print(f"✅ get_hotproducts: Works")
            except Exception as e:
                print(f"❌ get_hotproducts: {e}")
        else:
            print("❌ get_hotproducts: Method not available")
        
        # Check affiliate links
        if hasattr(api, 'get_affiliate_links'):
            try:
                links = api.get_affiliate_links(['https://www.aliexpress.com/item/1005003091506814.html'])
                print(f"✅ get_affiliate_links: Works")
            except Exception as e:
                print(f"❌ get_affiliate_links: {e}")
        else:
            print("❌ get_affiliate_links: Method not available")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()