#!/usr/bin/env python3
"""
Verification script for Vercel deployment.
Tests core endpoints to ensure the boot failure is fixed.
"""

import requests
import json
import sys
from typing import Dict, Any

# Update this with your Vercel deployment URL
VERCEL_URL = "https://alistach.vercel.app"
INTERNAL_API_KEY = "ALIINSIDER-2025"

def test_endpoint(name: str, method: str, path: str, headers: Dict[str, str] = None, 
                 data: Dict[str, Any] = None, expected_status: int = 200) -> bool:
    """Test a single endpoint."""
    url = f"{VERCEL_URL}{path}"
    headers = headers or {}
    
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Method: {method} {path}")
    print(f"Expected: {expected_status}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print(f"✅ PASS - Status code matches")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                print(f"Response preview: {json.dumps(response_data, indent=2)[:200]}...")
            except:
                print(f"Response (non-JSON): {response.text[:200]}...")
            
            return True
        else:
            print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ FAIL - Request timeout (>30s)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL - Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL - Unexpected error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("="*60)
    print("VERCEL DEPLOYMENT VERIFICATION")
    print(f"URL: {VERCEL_URL}")
    print("="*60)
    
    results = []
    
    # Test 1: Health check (no auth required)
    results.append(test_endpoint(
        name="Health Check",
        method="GET",
        path="/health",
        expected_status=200
    ))
    
    # Test 2: OpenAPI schema (no auth required)
    results.append(test_endpoint(
        name="OpenAPI GPT Schema",
        method="GET",
        path="/openapi-gpt.json",
        expected_status=200
    ))
    
    # Test 3: Categories (requires auth)
    results.append(test_endpoint(
        name="Get Categories",
        method="GET",
        path="/api/categories",
        headers={"x-internal-key": INTERNAL_API_KEY},
        expected_status=200
    ))
    
    # Test 4: Smart Search (requires auth)
    results.append(test_endpoint(
        name="Smart Product Search",
        method="POST",
        path="/api/products/smart-search",
        headers={
            "x-internal-key": INTERNAL_API_KEY,
            "Content-Type": "application/json"
        },
        data={
            "keywords": "laptop",
            "page_size": 5
        },
        expected_status=200
    ))
    
    # Test 5: Image Search (should return 503 - disabled)
    results.append(test_endpoint(
        name="Image Search (Disabled)",
        method="POST",
        path="/api/products/image-search",
        headers={
            "x-internal-key": INTERNAL_API_KEY,
            "Content-Type": "application/json"
        },
        data={
            "image_url": "https://example.com/test.jpg"
        },
        expected_status=503
    ))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Deployment is healthy!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - Check logs above")
        sys.exit(1)

if __name__ == "__main__":
    main()
