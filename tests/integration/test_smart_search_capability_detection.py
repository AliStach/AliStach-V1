"""Integration tests for smart search capability detection and fallback functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from src.api.main import app
from src.services.service_factory import ServiceFactory, ServiceWithMetadata, ServiceCapabilities
from src.services.service_capability_detector import ServiceCapabilityDetector
from src.services.smart_search_fallback import SmartSearchFallback
from src.services.aliexpress_service import AliExpressService
from src.models.responses import ProductResponse, ProductSearchResponse
from datetime import datetime


class TestSmartSearchCapabilityDetection:
    """Test smart search endpoint with different service configurations."""
    
    def setup_method(self):
        """Set up test client and common mocks."""
        self.client = TestClient(app)
        self.test_request = {
            "keywords": "test product",
            "page_no": 1,
            "page_size": 10,
            "generate_affiliate_links": True
        }
    
    def create_mock_basic_service(self):
        """Create a mock basic AliExpress service."""
        mock_service = Mock(spec=AliExpressService)
        mock_service.__class__.__name__ = 'AliExpressService'
        
        # Mock basic service methods
        mock_product = ProductResponse(
            product_id="123",
            product_title="Test Product",
            product_url="https://example.com/product/123",
            price="10.99",
            currency="USD"
        )
        
        mock_result = ProductSearchResponse(
            products=[mock_product],
            total_record_count=1,
            current_page=1,
            page_size=10
        )
        
        mock_service.get_products.return_value = mock_result
        
        # Ensure smart_product_search method does NOT exist
        if hasattr(mock_service, 'smart_product_search'):
            delattr(mock_service, 'smart_product_search')
        
        return mock_service
    
    def create_mock_enhanced_service(self):
        """Create a mock enhanced AliExpress service."""
        mock_service = Mock()
        mock_service.__class__.__name__ = 'EnhancedAliExpressService'
        
        # Mock enhanced service with smart_product_search
        from src.services.enhanced_aliexpress_service import SmartSearchResponse, ProductWithAffiliateResponse
        
        mock_product = ProductWithAffiliateResponse(
            product_id="123",
            product_title="Test Product",
            product_url="https://example.com/product/123",
            price="10.99",
            currency="USD",
            affiliate_url="https://affiliate.example.com/123",
            affiliate_status="generated"
        )
        
        mock_result = SmartSearchResponse(
            products=[mock_product],
            total_record_count=1,
            current_page=1,
            page_size=10,
            cache_hit=False,
            affiliate_links_cached=0,
            affiliate_links_generated=1,
            api_calls_saved=0,
            response_time_ms=150.0,
            service_type="enhanced",
            fallback_used=False,
            enhanced_features_available=True
        )
        
        mock_service.smart_product_search.return_value = mock_result
        return mock_service
    
    def create_service_with_metadata(self, service, service_type="basic"):
        """Create ServiceWithMetadata for testing."""
        capabilities = ServiceCapabilities(
            has_smart_search=(service_type == "enhanced"),
            has_caching=(service_type == "enhanced"),
            has_image_processing=(service_type == "enhanced"),
            supports_affiliate_links=True,
            environment_type="test"
        )
        
        return ServiceWithMetadata(
            service=service,
            capabilities=capabilities,
            service_type=service_type,
            created_at=datetime.utcnow()
        )
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_enhanced_service_scenario(self, mock_get_service):
        """Test smart search with enhanced service."""
        # Setup enhanced service
        enhanced_service = self.create_mock_enhanced_service()
        service_metadata = self.create_service_with_metadata(enhanced_service, "enhanced")
        mock_get_service.return_value = service_metadata
        
        # Make request
        response = self.client.post("/api/products/smart-search", json=self.test_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "service_metadata" in data["data"]
        assert data["data"]["service_metadata"]["service_type"] == "enhanced"
        assert data["data"]["service_metadata"]["fallback_used"] is False
        assert data["data"]["service_metadata"]["enhanced_features_available"] is True
        
        # Verify enhanced service was called
        enhanced_service.smart_product_search.assert_called_once()
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_basic_service_fallback_scenario(self, mock_get_service):
        """Test smart search with basic service fallback."""
        # Setup basic service
        basic_service = self.create_mock_basic_service()
        service_metadata = self.create_service_with_metadata(basic_service, "basic")
        mock_get_service.return_value = service_metadata
        
        # Make request
        response = self.client.post("/api/products/smart-search", json=self.test_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "service_metadata" in data["data"]
        assert data["data"]["service_metadata"]["service_type"] == "basic"
        assert data["data"]["service_metadata"]["fallback_used"] is True
        assert data["data"]["service_metadata"]["enhanced_features_available"] is False
        
        # Verify fallback metadata is present
        assert "fallback_info" in data["metadata"]
        assert data["metadata"]["fallback_info"]["fallback_used"] is True
        assert data["metadata"]["fallback_info"]["enhanced_features_available"] is False
        
        # Verify basic service was called through fallback
        basic_service.get_products.assert_called_once()
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_response_format_consistency(self, mock_get_service):
        """Test that both enhanced and basic services return consistent response format."""
        test_cases = [
            ("enhanced", self.create_mock_enhanced_service()),
            ("basic", self.create_mock_basic_service())
        ]
        
        for service_type, service in test_cases:
            with self.subTest(service_type=service_type):
                # Setup service
                service_metadata = self.create_service_with_metadata(service, service_type)
                mock_get_service.return_value = service_metadata
                
                # Make request
                response = self.client.post("/api/products/smart-search", json=self.test_request)
                
                # Verify response structure
                assert response.status_code == 200
                data = response.json()
                
                # Check required top-level fields
                assert "success" in data
                assert "data" in data
                assert "metadata" in data
                
                # Check required data fields
                response_data = data["data"]
                assert "products" in response_data
                assert "total_record_count" in response_data
                assert "current_page" in response_data
                assert "page_size" in response_data
                assert "performance_metrics" in response_data
                assert "service_metadata" in response_data
                
                # Check performance metrics are always present
                perf_metrics = response_data["performance_metrics"]
                required_metrics = [
                    "cache_hit", "response_time_ms", "affiliate_links_cached",
                    "affiliate_links_generated", "api_calls_saved"
                ]
                for metric in required_metrics:
                    assert metric in perf_metrics, f"Missing metric: {metric}"
                
                # Check service metadata
                service_meta = response_data["service_metadata"]
                assert "service_type" in service_meta
                assert "fallback_used" in service_meta
                assert "enhanced_features_available" in service_meta
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_attribute_error_handling(self, mock_get_service):
        """Test handling of AttributeError when method doesn't exist."""
        # Create a service that will cause AttributeError
        mock_service = Mock()
        mock_service.__class__.__name__ = 'UnknownService'
        
        # Remove smart_product_search method to simulate AttributeError
        if hasattr(mock_service, 'smart_product_search'):
            delattr(mock_service, 'smart_product_search')
        
        # Make get_products also fail to simulate complete method absence
        mock_service.get_products.side_effect = AttributeError("'UnknownService' object has no attribute 'get_products'")
        
        service_metadata = self.create_service_with_metadata(mock_service, "unknown")
        mock_get_service.return_value = service_metadata
        
        # Make request
        response = self.client.post("/api/products/smart-search", json=self.test_request)
        
        # Verify error response
        assert response.status_code == 503
        data = response.json()
        
        assert data["success"] is False
        assert "error" in data
        assert "service_info" in data["metadata"]
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_service_exception_handling(self, mock_get_service):
        """Test handling of AliExpress service exceptions."""
        from src.services.aliexpress_service import AliExpressServiceException
        
        # Setup basic service that throws exception
        basic_service = self.create_mock_basic_service()
        basic_service.get_products.side_effect = AliExpressServiceException("API rate limit exceeded")
        
        service_metadata = self.create_service_with_metadata(basic_service, "basic")
        mock_get_service.return_value = service_metadata
        
        # Make request
        response = self.client.post("/api/products/smart-search", json=self.test_request)
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        
        assert data["success"] is False
        assert "API rate limit exceeded" in data["error"]
        assert data["metadata"]["service_type"] == "basic"
    
    def test_service_capability_detector(self):
        """Test ServiceCapabilityDetector functionality."""
        # Test with enhanced service
        enhanced_service = self.create_mock_enhanced_service()
        assert ServiceCapabilityDetector.has_smart_search(enhanced_service) is True
        assert ServiceCapabilityDetector.get_service_type(enhanced_service) == "enhanced"
        
        capabilities = ServiceCapabilityDetector.get_capabilities(enhanced_service)
        assert capabilities["has_smart_search"] is True
        assert capabilities["has_enhanced_features"] is True
        
        # Test with basic service
        basic_service = self.create_mock_basic_service()
        assert ServiceCapabilityDetector.has_smart_search(basic_service) is False
        assert ServiceCapabilityDetector.get_service_type(basic_service) == "basic"
        
        capabilities = ServiceCapabilityDetector.get_capabilities(basic_service)
        assert capabilities["has_smart_search"] is False
        assert capabilities["has_enhanced_features"] is False
    
    def test_smart_search_fallback_functionality(self):
        """Test SmartSearchFallback class functionality."""
        # Create basic service and fallback wrapper
        basic_service = self.create_mock_basic_service()
        fallback = SmartSearchFallback(basic_service)
        
        # Test that fallback has smart_product_search method
        assert hasattr(fallback, 'smart_product_search')
        assert callable(getattr(fallback, 'smart_product_search'))
        
        # Test delegation to basic service for other methods
        assert hasattr(fallback, 'get_products')
        fallback.get_products()
        basic_service.get_products.assert_called()
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_performance_metrics_initialization(self, mock_get_service):
        """Test that all performance metrics are properly initialized."""
        # Test with basic service to ensure fallback initializes all metrics
        basic_service = self.create_mock_basic_service()
        service_metadata = self.create_service_with_metadata(basic_service, "basic")
        mock_get_service.return_value = service_metadata
        
        # Make request
        response = self.client.post("/api/products/smart-search", json=self.test_request)
        
        # Verify all metrics are present and properly typed
        assert response.status_code == 200
        data = response.json()
        
        perf_metrics = data["data"]["performance_metrics"]
        
        # Check that affiliate_links_cached is initialized (this was the original bug)
        assert "affiliate_links_cached" in perf_metrics
        assert isinstance(perf_metrics["affiliate_links_cached"], int)
        assert perf_metrics["affiliate_links_cached"] >= 0
        
        # Check other critical metrics
        assert isinstance(perf_metrics["affiliate_links_generated"], int)
        assert isinstance(perf_metrics["api_calls_saved"], int)
        assert isinstance(perf_metrics["response_time_ms"], (int, float))
        assert isinstance(perf_metrics["cache_hit"], bool)
    
    @patch('src.api.endpoints.products.get_service_with_metadata')
    def test_no_name_error_exceptions(self, mock_get_service):
        """Test that no NameError exceptions occur in any scenario."""
        test_scenarios = [
            ("enhanced", self.create_mock_enhanced_service()),
            ("basic", self.create_mock_basic_service())
        ]
        
        for service_type, service in test_scenarios:
            with self.subTest(service_type=service_type):
                service_metadata = self.create_service_with_metadata(service, service_type)
                mock_get_service.return_value = service_metadata
                
                # Make request - should never raise NameError
                try:
                    response = self.client.post("/api/products/smart-search", json=self.test_request)
                    # Should get either 200 (success) or 4xx/5xx (handled error), never NameError
                    assert response.status_code in [200, 400, 500, 503]
                except NameError as e:
                    pytest.fail(f"NameError occurred in {service_type} scenario: {e}")
                except Exception as e:
                    # Other exceptions are acceptable as long as they're not NameError
                    pass