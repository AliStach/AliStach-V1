#!/usr/bin/env python3
"""
Integration example showing how the new service modules work alongside
the existing AliExpressService class.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.utils.config import Config
    from src.services.aliexpress_service import AliExpressService
    from src.services.aliexpress import (
        AliExpressServiceFactory,
        AliexpressAffiliateProductQueryRequest
    )
    print("✅ Successfully imported both service approaches")
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)


def compare_approaches():
    """Compare the high-level service vs low-level service modules."""
    print("\n" + "="*70)
    print("COMPARISON: High-Level Service vs Service Modules")
    print("="*70)
    
    try:
        # Load configuration
        config = Config.from_env()
        
        print("\n🔧 Configuration:")
        print(f"   App Key: {config.app_key[:10]}...")
        print(f"   Language: {config.language}")
        print(f"   Currency: {config.currency}")
        print(f"   Tracking ID: {config.tracking_id}")
        
        # Approach 1: High-level AliExpressService
        print(f"\n📈 Approach 1: High-Level AliExpressService")
        print(f"   ✅ Pros: Built-in response parsing, error handling, retry logic")
        print(f"   ✅ Pros: Convenient methods with typed responses")
        print(f"   ✅ Pros: Automatic affiliate link generation")
        print(f"   ⚠️  Cons: Less control over raw API parameters")
        
        high_level_service = AliExpressService(config)
        print(f"   Service Info: {high_level_service.get_service_info()['service']}")
        
        # Approach 2: Low-level Service Modules
        print(f"\n🔧 Approach 2: Low-Level Service Modules")
        print(f"   ✅ Pros: Direct API access with full parameter control")
        print(f"   ✅ Pros: Matches official SDK structure exactly")
        print(f"   ✅ Pros: Easy to extend with new API endpoints")
        print(f"   ⚠️  Cons: Requires manual response parsing")
        
        factory = AliExpressServiceFactory(config)
        available_services = len(factory.get_available_services())
        print(f"   Available Services: {available_services} API endpoints")
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")


def demonstrate_use_cases():
    """Show when to use each approach."""
    print("\n" + "="*70)
    print("USE CASES: When to Use Each Approach")
    print("="*70)
    
    print(f"\n🎯 Use High-Level AliExpressService when:")
    print(f"   • You need quick, convenient access to common operations")
    print(f"   • You want built-in response parsing and error handling")
    print(f"   • You're building a typical affiliate application")
    print(f"   • You want automatic affiliate link generation")
    
    print(f"\n🔧 Use Service Modules when:")
    print(f"   • You need direct control over API parameters")
    print(f"   • You're implementing custom business logic")
    print(f"   • You want to match the official SDK structure exactly")
    print(f"   • You need to access newer API endpoints not yet in high-level service")
    print(f"   • You're building a library or framework on top of AliExpress API")


def show_parameter_flexibility():
    """Demonstrate the parameter flexibility of service modules."""
    print("\n" + "="*70)
    print("FLEXIBILITY: Service Module Parameter Control")
    print("="*70)
    
    try:
        config = Config.from_env()
        
        # Create a product query service with custom parameters
        print(f"\n🔍 Custom Product Query Example:")
        
        service = AliexpressAffiliateProductQueryRequest()
        service.set_config(config)
        
        # Set all available parameters
        service.keywords = "wireless headphones"
        service.category_ids = "509,3"  # Electronics categories
        service.page_no = 1
        service.page_size = 50  # Maximum allowed
        service.min_sale_price = 1000  # $10.00 in cents
        service.max_sale_price = 5000  # $50.00 in cents
        service.sort = "SALE_PRICE_ASC"
        service.ship_to_country = "US"
        service.delivery_days = 15
        service.platform_product_type = "ALL"
        service.target_currency = "USD"
        service.target_language = "EN"
        
        # Show all configured parameters
        print(f"   Keywords: {service.keywords}")
        print(f"   Categories: {service.category_ids}")
        print(f"   Price Range: ${service.min_sale_price/100:.2f} - ${service.max_sale_price/100:.2f}")
        print(f"   Page: {service.page_no}, Size: {service.page_size}")
        print(f"   Sort: {service.sort}")
        print(f"   Ship To: {service.ship_to_country}")
        print(f"   Max Delivery: {service.delivery_days} days")
        
        # Show prepared parameters (without executing)
        params = service._prepare_request_params()
        param_count = len([k for k, v in params.items() if v is not None])
        print(f"   Total Parameters: {param_count}")
        
    except Exception as e:
        print(f"❌ Parameter demo failed: {e}")


def show_factory_convenience():
    """Demonstrate the convenience of the service factory."""
    print("\n" + "="*70)
    print("CONVENIENCE: Service Factory Usage")
    print("="*70)
    
    try:
        config = Config.from_env()
        factory = AliExpressServiceFactory(config)
        
        print(f"\n🏭 Factory Benefits:")
        print(f"   • Automatic configuration injection")
        print(f"   • Convenient parameter setting")
        print(f"   • Service discovery and listing")
        print(f"   • Consistent interface across all services")
        
        # Quick service creation examples
        print(f"\n📋 Quick Service Creation:")
        
        # Product search
        product_service = factory.product_query(
            keywords="smartphone",
            page_size=20,
            sort="SALE_PRICE_ASC"
        )
        print(f"   Product Query: {product_service.getapiname()}")
        
        # Category service
        category_service = factory.category_get()
        print(f"   Category Get: {category_service.getapiname()}")
        
        # Link generation
        link_service = factory.link_generate(
            source_values="https://www.aliexpress.com/item/123456789.html",
            promotion_link_type=0
        )
        print(f"   Link Generate: {link_service.getapiname()}")
        
        # Image search
        image_service = factory.image_search(
            image_url="https://example.com/image.jpg",
            page_size=30
        )
        print(f"   Image Search: {image_service.getapiname()}")
        
        print(f"\n✅ All services created and configured successfully!")
        
    except Exception as e:
        print(f"❌ Factory demo failed: {e}")


def main():
    """Main demonstration function."""
    print("🔗 AliExpress Service Integration Example")
    print("=========================================")
    
    # Check configuration
    try:
        config = Config.from_env()
        print(f"✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Run demonstrations
    compare_approaches()
    demonstrate_use_cases()
    show_parameter_flexibility()
    show_factory_convenience()
    
    print("\n" + "="*70)
    print("✅ Integration example completed!")
    print("="*70)
    print(f"\n💡 Key Takeaways:")
    print(f"   • Both approaches complement each other")
    print(f"   • Use high-level service for common operations")
    print(f"   • Use service modules for advanced control")
    print(f"   • Factory pattern provides the best of both worlds")
    print(f"   • All services share the same configuration")


if __name__ == "__main__":
    main()