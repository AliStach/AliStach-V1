#!/usr/bin/env python3
"""
Test script for validating AliExpress API endpoints.
This script tests all the main API endpoints to ensure they're working correctly.
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


def test_endpoint(client, method, url, data=None, expected_status=200):
    """Test a single endpoint."""
    try:
        print(f"🔍 Testing {method} {url}")
        
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
            print(f"   Response: {response.text[:200]}...")
            return False
        
        try:
            json_response = response.json()
            print(f"   Success: {json_response.get('success', 'N/A')}")
            
            if 'data' in json_response:
                data = json_response['data']
                if isinstance(data, list):
                    print(f"   Data count: {len(data)}")
                elif isinstance(data, dict):
                    if 'products' in data:
                        print(f"   Products: {len(data['products'])}")
                    elif 'status' in data:
                        print(f"   Status: {data['status']}")
            
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
    print("🧪 AliExpress API Endpoint Testing")
    print("=" * 50)
    
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
    
    # Test cases
    test_cases = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "Get Categories",
            "method": "GET", 
            "url": f"{base_url}/api/categories",
            "expected_status": 200
        },
        {
            "name": "Get Child Categories",
            "method": "GET",
            "url": f"{base_url}/api/categories/3/children",
            "expected_status": 200
        },
        {
            "name": "Search Products (POST)",
            "method": "POST",
            "url": f"{base_url}/api/products/search",
            "data": {
                "keywords": "wireless headphones",
                "page_size": 5
            },
            "expected_status": 200
        },
        {
            "name": "Search Products (GET)",
            "method": "GET",
            "url": f"{base_url}/api/products/search?keywords=phone&page_size=3",
            "expected_status": 200
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    with httpx.Client(timeout=30.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}/{total}: {test_case['name']}")
            
            success = test_endpoint(
                client=client,
                method=test_case['method'],
                url=test_case['url'],
                data=test_case.get('data'),
                expected_status=test_case['expected_status']
            )
            
            if success:
                passed += 1
            
            print()
            
            # Small delay between tests
            time.sleep(1)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        return True
    else:
        print(f"❌ {total - passed} tests failed. Please check the server logs.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)