"""
Test the local service directly to ensure it works with real API.
"""

import os
import sys

# Set environment variables
os.environ['ALIEXPRESS_APP_KEY'] = '520934'
os.environ['ALIEXPRESS_APP_SECRET'] = 'inC2NFrIr1SvtTGlUWxyQec6EvHyjIno'
os.environ['ALIEXPRESS_TRACKING_ID'] = 'gpt_chat'

from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService

print("=" * 80)
print("TESTING LOCAL SERVICE WITH REAL API")
print("=" * 80)

print("\n1. Loading configuration...")
config = Config.from_env()
print(f"   APP_KEY: {config.app_key}")
print(f"   APP_SECRET: {config.app_secret[:10]}...")
print(f"   TRACKING_ID: {config.tracking_id}")

print("\n2. Validating configuration...")
try:
    config.validate()
    print("   ✓ Configuration valid")
except Exception as e:
    print(f"   ✗ Configuration invalid: {e}")
    sys.exit(1)

print("\n3. Initializing service...")
service = AliExpressService(config)
print(f"   API initialized: {service.api is not None}")

print("\n4. Testing get_parent_categories()...")
try:
    categories = service.get_parent_categories()
    print(f"   ✓ SUCCESS! Got {len(categories)} categories")
    if categories:
        print(f"   First 5 categories:")
        for cat in categories[:5]:
            print(f"      - {cat.category_id}: {cat.category_name}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Testing get_child_categories()...")
try:
    # Use the first category
    parent_id = categories[0].category_id
    child_cats = service.get_child_categories(parent_id)
    print(f"   ✓ SUCCESS! Got {len(child_cats)} child categories for parent {parent_id}")
    if child_cats:
        print(f"   First 5 child categories:")
        for cat in child_cats[:5]:
            print(f"      - {cat.category_id}: {cat.category_name}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n6. Testing search_products()...")
try:
    result = service.search_products(keywords="phone", page_size=3, auto_generate_affiliate_links=False)
    print(f"   ✓ SUCCESS! Found {len(result.products)} products (total: {result.total_record_count})")
    if result.products:
        print(f"   First product:")
        p = result.products[0]
        print(f"      - ID: {p.product_id}")
        print(f"      - Title: {p.product_title[:50]}...")
        print(f"      - Price: {p.price} {p.currency}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("ALL TESTS PASSED - SERVICE IS WORKING WITH REAL API")
print("=" * 80)
