"""Test smart search API endpoint with real data."""

import requests
import os
import subprocess
import time
import sys

API_BASE_URL = "http://localhost:8000"
INTERNAL_KEY = os.getenv("INTERNAL_API_KEY", "ALIINSIDER-2025")


def start_server():
    """Start the API server in the background."""
    print("Starting API server...")
    try:
        # Start server in background
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=1)
                if response.status_code in [200, 503]:  # 503 is ok during startup
                    print("✓ Server started successfully")
                    return process
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            print(f"  Waiting for server... ({i+1}/{max_retries})")
        
        print("✗ Server failed to start")
        process.kill()
        return None
        
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return None


def test_smart_search_endpoint():
    """Test the smart search endpoint."""
    print("\n" + "=" * 80)
    print("  TESTING SMART SEARCH API ENDPOINT")
    print("=" * 80 + "\n")
    
    headers = {
        "Content-Type": "application/json",
        "x-internal-key": INTERNAL_KEY
    }
    
    # Test 1: Basic smart search
    print("TEST 1: POST /api/products/smart-search (basic)")
    print("-" * 80)
    
    payload = {
        "keywords": "phone",
        "page_no": 1,
        "page_size": 5,
        "generate_affiliate_links": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/products/smart-search",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                result = data.get("data", {})
                products = result.get("products", [])
                metrics = data.get("metadata", {}).get("search_optimization", {})
                
                print(f"✓ SUCCESS")
                print(f"  - Products returned: {len(products)}")
                print(f"  - Total available: {result.get('total_record_count', 0)}")
                print(f"  - Cache hit: {metrics.get('cache_hit', False)}")
                print(f"  - Affiliate links cached: {metrics.get('affiliate_links_cached', 0)}")
                print(f"  - Affiliate links generated: {metrics.get('affiliate_links_generated', 0)}")
                print(f"  - API calls saved: {metrics.get('api_calls_saved', 0)}")
                print(f"  - Response time: {metrics.get('response_time_ms', 0):.2f}ms")
                
                if products:
                    product = products[0]
                    print(f"\n  Sample product:")
                    print(f"    - ID: {product.get('product_id')}")
                    print(f"    - Title: {product.get('product_title', '')[:60]}...")
                    print(f"    - Price: {product.get('price')} {product.get('currency')}")
                    print(f"    - Has affiliate URL: {bool(product.get('affiliate_url'))}")
                    print(f"    - Affiliate status: {product.get('affiliate_status')}")
            else:
                print(f"✗ FAILED: {data.get('error')}")
                return False
        else:
            print(f"✗ FAILED: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n")
    
    # Test 2: Smart search with filters
    print("TEST 2: POST /api/products/smart-search (with filters)")
    print("-" * 80)
    
    payload = {
        "keywords": "headphones",
        "min_sale_price": 10.0,
        "max_sale_price": 50.0,
        "page_no": 1,
        "page_size": 3,
        "generate_affiliate_links": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/products/smart-search",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("data", {})
                products = result.get("products", [])
                print(f"✓ SUCCESS")
                print(f"  - Products returned: {len(products)}")
                print(f"  - Total available: {result.get('total_record_count', 0)}")
            else:
                print(f"✗ FAILED: {data.get('error')}")
                return False
        else:
            print(f"✗ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    print("\n")
    
    # Test 3: Force refresh
    print("TEST 3: POST /api/products/smart-search (force refresh)")
    print("-" * 80)
    
    payload = {
        "keywords": "phone",
        "page_no": 1,
        "page_size": 3,
        "force_refresh": True,
        "generate_affiliate_links": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/products/smart-search",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("data", {})
                metrics = data.get("metadata", {}).get("search_optimization", {})
                print(f"✓ SUCCESS")
                print(f"  - Products returned: {len(result.get('products', []))}")
                print(f"  - Cache hit: {metrics.get('cache_hit', False)} (should be False)")
            else:
                print(f"✗ FAILED: {data.get('error')}")
                return False
        else:
            print(f"✗ FAILED: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("  ALL ENDPOINT TESTS PASSED!")
    print("=" * 80 + "\n")
    
    return True


if __name__ == "__main__":
    # Check if server is already running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        print("✓ Server is already running")
        server_process = None
    except:
        server_process = start_server()
        if not server_process:
            print("Failed to start server")
            exit(1)
    
    try:
        success = test_smart_search_endpoint()
        exit(0 if success else 1)
    finally:
        if server_process:
            print("\nStopping server...")
            server_process.kill()
            server_process.wait()
