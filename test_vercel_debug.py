"""Test Vercel debug endpoint to diagnose initialization."""

import requests
import json
import time

BASE_URL = "https://alistach.vercel.app"

print("="*80)
print("VERCEL DEBUG DIAGNOSTICS")
print("="*80)

# Test 1: Check version
print("\n1. Checking deployment version...")
try:
    r = requests.get(f"{BASE_URL}/", timeout=10)
    data = r.json()
    version = data.get('version', 'unknown')
    deployment_id = data.get('deployment_id', 'unknown')
    print(f"   Version: {version}")
    print(f"   Deployment ID: {deployment_id}")
    
    if version == "2.2.0-lazy-init":
        print(f"   ✓ New deployment is live!")
    else:
        print(f"   ⚠ Old deployment still active (expected: 2.2.0-lazy-init)")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 2: Check debug endpoint
print("\n2. Checking debug endpoint...")
try:
    r = requests.get(f"{BASE_URL}/debug/env", timeout=10)
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Debug endpoint accessible")
        print(f"\n   Environment Status:")
        print(f"   - Initialization: {data.get('initialization_status', 'unknown')}")
        print(f"   - Init Error: {data.get('initialization_error', 'none')}")
        print(f"   - VERCEL: {data.get('vercel', 'not_set')}")
        print(f"   - VERCEL_ENV: {data.get('vercel_env', 'not_set')}")
        print(f"   - APP_KEY present: {data.get('aliexpress_app_key_present', False)}")
        print(f"   - APP_KEY value: {data.get('aliexpress_app_key_value', 'NOT_SET')}")
        print(f"   - APP_SECRET present: {data.get('aliexpress_app_secret_present', False)}")
        print(f"   - APP_SECRET first10: {data.get('aliexpress_app_secret_first10', 'NOT_SET')}")
        print(f"   - TRACKING_ID: {data.get('aliexpress_tracking_id', 'not_set')}")
        print(f"   - All ALIEXPRESS keys: {data.get('all_aliexpress_keys', [])}")
    else:
        print(f"   ✗ Debug endpoint returned {r.status_code}")
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 3: Check health
print("\n3. Checking health endpoint...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✓ Health check passed!")
        data = r.json()
        if 'data' in data and 'service_info' in data['data']:
            print(f"   Service info: {data['data']['service_info'].get('service', 'unknown')}")
    else:
        print(f"   ✗ Health check failed")
        print(f"   Error: {r.json().get('error', 'unknown')}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test 4: Check categories
print("\n4. Checking categories endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/categories", 
                     headers={"x-internal-key": "ALIINSIDER-2025"}, 
                     timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        categories = data.get('data', [])
        print(f"   ✓ SUCCESS - Got {len(categories)} categories")
    else:
        print(f"   ✗ FAILED")
        print(f"   Error: {r.json().get('error', 'unknown')[:100]}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "="*80)
