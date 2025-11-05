"""Test configuration and fixtures for AliExpress API tests."""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
import httpx

from src.api.main import app
from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config() -> Config:
    """Create a test configuration."""
    return Config(
        app_key="test_app_key",
        app_secret="test_app_secret",
        tracking_id="test_tracking",
        language="EN",
        currency="USD",
        api_host="127.0.0.1",
        api_port=8000,
        log_level="DEBUG"
    )


@pytest.fixture
def mock_aliexpress_api():
    """Create a mock AliExpress API client."""
    mock_api = Mock()
    
    # Mock category responses
    mock_category = Mock()
    mock_category.category_id = "123"
    mock_category.category_name = "Electronics"
    mock_api.get_parent_categories.return_value = [mock_category]
    mock_api.get_child_categories.return_value = [mock_category]
    
    # Mock product responses
    mock_product = Mock()
    mock_product.product_id = "1005003091506814"
    mock_product.product_title = "Test Product"
    mock_product.product_detail_url = "https://www.aliexpress.com/item/1005003091506814.html"
    mock_product.target_sale_price = "29.99"
    mock_product.target_sale_price_currency = "USD"
    mock_product.product_main_image_url = "https://example.com/image.jpg"
    mock_product.commission_rate = "5.0"
    
    mock_products_result = Mock()
    mock_products_result.products = [mock_product]
    mock_products_result.total_record_count = 1
    mock_api.get_products.return_value = mock_products_result
    
    # Mock product details response
    mock_details_result = Mock()
    mock_details_result.products = [mock_product]
    mock_api.get_products_details.return_value = mock_details_result
    
    # Mock affiliate link responses
    mock_link = Mock()
    mock_link.source_value = "https://www.aliexpress.com/item/1005003091506814.html"
    mock_link.promotion_link = "https://s.click.aliexpress.com/e/_test_affiliate_link"
    mock_link.commission_rate = "5.0"
    
    mock_links_result = Mock()
    mock_links_result.promotion_links = [mock_link]
    mock_api.get_affiliate_links.return_value = mock_links_result
    
    return mock_api


@pytest.fixture
def mock_aliexpress_service(test_config, mock_aliexpress_api):
    """Create a mock AliExpress service."""
    service = AliExpressService(test_config)
    service.api = mock_aliexpress_api
    return service


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_test_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_id": "1005003091506814",
        "product_title": "Wireless Bluetooth Headphones",
        "product_url": "https://www.aliexpress.com/item/1005003091506814.html",
        "price": "29.99",
        "currency": "USD",
        "image_url": "https://example.com/image.jpg",
        "commission_rate": "5.0"
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        "category_id": "123",
        "category_name": "Electronics"
    }


@pytest.fixture
def sample_affiliate_link_data():
    """Sample affiliate link data for testing."""
    return {
        "original_url": "https://www.aliexpress.com/item/1005003091506814.html",
        "affiliate_url": "https://s.click.aliexpress.com/e/_test_affiliate_link",
        "tracking_id": "test_tracking",
        "commission_rate": "5.0"
    }