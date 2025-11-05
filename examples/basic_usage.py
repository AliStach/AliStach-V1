#!/usr/bin/env python3
"""
Basic usage examples for the AliExpress API service.

This file demonstrates common usage patterns and best practices.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config, ConfigurationError
from src.services.aliexpress_service import AliExpressService, AliExpressServiceException


def example_basic_setup():
    """Example: Basic service setup and configuration."""
    print("=== Basic Setup Example ===")
    
    try:
        # Load configuration from environment variables
        config = Config.from_env()
        config.validate()
        
        # Initialize the service
        service = AliExpressService(config)
        
        print(f"✅ Service initialized successfully")
        print(f"   Language: {config.language}")
        print(f"   Currency: {config.currency}")
        print(f"   Tracking ID: {config.tracking_id}")
        
        return service
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return None
    except AliExpressServiceException as e:
        print(f"❌ Service error: {e}")
        return None


def example_categories(service: AliExpressService):
    """Example: Working with categories."""
    print("\n=== Categories Example ===")
    
    try:
        # Get parent categories
        print("📂 Fetching parent categories...")
        parent_categories = service.get_parent_categories()
        
        print(f"✅ Found {len(parent_categories)} parent categories")
        
        # Show first 3 categories
        for i, category in enumerate(parent_categories[:3]):
            print(f"   {i+1}. {category.category_name} (ID: {category.category_id})")
        
        # Get child categories for the first parent
        if parent_categories:
            first_parent = parent_categories[0]
            print(f"\n📁 Fetching child categories for '{first_parent.category_name}'...")
            
            child_categories = service.get_child_categories(first_parent.category_id)
            print(f"✅ Found {len(child_categories)} child categories")
            
            for i, category in enumerate(child_categories[:3]):
                print(f"   {i+1}. {category.category_name} (ID: {category.category_id})")
                
    except AliExpressServiceException as e:
        print(f"❌ Categories error: {e}")


def example_product_search(service: AliExpressService):
    """Example: Searching for products."""
    print("\n=== Product Search Example ===")
    
    try:
        # Basic product search
        print("🔍 Searching for 'wireless headphones'...")
        search_result = service.search_products(
            keywords="wireless headphones",
            page_size=5
        )
        
        print(f"✅ Found {search_result.total_record_count} total products")
        print(f"   Showing {len(search_result.products)} products:")
        
        for i, product in enumerate(search_result.products):
            print(f"\n   Product {i+1}:")
            print(f"   📱 Title: {product.product_title[:50]}...")
            print(f"   💰 Price: {product.price} {product.currency}")
            print(f"   🔗 URL: {product.product_url[:50]}...")
            if product.commission_rate:
                print(f"   💼 Commission: {product.commission_rate}%")
        
        return search_result.products
        
    except AliExpressServiceException as e:
        print(f"❌ Search error: {e}")
        return []


def example_affiliate_links(service: AliExpressService, products):
    """Example: Generating affiliate links."""
    print("\n=== Affiliate Links Example ===")
    
    if not products:
        print("⚠️  No products available for affiliate link generation")
        return
    
    try:
        # Get URLs from first 2 products
        product_urls = [product.product_url for product in products[:2]]
        
        print(f"🔗 Generating affiliate links for {len(product_urls)} products...")
        affiliate_links = service.get_affiliate_links(product_urls)
        
        print(f"✅ Generated {len(affiliate_links)} affiliate links:")
        
        for i, link in enumerate(affiliate_links):
            print(f"\n   Link {i+1}:")
            print(f"   📎 Original: {link.original_url[:50]}...")
            print(f"   🔗 Affiliate: {link.affiliate_url[:50]}...")
            print(f"   🎯 Tracking ID: {link.tracking_id}")
            if link.commission_rate:
                print(f"   💼 Commission: {link.commission_rate}%")
                
    except AliExpressServiceException as e:
        print(f"❌ Affiliate links error: {e}")


def example_enhanced_search(service: AliExpressService):
    """Example: Enhanced product search with filters."""
    print("\n=== Enhanced Search Example ===")
    
    try:
        # Search with price filters
        print("🔍 Searching for phones under $200...")
        search_result = service.get_products(
            keywords="smartphone",
            max_sale_price=200.0,
            min_sale_price=50.0,
            page_size=3
        )
        
        print(f"✅ Found {search_result.total_record_count} products in price range")
        
        for i, product in enumerate(search_result.products):
            print(f"\n   Product {i+1}:")
            print(f"   📱 Title: {product.product_title[:40]}...")
            print(f"   💰 Price: ${product.price}")
            
    except AliExpressServiceException as e:
        print(f"❌ Enhanced search error: {e}")


def example_error_handling():
    """Example: Proper error handling patterns."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Try to create service with invalid config
        config = Config(
            app_key="invalid",
            app_secret="invalid",
            tracking_id="test"
        )
        
        service = AliExpressService(config)
        
        # This will likely fail with API error
        categories = service.get_parent_categories()
        
    except ConfigurationError as e:
        print(f"🔧 Configuration Error: {e}")
        print("💡 Check your environment variables")
        
    except AliExpressServiceException as e:
        print(f"🔌 API Error: {e}")
        print("💡 Check your AliExpress credentials and permissions")
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("💡 This might be a bug - please report it")


def main():
    """Run all examples."""
    print("🚀 AliExpress API Service - Usage Examples")
    print("=" * 50)
    
    # Example 1: Basic setup
    service = example_basic_setup()
    
    if service is None:
        print("\n❌ Cannot continue without valid service instance")
        print("💡 Make sure you have set ALIEXPRESS_APP_KEY and ALIEXPRESS_APP_SECRET")
        return
    
    # Example 2: Categories
    example_categories(service)
    
    # Example 3: Product search
    products = example_product_search(service)
    
    # Example 4: Affiliate links
    example_affiliate_links(service, products)
    
    # Example 5: Enhanced search
    example_enhanced_search(service)
    
    # Example 6: Error handling
    example_error_handling()
    
    print("\n🎉 Examples completed!")
    print("\n💡 Next Steps:")
    print("   - Check the FastAPI endpoints: python -m src.api.main")
    print("   - Run the full demo: python scripts/demo.py")
    print("   - Read the documentation: http://localhost:8000/docs")


if __name__ == "__main__":
    main()