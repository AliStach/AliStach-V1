"""Test the live running server with real API calls."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
HEADERS = {
    "x-internal-key": "ALIINSIDER-2025",
    "Content-Type": "application/json"
}

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_endpoint(name, method, url, **kwargs):
    """Test an endpoint and return success status."""
    print(f"\n{'─'*80}")
    print(f"TEST: {name}")
    print(f"{'─'*80}")
    print(f"Request: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS, timeout=30, **kwargs)
        elif method == "POST":
            response = requests.post(url, headers=HEADERS, timeout=30, **kwargs)
        else:
            print(f"✗ Unsupported method: {method}")
            return False
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS - Real AliExpress API Response")
            
            # Show sample data
            if "data" in data:
                if isinstance(data["data"], list) and len(data["data"]) > 0:
                    print(f"\nSample data (first item):")
                    print(json.dumps(data["data"][0], indent=2)[:500])
                elif isinstance(data["data"], dict):
                    print(f"\nResponse data keys: {list(data['data'].keys())}")
            
            return True
        else:
            print(f"✗ FAILED")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print_header("REAL API VERIFICATION - LIVE SERVER")
    print(f"Testing server at: {BASE_URL}")
    print(f"Using real AliExpress credentials")
    
    results = {}
    
    # Test 1: Health Check
    results["health"] = test_endpoint(
        "Health Check",
        "GET",
        f"{BASE_URL}/health"
    )
    
    time.sleep(1)
    
    # Test 2: Get Parent Categories
    results["categories"] = test_endpoint(
        "Get Parent Categories",
        "GET",
        f"{BASE_URL}/api/categories"
    )
    
    time.sleep(2)
    
    # Test 3: Search Products
    results["search"] = test_endpoint(
        "Search Products",
        "GET",
        f"{BASE_URL}/api/products/search?keywords=phone&page_size=3"
    )
    
    time.sleep(2)
    
    # Test 4: Generate Affiliate Links
    results["affiliate"] = test_endpoint(
        "Generate Affiliate Links",
        "POST",
        f"{BASE_URL}/api/affiliate/links",
        json={"urls": ["https://www.aliexpress.com/item/1005001234567890.html"]}
    )
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    for test_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Real API is working correctly!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
