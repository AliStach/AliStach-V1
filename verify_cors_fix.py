"""Verify CORS/origin validation fix for Vercel deployment."""

import requests
import sys

BASE_URL = "https://aliexpress-api-proxy.vercel.app"

def test_origin(origin, should_pass=True):
    """Test an origin and verify it's allowed or blocked as expected."""
    # Use root endpoint instead of /health (health bypasses security checks)
    url = f"{BASE_URL}/"
    headers = {}
    
    if origin:
        headers["Origin"] = origin
    
    test_name = f"Origin: {origin or 'None (direct access)'}"
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Expected: {'✅ ALLOWED' if should_pass else '❌ BLOCKED'}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        # Check if blocked
        is_blocked = response.status_code == 403
        
        if is_blocked:
            try:
                data = response.json()
                error = data.get('error', 'Unknown error')
                print(f"Error: {error}")
            except:
                print(f"Response: {response.text[:200]}")
        else:
            try:
                data = response.json()
                print(f"Response: {data}")
            except:
                print(f"Response (text): {response.text[:200]}")
        
        # Verify expectation
        if should_pass and not is_blocked:
            print("✅ PASS: Origin allowed as expected")
            return True
        elif not should_pass and is_blocked:
            print("✅ PASS: Origin blocked as expected")
            return True
        elif should_pass and is_blocked:
            print("❌ FAIL: Origin should be allowed but was blocked")
            return False
        else:
            print("❌ FAIL: Origin should be blocked but was allowed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all CORS validation tests."""
    print("=" * 60)
    print("CORS/Origin Validation Fix Verification")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    
    tests = [
        # Should be allowed
        (None, True, "Direct access (no origin header)"),
        ("https://aliexpress-api-proxy.vercel.app", True, "Same origin (Vercel domain)"),
        ("https://chat.openai.com", True, "OpenAI Chat"),
        ("https://chatgpt.com", True, "ChatGPT"),
        ("http://localhost:3000", True, "Localhost development"),
        
        # Should be blocked
        ("https://evil-domain.com", False, "Unauthorized domain"),
        ("https://random-site.com", False, "Random unauthorized site"),
    ]
    
    results = []
    for origin, should_pass, description in tests:
        print(f"\n\n{'#'*60}")
        print(f"Test: {description}")
        print(f"{'#'*60}")
        result = test_origin(origin, should_pass)
        results.append((description, result))
    
    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for description, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {description}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! CORS fix is working correctly.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
