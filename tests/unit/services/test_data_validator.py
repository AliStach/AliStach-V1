"""Unit tests for DataValidator."""

import pytest
from src.services.data_validator import ProductDataValidator, SearchResultValidator
from src.models.responses import ProductResponse


class TestProductDataValidator:
    """Test ProductDataValidator class."""
    
    @pytest.fixture
    def valid_product(self):
        """Create a valid product for testing."""
        return ProductResponse(
            product_id="1005001",
            product_title="Test Product Title",
            product_url="https://www.aliexpress.com/item/1005001.html",
            price="29.99",
            currency="USD",
            image_url="https://example.com/image.jpg",
            commission_rate="5.0%"
        )
    
    def test_validate_valid_product(self, valid_product):
        """Test validation of valid product."""
        is_valid, issues = ProductDataValidator.validate_product(valid_product)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_missing_product_id(self, valid_product):
        """Test validation with missing product ID."""
        valid_product.product_id = None
        
        is_valid, issues = ProductDataValidator.validate_product(valid_product)
        
        assert is_valid is False
        assert any("product_id" in issue.lower() for issue in issues)
    
    def test_validate_short_title(self, valid_product):
        """Test validation with short title."""
        valid_product.product_title = "ABC"
        
        is_valid, issues = ProductDataValidator.validate_product(valid_product)
        
        assert is_valid is False
        assert any("title too short" in issue.lower() for issue in issues)
    
    def test_validate_invalid_url(self, valid_product):
        """Test validation with invalid URL."""
        valid_product.product_url = "not-a-url"
        
        is_valid, issues = ProductDataValidator.validate_product(valid_product)
        
        assert is_valid is False
        assert any("url" in issue.lower() for issue in issues)
    
    def test_validate_invalid_price(self, valid_product):
        """Test validation with invalid price."""
        valid_product.price = "invalid"
        
        is_valid, issues = ProductDataValidator.validate_product(valid_product)
        
        assert is_valid is False
        assert any("price" in issue.lower() for issue in issues)
    
    def test_validate_invalid_currency(self, valid_product):
        """Test validation with invalid currency."""
        valid_product.currency = "XXX"
        
        is_valid, issues = ProductDataValidator.validate_product(valid_product)
        
        assert is_valid is False
        assert any("currency" in issue.lower() for issue in issues)
    
    def test_sanitize_product(self, valid_product):
        """Test product sanitization."""
        valid_product.product_title = "  Test   Product  "
        valid_product.currency = "usd"
        valid_product.price = "29.9"
        
        sanitized = ProductDataValidator.sanitize_product(valid_product)
        
        assert sanitized.product_title == "Test Product"
        assert sanitized.currency == "USD"
        assert sanitized.price == "29.90"
    
    def test_validate_and_sanitize(self, valid_product):
        """Test combined validation and sanitization."""
        valid_product.product_title = "  Test Product  "
        
        sanitized, is_valid, issues = ProductDataValidator.validate_and_sanitize(valid_product)
        
        assert is_valid is True
        assert sanitized.product_title == "Test Product"
    
    def test_filter_valid_products(self):
        """Test filtering valid products."""
        products = [
            ProductResponse(
                product_id="1005001",
                product_title="Valid Product",
                product_url="https://example.com/1",
                price="29.99",
                currency="USD"
            ),
            ProductResponse(
                product_id="",  # Invalid
                product_title="Invalid Product",
                product_url="https://example.com/2",
                price="19.99",
                currency="USD"
            ),
            ProductResponse(
                product_id="1005003",
                product_title="Another Valid",
                product_url="https://example.com/3",
                price="39.99",
                currency="USD"
            )
        ]
        
        valid_products, valid_count, invalid_count = ProductDataValidator.filter_valid_products(
            products,
            log_invalid=False
        )
        
        assert valid_count == 2
        assert invalid_count == 1
        assert len(valid_products) == 2
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert ProductDataValidator._is_valid_url("https://www.aliexpress.com/item/123.html")
        assert ProductDataValidator._is_valid_url("http://example.com")
        assert not ProductDataValidator._is_valid_url("not-a-url")
        assert not ProductDataValidator._is_valid_url("")
        assert not ProductDataValidator._is_valid_url(None)


class TestSearchResultValidator:
    """Test SearchResultValidator class."""
    
    def test_deduplicate_products(self):
        """Test product deduplication."""
        products = [
            ProductResponse(
                product_id="1005001",
                product_title="Product 1",
                product_url="https://example.com/1",
                price="29.99",
                currency="USD"
            ),
            ProductResponse(
                product_id="1005001",  # Duplicate
                product_title="Product 1 Again",
                product_url="https://example.com/1",
                price="29.99",
                currency="USD"
            ),
            ProductResponse(
                product_id="1005002",
                product_title="Product 2",
                product_url="https://example.com/2",
                price="39.99",
                currency="USD"
            )
        ]
        
        unique = SearchResultValidator.deduplicate_products(products)
        
        assert len(unique) == 2
        assert unique[0].product_id == "1005001"
        assert unique[1].product_id == "1005002"
    
    def test_apply_quality_filters_commission_rate(self):
        """Test quality filtering by commission rate."""
        products = [
            ProductResponse(
                product_id="1005001",
                product_title="High Commission",
                product_url="https://example.com/1",
                price="29.99",
                currency="USD",
                commission_rate="8.0%"
            ),
            ProductResponse(
                product_id="1005002",
                product_title="Low Commission",
                product_url="https://example.com/2",
                price="39.99",
                currency="USD",
                commission_rate="3.0%"
            )
        ]
        
        filtered = SearchResultValidator.apply_quality_filters(
            products,
            min_commission_rate=5.0
        )
        
        assert len(filtered) == 1
        assert filtered[0].product_id == "1005001"
    
    def test_apply_quality_filters_require_image(self):
        """Test quality filtering requiring images."""
        products = [
            ProductResponse(
                product_id="1005001",
                product_title="With Image",
                product_url="https://example.com/1",
                price="29.99",
                currency="USD",
                image_url="https://example.com/image.jpg"
            ),
            ProductResponse(
                product_id="1005002",
                product_title="No Image",
                product_url="https://example.com/2",
                price="39.99",
                currency="USD",
                image_url=None
            )
        ]
        
        filtered = SearchResultValidator.apply_quality_filters(
            products,
            require_image=True
        )
        
        assert len(filtered) == 1
        assert filtered[0].product_id == "1005001"
