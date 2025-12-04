"""Unit tests for EnhancedAliExpressService with smart search functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.services.enhanced_aliexpress_service import (
    EnhancedAliExpressService,
    SmartSearchResponse,
    ProductWithAffiliateResponse
)
from src.services.cache_config import CacheConfig
from src.models.responses import ProductResponse, ProductSearchResponse
from src.utils.config import Config


@pytest.fixture
def test_config():
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
def test_cache_config():
    """Create a test cache configuration with caching disabled for unit tests."""
    return CacheConfig(
        enable_redis_cache=False,
        enable_database_cache=False,
        enable_memory_cache=True,
        search_results_ttl=3600,
        affiliate_links_ttl=86400,
        product_metadata_ttl=7200
    )


@pytest.fixture
def mock_cache_service():
    """Create a mock cache service."""
    cache_service = AsyncMock()
    cache_service.get_cached_search_result = AsyncMock(return_value=None)
    cache_service.cache_search_result = AsyncMock()
    cache_service.get_cached_affiliate_links = AsyncMock(return_value=([], []))
    cache_service.cache_affiliate_links = AsyncMock()
    cache_service.get_cache_stats = Mock(return_value={
        'hit_rate_percentage': 0,
        'api_calls_saved': 0
    })
    return cache_service


@pytest.fixture
def sample_products():
    """Create sample product responses."""
    return [
        ProductResponse(
            product_id="1005001",
            product_title="Test Product 1",
            product_url="https://www.aliexpress.com/item/1005001.html",
            price="29.99",
            currency="USD",
            image_url="https://example.com/image1.jpg",
            commission_rate="5.0"
        ),
        ProductResponse(
            product_id="1005002",
            product_title="Test Product 2",
            product_url="https://www.aliexpress.com/item/1005002.html",
            price="39.99",
            currency="USD",
            image_url="https://example.com/image2.jpg",
            commission_rate="6.0"
        )
    ]


@pytest.fixture
def enhanced_service(test_config, test_cache_config, mock_cache_service):
    """Create an enhanced AliExpress service with mocked cache."""
    service = EnhancedAliExpressService(test_config, test_cache_config)
    service.cache_service = mock_cache_service
    return service


class TestSmartProductSearch:
    """Test suite for smart_product_search method."""
    
    @pytest.mark.asyncio
    async def test_cache_miss_initializes_variables_correctly(
        self, enhanced_service, sample_products
    ):
        """
        Test that affiliate_links_cached is properly initialized in cache miss scenario.
        This is the core bug fix test - ensures no NameError occurs.
        """
        # Mock the parent class get_products method
        mock_search_result = ProductSearchResponse(
            products=sample_products,
            total_record_count=2,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            # Execute smart search with cache miss
            result = await enhanced_service.smart_product_search(
                keywords="test",
                page_no=1,
                page_size=20
            )
            
            # Verify the response is valid
            assert isinstance(result, SmartSearchResponse)
            assert result.cache_hit is False
            
            # Verify metrics are properly initialized (the bug fix)
            assert result.affiliate_links_cached == 0  # Should be 0 in cache miss
            assert result.affiliate_links_generated == 2  # Should match product count
            assert result.api_calls_saved == 0  # Should be 0 in cache miss (we made the call)
            
            # Verify products are present
            assert len(result.products) == 2
            assert all(isinstance(p, ProductWithAffiliateResponse) for p in result.products)
    
    @pytest.mark.asyncio
    async def test_cache_miss_with_no_products(self, enhanced_service):
        """Test cache miss scenario when no products are returned."""
        # Mock empty search result
        mock_search_result = ProductSearchResponse(
            products=[],
            total_record_count=0,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            result = await enhanced_service.smart_product_search(
                keywords="nonexistent",
                page_no=1,
                page_size=20
            )
            
            # Verify metrics are correct even with no products
            assert result.affiliate_links_cached == 0
            assert result.affiliate_links_generated == 0
            assert result.api_calls_saved == 0
            assert len(result.products) == 0
    
    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_data(
        self, enhanced_service, sample_products, mock_cache_service
    ):
        """Test that cache hit scenario works correctly."""
        # Mock cache hit
        cached_data = {
            'products': sample_products,
            'total_record_count': 2,
            'cached_at': datetime.utcnow()
        }
        mock_cache_service.get_cached_search_result = AsyncMock(return_value=cached_data)
        
        result = await enhanced_service.smart_product_search(
            keywords="test",
            page_no=1,
            page_size=20
        )
        
        # Verify cache hit
        assert result.cache_hit is True
        assert result.api_calls_saved == 1  # Saved the search API call
        assert len(result.products) == 2
        
        # Verify get_products was NOT called (cache hit)
        with patch.object(enhanced_service, 'get_products') as mock_get_products:
            await enhanced_service.smart_product_search(
                keywords="test",
                page_no=1,
                page_size=20
            )
            mock_get_products.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_force_refresh_bypasses_cache(
        self, enhanced_service, sample_products, mock_cache_service
    ):
        """Test that force_refresh parameter bypasses cache."""
        # Mock cache with data
        cached_data = {
            'products': sample_products,
            'total_record_count': 2,
            'cached_at': datetime.utcnow()
        }
        mock_cache_service.get_cached_search_result = AsyncMock(return_value=cached_data)
        
        # Mock fresh API call
        mock_search_result = ProductSearchResponse(
            products=sample_products,
            total_record_count=2,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            result = await enhanced_service.smart_product_search(
                keywords="test",
                page_no=1,
                page_size=20,
                force_refresh=True
            )
            
            # Verify cache was bypassed
            assert result.cache_hit is False
            assert result.affiliate_links_cached == 0
            assert result.api_calls_saved == 0
    
    @pytest.mark.asyncio
    async def test_metric_accuracy_with_multiple_products(
        self, enhanced_service
    ):
        """Test that metrics are accurate with various product counts."""
        for product_count in [1, 5, 10, 20]:
            products = [
                ProductResponse(
                    product_id=f"100500{i}",
                    product_title=f"Test Product {i}",
                    product_url=f"https://www.aliexpress.com/item/100500{i}.html",
                    price="29.99",
                    currency="USD"
                )
                for i in range(product_count)
            ]
            
            mock_search_result = ProductSearchResponse(
                products=products,
                total_record_count=product_count,
                current_page=1,
                page_size=20
            )
            
            with patch.object(
                enhanced_service, 'get_products', return_value=mock_search_result
            ):
                result = await enhanced_service.smart_product_search(
                    keywords="test",
                    page_no=1,
                    page_size=20
                )
                
                # Verify metrics match product count
                assert result.affiliate_links_generated == product_count
                assert result.affiliate_links_cached == 0
                assert len(result.products) == product_count
    
    @pytest.mark.asyncio
    async def test_response_time_tracking(self, enhanced_service, sample_products):
        """Test that response time is tracked correctly."""
        mock_search_result = ProductSearchResponse(
            products=sample_products,
            total_record_count=2,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            result = await enhanced_service.smart_product_search(
                keywords="test",
                page_no=1,
                page_size=20
            )
            
            # Verify response time is tracked (may be 0 in fast mocked tests)
            assert result.response_time_ms >= 0
            assert isinstance(result.response_time_ms, float)
    
    @pytest.mark.asyncio
    async def test_search_params_filtering(self, enhanced_service, sample_products):
        """Test that None values are filtered from search params."""
        mock_search_result = ProductSearchResponse(
            products=sample_products,
            total_record_count=2,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            result = await enhanced_service.smart_product_search(
                keywords="test",
                category_id=None,  # Should be filtered out
                max_sale_price=None,  # Should be filtered out
                min_sale_price=None,  # Should be filtered out
                page_no=1,
                page_size=20
            )
            
            # Verify search completed successfully
            assert isinstance(result, SmartSearchResponse)
            assert len(result.products) == 2
    
    @pytest.mark.asyncio
    async def test_product_with_affiliate_response_structure(
        self, enhanced_service, sample_products
    ):
        """Test that ProductWithAffiliateResponse has correct structure."""
        mock_search_result = ProductSearchResponse(
            products=sample_products,
            total_record_count=2,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            result = await enhanced_service.smart_product_search(
                keywords="test",
                page_no=1,
                page_size=20
            )
            
            # Verify product structure
            for product in result.products:
                assert hasattr(product, 'product_id')
                assert hasattr(product, 'product_title')
                assert hasattr(product, 'product_url')
                assert hasattr(product, 'affiliate_url')
                assert hasattr(product, 'affiliate_status')
                assert product.affiliate_status == "auto_generated"
                assert product.generated_at is not None
    
    @pytest.mark.asyncio
    async def test_to_dict_serialization(self, enhanced_service, sample_products):
        """Test that SmartSearchResponse can be serialized to dict."""
        mock_search_result = ProductSearchResponse(
            products=sample_products,
            total_record_count=2,
            current_page=1,
            page_size=20
        )
        
        with patch.object(
            enhanced_service, 'get_products', return_value=mock_search_result
        ):
            result = await enhanced_service.smart_product_search(
                keywords="test",
                page_no=1,
                page_size=20
            )
            
            # Verify serialization
            result_dict = result.to_dict()
            assert isinstance(result_dict, dict)
            assert 'products' in result_dict
            assert 'performance_metrics' in result_dict
            assert 'affiliate_links_cached' in result_dict['performance_metrics']
            assert 'affiliate_links_generated' in result_dict['performance_metrics']
            assert 'api_calls_saved' in result_dict['performance_metrics']


class TestSmartSearchResponseDataclass:
    """Test suite for SmartSearchResponse dataclass."""
    
    def test_default_values(self):
        """Test that SmartSearchResponse has correct default values."""
        response = SmartSearchResponse(
            products=[],
            total_record_count=0,
            current_page=1,
            page_size=20
        )
        
        # Verify defaults
        assert response.cache_hit is False
        assert response.cached_at is None
        assert response.affiliate_links_cached == 0
        assert response.affiliate_links_generated == 0
        assert response.api_calls_saved == 0
        assert response.response_time_ms == 0
    
    def test_custom_values(self):
        """Test that SmartSearchResponse accepts custom values."""
        now = datetime.utcnow()
        response = SmartSearchResponse(
            products=[],
            total_record_count=10,
            current_page=2,
            page_size=20,
            cache_hit=True,
            cached_at=now,
            affiliate_links_cached=5,
            affiliate_links_generated=3,
            api_calls_saved=2,
            response_time_ms=123.45
        )
        
        # Verify custom values
        assert response.cache_hit is True
        assert response.cached_at == now
        assert response.affiliate_links_cached == 5
        assert response.affiliate_links_generated == 3
        assert response.api_calls_saved == 2
        assert response.response_time_ms == 123.45


class TestProductWithAffiliateResponse:
    """Test suite for ProductWithAffiliateResponse dataclass."""
    
    def test_default_affiliate_status(self):
        """Test that ProductWithAffiliateResponse has correct default status."""
        product = ProductWithAffiliateResponse(
            product_id="123",
            product_title="Test",
            product_url="https://example.com",
            price="10.00",
            currency="USD"
        )
        
        assert product.affiliate_status == "not_requested"
        assert product.affiliate_url is None
        assert product.affiliate_error is None
    
    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all relevant fields."""
        now = datetime.utcnow()
        product = ProductWithAffiliateResponse(
            product_id="123",
            product_title="Test",
            product_url="https://example.com",
            price="10.00",
            currency="USD",
            affiliate_url="https://affiliate.example.com",
            affiliate_status="generated",
            generated_at=now
        )
        
        product_dict = product.to_dict()
        assert 'product_id' in product_dict
        assert 'affiliate_url' in product_dict
        assert 'affiliate_status' in product_dict
        assert 'affiliate_generated_at' in product_dict
