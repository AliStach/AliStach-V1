"""
Test the deployed Vercel API to see if it's using real or mock data.
"""

import requests
import json

BASE_URL = "https://aliexpress-api-proxy.vercel.app"
INTERNAL_KEY = "ALIINSIDER-2025"

def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def test_endpoint(endpoint, method="GET", data=None):
    """Test an endpoint and display results."""
    url = BASE_URL + endpoint
    headers = {"x-internal-key": INTERNAL_KEY}
    
    print(f"Testing: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ SUCCESS - Response received:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
            return True, data
        else:
            print(f"\n✗ FAILED - Status {response.status_code}")
            print(response.text[:500])
            return False, None
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False, None

def main():
    print_section("DEPLOYED API TEST - Vercel Production")
    
    print("Testing deployed API at:", BASE_URL)
    print("Using internal key:", INTERNAL_KEY)
    
    results = {}
    
    # Test 1: Categories
    print_section("TEST 1: Categories")
    success, data = test_endpoint("/api/categories")
    results["categories"] = success
    
    # Test 2: Child Categories
    print_section("TEST 2: Child Categories (parent_id=3)")
    success, data = test_endpoint("/api/categories/3/children")
    results["child_categories"] = success
    
    # Test 3: Product Search
    print_section("TEST 3: Product Search (keywords=phone)")
    success, data = test_endpoint("/api/products/search?keywords=phone&page_size=3")
    results["product_search"] = success
    
    # Extract product ID if available
    product_id = None
    if success and data and "data" in data and len(data["data"]) > 0:
        product_id = data["data"][0].get("product_id")
    
    # Test 4: Product Details
    print_section("TEST 4: Product Details")
    if product_id:
        success, data = test_endpoint(
            "/api/products/details",
            method="POST",
            data={"product_ids": [product_id]}
        )
        results["product_details"] = success
    else:
        print("⚠ SKIPPED: No product ID available")
        results["product_details"] = False
    
    # Test 5: Affiliate Links
    print_section("TEST 5: Affiliate Links")
    test_url = "https://www.aliexpress.com/item/1005004567890123.html"
    success, data = test_endpoint(
        "/api/affiliate/links",
        method="POST",
        data={"urls": [test_url]}
    )
    results["affiliate_links"] = success
    
    # Test 6: Health Check
    print_section("TEST 6: Health Check")
    success, data = test_endpoint("/health")
    results["health"] = success
    
    if success and data:
        print("\n📊 Service Info:")
        if "data" in data and "service_info" in data["data"]:
            service_info = data["data"]["service_info"]
            print(f"  Service: {service_info.get('service', 'unknown')}")
            print(f"  Status: {service_info.get('status', 'unknown')}")
    
    # Summary
    print_section("SUMMARY")
    print("Endpoint Test Results:")
    for endpoint, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {endpoint}")
    
    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
