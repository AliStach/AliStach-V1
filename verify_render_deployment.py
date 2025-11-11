#!/usr/bin/env python3
"""
Render.com Deployment Verification Script

This script verifies that the Render deployment is working correctly
by testing all critical endpoints and checking their responses.

Usage:
    python verify_render_deployment.py
    python verify_render_deployment.py --url https://your-custom-url.onrender.com
"""

import sys
import time
import json
import argparse
from typing import Dict, Tuple
try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not found")
    print("Install it with: pip install requests")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def test_endpoint(url: str, endpoint: str, expected_status: int = 200, 
                  method: str = "GET", timeout: int = 30) -> Tuple[bool, Dict]:
    """
    Test an endpoint and return success status and response data
    
    Args:
        url: Base URL
        endpoint: Endpoint path
        expected_status: Expected HTTP status code
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds
    
    Returns:
        Tuple of (success: bool, data: dict)
    """
    full_url = f"{url}{endpoint}"
    print(f"\n{Colors.BOLD}Testing: {endpoint}{Colors.END}")
    print(f"URL: {full_url}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(full_url, timeout=timeout)
        elif method == "POST":
            response = requests.post(full_url, json={}, timeout=timeout)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed_time:.0f}ms")
        
        # Check status code
        if response.status_code != expected_status:
            print_error(f"Expected status {expected_status}, got {response.status_code}")
            return False, {"error": f"Wrong status code: {response.status_code}"}
        
        # Try to parse JSON
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)[:200]}...")
            return True, data
        except json.JSONDecodeError:
            print_warning("Response is not JSON")
            return True, {"text": response.text[:200]}
    
    except requests.exceptions.Timeout:
        print_error(f"Request timed out after {timeout} seconds")
        return False, {"error": "timeout"}
    
    except requests.exceptions.ConnectionError:
        print_error("Connection error - service may not be running")
        return False, {"error": "connection_error"}
    
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        return False, {"error": str(e)}


def verify_deployment(base_url: str):
    """
    Verify the Render deployment by testing all critical endpoints
    
    Args:
        base_url: Base URL of the deployed service
    """
    print_header("Render.com Deployment Verification")
    
    print_info(f"Testing deployment at: {base_url}")
    print_info("This may take 30-60 seconds on first request (cold start)")
    
    results = {}
    
    # Test 1: Health Check
    print_header("Test 1: Health Check")
    success, data = test_endpoint(base_url, "/health", timeout=60)
    results["health"] = success
    
    if success:
        print_success("Health check passed!")
        if "status" in data:
            print_info(f"Status: {data.get('status')}")
        if "environment" in data:
            print_info(f"Environment: {data.get('environment')}")
        if "platform" in data:
            print_info(f"Platform: {data.get('platform')}")
    else:
        print_error("Health check failed!")
        print_warning("Service may still be starting up. Wait 1 minute and try again.")
    
    # Test 2: OpenAPI Specification
    print_header("Test 2: OpenAPI Specification")
    success, data = test_endpoint(base_url, "/openapi-gpt.json")
    results["openapi"] = success
    
    if success:
        print_success("OpenAPI spec accessible!")
        if "openapi" in data:
            print_info(f"OpenAPI Version: {data.get('openapi')}")
        if "info" in data and "title" in data["info"]:
            print_info(f"API Title: {data['info']['title']}")
    else:
        print_error("OpenAPI spec not accessible!")
    
    # Test 3: Root Endpoint
    print_header("Test 3: Root Endpoint")
    success, data = test_endpoint(base_url, "/")
    results["root"] = success
    
    if success:
        print_success("Root endpoint accessible!")
    else:
        print_error("Root endpoint not accessible!")
    
    # Test 4: Interactive Documentation
    print_header("Test 4: Interactive Documentation")
    success, data = test_endpoint(base_url, "/docs")
    results["docs"] = success
    
    if success:
        print_success("Interactive docs accessible!")
        print_info(f"Visit: {base_url}/docs")
    else:
        print_error("Interactive docs not accessible!")
    
    # Test 5: API Status (if available)
    print_header("Test 5: API Status")
    success, data = test_endpoint(base_url, "/api/status")
    results["api_status"] = success
    
    if success:
        print_success("API status endpoint accessible!")
    else:
        print_warning("API status endpoint not available (may be optional)")
    
    # Summary
    print_header("Verification Summary")
    
    total_tests = len([k for k in results.keys() if k != "api_status"])
    passed_tests = sum([1 for k, v in results.items() if v and k != "api_status"])
    
    print(f"\n{Colors.BOLD}Results:{Colors.END}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    
    print(f"\n{Colors.BOLD}Endpoint Status:{Colors.END}")
    for endpoint, success in results.items():
        if endpoint == "api_status":
            continue  # Skip optional endpoint
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {endpoint:20} {status}")
    
    # Final verdict
    print()
    if passed_tests == total_tests:
        print_success("🎉 All tests passed! Deployment is successful!")
        print_info(f"Your API is live at: {base_url}")
        print_info(f"Interactive docs: {base_url}/docs")
        print_info(f"OpenAPI spec: {base_url}/openapi-gpt.json")
        return 0
    else:
        print_error("Some tests failed. Please check the logs above.")
        print_warning("If this is a cold start, wait 1 minute and run the script again.")
        return 1


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Verify Render.com deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python verify_render_deployment.py
  python verify_render_deployment.py --url https://my-api.onrender.com
        """
    )
    parser.add_argument(
        "--url",
        default="https://alistach-api.onrender.com",
        help="Base URL of the deployed service (default: https://alistach-api.onrender.com)"
    )
    
    args = parser.parse_args()
    
    # Remove trailing slash if present
    base_url = args.url.rstrip("/")
    
    try:
        exit_code = verify_deployment(base_url)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
