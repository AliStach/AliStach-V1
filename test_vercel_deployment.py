"""Test Vercel deployment."""

import requests
import json

BASE_URL = "https://alistach.vercel.app"

print("="*80)
print("TESTING VERCEL DEPLOYMENT")
print("="*80)

# Test health
print("\n1. Testing /health endpoint...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=30)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ SUCCESS")
        print(f"   Service info: {data.get('data', {}).get('service_info', {})}")
    else:
        print(f"   ✗ FAILED")
        print(f"   Error: {r.json().get('error', 'Unknown')}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

# Test categories
print("\n2. Testing /api/categories endpoint...")
try:
    r = requests.get(f"{BASE_URL}/api/categories", headers={"x-internal-key": "ALIINSIDER-2025"}, timeout=30)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        categories = data.get('data', [])
        print(f"   ✓ SUCCESS - Got {len(categories)} categories")
        if categories:
            print(f"   First category: {categories[0]}")
    else:
        print(f"   ✗ FAILED")
        error_data = r.json()
        print(f"   Error: {error_data.get('error', 'Unknown')}")
except Exception as e:
    print(f"   ✗ ERROR: {e}")

print("\n" + "="*80)
