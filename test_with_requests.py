"""
Test the API by making actual HTTP requests to localhost.
Run this after starting the server with: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
HEADERS = {"x-internal-key": "ALIINSIDER-2025"}

def test_endpoint(name, method, path, **kwargs):
    """Test an endpoint."""
    url = BASE_URL + path
    print(f"\n{'=' * 80}")
    print(f"TEST: {name}")
    print(f"{'=' * 80}")
    print(f"Request: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=10, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, timeout=10, **kwargs)
        else:
            print(f"✗ Unsupported method")
            return False, None
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS")
            
            # Check response data
            if "data" in data:
                if isinstance(data["data"], dict) and "service_info" in data["data"]:
                    print(f"✓ REAL ALIEXPRESS DATA")
                
                # Show sample
                if isinstance(data["data"], list) and len(data["data"]) > 0:
                    print(f"Sample (first item):")
                    print(json.dumps(data["data"][0], indent=2)[:300] + "...")
            
            return True, data
        else:
            print(f"✗ FAILED")
            print(f"Response: {response.text[:500]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"✗ CONNECTION ERROR: Server not running?")
        print(f"   Start server with: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000")
        return False, None
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False, None

print("=" * 80)
print("TESTING LOCAL API SERVER")
print("=" * 80)
print(f"Base URL: {BASE_URL}")
print(f"Make sure server is running!")

# Wait a moment
time.sleep(1)

# Test 1: Health
success, data = test_endpoint("Health Check", "GET", "/health")

# Test 2: Categories
success, data = test_endpoint("Get Categories", "GET", "/api/categories")

if success and data and "data" in data and len(data["data"]) > 0:
    parent_id = data["data"][0]["category_id"]
    
    # Test 3: Child Categories
    test_endpoint(f"Get Child Categories", "GET", f"/api/categories/{parent_id}/children")

# Test 4: Product Search
success, data = test_endpoint("Search Products", "GET", "/api/products/search?keywords=phone&page_size=3")

product_ids = []
if success and data and "data" in data and len(data["data"]) > 0:
    product_ids = [p["product_id"] for p in data["data"][:2]]

# Test 5: Product Details
if product_ids:
    test_endpoint("Get Product Details", "POST", "/api/products/details", json={"product_ids": product_ids})

# Test 6: Affiliate Links
test_endpoint("Generate Affiliate Links", "POST", "/api/affiliate/links", 
              json={"urls": ["https://www.aliexpress.com/item/1005004567890123.html"]})

print(f"\n{'=' * 80}")
print("TESTING COMPLETE")
print(f"{'=' * 80}")
