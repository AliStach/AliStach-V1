#!/usr/bin/env python3
"""
Demo script for AliExpress API service.
This script demonstrates the core functionality of the refactored Python service.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config, ConfigurationError
from src.services.aliexpress_service import AliExpressService, AliExpressServiceException


def demo_basic_functionality(service):
    """Demo basic AliExpress API functionality."""
    print("📂 Getting parent categories...")
    parent_categories = service.get_parent_categories()
    
    print(f"✅ Found {len(parent_categories)} parent categories:")
    for i, category in enumerate(parent_categories[:5]):  # Show first 5
        print(f"   {i+1}. ID: {category.category_id} | Name: {category.category_name}")
    
    if parent_categories:
        # Get child categories for the first parent
        first_parent = parent_categories[0]
        print(f"\n📁 Getting child categories for '{first_parent.category_name}' (ID: {first_parent.category_id})...")
        
        try:
            child_categories = service.get_child_categories(first_parent.category_id)
            print(f"✅ Found {len(child_categories)} child categories:")
            for i, category in enumerate(child_categories[:3]):  # Show first 3
                print(f"   {i+1}. ID: {category.category_id} | Name: {category.category_name}")
        except Exception as e:
            print(f"⚠️  Could not get child categories: {e}")
    
    print()


def demo_product_search(service):
    """Demo product search functionality."""
    print("🔍 Searching for products...")
    
    try:
        # Search for products
        search_result = service.search_products(
            keywords="wireless headphones",
            page_size=3
        )
        
        print(f"✅ Found {search_result.total_record_count} total products (showing {len(search_result.products)}):")
        
        for i, product in enumerate(search_result.products):
            print(f"\n   Product {i+1}:")
            print(f"   📱 Title: {product.product_title[:50]}...")
            print(f"   💰 Price: {product.price} {product.currency}")
            print(f"   🔗 URL: {product.product_url[:60]}...")
            if product.commission_rate:
                print(f"   💼 Commission: {product.commission_rate}%")
        
        print()
        
        # Demo affiliate link generation
        if search_result.products:
            print("🔗 Generating affiliate links...")
            product_urls = [product.product_url for product in search_result.products[:2]]
            
            try:
                affiliate_links = service.get_affiliate_links(product_urls)
                print(f"✅ Generated {len(affiliate_links)} affiliate links:")
                
                for i, link in enumerate(affiliate_links):
                    print(f"\n   Link {i+1}:")
                    print(f"   📎 Original: {link.original_url[:50]}...")
                    print(f"   🔗 Affiliate: {link.affiliate_url[:50]}...")
                    print(f"   🎯 Tracking ID: {link.tracking_id}")
                    if link.commission_rate:
                        print(f"   💼 Commission: {link.commission_rate}%")
                        
            except Exception as e:
                print(f"⚠️  Could not generate affiliate links: {e}")
                print("💡 This may require special API permissions")
        
    except Exception as e:
        print(f"⚠️  Product search failed: {e}")
    
    print()


def demo_service_info(service):
    """Demo service information."""
    print("ℹ️  Service Information:")
    
    try:
        service_info = service.get_service_info()
        print(f"   📋 Service: {service_info['service']}")
        print(f"   🔢 Version: {service_info['version']}")
        print(f"   🌐 Language: {service_info['language']}")
        print(f"   💱 Currency: {service_info['currency']}")
        print(f"   🎯 Tracking ID: {service_info['tracking_id']}")
        print(f"   ✅ Status: {service_info['status']}")
        
        print(f"\n   🔧 Supported Endpoints ({len(service_info['supported_endpoints'])}):")
        for endpoint in service_info['supported_endpoints']:
            print(f"      • {endpoint}")
            
        if 'notes' in service_info:
            print(f"\n   📝 Important Notes:")
            for feature, note in service_info['notes'].items():
                print(f"      • {feature}: {note}")
                
    except Exception as e:
        print(f"⚠️  Could not get service info: {e}")
    
    print()


def main():
    """Main demo function demonstrating the refactored AliExpress service."""
    print("🚀 AliExpress API Service Demo")
    print("=" * 50)
    print()
    
    try:
        # Load configuration from environment
        print("🔧 Loading configuration...")
        config = Config.from_env()
        config.validate()
        print(f"✅ Configuration loaded successfully")
        print(f"   - App Key: {config.app_key}")
        print(f"   - Language: {config.language}")
        print(f"   - Currency: {config.currency}")
        print(f"   - Tracking ID: {config.tracking_id}")
        print()
        
        # Initialize AliExpress service
        print("🚀 Initializing AliExpress service...")
        service = AliExpressService(config)
        print("✅ AliExpress service initialized successfully")
        print()
        
        # Demo 1: Basic functionality (categories)
        print("=" * 50)
        print("📂 DEMO 1: Category Management")
        print("=" * 50)
        demo_basic_functionality(service)
        
        # Demo 2: Product search and affiliate links
        print("=" * 50)
        print("🔍 DEMO 2: Product Search & Affiliate Links")
        print("=" * 50)
        demo_product_search(service)
        
        # Demo 3: Service information
        print("=" * 50)
        print("ℹ️  DEMO 3: Service Information")
        print("=" * 50)
        demo_service_info(service)
        
        print("🎉 Demo completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ Category retrieval (parent and child)")
        print("   ✅ Product search with filtering")
        print("   ✅ Automatic affiliate link generation")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Service configuration and status")
        print("\n🔗 The service is ready for integration with your applications!")
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure you have set the following environment variables:")
        print("   - ALIEXPRESS_APP_KEY")
        print("   - ALIEXPRESS_APP_SECRET")
        print("   - ALIEXPRESS_TRACKING_ID (optional, defaults to 'gpt_chat')")
        sys.exit(1)
        
    except AliExpressServiceException as e:
        print(f"❌ AliExpress service error: {e}")
        print("\n💡 This might be due to:")
        print("   - Invalid API credentials")
        print("   - Network connectivity issues")
        print("   - AliExpress API rate limits")
        print("   - Missing API permissions")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n💡 Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()