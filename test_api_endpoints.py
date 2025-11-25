"""
Test API endpoints directly without starting a server.
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

import json
from fastapi.testclient import TestClient

# Now import the app
from src.api.main import app

print("=" * 80)
print("TESTING API ENDPOINTS WITH REAL ALIEXPRESS DATA")
print("=" * 80)

client = TestClient(app, base_url="http://localhost:8000")
headers = {
    "x-internal-key": "ALIINSIDER-2025",
    "host": "localhost"
}

def test_endpoint(name, method, url, **kwargs):
    """Test an endpoint and display results."""
    print(f"\n{'=' * 80}")
    print(f"TEST: {name}")
    print(f"{'=' * 80}")
    print(f"Request: {method} {url}")
    
    try:
        if method == "GET":
            response = client.get(url, headers=headers, **kwargs)
        elif method == "POST":
            response = client.post(url, headers=headers, **kwargs)
        else:
            print(f"✗ Unsupported method: {method}")
            return False, None
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS - Response from REAL ALIEXPRESS API")
            
            # Display sample data
            if "data" in data:
                if isinstance(data["data"], list) and len(data["data"]) > 0:
                    print(f"Sample data (first item):")
                    print(json.dumps(data["data"][0], indent=2)[:500] + "...")
                elif isinstance(data["data"], dict):
                    print(f"Response data:")
                    print(json.dumps(data["data"], indent=2)[:500] + "...")
            
            return True, data
        else:
            print(f"✗ FAILED")
            print(f"Response: {response.text[:500]}")
            return False, None
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None

# Test 1: Health Check
success, data = test_endpoint(
    "Health Check",
    "GET",
    "/health"
)

# Test 2: Categories
success, data = test_endpoint(
    "Get Categories",
    "GET",
    "/api/categories"
)

if success and data and "data" in data and len(data["data"]) > 0:
    parent_id = data["data"][0]["category_id"]
    
    # Test 3: Child Categories
    success, data = test_endpoint(
        f"Get Child Categories (parent_id={parent_id})",
        "GET",
        f"/api/categories/{parent_id}/children"
    )

# Test 4: Product Search
success, data = test_endpoint(
    "Search Products",
    "GET",
    "/api/products/search?keywords=phone&page_size=3"
)

product_ids = []
if success and data and "data" in data and len(data["data"]) > 0:
    product_ids = [p["product_id"] for p in data["data"][:2]]

# Test 5: Product Details
if product_ids:
    success, data = test_endpoint(
        "Get Product Details",
        "POST",
        "/api/products/details",
        json={"product_ids": product_ids}
    )

# Test 6: Affiliate Links
success, data = test_endpoint(
    "Generate Affiliate Links",
    "POST",
    "/api/affiliate/links",
    json={"urls": ["https://www.aliexpress.com/item/1005004567890123.html"]}
)

print(f"\n{'=' * 80}")
print("TESTING COMPLETE")
print(f"{'=' * 80}")
