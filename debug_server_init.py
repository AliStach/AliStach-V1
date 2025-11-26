"""Debug script to see exactly what the server is using."""

import os
import sys

# Set environment variables explicitly
os.environ['ALIEXPRESS_APP_KEY'] = '520934'
os.environ['ALIEXPRESS_APP_SECRET'] = 'inC2NFrIr1SvtTGlUWxyQec6EvHyjIno'
os.environ['ALIEXPRESS_TRACKING_ID'] = 'gpt_chat'
os.environ['ALIEXPRESS_LANGUAGE'] = 'EN'
os.environ['ALIEXPRESS_CURRENCY'] = 'USD'

from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService
from aliexpress_api import models

print("="*80)
print("DEBUG: Server Initialization")
print("="*80)

# Load config exactly as the server does
config = Config.from_env()

print("\n1. Config values:")
print(f"   app_key: {config.app_key}")
print(f"   app_secret: {config.app_secret}")
print(f"   tracking_id: {config.tracking_id}")
print(f"   language: {config.language}")
print(f"   currency: {config.currency}")

print("\n2. Models enum values:")
print(f"   Language.{config.language}: {getattr(models.Language, config.language)}")
print(f"   Currency.{config.currency}: {getattr(models.Currency, config.currency)}")

# Initialize service exactly as the server does
print("\n3. Initializing AliExpressService...")
service = AliExpressService(config)

print(f"   ✓ Service initialized")
print(f"   API object: {service.api}")
print(f"   API key: {service.api._key if hasattr(service.api, '_key') else 'N/A'}")
print(f"   API secret: {service.api._secret[:10] if hasattr(service.api, '_secret') else 'N/A'}...")

# Try an API call
print("\n4. Testing API call...")
try:
    categories = service.get_parent_categories()
    print(f"   ✓ SUCCESS! Got {len(categories)} categories")
    for i, cat in enumerate(categories[:3], 1):
        print(f"     {i}. {cat.category_name} (ID: {cat.category_id})")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
