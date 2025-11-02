#!/usr/bin/env python3
"""
Basic usage examples for the AliExpress API service.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService


def example_1_basic_setup():
    """Example 1: Basic service setup and configuration."""
    print("Example 1: Basic Setup")
    print("-" * 30)
    
    # Load configuration from environment
    config = Config.from_env()
    print(f"Loaded config: {config.language}/{config.currency}")
    
    # Initialize service
    service = AliExpressService(config)
    print("Service initialized successfully")
    print()


def example_2_get_categories():
    """Example 2: Get parent and child categories."""
    print("Example 2: Categories")
    print("-" * 30)
    
    config = Config.from_env()
    service = AliExpressService(config)
    
    # Get parent categories
    categories = service.get_parent_categories()
    print(f"Found {len(categories)} parent categories:")
    
    for i, category in enumerate(categories[:5]):  # Show first 5
        print(f"  {i+1}. {category.category_name} (ID: {category.category_id})")
    
    if categories:
        # Get child categories for first parent
        first_parent = categories[0]
        children = service.get_child_categories(first_parent.category_id)
        print(f"\nChild categories of '{first_parent.category_name}': {len(children)}")
        
        for child in children[:3]:  # Show first 3
            print(f"  - {child.category_name} (ID: {child.category_id})")
    
    print()


def example_3_search_products():
    """Example 3: Search for products."""
    print("Example 3: Product Search")
    print("-" * 30)
    
    config = Config.from_env()
    service = AliExpressService(config)
    
    # Search for products
    results = service.search_products(
        keywords="wireless headphones",
        page_size=5
    )
    
    print(f"Found {results.total_record_count} total products")
    print(f"Showing {len(results.products)} products on page {results.current_page}:")
    
    for i, product in enumerate(results.products, 1):
        print(f"  {i}. {product.product_title}")
        print(f"     Price: {product.price} {product.currency}")
        print(f"     ID: {product.product_id}")
        print()


def example_4_error_handling():
    """Example 4: Error handling."""
    print("Example 4: Error Handling")
    print("-" * 30)
    
    config = Config.from_env()
    service = AliExpressService(config)
    
    try:
        # This should work
        categories = service.get_parent_categories()
        print(f"✅ Successfully got {len(categories)} categories")
        
        # This might fail with invalid parent ID
        try:
            children = service.get_child_categories("invalid_id")
            print(f"Got {len(children)} children for invalid ID")
        except Exception as e:
            print(f"❌ Expected error for invalid ID: {e}")
        
        # This should fail with validation error
        try:
            results = service.search_products(page_size=100)  # Too large
        except Exception as e:
            print(f"❌ Expected validation error: {e}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()


def main():
    """Run all examples."""
    print("🚀 AliExpress API Service Examples")
    print("=" * 50)
    
    try:
        example_1_basic_setup()
        example_2_get_categories()
        example_3_search_products()
        example_4_error_handling()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("\n💡 Make sure you have:")
        print("   - Set up your .env file with AliExpress credentials")
        print("   - Installed all dependencies: pip install -r requirements.txt")


if __name__ == "__main__":
    main()