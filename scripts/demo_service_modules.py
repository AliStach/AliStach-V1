#!/usr/bin/env python3
"""
Demonstration script for AliExpress API service modules.

This script shows how to use the individual service modules that follow
the same structure and pattern as the official SDK.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.utils.config import Config
    from src.services.aliexpress import (
        AliExpressServiceFactory,
        AliexpressAffiliateProductQueryRequest,
        AliexpressAffiliateCategoryGetRequest,
        AliexpressAffiliateLinkGenerateRequest,
        AliexpressAffiliateImageSearchRequest
    )
    print("✅ Successfully imported AliExpress service modules")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


def demo_factory_usage():
    """Demonstrate using the service factory."""
    print("\n" + "="*60)
    print("DEMO: Using AliExpress Service Factory")
    print("="*60)
    
    try:
        # Load configuration
        config = Config.from_env()
        print(f"✅ Configuration loaded successfully")
        print(f"   Language: {config.language}")
        print(f"   Currency: {config.currency}")
        
        # Create factory
        factory = AliExpressServiceFactory(config)
        
        # List available services
        print(f"\n📋 Available services:")
        services = factory.get_available_services()
        for service_name, description in services.items():
            print(f"   • {service_name}: {description}")
        
        # Create a product query service using factory
        print(f"\n🔍 Creating product query service...")
        product_service = factory.product_query(
            keywords="smartphone",
            page_size=5,
            sort="SALE_PRICE_ASC"
        )
        
        print(f"✅ Product query service created")
        print(f"   API Name: {product_service.getapiname()}")
        print(f"   Keywords: {product_service.keywords}")
        print(f"   Page Size: {product_service.page_size}")
        print(f"   Sort: {product_service.sort}")
        
        # Create category service using factory
        print(f"\n📂 Creating category service...")
        category_service = factory.category_get()
        
        print(f"✅ Category service created")
        print(f"   API Name: {category_service.getapiname()}")
        
    except Exception as e:
        print(f"❌ Factory demo failed: {e}")


def demo_direct_usage():
    """Demonstrate using service modules directly."""
    print("\n" + "="*60)
    print("DEMO: Using Service Modules Directly")
    print("="*60)
    
    try:
        # Load configuration
        config = Config.from_env()
        
        # Create product query service directly
        print(f"\n🔍 Creating product query service directly...")
        product_service = AliexpressAffiliateProductQueryRequest()
        product_service.set_config(config)
        
        # Set parameters
        product_service.keywords = "laptop"
        product_service.page_no = 1
        product_service.page_size = 10
        product_service.target_currency = config.currency
        product_service.target_language = config.language
        product_service.sort = "SALE_PRICE_ASC"
        
        print(f"✅ Product query service configured")
        print(f"   API Name: {product_service.getapiname()}")
        print(f"   Keywords: {product_service.keywords}")
        print(f"   Currency: {product_service.target_currency}")
        print(f"   Language: {product_service.target_language}")
        
        # Create link generation service
        print(f"\n🔗 Creating link generation service...")
        link_service = AliexpressAffiliateLinkGenerateRequest()
        link_service.set_config(config)
        
        # Set parameters
        link_service.source_values = "https://www.aliexpress.com/item/1005001234567890.html"
        link_service.promotion_link_type = 0
        
        print(f"✅ Link generation service configured")
        print(f"   API Name: {link_service.getapiname()}")
        print(f"   Source Values: {link_service.source_values}")
        
        # Create image search service
        print(f"\n🖼️ Creating image search service...")
        image_service = AliexpressAffiliateImageSearchRequest()
        image_service.set_config(config)
        
        # Set parameters
        image_service.image_url = "https://example.com/sample-image.jpg"
        image_service.page_size = 20
        image_service.target_currency = config.currency
        image_service.target_language = config.language
        
        print(f"✅ Image search service configured")
        print(f"   API Name: {image_service.getapiname()}")
        print(f"   Image URL: {image_service.image_url}")
        
    except Exception as e:
        print(f"❌ Direct usage demo failed: {e}")


def demo_api_execution():
    """Demonstrate executing API calls (with error handling)."""
    print("\n" + "="*60)
    print("DEMO: API Execution (Error Handling)")
    print("="*60)
    
    try:
        # Load configuration
        config = Config.from_env()
        
        # Create and configure category service
        print(f"\n📂 Testing category API call...")
        category_service = AliexpressAffiliateCategoryGetRequest()
        category_service.set_config(config)
        
        print(f"   API URL: {category_service.get_api_url()}")
        print(f"   API Method: {category_service.getapiname()}")
        
        # Note: We're not actually executing the API call in this demo
        # to avoid making real API requests during demonstration
        print(f"   ⚠️  API execution skipped in demo mode")
        print(f"   ℹ️  To execute real API calls, call service.execute()")
        
        # Show how parameters would be prepared
        print(f"\n🔧 Parameter preparation example...")
        params = category_service._prepare_request_params()
        
        # Remove sensitive information for display
        display_params = {k: v for k, v in params.items() if k not in ['app_key', 'sign']}
        print(f"   Parameters: {json.dumps(display_params, indent=2)}")
        
    except Exception as e:
        print(f"❌ API execution demo failed: {e}")


def main():
    """Main demonstration function."""
    print("🚀 AliExpress API Service Modules Demo")
    print("=====================================")
    
    # Check if configuration is available
    try:
        config = Config.from_env()
        print(f"✅ Configuration available")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print(f"ℹ️  Please ensure .env file is configured with AliExpress API credentials")
        return
    
    # Run demonstrations
    demo_factory_usage()
    demo_direct_usage()
    demo_api_execution()
    
    print("\n" + "="*60)
    print("✅ Demo completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Configure your .env file with valid AliExpress API credentials")
    print("2. Use the service modules in your application")
    print("3. Call service.execute() to make actual API requests")
    print("4. Handle the JSON responses according to your needs")


if __name__ == "__main__":
    main()