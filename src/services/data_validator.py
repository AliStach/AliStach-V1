"""Data validation and sanitization service for API responses."""

import logging
import re
from typing import Optional, Tuple, List
from ..models.responses import ProductResponse

logger = logging.getLogger(__name__)

class ProductDataValidator:
    """
    Validate and sanitize product data from AliExpress API.
    
    Ensures data quality and consistency before returning to clients.
    """
    
    # Valid currency codes
    VALID_CURRENCIES = ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'BRL', 'RUB', 'JPY', 'CNY']
    
    # Price limits (in USD equivalent)
    MIN_PRICE = 0.01
    MAX_PRICE = 1000000.0
    
    # Title length limits
    MIN_TITLE_LENGTH = 5
    MAX_TITLE_LENGTH = 500
    
    @classmethod
    def validate_product(cls, product: ProductResponse) -> Tuple[bool, List[str]]:
        """
        Validate product data quality.
        
        Args:
            product: Product response to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Required field validation
        if not product.product_id:
            issues.append("Missing product_id")
        elif not isinstance(product.product_id, str) or len(product.product_id) < 5:
            issues.append(f"Invalid product_id format: {product.product_id}")
        
        # Title validation
        if not product.product_title:
            issues.append("Missing product_title")
        elif len(product.product_title) < cls.MIN_TITLE_LENGTH:
            issues.append(f"Product title too short: {len(product.product_title)} chars")
        elif len(product.product_title) > cls.MAX_TITLE_LENGTH:
            issues.append(f"Product title too long: {len(product.product_title)} chars")
        
        # URL validation
        if not product.product_url:
            issues.append("Missing product_url")
        elif not cls._is_valid_url(product.product_url):
            issues.append(f"Invalid product_url format: {product.product_url}")
        
        # Price validation
        try:
            price = float(product.price)
            if price < cls.MIN_PRICE:
                issues.append(f"Price too low: {price}")
            elif price > cls.MAX_PRICE:
                issues.append(f"Price suspiciously high: {price}")
        except (ValueError, TypeError) as e:
            logger.warning(
                "Invalid price format during validation",
                extra={
                    "product_id": product.product_id,
                    "price": product.price,
                    "error_type": type(e).__name__
                }
            )
            issues.append(f"Invalid price format: {product.price}")
        
        # Currency validation
        if product.currency:
            if product.currency.upper() not in cls.VALID_CURRENCIES:
                issues.append(f"Invalid currency code: {product.currency}")
        else:
            issues.append("Missing currency")
        
        # Image URL validation (optional but should be valid if present)
        if product.image_url and not cls._is_valid_url(product.image_url):
            issues.append(f"Invalid image_url format: {product.image_url}")
        
        # Commission rate validation (optional)
        if product.commission_rate:
            try:
                rate = float(product.commission_rate.rstrip('%'))
                if rate < 0 or rate > 50:
                    issues.append(f"Suspicious commission rate: {product.commission_rate}")
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(
                    "Invalid commission rate format during validation",
                    extra={
                        "product_id": product.product_id,
                        "commission_rate": product.commission_rate,
                        "error_type": type(e).__name__
                    }
                )
                issues.append(f"Invalid commission_rate format: {product.commission_rate}")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @classmethod
    def sanitize_product(cls, product: ProductResponse) -> ProductResponse:
        """
        Sanitize product data to ensure consistency.
        
        Args:
            product: Product response to sanitize
            
        Returns:
            Sanitized product response
        """
        # Trim whitespace from strings
        if product.product_title:
            product.product_title = product.product_title.strip()
            # Remove excessive whitespace
            product.product_title = re.sub(r'\s+', ' ', product.product_title)
        
        # Normalize currency code
        if product.currency:
            product.currency = product.currency.upper().strip()
        
        # Ensure price is properly formatted
        try:
            price_float = float(product.price)
            product.price = f"{price_float:.2f}"
        except (ValueError, TypeError) as e:
            logger.warning(
                "Could not format price, using default",
                extra={
                    "product_id": product.product_id,
                    "price": product.price,
                    "error_type": type(e).__name__
                }
            )
            product.price = "0.00"
        
        # Normalize URLs (remove tracking parameters if needed)
        if product.product_url:
            product.product_url = product.product_url.strip()
        
        if product.image_url:
            product.image_url = product.image_url.strip()
        
        # Normalize commission rate
        if product.commission_rate:
            try:
                # Ensure it's in percentage format
                rate = float(product.commission_rate.rstrip('%'))
                product.commission_rate = f"{rate:.1f}%"
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(
                    "Could not normalize commission rate, setting to None",
                    extra={
                        "product_id": product.product_id,
                        "commission_rate": product.commission_rate,
                        "error_type": type(e).__name__
                    }
                )
                product.commission_rate = None
        
        return product
    
    @classmethod
    def validate_and_sanitize(cls, product: ProductResponse) -> Tuple[ProductResponse, bool, List[str]]:
        """
        Validate and sanitize product in one operation.
        
        Args:
            product: Product response to process
            
        Returns:
            Tuple of (sanitized_product, is_valid, issues)
        """
        # First sanitize
        sanitized_product = cls.sanitize_product(product)
        
        # Then validate
        is_valid, issues = cls.validate_product(sanitized_product)
        
        return sanitized_product, is_valid, issues
    
    @classmethod
    def filter_valid_products(
        cls,
        products: List[ProductResponse],
        log_invalid: bool = True
    ) -> Tuple[List[ProductResponse], int, int]:
        """
        Filter list of products, keeping only valid ones.
        
        Args:
            products: List of products to filter
            log_invalid: Whether to log invalid products
            
        Returns:
            Tuple of (valid_products, valid_count, invalid_count)
        """
        valid_products = []
        invalid_count = 0
        
        for product in products:
            sanitized_product, is_valid, issues = cls.validate_and_sanitize(product)
            
            if is_valid:
                valid_products.append(sanitized_product)
            else:
                invalid_count += 1
                if log_invalid:
                    logger.warning(
                        f"Invalid product filtered out: {product.product_id}",
                        extra={
                            'extra_fields': {
                                'product_id': product.product_id,
                                'issues': issues,
                                'product_title': product.product_title[:50] if product.product_title else None
                            }
                        }
                    )
        
        valid_count = len(valid_products)
        
        if invalid_count > 0:
            logger.info(
                f"Product validation complete: {valid_count} valid, {invalid_count} invalid",
                extra={
                    'extra_fields': {
                        'valid_count': valid_count,
                        'invalid_count': invalid_count,
                        'total_count': len(products),
                        'validity_rate': round((valid_count / len(products)) * 100, 2) if products else 0
                    }
                }
            )
        
        return valid_products, valid_count, invalid_count
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """
        Check if URL is valid.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))

class SearchResultValidator:
    """Validate search result quality and apply filters."""
    
    @classmethod
    def deduplicate_products(cls, products: List[ProductResponse]) -> List[ProductResponse]:
        """
        Remove duplicate products based on product_id.
        
        Args:
            products: List of products
            
        Returns:
            Deduplicated list of products
        """
        seen_ids = set()
        unique_products = []
        duplicate_count = 0
        
        for product in products:
            if product.product_id not in seen_ids:
                seen_ids.add(product.product_id)
                unique_products.append(product)
            else:
                duplicate_count += 1
        
        if duplicate_count > 0:
            logger.info(f"Removed {duplicate_count} duplicate products")
        
        return unique_products
    
    @classmethod
    def apply_quality_filters(
        cls,
        products: List[ProductResponse],
        min_commission_rate: Optional[float] = None,
        require_image: bool = False
    ) -> List[ProductResponse]:
        """
        Apply quality filters to products.
        
        Args:
            products: List of products to filter
            min_commission_rate: Minimum commission rate (e.g., 5.0 for 5%)
            require_image: Whether to require image URL
            
        Returns:
            Filtered list of products
        """
        filtered_products = []
        
        for product in products:
            # Check commission rate
            if min_commission_rate is not None and product.commission_rate:
                try:
                    rate = float(product.commission_rate.rstrip('%'))
                    if rate < min_commission_rate:
                        continue
                except (ValueError, TypeError, AttributeError) as e:
                    logger.debug(
                        "Skipping product due to invalid commission rate format",
                        extra={
                            "product_id": product.product_id,
                            "commission_rate": product.commission_rate,
                            "error_type": type(e).__name__
                        }
                    )
                    continue
            
            # Check image requirement
            if require_image and not product.image_url:
                continue
            
            filtered_products.append(product)
        
        removed_count = len(products) - len(filtered_products)
        if removed_count > 0:
            logger.info(f"Quality filters removed {removed_count} products")
        
        return filtered_products
