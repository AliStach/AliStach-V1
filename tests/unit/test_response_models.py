"""Unit tests for response models."""

import pytest
from datetime import datetime
from src.models.responses import (
    CategoryResponse,
    ProductResponse,
    ProductDetailResponse,
    AffiliateLink,
    HotProductResponse,
    ProductSearchResponse,
    ServiceResponse
)


class TestResponseModels:
    """Test response model functionality."""
    
    def test_category_response_creation(self):
        """Test CategoryResponse creation and serialization."""
        category = CategoryResponse(
            category_id="123",
            category_name="Electronics",
            parent_id="456"
        )
        
        assert category.category_id == "123"
        assert category.category_name == "Electronics"
        assert category.parent_id == "456"
        
        # Test serialization
        data = category.to_dict()
        assert data['category_id'] == "123"
        assert data['category_name'] == "Electronics"
        assert data['parent_id'] == "456"
    
    def test_category_response_without_parent(self):
        """Test CategoryResponse without parent ID."""
        category = CategoryResponse(
            category_id="123",
            category_name="Electronics"
        )
        
        assert category.parent_id is None
        
        data = category.to_dict()
        assert data['parent_id'] is None
    
    def test_product_response_creation(self):
        """Test ProductResponse creation and serialization."""
        product = ProductResponse(
            product_id="1005003091506814",
            product_title="Wireless Headphones",
            product_url="https://example.com/product",
            price="29.99",
            currency="USD",
            image_url="https://example.com/image.jpg",
            commission_rate="5.0"
        )
        
        assert product.product_id == "1005003091506814"
        assert product.product_title == "Wireless Headphones"
        assert product.price == "29.99"
        assert product.currency == "USD"
        
        # Test serialization
        data = product.to_dict()
        assert data['product_id'] == "1005003091506814"
        assert data['product_url'] == "https://example.com/product"
        assert data['commission_rate'] == "5.0"
    
    def test_product_response_minimal(self):
        """Test ProductResponse with minimal required fields."""
        product = ProductResponse(
            product_id="123",
            product_title="Test Product",
            product_url="https://example.com",
            price="10.00",
            currency="USD"
        )
        
        assert product.image_url is None
        assert product.commission_rate is None
        assert product.original_price is None
        
        data = product.to_dict()
        assert data['image_url'] is None
        assert data['commission_rate'] is None
    
    def test_affiliate_link_creation(self):
        """Test AffiliateLink creation and serialization."""
        link = AffiliateLink(
            original_url="https://www.aliexpress.com/item/123.html",
            affiliate_url="https://s.click.aliexpress.com/e/_affiliate",
            tracking_id="test_tracking",
            commission_rate="5.0"
        )
        
        assert link.original_url == "https://www.aliexpress.com/item/123.html"
        assert link.affiliate_url == "https://s.click.aliexpress.com/e/_affiliate"
        assert link.tracking_id == "test_tracking"
        assert link.commission_rate == "5.0"
        
        # Test serialization
        data = link.to_dict()
        assert data['original_url'] == "https://www.aliexpress.com/item/123.html"
        assert data['tracking_id'] == "test_tracking"
    
    def test_product_search_response_creation(self):
        """Test ProductSearchResponse creation and serialization."""
        products = [
            ProductResponse(
                product_id="1",
                product_title="Product 1",
                product_url="https://example.com/1",
                price="10.00",
                currency="USD"
            ),
            ProductResponse(
                product_id="2",
                product_title="Product 2",
                product_url="https://example.com/2",
                price="20.00",
                currency="USD"
            )
        ]
        
        search_response = ProductSearchResponse(
            products=products,
            total_record_count=100,
            current_page=1,
            page_size=20
        )
        
        assert len(search_response.products) == 2
        assert search_response.total_record_count == 100
        assert search_response.current_page == 1
        assert search_response.page_size == 20
        
        # Test serialization
        data = search_response.to_dict()
        assert len(data['products']) == 2
        assert data['total_record_count'] == 100
        assert data['current_page'] == 1
        assert data['page_size'] == 20
    
    def test_hot_product_response_creation(self):
        """Test HotProductResponse creation and serialization."""
        products = [
            ProductResponse(
                product_id="1",
                product_title="Hot Product",
                product_url="https://example.com/hot",
                price="15.00",
                currency="USD"
            )
        ]
        
        hot_response = HotProductResponse(
            products=products,
            total_count=50
        )
        
        assert len(hot_response.products) == 1
        assert hot_response.total_count == 50
        
        # Test serialization
        data = hot_response.to_dict()
        assert len(data['products']) == 1
        assert data['total_count'] == 50
    
    def test_service_response_success(self):
        """Test ServiceResponse success creation."""
        test_data = {"message": "Success"}
        response = ServiceResponse.success_response(
            data=test_data,
            metadata={"custom": "metadata"}
        )
        
        assert response.success is True
        assert response.data == test_data
        assert response.error is None
        assert "custom" in response.metadata
        assert "request_id" in response.metadata
        assert "timestamp" in response.metadata
        
        # Test serialization
        data = response.to_dict()
        assert data['success'] is True
        assert data['data'] == test_data
        assert 'error' not in data
        assert data['metadata']['custom'] == "metadata"
    
    def test_service_response_error(self):
        """Test ServiceResponse error creation."""
        error_message = "Something went wrong"
        response = ServiceResponse.error_response(
            error=error_message,
            metadata={"error_code": "E001"}
        )
        
        assert response.success is False
        assert response.data is None
        assert response.error == error_message
        assert "error_code" in response.metadata
        assert "request_id" in response.metadata
        
        # Test serialization
        data = response.to_dict()
        assert data['success'] is False
        assert data['error'] == error_message
        assert 'data' not in data
        assert data['metadata']['error_code'] == "E001"
    
    def test_service_response_with_model_data(self):
        """Test ServiceResponse with model data."""
        category = CategoryResponse(
            category_id="123",
            category_name="Test Category"
        )
        
        response = ServiceResponse.success_response(data=category)
        
        # Test serialization handles model data
        data = response.to_dict()
        assert data['success'] is True
        assert data['data']['category_id'] == "123"
        assert data['data']['category_name'] == "Test Category"
    
    def test_service_response_with_list_data(self):
        """Test ServiceResponse with list of models."""
        categories = [
            CategoryResponse(category_id="1", category_name="Cat 1"),
            CategoryResponse(category_id="2", category_name="Cat 2")
        ]
        
        response = ServiceResponse.success_response(data=categories)
        
        # Test serialization handles list of models
        data = response.to_dict()
        assert data['success'] is True
        assert len(data['data']) == 2
        assert data['data'][0]['category_id'] == "1"
        assert data['data'][1]['category_id'] == "2"