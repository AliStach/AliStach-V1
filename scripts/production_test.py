#!/usr/bin/env python3
"""
Production readiness test - comprehensive validation of all systems.
Tests security, performance, reliability, and compliance aspects.
"""

import sys
import os
import time
import json
import asyncio
from typing import Dict, List, Tuple, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

try:
    import httpx
    import psutil
except ImportError:
    print("❌ Required packages not installed. Installing...")
    os.system("pip install httpx psutil")
    import httpx
    import psutil


class ProductionValidator:
    """Comprehensive production readiness validator."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            'security': [],
            'performance': [],
            'reliability': [],
            'compliance': [],
            'functionality': []
        }
        self.start_time = time.time()
    
    def log_result(self, category: str, test_name: str, passed: bool, 
                   details: str = "", metrics: Dict[str, Any] = None):
        """Log test result with categorization."""
        result = {
            'test': test_name,
            'passed': passed,
            'details': details,
            'metrics': metrics or {},
            'timestamp': time.time()
        }
        self.results[category].append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} [{category.upper()}] {test_name}")
        if details:
            print(f"    {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"    {key}: {value}")
    
    async def test_security_features(self):
        """Test security implementations."""
        print("\n🔒 SECURITY VALIDATION")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test rate limiting
            try:
                responses = []
                start = time.time()
                
                # Send rapid requests to trigger rate limiting
                tasks = [client.get(f"{self.base_url}/health") for _ in range(10)]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                elapsed = time.time() - start
                success_count = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
                
                self.log_result(
                    'security', 
                    'Rate Limiting Protection',
                    success_count < 10,  # Should be rate limited
                    f"Processed {success_count}/10 requests in {elapsed:.2f}s",
                    {'requests_per_second': success_count / elapsed}
                )
            except Exception as e:
                self.log_result('security', 'Rate Limiting Protection', False, str(e))
            
            # Test CORS protection
            try:
                headers = {'Origin': 'https://malicious-site.com'}
                response = await client.get(f"{self.base_url}/health", headers=headers)
                
                cors_headers = response.headers.get('access-control-allow-origin', '')
                cors_protected = 'malicious-site.com' not in cors_headers
                
                self.log_result(
                    'security',
                    'CORS Protection',
                    cors_protected,
                    f"CORS header: {cors_headers}",
                    {'cors_properly_configured': cors_protected}
                )
            except Exception as e:
                self.log_result('security', 'CORS Protection', False, str(e))
            
            # Test input validation
            try:
                invalid_data = {
                    'keywords': 'x' * 1000,  # Extremely long input
                    'page_size': 999,  # Invalid page size
                    'page_no': -1  # Invalid page number
                }
                response = await client.post(f"{self.base_url}/api/products/search", json=invalid_data)
                
                validation_working = response.status_code == 422  # Validation error expected
                
                self.log_result(
                    'security',
                    'Input Validation',
                    validation_working,
                    f"Response status: {response.status_code}",
                    {'validation_active': validation_working}
                )
            except Exception as e:
                self.log_result('security', 'Input Validation', False, str(e))
    
    async def test_performance_metrics(self):
        """Test performance characteristics."""
        print("\n⚡ PERFORMANCE VALIDATION")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test response times
            response_times = []
            
            for i in range(5):
                start = time.time()
                try:
                    response = await client.get(f"{self.base_url}/health")
                    elapsed = (time.time() - start) * 1000
                    response_times.append(elapsed)
                    
                    if response.status_code != 200:
                        break
                except Exception:
                    break
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                performance_good = avg_response_time < 500  # Under 500ms average
                
                self.log_result(
                    'performance',
                    'Response Time Performance',
                    performance_good,
                    f"Average: {avg_response_time:.2f}ms, Max: {max_response_time:.2f}ms",
                    {
                        'avg_response_ms': avg_response_time,
                        'max_response_ms': max_response_time,
                        'samples': len(response_times)
                    }
                )
            
            # Test concurrent requests
            try:
                start = time.time()
                tasks = [client.get(f"{self.base_url}/health") for _ in range(20)]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                elapsed = time.time() - start
                
                successful_responses = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
                throughput = successful_responses / elapsed
                
                concurrency_good = successful_responses >= 18  # At least 90% success
                
                self.log_result(
                    'performance',
                    'Concurrent Request Handling',
                    concurrency_good,
                    f"Handled {successful_responses}/20 concurrent requests in {elapsed:.2f}s",
                    {
                        'throughput_rps': throughput,
                        'success_rate': successful_responses / 20,
                        'concurrent_requests': 20
                    }
                )
            except Exception as e:
                self.log_result('performance', 'Concurrent Request Handling', False, str(e))
    
    async def test_reliability_features(self):
        """Test system reliability and error handling."""
        print("\n🛡️ RELIABILITY VALIDATION")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test error handling
            try:
                response = await client.get(f"{self.base_url}/api/products/details/invalid_id")
                
                error_handled = response.status_code in [400, 404, 422]
                
                if error_handled:
                    try:
                        error_data = response.json()
                        has_error_structure = 'success' in error_data and 'error' in error_data
                    except:
                        has_error_structure = False
                else:
                    has_error_structure = False
                
                self.log_result(
                    'reliability',
                    'Error Handling',
                    error_handled and has_error_structure,
                    f"Status: {response.status_code}, Structured: {has_error_structure}",
                    {'proper_error_response': error_handled and has_error_structure}
                )
            except Exception as e:
                self.log_result('reliability', 'Error Handling', False, str(e))
            
            # Test health endpoint reliability
            health_checks = []
            for i in range(10):
                try:
                    response = await client.get(f"{self.base_url}/health")
                    health_checks.append(response.status_code == 200)
                    await asyncio.sleep(0.1)
                except:
                    health_checks.append(False)
            
            health_reliability = sum(health_checks) / len(health_checks)
            reliable = health_reliability >= 0.95  # 95% uptime
            
            self.log_result(
                'reliability',
                'Health Endpoint Reliability',
                reliable,
                f"Success rate: {health_reliability:.1%}",
                {'uptime_percentage': health_reliability * 100}
            )
    
    async def test_functionality_coverage(self):
        """Test core functionality coverage."""
        print("\n🔧 FUNCTIONALITY VALIDATION")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test core endpoints
            endpoints = [
                ('GET', '/health', None, 'Health Check'),
                ('GET', '/api/categories', None, 'Categories List'),
                ('POST', '/api/products/search', {'keywords': 'test', 'page_size': 3}, 'Product Search'),
                ('GET', '/api/products/search?keywords=test&page_size=3', None, 'Product Search GET'),
            ]
            
            working_endpoints = 0
            total_endpoints = len(endpoints)
            
            for method, path, data, name in endpoints:
                try:
                    if method == 'GET':
                        response = await client.get(f"{self.base_url}{path}")
                    else:
                        response = await client.post(f"{self.base_url}{path}", json=data)
                    
                    endpoint_working = response.status_code == 200
                    if endpoint_working:
                        try:
                            json_data = response.json()
                            endpoint_working = json_data.get('success', False)
                        except:
                            endpoint_working = False
                    
                    if endpoint_working:
                        working_endpoints += 1
                    
                    self.log_result(
                        'functionality',
                        f'{name} Endpoint',
                        endpoint_working,
                        f"Status: {response.status_code}",
                        {'endpoint_functional': endpoint_working}
                    )
                except Exception as e:
                    self.log_result('functionality', f'{name} Endpoint', False, str(e))
            
            # Overall functionality score
            functionality_score = working_endpoints / total_endpoints
            functionality_good = functionality_score >= 0.8
            
            self.log_result(
                'functionality',
                'Overall Functionality Coverage',
                functionality_good,
                f"Working endpoints: {working_endpoints}/{total_endpoints} ({functionality_score:.1%})",
                {
                    'coverage_percentage': functionality_score * 100,
                    'working_endpoints': working_endpoints,
                    'total_endpoints': total_endpoints
                }
            )
    
    async def test_compliance_standards(self):
        """Test compliance with standards and best practices."""
        print("\n📋 COMPLIANCE VALIDATION")
        print("=" * 50)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test OpenAPI documentation
            try:
                response = await client.get(f"{self.base_url}/openapi.json")
                
                openapi_available = response.status_code == 200
                if openapi_available:
                    try:
                        openapi_data = response.json()
                        has_required_fields = all(field in openapi_data for field in ['openapi', 'info', 'paths'])
                    except:
                        has_required_fields = False
                else:
                    has_required_fields = False
                
                self.log_result(
                    'compliance',
                    'OpenAPI Documentation',
                    openapi_available and has_required_fields,
                    f"Available: {openapi_available}, Valid: {has_required_fields}",
                    {'openapi_compliant': openapi_available and has_required_fields}
                )
            except Exception as e:
                self.log_result('compliance', 'OpenAPI Documentation', False, str(e))
            
            # Test response format consistency
            try:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    has_standard_format = all(field in data for field in ['success', 'metadata'])
                    
                    self.log_result(
                        'compliance',
                        'Response Format Consistency',
                        has_standard_format,
                        f"Standard format: {has_standard_format}",
                        {'consistent_response_format': has_standard_format}
                    )
                else:
                    self.log_result('compliance', 'Response Format Consistency', False, f"Health check failed: {response.status_code}")
            except Exception as e:
                self.log_result('compliance', 'Response Format Consistency', False, str(e))
    
    def generate_report(self):
        """Generate comprehensive production readiness report."""
        print("\n" + "=" * 80)
        print("📊 PRODUCTION READINESS REPORT")
        print("=" * 80)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            if tests:
                category_passed = sum(1 for test in tests if test['passed'])
                category_total = len(tests)
                category_percentage = (category_passed / category_total) * 100
                
                print(f"\n🔍 {category.upper()}: {category_passed}/{category_total} ({category_percentage:.1f}%)")
                
                for test in tests:
                    status = "✅" if test['passed'] else "❌"
                    print(f"  {status} {test['test']}")
                    if test['details']:
                        print(f"      {test['details']}")
                
                total_tests += category_total
                passed_tests += category_passed
        
        overall_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL SCORE: {passed_tests}/{total_tests} ({overall_percentage:.1f}%)")
        
        if overall_percentage >= 90:
            print("🎉 EXCELLENT - Production ready!")
        elif overall_percentage >= 80:
            print("✅ GOOD - Minor issues to address")
        elif overall_percentage >= 70:
            print("⚠️ FAIR - Several issues need attention")
        else:
            print("❌ POOR - Major issues must be resolved")
        
        execution_time = time.time() - self.start_time
        print(f"\n⏱️ Total execution time: {execution_time:.2f} seconds")
        
        return overall_percentage >= 80


async def main():
    """Run comprehensive production validation."""
    print("🚀 PRODUCTION READINESS VALIDATION")
    print("=" * 80)
    
    validator = ProductionValidator()
    
    # Check if server is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{validator.base_url}/health")
            if response.status_code != 200:
                print(f"❌ Server not responding at {validator.base_url}")
                print("💡 Start the server with: python -m src.api.main")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Start the server with: python -m src.api.main")
        return False
    
    print(f"✅ Server running at {validator.base_url}")
    
    # Run all validation tests
    await validator.test_security_features()
    await validator.test_performance_metrics()
    await validator.test_reliability_features()
    await validator.test_functionality_coverage()
    await validator.test_compliance_standards()
    
    # Generate final report
    production_ready = validator.generate_report()
    
    return production_ready


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)