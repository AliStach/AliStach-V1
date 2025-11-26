"""Verify AliExpress API credentials directly."""

import os
import sys

# Set credentials
os.environ['ALIEXPRESS_APP_KEY'] = '520934'
os.environ['ALIEXPRESS_APP_SECRET'] = 'inC2NFrIr1SvtTGlUWxyQec6EvHyjIno'
os.environ['ALIEXPRESS_TRACKING_ID'] = 'gpt_chat'

from src.utils.config import Config
from aliexpress_api import AliexpressApi, models

print("="*80)
print("ALIEXPRESS API CREDENTIALS VERIFICATION")
print("="*80)

# Load config
config = Config.from_env()
print(f"\n✓ Configuration loaded:")
print(f"  APP_KEY: {config.app_key}")
print(f"  APP_SECRET: {config.app_secret[:10]}...{config.app_secret[-10:]}")
print(f"  TRACKING_ID: {config.tracking_id}")
print(f"  LANGUAGE: {config.language}")
print(f"  CURRENCY: {config.currency}")

# Try to initialize SDK directly
print(f"\n📡 Testing direct SDK initialization...")
try:
    api = AliexpressApi(
        key=config.app_key,
        secret=config.app_secret,
        language=getattr(models.Language, config.language),
        currency=getattr(models.Currency, config.currency),
        tracking_id=config.tracking_id
    )
    print("✓ SDK initialized successfully")
    
    # Try a simple API call
    print(f"\n🔍 Testing API call: get_parent_categories()...")
    try:
        categories = api.get_parent_categories()
        if categories:
            print(f"✓ SUCCESS! Got {len(categories)} categories")
            print(f"\nFirst 3 categories:")
            for i, cat in enumerate(categories[:3], 1):
                print(f"  {i}. {cat.category_name} (ID: {cat.category_id})")
        else:
            print("⚠ API returned empty result")
    except Exception as e:
        print(f"✗ API call failed: {e}")
        print(f"\nError type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        
        # Check if it's a signature error
        if "signature" in str(e).lower():
            print("\n❌ SIGNATURE ERROR DETECTED")
            print("This usually means:")
            print("  1. APP_KEY or APP_SECRET is incorrect")
            print("  2. Credentials have expired or been revoked")
            print("  3. API access has been restricted")
            print("\n⚠ Please verify your credentials at:")
            print("   https://open.aliexpress.com/")
        
except Exception as e:
    print(f"✗ SDK initialization failed: {e}")

print("\n" + "="*80)
