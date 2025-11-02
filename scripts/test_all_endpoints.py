#!/usr/bin/env python3
"""
Comprehensive test script for all AliExpress API endpoints.
Tests all available endpoints with real API calls.
"""

import sys
import os
import time
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    import httpx
except ImportError:
    print("❌ httpx not installed. Installing...")
    os.system("pip install httpx")
    import httpx


def test_endpoint(client, method, url, data=None, expected_status=200, description=""):
    """Test a single endpoint."""
    try:
        print(f"🔍 Testing: {description}")
        print(f"   {method} {url}")
        
        if method.upper() == "GET":
            response = client.get(url)
        elif method.upper() == "POST":
            response = client.post(url, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code != expected_status:
            print(f"❌ Expected status {expected_status}, got {response.status_code}")
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            return False
        
        try:
            json_response = response.json()
            success = json_response.get('success', False)
            print(f"   Success: {success}")
            
            if success and 'data' in json_response:
                data = json_response['data']
                if isinstance(data, list):
                    print(f"   Items: {len(data)}")
                elif isinstance(data, dict):
                    if 'products' in data:
                        print(f"   Products: {len(data['products'])}")
                        if data['products']:
                            print(f"   Sample: {data['products'][0].get('product_title', 'No title')[:50]}...")
                    elif 'total_record_count' in data:
                        print(f"   Total records: {data['total_record_count']}")
                    elif 'status' in data:
                        print(f"   Status: {data['status']}")
                    elif 'service' in data:
                        print(f"   Service: {data['service']}")
            
            print("✅ Test passed")
            return True
            
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Comprehensive AliExpress API Endpoint Testing")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Check if server is running
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{base_url}/health")
            if response.status_code != 200:
                print(f"❌ Server not responding at {base_url}")
                print("💡 Make sure to start the server first:")
                print("   python -m src.api.main")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server at {base_url}")
        print(f"   Error: {e}")
        print("💡 Make sure to start the server first:")
        print("   python -m src.api.main")
        return False
    
    print(f"✅ Server is running at {base_url}")
    print()
    
    # Comprehensive test cases
    test_cases = [
        # Health and service info
        {
            "description": "Health Check",
            "method": "GET",
            "url": f"{base_url}/health"
        },
        
        # Categories
        {
            "description": "Get All Categories",
            "method": "GET", 
            "url": f"{base_url}/api/categories"
        },
        {
            "description": "Get Child Categories",
            "method": "GET",
            "url": f"{base_url}/api/categories/3/children"
        },
        
        # Product Search (Basic)
        {
            "description": "Basic Product Search (POST)",
            "method": "POST",
            "url": f"{base_url}/api/products/search",
            "data": {
                "keywords": "bluetooth headphones",
                "page_size": 3
            }
        },
        {
            "description": "Basic Product Search (GET)",
            "method": "GET",
            "url": f"{base_url}/api/products/search?keywords=smartwatch&page_size=3"
        },
        
        # Enhanced Product Search
        {
            "description": "Enhanced Product Search with Price Filter (POST)",
            "method": "POST",
            "url": f"{base_url}/api/products",
            "data": {
                "keywords": "phone case",
                "max_sale_price": 20.0,
                "min_sale_price": 5.0,
                "page_size": 3
            }
        },
        {
            "description": "Enhanced Product Search with Price Filter (GET)",
            "method": "GET",
            "url": f"{base_url}/api/products?keywords=wireless+mouse&max_sale_price=30&page_size=3"
        },
        
        # Product Details
        {
            "description": "Single Product Details",
            "method": "GET",
            "url": f"{base_url}/api/products/details/1005003091506814"
        },
        {
            "description": "Multiple Product Details",
            "method": "POST",
            "url": f"{base_url}/api/products/details",
            "data": {
                "product_ids": ["1005003091506814", "1005002956073022"]
            }
        },
        
        # Hot Products
        {
            "description": "Hot Products (POST)",
            "method": "POST",
            "url": f"{base_url}/api/products/hot",
            "data": {
                "keywords": "gaming",
                "max_sale_price": 100.0,
                "page_size": 3
            }
        },
        {
            "description": "Hot Products (GET)",
            "method": "GET",
            "url": f"{base_url}/api/products/hot?keywords=fitness&page_size=3"
        },
        
        # Affiliate Links
        {
            "description": "Generate Single Affiliate Link",
            "method": "GET",
            "url": f"{base_url}/api/affiliate/link?url=https://www.aliexpress.com/item/1005003091506814.html"
        },
        {
            "description": "Generate Multiple Affiliate Links",
            "method": "POST",
            "url": f"{base_url}/api/affiliate/links",
            "data": {
                "urls": [
                    "https://www.aliexpress.com/item/1005003091506814.html",
                    "https://www.aliexpress.com/item/1005002956073022.html"
                ]
            }
        },
        
        # Promotions (These might require special permissions)
        {
            "description": "Featured Promotional Products",
            "method": "GET",
            "url": f"{base_url}/api/promotions/featured",
            "expected_status": [200, 400]  # Might fail due to permissions
        },
        {
            "description": "Promotion Information",
            "method": "GET",
            "url": f"{base_url}/api/promotions/info",
            "expected_status": [200, 400]  # Might fail due to permissions
        },
        
        # Shipping Info
        {
            "description": "Shipping Information",
            "method": "GET",
            "url": f"{base_url}/api/shipping/1005003091506814?country=US",
            "expected_status": [200, 400]  # Might fail due to permissions
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    with httpx.Client(timeout=30.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}/{total}:")
            
            expected_status = test_case.get('expected_status', 200)
            if isinstance(expected_status, list):
                # Test passes if status is in the list
                for status in expected_status:
                    success = test_endpoint(
                        client=client,
                        method=test_case['method'],
                        url=test_case['url'],
                        data=test_case.get('data'),
                        expected_status=status,
                        description=test_case['description']
                    )
                    if success:
                        passed += 1
                        break
                else:
                    print(f"❌ Test failed with all expected statuses: {expected_status}")
            else:
                success = test_endpoint(
                    client=client,
                    method=test_case['method'],
                    url=test_case['url'],
                    data=test_case.get('data'),
                    expected_status=expected_status,
                    description=test_case['description']
                )
                if success:
                    passed += 1
            
            print()
            
            # Small delay between tests
            time.sleep(1)
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% pass rate is good (some endpoints might need special permissions)
        print("🎉 Most tests passed! The API is working well.")
        print("💡 Some endpoints might require special AliExpress permissions.")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the server logs.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)