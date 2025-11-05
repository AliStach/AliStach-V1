"""Integration tests for full API workflows."""

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


class TestFullWorkflow:
    """Test complete API workflows."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(_test_app)
    
    @pytest.fixture
    def comprehensive_mock_service(self):
        """Create comprehensive mock service for workflow testing."""
        mock = Mock()
        
        # Mock all required methods
        from src.models.responses import (
            CategoryResponse, ProductResponse, ProductSearchResponse, 
            ProductDetailResponse, AffiliateLink
        )
        
        # Categories
        mock.get_parent_categories.return_value = [
            CategoryResponse(category_id="1", category_name="Electronics"),
            CategoryResponse(category_id="2", category_name="Fashion")
        ]
        
        mock.get_child_categories.return_value = [
            CategoryResponse(category_id="11", category_name="Smartphones", parent_id="1"),
            CategoryResponse(category_id="12", category_name="Laptops", parent_id="1")
        ]
        
        # Products
        products = [
            ProductResponse(
                product_id="1001",
                product_title="iPhone 15",
                product_url="https://www.aliexpress.com/item/1001.html",
                price="899.99",
                currency="USD",
                image_url="https://example.com/iphone.jpg",
                commission_rate="3.5"
            ),
            ProductResponse(
                product_id="1002",
                product_title="Samsung Galaxy S24",
                product_url="https://www.aliexpress.com/item/1002.html",
                price="799.99",
                currency="USD",
                image_url="https://example.com/samsung.jpg",
                commission_rate="4.0"
            )
        ]
        
        # Make search_products dynamic to respect parameters
        def mock_search_products(**kwargs):
            page_size = kwargs.get('page_size', 20)
            page_no = kwargs.get('page_no', 1)
            return ProductSearchResponse(
                products=products[:page_size],  # Return only requested number of products
                total_record_count=150,
                current_page=page_no,
                page_size=page_size
            )
        
        def mock_get_products(**kwargs):
            page_size = kwargs.get('page_size', 20)
            page_no = kwargs.get('page_no', 1)
            return ProductSearchResponse(
                products=products[:page_size],  # Return only requested number of products
                total_record_count=150,
                current_page=page_no,
                page_size=page_size
            )
        
        mock.search_products.side_effect = mock_search_products
        mock.get_products.side_effect = mock_get_products
        
        # Product details
        mock.get_products_details.return_value = [
            ProductDetailResponse(
                product_id="1001",
                product_title="iPhone 15",
                product_url="https://www.aliexpress.com/item/1001.html",
                price="899.99",
                currency="USD",
                image_url="https://example.com/iphone.jpg",
                gallery_images=["https://example.com/iphone1.jpg", "https://example.com/iphone2.jpg"],
                description="Latest iPhone with advanced features",
                specifications={"storage": "128GB", "color": "Blue"},
                shipping_info={"method": "Standard", "time": "7-15 days"},
                seller_info={"name": "Apple Store", "rating": "98.5%"}
            )
        ]
        
        # Affiliate links
        mock.get_affiliate_links.return_value = [
            AffiliateLink(
                original_url="https://www.aliexpress.com/item/1001.html",
                affiliate_url="https://s.click.aliexpress.com/e/_affiliate_1001",
                tracking_id="test_tracking",
                commission_rate="3.5"
            ),
            AffiliateLink(
                original_url="https://www.aliexpress.com/item/1002.html",
                affiliate_url="https://s.click.aliexpress.com/e/_affiliate_1002",
                tracking_id="test_tracking",
                commission_rate="4.0"
            )
        ]
        
        # Service info
        mock.get_service_info.return_value = {
            "service": "AliExpress API Service",
            "version": "2.0.0",
            "status": "active",
            "supported_endpoints": ["categories", "products", "affiliate"]
        }
        
        # Mock config attribute
        mock_config = Mock()
        mock_config.tracking_id = "test_tracking"
        mock.config = mock_config
        
        return mock
    
    def test_complete_product_discovery_workflow(self, client, comprehensive_mock_service):
        """Test complete product discovery workflow."""
        with patch('src.api.main.service_instance', comprehensive_mock_service):
            # Step 1: Get categories
            response = client.get("/api/categories")
            assert response.status_code == 200
            categories = response.json()['data']
            assert len(categories) == 2
            
            # Step 2: Get child categories for Electronics
            response = client.get("/api/categories/1/children")
            assert response.status_code == 200
            child_categories = response.json()['data']
            assert len(child_categories) == 2
            assert child_categories[0]['category_name'] == "Smartphones"
            
            # Step 3: Search for products in smartphones category
            search_data = {
                "keywords": "iPhone",
                "category_ids": "11",
                "page_size": 10
            }
            response = client.post("/api/products/search", json=search_data)
            assert response.status_code == 200
            search_results = response.json()['data']
            assert len(search_results['products']) == 2
            assert search_results['total_record_count'] == 150
            
            # Step 4: Get detailed information for specific product
            product_id = search_results['products'][0]['product_id']
            response = client.get(f"/api/products/details/{product_id}")
            assert response.status_code == 200
            product_details = response.json()['data']
            assert product_details['product_id'] == "1001"
            assert 'specifications' in product_details
            assert 'shipping_info' in product_details
            
            # Step 5: Generate affiliate links for products
            product_urls = [product['product_url'] for product in search_results['products']]
            link_data = {"urls": product_urls}
            response = client.post("/api/affiliate/links", json=link_data)
            assert response.status_code == 200
            affiliate_links = response.json()['data']
            assert len(affiliate_links) == 2
            assert all('affiliate_url' in link for link in affiliate_links)
    
    def test_price_filtered_search_workflow(self, client, comprehensive_mock_service):
        """Test price-filtered product search workflow."""
        with patch('src.api.main.service_instance', comprehensive_mock_service):
            # Search with price filters
            search_data = {
                "keywords": "smartphone",
                "min_sale_price": 500.0,
                "max_sale_price": 1000.0,
                "page_size": 20
            }
            response = client.post("/api/products", json=search_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data['success'] is True
            products = data['data']['products']
            assert len(products) == 2
            
            # Verify all products are within price range (mock data should reflect this)
            for product in products:
                price = float(product['price'])
                assert 500.0 <= price <= 1000.0
    
    def test_bulk_product_details_workflow(self, client, comprehensive_mock_service):
        """Test bulk product details retrieval workflow."""
        with patch('src.api.main.service_instance', comprehensive_mock_service):
            # First, search for products
            response = client.get("/api/products/search?keywords=phone&page_size=5")
            assert response.status_code == 200
            
            search_results = response.json()['data']
            product_ids = [product['product_id'] for product in search_results['products']]
            
            # Get bulk details
            details_data = {"product_ids": product_ids}
            response = client.post("/api/products/details", json=details_data)
            assert response.status_code == 200
            
            details_response = response.json()
            assert details_response['success'] is True
            assert details_response['metadata']['requested_count'] == len(product_ids)
            assert details_response['metadata']['returned_count'] == 1  # Mock returns 1
    
    def test_error_handling_workflow(self, client, comprehensive_mock_service):
        """Test error handling throughout the workflow."""
        with patch('src.api.main.service_instance', comprehensive_mock_service):
            # Test invalid category ID
            response = client.get("/api/categories/invalid/children")
            # Should still work with mock, but test the structure
            assert response.status_code in [200, 400]
            
            # Test invalid product search parameters
            search_data = {
                "keywords": "test",
                "page_size": 100,  # Exceeds limit
                "page_no": -1      # Invalid page number
            }
            response = client.post("/api/products/search", json=search_data)
            assert response.status_code == 422  # Validation error
            
            # Test empty affiliate links request
            link_data = {"urls": []}
            response = client.post("/api/affiliate/links", json=link_data)
            assert response.status_code == 422  # Validation error
    
    def test_pagination_workflow(self, client, comprehensive_mock_service):
        """Test pagination throughout the API."""
        with patch('src.api.main.service_instance', comprehensive_mock_service):
            # Test different page sizes and numbers
            for page_size in [5, 10, 20]:
                response = client.get(f"/api/products/search?keywords=test&page_size={page_size}")
                assert response.status_code == 200
                
                data = response.json()['data']
                assert data['page_size'] == page_size
                assert data['current_page'] == 1
            
            # Test different page numbers
            for page_no in [1, 2, 3]:
                search_data = {
                    "keywords": "test",
                    "page_no": page_no,
                    "page_size": 10
                }
                response = client.post("/api/products/search", json=search_data)
                assert response.status_code == 200
                
                data = response.json()['data']
                assert data['current_page'] == page_no
    
    def test_service_health_and_info_workflow(self, client, comprehensive_mock_service):
        """Test service health and information endpoints."""
        with patch('src.api.main.service_instance', comprehensive_mock_service), \
             patch('src.api.main.config_instance') as mock_config:
            
            mock_config.language = "EN"
            mock_config.currency = "USD"
            mock_config.api_host = "0.0.0.0"
            mock_config.api_port = 8000
            mock_config.log_level = "INFO"
            
            # Test health check
            response = client.get("/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data['success'] is True
            assert 'service_info' in health_data['data']
            
            # Test system info
            response = client.get("/system/info")
            assert response.status_code == 200
            system_data = response.json()
            assert system_data['success'] is True
            assert 'service' in system_data['data']
            assert 'configuration' in system_data['data']
            assert 'api_endpoints' in system_data['data']
            
            # Test OpenAPI spec
            response = client.get("/openapi.json")
            assert response.status_code == 200
            openapi_data = response.json()
            assert 'openapi' in openapi_data
            assert 'paths' in openapi_data
    
    def test_concurrent_requests_simulation(self, client, comprehensive_mock_service):
        """Test handling of multiple concurrent requests."""
        with patch('src.api.main.service_instance', comprehensive_mock_service):
            # Simulate multiple concurrent requests
            responses = []
            
            # Make multiple requests
            for i in range(5):
                response = client.get(f"/api/products/search?keywords=test{i}&page_size=5")
                responses.append(response)
            
            # Verify all requests succeeded
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data['success'] is True
                assert len(data['data']['products']) == 2  # Mock returns 2 products