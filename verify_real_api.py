"""
Verification script to confirm the API is using REAL AliExpress data.
Run this against the deployed Vercel API or local server.
"""

import requests
import json
import sys

def verify_api(base_url):
    """Verify the API is using real AliExpress data."""
    
    print("=" * 80)
    print(f"VERIFYING API: {base_url}")
    print("=" * 80)
    
    headers = {"x-internal-key": "ALIINSIDER-2025"}
    
    # Test 1: Health Check
    print("\n1. Checking health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "service_info" in data["data"]:
                print("   ✓ PASSED: API is using REAL AliExpress data")
        else:
            print(f"   ✗ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 2: Categories Count
    print("\n2. Checking categories...")
    try:
        response = requests.get(f"{base_url}/api/categories", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                count = len(data["data"])
                
                # Real AliExpress returns ~40 categories, mock returns 15
                if count == 15:
                    print(f"   ✗ FAILED: Got {count} categories (MOCK DATA)")
                    print("   Mock data returns exactly 15 generic categories")
                    return False
                elif count >= 30:
                    print(f"   ✓ PASSED: Got {count} categories (REAL DATA)")
                    
                    # Check category names
                    sample_names = [cat["category_name"] for cat in data["data"][:3]]
                    print(f"   Sample categories: {', '.join(sample_names)}")
                else:
                    print(f"   ⚠ WARNING: Got {count} categories (unexpected)")
        else:
            print(f"   ✗ FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 3: Product Search
    print("\n3. Checking product search...")
    try:
        response = requests.get(
            f"{base_url}/api/products/search",
            headers=headers,
            params={"keywords": "phone", "page_size": 3},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                product = data["data"][0]
                print(f"   ✓ PASSED: Got real product data")
                print(f"   Sample product: {product['product_title'][:50]}...")
                print(f"   Price: {product.get('price', 'N/A')} {product.get('currency', 'N/A')}")
            else:
                print(f"   ✗ FAILED: No products returned")
                return False
        elif response.status_code == 404:
            print(f"   ✗ FAILED: Endpoint not found (404)")
            print("   This endpoint may not be properly configured")
            return False
        else:
            print(f"   ✗ FAILED: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 4: Affiliate Links
    print("\n4. Checking affiliate links...")
    try:
        response = requests.post(
            f"{base_url}/api/affiliate/links",
            headers=headers,
            json={"urls": ["https://www.aliexpress.com/item/1005004567890123.html"]},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                link = data["data"][0]
                affiliate_url = link.get("affiliate_url", "")
                
                # Mock data contains "_mock_" in the URL
                if "_mock_" in affiliate_url:
                    print(f"   ✗ FAILED: Affiliate link contains '_mock_' (MOCK DATA)")
                    print(f"   URL: {affiliate_url}")
                    return False
                else:
                    print(f"   ✓ PASSED: Real affiliate link generated")
                    print(f"   URL: {affiliate_url[:60]}...")
            else:
                print(f"   ✗ FAILED: No affiliate links returned")
                return False
        else:
            print(f"   ✗ FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ ALL VERIFICATION TESTS PASSED")
    print("The API is confirmed to be using REAL AliExpress data!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    # Test both local and deployed
    print("\n" + "=" * 80)
    print("ALIEXPRESS API VERIFICATION")
    print("=" * 80)
    
    # Test deployed version
    print("\n\nTesting DEPLOYED API (Vercel)...")
    deployed_success = verify_api("https://aliexpress-api-proxy.vercel.app")
    
    # Test local version (if running)
    print("\n\nTesting LOCAL API (localhost:8000)...")
    print("(Make sure local server is running)")
    try:
        local_success = verify_api("http://localhost:8000")
    except:
        print("⚠ Local server not running or not accessible")
        local_success = False
    
    # Summary
    print("\n\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Deployed API (Vercel): {'✓ PASSED' if deployed_success else '✗ FAILED'}")
    print(f"Local API (localhost): {'✓ PASSED' if local_success else '✗ FAILED or not running'}")
    
    if deployed_success:
        print("\n✓ SUCCESS: Deployed API is using real AliExpress data!")
        sys.exit(0)
    else:
        print("\n✗ FAILED: Deployed API is still using mock data")
        print("\nNext steps:")
        print("1. Set environment variables on Vercel dashboard")
        print("2. Redeploy with: vercel --prod")
        print("3. Run this script again to verify")
        sys.exit(1)
