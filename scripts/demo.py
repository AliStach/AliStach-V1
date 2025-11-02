#!/usr/bin/env python3
"""
Demo script for AliExpress API service.
This script replicates the functionality of the original working code.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config, ConfigurationError
from src.services.aliexpress_service import AliExpressService, AliExpressServiceException


def main():
    """Main demo function."""
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
        
        # Get parent categories (replicating original functionality)
        print("📂 Parent Categories:")
        print()
        
        parent_categories = service.get_parent_categories()
        
        for parent in parent_categories:
            print(f"ID: {parent.category_id} | Name: {parent.category_name}")
        
        # Get child categories for the first parent (replicating original functionality)
        if parent_categories:
            first_parent = parent_categories[0]
            first_parent_id = first_parent.category_id
            
            print(f"\n📁 Child Categories of {first_parent.category_name}:")
            print()
            
            child_categories = service.get_child_categories(first_parent_id)
            for child in child_categories:
                print(f"  ↳ ID: {child.category_id} | Name: {child.category_name}")
        
        print(f"\n✅ Demo completed successfully! Found {len(parent_categories)} parent categories.")
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Make sure you have set the following environment variables:")
        print("   - ALIEXPRESS_APP_KEY")
        print("   - ALIEXPRESS_APP_SECRET")
        print("   - ALIEXPRESS_TRACKING_ID (optional, defaults to 'gpt_chat')")
        sys.exit(1)
        
    except AliExpressServiceException as e:
        print(f"❌ AliExpress service error: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()