"""Unit tests for AliExpress service."""

import pytest
from unittest.mock import Mock, patch
from src.services.aliexpress_service import (
    AliExpressService, 
    AliExpressServiceException,
    APIError,
    ValidationError,
    PermissionError,
    RateLimitError
)
from src.models.responses import CategoryResponse, ProductResponse, AffiliateLink


class TestAliExpressService:
    """Test AliExpress service functionality."""
    
    def test_service_initialization(self, test_config):
        """Test service initialization."""
        with patch('src.services.aliexpress_service.AliexpressApi') as mock_api_class:
            service = AliExpressService(test_config)
            
            assert service.config == test_config
            mock_api_class.assert_called_once()
    
    def test_get_parent_categories_success(self, mock_aliexpress_service):
        """Test successful parent categories retrieval."""
        categories = mock_aliexpress_service.get_parent_categories()
        
        assert len(categories) == 1
        assert isinstance(categories[0], CategoryResponse)
        assert categories[0].category_id == "123"
        assert categories[0].category_name == "Electronics"
    
    def test_get_parent_categories_api_error(self, mock_aliexpress_service):
        """Test parent categories retrieval with API error."""
        mock_aliexpress_service.api.get_parent_categories.side_effect = Exception("API Error")
        
        with pytest.raises(APIError, match="API call failed for parent_categories"):
            mock_aliexpress_service.get_parent_categories()
    
    def test_get_child_categories_success(self, mock_aliexpress_service):
        """Test successful child categories retrieval."""
        categories = mock_aliexpress_service.get_child_categories("123")
        
        assert len(categories) == 1
        assert isinstance(categories[0], CategoryResponse)
        assert categories[0].category_id == "123"
        assert categories[0].parent_id == "123"
    
    def test_get_child_categories_empty_parent_id(self, mock_aliexpress_service):
        """Test child categories with empty parent ID."""
        with pytest.raises(ValidationError, match="parent_id cannot be empty"):
            mock_aliexpress_service.get_child_categories("")
    
    def test_search_products_success(self, mock_aliexpress_service):
        """Test successful product search."""
        result = mock_aliexpress_service.search_products(
            keywords="test",
            page_size=10
        )
        
        assert result.total_record_count == 1
        assert len(result.products) == 1
        assert isinstance(result.products[0], ProductResponse)
        assert result.products[0].product_id == "1005003091506814"
    
    def test_search_products_invalid_page_size(self, mock_aliexpress_service):
        """Test product search with invalid page size."""
        with pytest.raises(ValidationError, match="page_size cannot exceed 50"):
            mock_aliexpress_service.search_products(page_size=100)
    
    def test_search_products_invalid_page_no(self, mock_aliexpress_service):
        """Test product search with invalid page number."""
        with pytest.raises(ValidationError, match="page_no must be at least 1"):
            mock_aliexpress_service.search_products(page_no=0)
    
    def test_get_products_details_success(self, mock_aliexpress_service):
        """Test successful product details retrieval."""
        product_ids = ["1005003091506814"]
        results = mock_aliexpress_service.get_products_details(product_ids)
        
        assert len(results) == 1
        assert results[0].product_id == "1005003091506814"
    
    def test_get_products_details_empty_list(self, mock_aliexpress_service):
        """Test product details with empty product IDs."""
        with pytest.raises(ValidationError, match="product_ids cannot be empty"):
            mock_aliexpress_service.get_products_details([])
    
    def test_get_products_details_too_many_ids(self, mock_aliexpress_service):
        """Test product details with too many product IDs."""
        product_ids = [f"id_{i}" for i in range(25)]
        
        with pytest.raises(ValidationError, match="Cannot request details for more than 20 products"):
            mock_aliexpress_service.get_products_details(product_ids)
    
    def test_get_affiliate_links_success(self, mock_aliexpress_service):
        """Test successful affiliate link generation."""
        urls = ["https://www.aliexpress.com/item/1005003091506814.html"]
        results = mock_aliexpress_service.get_affiliate_links(urls)
        
        assert len(results) == 1
        assert isinstance(results[0], AffiliateLink)
        assert results[0].original_url == "https://www.aliexpress.com/item/1005003091506814.html"
        assert "affiliate" in results[0].affiliate_url
    
    def test_get_affiliate_links_empty_list(self, mock_aliexpress_service):
        """Test affiliate links with empty URL list."""
        with pytest.raises(ValidationError, match="urls cannot be empty"):
            mock_aliexpress_service.get_affiliate_links([])
    
    def test_get_affiliate_links_too_many_urls(self, mock_aliexpress_service):
        """Test affiliate links with too many URLs."""
        urls = [f"https://example.com/item/{i}" for i in range(55)]
        
        with pytest.raises(ValidationError, match="Cannot process more than 50 URLs"):
            mock_aliexpress_service.get_affiliate_links(urls)
    
    def test_handle_api_error_permission_error(self, mock_aliexpress_service):
        """Test API error handling for permission errors."""
        error = Exception("App does not have permission to access this resource")
        
        with pytest.raises(PermissionError):
            mock_aliexpress_service._handle_api_error(error, "test_operation")
    
    def test_handle_api_error_rate_limit_error(self, mock_aliexpress_service):
        """Test API error handling for rate limit errors."""
        error = Exception("Rate limit exceeded")
        
        with pytest.raises(RateLimitError):
            mock_aliexpress_service._handle_api_error(error, "test_operation")
    
    def test_handle_api_error_validation_error(self, mock_aliexpress_service):
        """Test API error handling for validation errors."""
        error = Exception("Invalid parameter provided")
        
        with pytest.raises(ValidationError):
            mock_aliexpress_service._handle_api_error(error, "test_operation")
    
    def test_handle_api_error_generic_error(self, mock_aliexpress_service):
        """Test API error handling for generic errors."""
        error = Exception("Unknown error occurred")
        
        with pytest.raises(APIError):
            mock_aliexpress_service._handle_api_error(error, "test_operation")
    
    def test_get_permission_guidance(self, mock_aliexpress_service):
        """Test permission guidance messages."""
        guidance = mock_aliexpress_service._get_permission_guidance("hot_products")
        assert "Hot products require special API permissions" in guidance
        
        guidance = mock_aliexpress_service._get_permission_guidance("orders")
        assert "Order tracking requires affiliate account" in guidance
        
        guidance = mock_aliexpress_service._get_permission_guidance("unknown_operation")
        assert "This operation requires special API permissions" in guidance
    
    def test_get_service_info(self, mock_aliexpress_service):
        """Test service information retrieval."""
        info = mock_aliexpress_service.get_service_info()
        
        assert info['service'] == 'AliExpress API Service'
        assert info['version'] == '2.0.0'
        assert 'supported_endpoints' in info
        assert 'sdk_methods' in info
        assert 'notes' in info