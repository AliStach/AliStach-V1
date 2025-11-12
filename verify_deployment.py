"""Verify Vercel deployment is working correctly."""

import requests
import sys

BASE_URL = "https://aliexpress-api-proxy.vercel.app"

def test_endpoint(path, expected_status=None):
    """Test an endpoint and return results."""
    url = f"{BASE_URL}{path}"
    print(f"\nTesting: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Check if it's trying to download a file
        content_disposition = response.headers.get('content-disposition', '')
        if 'attachment' in content_disposition.lower():
            print("  ❌ ERROR: Response is trying to download a file!")
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type or 'text/html' in content_type:
            print("  ✅ Correct content type (not a file download)")
        else:
            print(f"  ⚠️  Unexpected content type: {content_type}")
        
        # Try to parse JSON
        try:
            data = response.json()
            print(f"  Response: {data}")
            return True
        except:
            print(f"  Response (text): {response.text[:200]}")
            return 'text/html' in content_type  # HTML is OK (docs page)
            
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Vercel Deployment Verification")
    print("=" * 60)
    
    tests = [
        ("/", None),
        ("/health", None),
        ("/docs", None),
    ]
    
    results = []
    for path, expected in tests:
        results.append(test_endpoint(path, expected))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! Deployment is working correctly.")
        print("   The app is serving HTTP responses, not downloading files.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
