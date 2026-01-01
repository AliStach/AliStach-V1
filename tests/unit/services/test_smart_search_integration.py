"""Unit tests for smart search capability detection and fallback functionality."""

import pytest
from unittest.mock import Mock, AsyncMock
from src.services.service_capability_detector import ServiceCapabilityDetector
from src.services.smart_search_fallback import SmartSearchFallback
from src.services.service_factory import ServiceFactory, ServiceWithMetadata, ServiceCapabilities
from src.services.aliexpress_service import AliExpressService
from src.models.responses import ProductResponse, ProductSearchResponse
from datetime import datetime


class TestServiceCapabilityDetector:
    """Test ServiceCapabilityDetector functionality."""
    
    def test_has_smart_search_with_enhanced_service(self):
        """Test detection of smart_product_search method on enhanced service."""
        mock_service = Mock()
        mock_service.smart_product_search = AsyncMock()
        
        assert ServiceCapabilityDetector.has_smart_search(mock_service) is True
    
    def test_has_smart_search_with_basic_service(self):
        """Test detection when smart_product_search method is missing."""
        mock_service = Mock(spec=AliExpressService)
        # Ensure smart_product_search doesn't exist
        if hasattr(mock_service, 'smart_product_search'):
            delattr(mock_service, 'smart_product_search')
        
        assert ServiceCapabilityDetector.has_smart_search(mock_service) is False
    
    def test_get_service_type_enhanced(self):
        """Test service type detection for enhanced service."""
        mock_service = Mock()
        mock_service.__class__.__name__ = 'EnhancedAliExpressService'
        
        assert ServiceCapabilityDetector.get_service_type(mock_service) == 'enhanced'
    
    def test_get_service_type_basic(self):
        """Test service type detection for basic service."""
        mock_service = Mock()
        mock_service.__class__.__name__ = 'AliExpressService'
        
        assert ServiceCapabilityDetector.get_service_type(mock_service) == 'basic'
    
    def test_get_service_type_unknown(self):
        """Test service type detection for unknown service."""
        mock_service = Mock()
        mock_service.__class__.__name__ = 'UnknownService'
        
        assert ServiceCapabilityDetector.get_service_type(mock_service) == 'unknown'
    
    def test_get_capabilities_enhanced_service(self):
        """Test capability detection for enhanced service."""
        mock_service = Mock()
        mock_service.__class__.__name__ = 'EnhancedAliExpressService'
        mock_service.smart_product_search = AsyncMock()
        mock_service.cache_service = Mock()
        mock_service.image_service = Mock()
        mock_service.get_affiliate_links = Mock()
        
        capabilities = ServiceCapabilityDetector.get_capabilities(mock_service)
        
        assert capabilities['has_smart_search'] is True
        assert capabilities['has_caching'] is True
        assert capabilities['has_image_processing'] is True
        assert capabilities['supports_affiliate_links'] is True
        assert capabilities['has_enhanced_features'] is True
    
    def test_get_capabilities_basic_service(self):
        """Test capability detection for basic service."""
        mock_service = Mock(spec=AliExpressService)
        mock_service.__class__.__name__ = 'AliExpressService'
        mock_service.get_affiliate_links = Mock()
        
        # Remove enhanced-only attributes
        for attr in ['smart_product_search', 'cache_service', 'image_service']:
            if hasattr(mock_service, attr):
                delattr(mock_service, attr)
        
        capabilities = ServiceCapabilityDetector.get_capabilities(mock_service)
        
        assert capabilities['has_smart_search'] is False
        assert capabilities['has_caching'] is False
        assert capabilities['has_image_processing'] is False
        assert capabilities['supports_affiliate_links'] is True
        assert capabilities['has_enhanced_features'] is False


class TestSmartSearchFallback:
    """Test SmartSearchFallback functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_basic_service = Mock(spec=AliExpressService)
        self.fallback = SmartSearchFallback(self.mock_basic_service)
        
        # Setup mock product response
        self.mock_product = ProductResponse(
            product_id="123",
            product_title="Test Product",
            product_url="https://example.com/product/123",
            price="10.99",
            currency="USD"
        )
        
        self.mock_search_result = ProductSearchResponse(
            products=[self.mock_product],
            total_record_count=1,
            current_page=1,
            page_size=10
        )
        
        self.mock_basic_service.get_products.return_value = self.mock_search_result
    
    @pytest.mark.asyncio
    async def test_smart_product_search_method_exists(self):
        """Test that fallback provides smart_product_search method."""
        assert hasattr(self.fallback, 'smart_product_search')
        assert callable(getattr(self.fallback, 'smart_product_search'))
    
    @pytest.mark.asyncio
    async def test_smart_product_search_calls_basic_service(self):
        """Test that fallback calls basic service get_products method."""
        await self.fallback.smart_product_search(
            keywords="test",
            category_id="123",
            page_no=1,
            page_size=10
        )
        
        self.mock_basic_service.get_products.assert_called_once()
        call_args = self.mock_basic_service.get_products.call_args
        assert call_args.kwargs['keywords'] == "test"
        assert call_args.kwargs['category_id'] == "123"
        assert call_args.kwargs['page_no'] == 1
        assert call_args.kwargs['page_size'] == 10
    
    @pytest.mark.asyncio
    async def test_smart_product_search_returns_compatible_response(self):
        """Test that fallback returns SmartSearchResponse format."""
        result = await self.fallback.smart_product_search(keywords="test")
        
        # Check that result has SmartSearchResponse structure
        assert hasattr(result, 'products')
        assert hasattr(result, 'total_record_count')
        assert hasattr(result, 'current_page')
        assert hasattr(result, 'page_size')
        assert hasattr(result, 'cache_hit')
        assert hasattr(result, 'affiliate_links_cached')
        assert hasattr(result, 'affiliate_links_generated')
        assert hasattr(result, 'api_calls_saved')
        assert hasattr(result, 'response_time_ms')
        assert hasattr(result, 'service_type')
        assert hasattr(result, 'fallback_used')
        assert hasattr(result, 'enhanced_features_available')
    
    @pytest.mark.asyncio
    async def test_fallback_response_field_initialization(self):
        """Test that all response fields are properly initialized."""
        result = await self.fallback.smart_product_search(keywords="test")
        
        # Check critical fields that caused the original NameError
        assert result.affiliate_links_cached == 0  # Must be initialized
        assert result.affiliate_links_generated >= 0
        assert result.api_calls_saved == 0
        assert isinstance(result.response_time_ms, (int, float))
        assert result.cache_hit is False
        assert result.service_type == "basic"
        assert result.fallback_used is True
        assert result.enhanced_features_available is False
    
    @pytest.mark.asyncio
    async def test_fallback_product_conversion(self):
        """Test that products are converted to ProductWithAffiliateResponse format."""
        result = await self.fallback.smart_product_search(keywords="test")
        
        assert len(result.products) == 1
        product = result.products[0]
        
        # Check that product has affiliate fields
        assert hasattr(product, 'affiliate_url')
        assert hasattr(product, 'affiliate_status')
        assert hasattr(product, 'affiliate_error')
        assert hasattr(product, 'cached_at')
        assert hasattr(product, 'generated_at')
        
        # Check fallback-specific values
        assert product.affiliate_status == "fallback_basic_service"
        assert product.affiliate_url == product.product_url  # Should use original URL
    
    def test_method_delegation(self):
        """Test that other methods are delegated to basic service."""
        # Test that non-smart_product_search methods are delegated
        self.fallback.get_products()
        self.mock_basic_service.get_products.assert_called()
        
        # Test attribute access delegation
        self.mock_basic_service.some_attribute = "test_value"
        assert self.fallback.some_attribute == "test_value"


class TestServiceFactoryWithMetadata:
    """Test ServiceFactory metadata functionality."""
    
    def test_service_capabilities_creation(self):
        """Test ServiceCapabilities dataclass creation."""
        capabilities = ServiceCapabilities(
            has_smart_search=True,
            has_caching=True,
            has_image_processing=False,
            supports_affiliate_links=True,
            environment_type="test"
        )
        
        assert capabilities.has_smart_search is True
        assert capabilities.has_caching is True
        assert capabilities.has_image_processing is False
        assert capabilities.supports_affiliate_links is True
        assert capabilities.environment_type == "test"
    
    def test_service_with_metadata_creation(self):
        """Test ServiceWithMetadata dataclass creation."""
        mock_service = Mock()
        capabilities = ServiceCapabilities(
            has_smart_search=False,
            has_caching=False,
            has_image_processing=False,
            supports_affiliate_links=True,
            environment_type="test"
        )
        
        service_metadata = ServiceWithMetadata(
            service=mock_service,
            capabilities=capabilities,
            service_type="basic",
            created_at=datetime.utcnow()
        )
        
        assert service_metadata.service is mock_service
        assert service_metadata.capabilities is capabilities
        assert service_metadata.service_type == "basic"
        assert isinstance(service_metadata.created_at, datetime)


class TestSmartSearchResponseEnhancements:
    """Test SmartSearchResponse enhancements for fallback support."""
    
    def test_from_basic_search_class_method(self):
        """Test SmartSearchResponse.from_basic_search class method."""
        from src.services.enhanced_aliexpress_service import SmartSearchResponse
        
        # Create mock basic result
        mock_product = ProductResponse(
            product_id="123",
            product_title="Test Product",
            product_url="https://example.com/product/123",
            price="10.99",
            currency="USD"
        )
        
        mock_basic_result = ProductSearchResponse(
            products=[mock_product],
            total_record_count=1,
            current_page=1,
            page_size=10
        )
        
        # Create SmartSearchResponse from basic result
        response = SmartSearchResponse.from_basic_search(mock_basic_result, 150.0)
        
        # Verify all fields are properly initialized
        assert len(response.products) == 1
        assert response.total_record_count == 1
        assert response.current_page == 1
        assert response.page_size == 10
        assert response.cache_hit is False
        assert response.affiliate_links_cached == 0  # Critical: prevents NameError
        assert response.affiliate_links_generated == 1
        assert response.api_calls_saved == 0
        assert response.response_time_ms == 150.0
        assert response.service_type == "basic"
        assert response.fallback_used is True
        assert response.enhanced_features_available is False
    
    def test_to_dict_includes_service_metadata(self):
        """Test that to_dict includes service metadata fields."""
        from src.services.enhanced_aliexpress_service import SmartSearchResponse, ProductWithAffiliateResponse
        
        product = ProductWithAffiliateResponse(
            product_id="123",
            product_title="Test Product",
            product_url="https://example.com/product/123",
            price="10.99",
            currency="USD"
        )
        
        response = SmartSearchResponse(
            products=[product],
            total_record_count=1,
            current_page=1,
            page_size=10,
            service_type="basic",
            fallback_used=True,
            enhanced_features_available=False
        )
        
        result_dict = response.to_dict()
        
        # Check that service metadata is included
        assert "service_metadata" in result_dict
        service_meta = result_dict["service_metadata"]
        assert service_meta["service_type"] == "basic"
        assert service_meta["fallback_used"] is True
        assert service_meta["enhanced_features_available"] is False


class TestProductionSafetyGuarantees:
    """Test that the implementation prevents production issues."""
    
    @pytest.mark.asyncio
    async def test_no_name_error_in_fallback_scenario(self):
        """Test that fallback scenario never causes NameError."""
        mock_basic_service = Mock(spec=AliExpressService)
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
        
        mock_basic_service.get_products.return_value = mock_result
        
        fallback = SmartSearchFallback(mock_basic_service)
        
        # This should never raise NameError
        try:
            result = await fallback.smart_product_search(keywords="test")
            
            # Verify all critical fields exist and are properly typed
            assert hasattr(result, 'affiliate_links_cached')
            assert isinstance(result.affiliate_links_cached, int)
            assert hasattr(result, 'affiliate_links_generated')
            assert isinstance(result.affiliate_links_generated, int)
            assert hasattr(result, 'api_calls_saved')
            assert isinstance(result.api_calls_saved, int)
            
        except NameError as e:
            pytest.fail(f"NameError should never occur in fallback scenario: {e}")
    
    def test_service_capability_detector_safety(self):
        """Test that ServiceCapabilityDetector handles edge cases safely."""
        # Test with None service
        assert ServiceCapabilityDetector.has_smart_search(None) is False
        
        # Test with service missing __class__
        mock_service = Mock()
        del mock_service.__class__
        # Should not crash, should return 'unknown'
        service_type = ServiceCapabilityDetector.get_service_type(mock_service)
        assert service_type in ['unknown', 'basic', 'enhanced']  # Any safe value
    
    def test_attribute_error_prevention(self):
        """Test that missing attributes are handled gracefully."""
        mock_service = Mock()
        
        # Remove all attributes to simulate minimal service
        for attr in ['smart_product_search', 'cache_service', 'image_service', 'get_affiliate_links']:
            if hasattr(mock_service, attr):
                delattr(mock_service, attr)
        
        # Should not raise AttributeError
        capabilities = ServiceCapabilityDetector.get_capabilities(mock_service)
        
        # Should return safe defaults
        assert isinstance(capabilities, dict)
        assert 'has_smart_search' in capabilities
        assert 'has_caching' in capabilities
        assert 'has_image_processing' in capabilities
        assert 'supports_affiliate_links' in capabilities