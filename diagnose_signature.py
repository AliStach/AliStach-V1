"""
Diagnose the signature generation issue with AliExpress API.
"""

import os
import sys
import hashlib
import time
from datetime import datetime

# Set credentials
os.environ['ALIEXPRESS_APP_KEY'] = '520934'
os.environ['ALIEXPRESS_APP_SECRET'] = 'inC2NFrIr1SvtTGlUWxyQec6EvHyjIno'
os.environ['ALIEXPRESS_TRACKING_ID'] = 'gpt_chat'

print("=" * 80)
print("ALIEXPRESS API SIGNATURE DIAGNOSTIC")
print("=" * 80)

print("\n1. Checking credentials...")
print(f"   APP_KEY: {os.environ['ALIEXPRESS_APP_KEY']}")
print(f"   APP_SECRET: {os.environ['ALIEXPRESS_APP_SECRET']}")
print(f"   TRACKING_ID: {os.environ['ALIEXPRESS_TRACKING_ID']}")

print("\n2. Importing SDK...")
try:
    from aliexpress_api import AliexpressApi, models
    print("   ✓ SDK imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import SDK: {e}")
    sys.exit(1)

print("\n3. Initializing API client...")
try:
    api = AliexpressApi(
        key=os.environ['ALIEXPRESS_APP_KEY'],
        secret=os.environ['ALIEXPRESS_APP_SECRET'],
        language=models.Language.EN,
        currency=models.Currency.USD,
        tracking_id=os.environ['ALIEXPRESS_TRACKING_ID']
    )
    print("   ✓ API client initialized")
except Exception as e:
    print(f"   ✗ Failed to initialize API: {e}")
    sys.exit(1)

print("\n4. Inspecting SDK internals...")
try:
    # Check if we can access the internal request builder
    print(f"   API Key in client: {api._key}")
    print(f"   API Secret in client: {api._secret[:10]}...")
    
    # Try to access the request building mechanism
    import aliexpress_api.skd.api.rest as rest
    print(f"   REST module: {rest}")
    
except Exception as e:
    print(f"   ⚠ Could not inspect internals: {e}")

print("\n5. Testing a simple API call...")
print("   Calling: get_parent_categories()")

try:
    # Enable debug mode if possible
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    categories = api.get_parent_categories()
    print(f"   ✓ SUCCESS! Got {len(categories)} categories")
    if categories:
        print(f"   First category: {categories[0].category_name}")
    
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    print(f"   Error type: {type(e).__name__}")
    
    # Try to extract more details
    if hasattr(e, '__dict__'):
        print(f"   Error details: {e.__dict__}")
    
    # Check if it's a signature error
    error_str = str(e).lower()
    if 'signature' in error_str:
        print("\n   🔍 SIGNATURE ERROR DETECTED")
        print("   This means the SDK is generating signatures that AliExpress rejects.")
        print("   Possible causes:")
        print("   - Incorrect APP_KEY or APP_SECRET")
        print("   - SDK version incompatibility")
        print("   - AliExpress API changes")
        print("   - Timestamp/timezone issues")

print("\n6. Checking SDK version and source...")
try:
    import aliexpress_api
    print(f"   SDK version: {aliexpress_api.__version__ if hasattr(aliexpress_api, '__version__') else 'unknown'}")
    print(f"   SDK location: {aliexpress_api.__file__}")
    
    # Check if there's a way to see the actual request being made
    import aliexpress_api.skd.api.base as base
    print(f"   Base API module: {base.__file__}")
    
except Exception as e:
    print(f"   ⚠ Could not check SDK details: {e}")

print("\n7. Manual signature test...")
print("   Testing if we can generate a valid signature manually...")

try:
    # AliExpress uses HMAC-MD5 for signatures
    # Format: secret + method_name + params (sorted) + secret
    
    app_key = os.environ['ALIEXPRESS_APP_KEY']
    app_secret = os.environ['ALIEXPRESS_APP_SECRET']
    
    # Example parameters for category API
    timestamp = str(int(time.time() * 1000))
    params = {
        'app_key': app_key,
        'method': 'aliexpress.affiliate.category.get',
        'timestamp': timestamp,
        'format': 'json',
        'v': '2.0',
        'sign_method': 'md5',
    }
    
    # Sort parameters
    sorted_params = sorted(params.items())
    
    # Build signature string
    sign_str = app_secret
    for key, value in sorted_params:
        sign_str += f"{key}{value}"
    sign_str += app_secret
    
    # Generate MD5 signature
    signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    print(f"   Generated signature: {signature}")
    print(f"   Signature string (first 100 chars): {sign_str[:100]}...")
    print(f"   Timestamp: {timestamp}")
    
except Exception as e:
    print(f"   ✗ Failed to generate manual signature: {e}")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
