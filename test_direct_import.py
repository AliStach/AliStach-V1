"""
Test by directly importing and initializing the service.
"""

import os
import sys

# Set environment variables BEFORE any imports
os.environ['ALIEXPRESS_APP_KEY'] = '520934'
os.environ['ALIEXPRESS_APP_SECRET'] = 'inC2NFrIr1SvtTGlUWxyQec6EvHyjIno'
os.environ['ALIEXPRESS_TRACKING_ID'] = 'gpt_chat'
os.environ['INTERNAL_API_KEY'] = 'ALIINSIDER-2025'
os.environ['ALIEXPRESS_LANGUAGE'] = 'EN'
os.environ['ALIEXPRESS_CURRENCY'] = 'USD'

print("Testing direct import and initialization...")

print("\n1. Importing modules...")
try:
    from src.utils.config import Config
    from src.services.aliexpress_service import AliExpressService
    print("   ✓ Modules imported")
except Exception as e:
    print(f"   ✗ Failed to import: {e}")
    sys.exit(1)

print("\n2. Loading config...")
try:
    config = Config.from_env()
    print(f"   ✓ Config loaded")
    print(f"   APP_KEY: {config.app_key}")
    print(f"   APP_SECRET: {config.app_secret[:10]}...")
except Exception as e:
    print(f"   ✗ Failed to load config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Validating config...")
try:
    config.validate()
    print("   ✓ Config valid")
except Exception as e:
    print(f"   ✗ Config invalid: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Initializing service...")
try:
    service = AliExpressService(config)
    print(f"   ✓ Service initialized")
    print(f"   API object: {service.api}")
except Exception as e:
    print(f"   ✗ Failed to initialize service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Testing API call...")
try:
    categories = service.get_parent_categories()
    print(f"   ✓ Got {len(categories)} categories")
except Exception as e:
    print(f"   ✗ API call failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ ALL TESTS PASSED")
