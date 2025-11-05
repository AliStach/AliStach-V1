"""Integration tests for API endpoints."""

import pytest
from unittest.mock import patch, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Create a test app without security middleware
_test_app = FastAPI()

# Import and include routers without security
from src.api.endpoints.categories import router as categories_router
from src.api.endpoints.products import router as products_router
from src.api.endpoints.affiliate import router as affiliate_router
from src.api.main import health_check, get_openapi_spec, get_system_info

_test_app.include_router(categories_router, prefix="/api", tags=["categories"])
_test_app.include_router(products_router, prefix="/api", tags=["products"])
_test_app.include_router(affiliate_router, prefix="/api", tags=["affiliate"])

# Add the main endpoints
_test_app.get("/health")(health_check)
_test_app.get("/openapi.json")(get_openapi_spec)
_test_app.get("/system/info")(get_system_info)


class TestAPIEndpoints:
    """Test API endpoint integration."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(_test_app)
    
    @pytest.fixture
    def mock_service(self):
        """Mock the service instance."""
        mock = Mock()
        
        # Mock category responses
        from src.models.responses import CategoryResponse
        mock.get_parent_categories.return_value = [
            CategoryResponse(category_id="1", category_name="Electronics"),
            CategoryResponse(category_id="2", category_name="Fashion")
        ]
        mock.get_child_categories.return_value = [
            CategoryResponse(category_id="11", category_name="Phones", parent_id="1")
        ]
        
        # Mock product responses
        from src.models.responses import ProductResponse, ProductSearchResponse
        products = [
            ProductResponse(
                product_id="123",
                product_title="Test Product",
                product_url="https://example.com/product",
                price="29.99",
                currency="USD"
            )
        ]
        mock.search_products.return_value = ProductSearchResponse(
            products=products,
            total_record_count=1,
            current_page=1,
            page_size=20
        )
        mock.get_products.return_value = ProductSearchResponse(
            products=products,
            total_record_count=1,
            current_page=1,
            page_size=20
        )
        
        # Mock affiliate links
        from src.models.responses import AffiliateLink
        mock.get_affiliate_links.return_value = [
            AffiliateLink(
                original_url="https://example.com/product",
                affiliate_url="https://affiliate.example.com/product",
                tracking_id="test_tracking",
                commission_rate="5.0"
            )
        ]
        
        # Mock service info
        mock.get_service_info.return_value = {
            "service": "AliExpress API Service",
            "status": "active"
        }
        
        # Mock config attribute
        mock_config = Mock()
        mock_config.tracking_id = "test_tracking"
        mock.config = mock_config
        
        return mock
    
    def test_health_endpoint(self, client, mock_service):
        """Test health check endpoint."""
        with patch('src.api.main.service_instance', mock_service), \
             patch('src.api.main.config_instance') as mock_config:
            
            mock_config.language = "EN"
            mock_config.currency = "USD"
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'service_info' in data['data']
    
    def test_openapi_spec_endpoint(self, client):
        """Test OpenAPI specification endpoint."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert 'openapi' in data
        assert 'info' in data
        assert 'paths' in data
    
    def test_system_info_endpoint(self, client, mock_service):
        """Test system information endpoint."""
        with patch('src.api.main.service_instance', mock_service), \
             patch('src.api.main.config_instance') as mock_config:
            
            mock_config.language = "EN"
            mock_config.currency = "USD"
            mock_config.api_host = "0.0.0.0"
            mock_config.api_port = 8000
            mock_config.log_level = "INFO"
            
            response = client.get("/system/info")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert 'service' in data['data']
            assert 'configuration' in data['data']
            assert 'api_endpoints' in data['data']
    
    def test_get_categories_endpoint(self, client, mock_service):
        """Test get categories endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/categories")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']) == 2
            assert data['data'][0]['category_name'] == "Electronics"
            assert data['metadata']['total_count'] == 2
    
    def test_get_child_categories_endpoint(self, client, mock_service):
        """Test get child categories endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/categories/1/children")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']) == 1
            assert data['data'][0]['parent_id'] == "1"
            assert data['metadata']['parent_id'] == "1"
    
    def test_get_child_categories_empty_parent_id(self, client, mock_service):
        """Test get child categories with empty parent ID."""
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/categories/ /children")
            
            assert response.status_code == 400
            data = response.json()
            assert data['success'] is False
            assert "parent_id cannot be empty" in data['error']
    
    def test_search_products_post_endpoint(self, client, mock_service):
        """Test product search POST endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            search_data = {
                "keywords": "headphones",
                "page_size": 10
            }
            response = client.post("/api/products/search", json=search_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['products']) == 1
            assert data['data']['products'][0]['product_title'] == "Test Product"
            assert 'search_params' in data['metadata']
    
    def test_search_products_get_endpoint(self, client, mock_service):
        """Test product search GET endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/products/search?keywords=headphones&page_size=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['products']) == 1
            assert 'search_params' in data['metadata']
    
    def test_get_products_post_endpoint(self, client, mock_service):
        """Test enhanced product search POST endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            search_data = {
                "keywords": "phone",
                "max_sale_price": 100.0,
                "min_sale_price": 10.0,
                "page_size": 5
            }
            response = client.post("/api/products", json=search_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['products']) == 1
    
    def test_get_products_get_endpoint(self, client, mock_service):
        """Test enhanced product search GET endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/products?keywords=phone&max_sale_price=100&page_size=5")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']['products']) == 1
    
    def test_generate_affiliate_links_post_endpoint(self, client, mock_service):
        """Test affiliate links generation POST endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            link_data = {
                "urls": ["https://example.com/product"]
            }
            response = client.post("/api/affiliate/links", json=link_data)
            

            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['data']) == 1
            assert data['data'][0]['original_url'] == "https://example.com/product"
            assert 'requested_count' in data['metadata']
            assert 'generated_count' in data['metadata']
    
    def test_generate_affiliate_link_get_endpoint(self, client, mock_service):
        """Test single affiliate link generation GET endpoint."""
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/affiliate/link?url=https://example.com/product")
            
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['data']['original_url'] == "https://example.com/product"
            assert 'original_url' in data['metadata']
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON requests."""
        response = client.post(
            "/api/products/search",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_validation_error_handling(self, client, mock_service):
        """Test validation error handling."""
        with patch('src.api.main.service_instance', mock_service):
            # Invalid page size
            search_data = {
                "keywords": "test",
                "page_size": 100  # Exceeds maximum
            }
            response = client.post("/api/products/search", json=search_data)
            
            assert response.status_code == 422  # Validation error
    
    def test_service_not_initialized_error(self, client):
        """Test handling when service is not initialized."""
        with patch('src.api.main.service_instance', None):
            response = client.get("/api/categories")
            
            assert response.status_code == 503
            data = response.json()
            assert "Service not initialized" in data['detail']
    
    def test_service_exception_handling(self, client, mock_service):
        """Test service exception handling."""
        from src.services.aliexpress_service import AliExpressServiceException
        
        mock_service.get_parent_categories.side_effect = AliExpressServiceException("Test error")
        
        with patch('src.api.main.service_instance', mock_service):
            response = client.get("/api/categories")
            
            assert response.status_code == 400
            data = response.json()
            assert data['success'] is False
            assert "Test error" in data['error']