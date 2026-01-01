#!/usr/bin/env python3
"""Test production issues"""

import requests
import json
import time

def test_health_endpoint():
    """Test health endpoint response time"""
    print("🏥 Testing Health Endpoint...")
    
    headers = {
        "x-vercel-protection-bypass": "4uPEirWZEyeECM2l2q5ktThP8W0wcQ73"
    }
    
    start_time = time.time()
    try:
        response = requests.get("https://alistach.vercel.app/health", headers=headers, timeout=15)
        response_time = (time.time() - start_time) * 1000
        
        print(f"Status: {response.status_code}")
        print(f"Response Time: {response_time:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            return True, response_time
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False, response_time
            
    except requests.exceptions.Timeout:
        response_time = (time.time() - start_time) * 1000
        print(f"❌ Health check timed out after {response_time:.2f}ms")
        return False, response_time
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        print(f"❌ Health check error: {e}")
        return False, response_time

def test_smart_search():
    """Test smart search for affiliate_links_cached error"""
    print("\n🔍 Testing Smart Search...")
    
    headers = {
        "Content-Type": "application/json",
        "x-vercel-protection-bypass": "4uPEirWZEyeECM2l2q5ktThP8W0wcQ73",
        "x-internal-key": "ALIINSIDER-2025"
    }
    
    payload = {
        "keywords": "test",
        "page_size": 1
    }
    
    try:
        response = requests.post(
            "https://alistach.vercel.app/api/products/smart-search",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Smart search passed")
            return True
        else:
            data = response.json()
            error_msg = data.get('error', 'Unknown error')
            print(f"❌ Smart search failed: {error_msg}")
            
            if 'affiliate_links_cached' in error_msg:
                print("🎯 CONFIRMED: affiliate_links_cached NameError in production")
            
            return False
            
    except Exception as e:
        print(f"❌ Smart search error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Production Issues")
    print("=" * 50)
    
    # Test health endpoint
    health_ok, health_time = test_health_endpoint()
    
    # Test smart search
    search_ok = test_smart_search()
    
    print("\n📋 SUMMARY")
    print("=" * 50)
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'} ({health_time:.2f}ms)")
    print(f"Smart Search: {'✅ PASS' if search_ok else '❌ FAIL'}")