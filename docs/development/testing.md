# Testing Guide

## Overview

The project uses pytest for testing with comprehensive unit, integration, and end-to-end tests.

## Test Structure

```
tests/
├── unit/              # Unit tests (fast, isolated)
│   ├── api/
│   ├── middleware/
│   ├── models/
│   ├── services/
│   └── utils/
├── integration/       # Integration tests
├── e2e/              # End-to-end tests
├── fixtures/         # Test fixtures
└── conftest.py       # Pytest configuration
```

## Running Tests

### All Tests
```bash
python -m pytest
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# Specific test file
python -m pytest tests/unit/test_config.py

# Specific test function
python -m pytest tests/unit/test_config.py::test_config_from_env
```

### With Coverage
```bash
# Generate coverage report
python -m pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html
```

### Test Markers
```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Skip slow tests
python -m pytest -m "not slow"
```

## Writing Tests

### Unit Test Example
```python
# tests/unit/services/test_cache_service.py

import pytest
from src.services.cache_service import CacheService

class TestCacheService:
    """Test cache service functionality."""
    
    def test_cache_set_and_get(self):
        """Test setting and getting cache values."""
        cache = CacheService()
        cache.set("test_key", "test_value", ttl=60)
        
        result = cache.get("test_key")
        assert result == "test_value"
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        cache = CacheService()
        cache.set("test_key", "test_value", ttl=0)
        
        result = cache.get("test_key")
        assert result is None
```

### Integration Test Example
```python
# tests/integration/test_api_endpoints.py

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test API endpoint integration."""
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_product_search(self):
        """Test product search endpoint."""
        response = client.post(
            "/api/products/search",
            json={"keywords": "test", "page_size": 10}
        )
        assert response.status_code == 200
        assert "data" in response.json()
```

### Using Fixtures
```python
# tests/conftest.py

import pytest
from src.utils.config import Config
from src.services.aliexpress_service import AliExpressService

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return Config(
        aliexpress_app_key="test_key",
        aliexpress_app_secret="test_secret",
        aliexpress_tracking_id="test_tracking"
    )

@pytest.fixture
def mock_service(test_config):
    """Provide mocked service."""
    return AliExpressService(test_config)

# Use in tests
def test_with_fixture(mock_service):
    result = mock_service.get_categories()
    assert result is not None
```

## Test Coverage Goals

- **Overall**: 90%+
- **Unit Tests**: 95%+
- **Integration Tests**: 85%+
- **Critical Paths**: 100%

## Mocking

### Mock External APIs
```python
from unittest.mock import patch, MagicMock

@patch('src.services.aliexpress_service.AliexpressApi')
def test_api_call(mock_api):
    """Test with mocked API."""
    mock_api.return_value.execute.return_value = {"success": True}
    
    service = AliExpressService(config)
    result = service.search_products(keywords="test")
    
    assert result.success
    mock_api.assert_called_once()
```

### Mock Database
```python
@pytest.fixture
def mock_db():
    """Provide in-memory database."""
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    return engine
```

## Continuous Integration

Tests run automatically on:
- Push to main branch
- Pull requests
- Manual trigger

### GitHub Actions
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=src
```

## Best Practices

1. **Test Naming**: Use descriptive names
   - `test_search_products_with_valid_keywords`
   - `test_cache_returns_none_when_expired`

2. **Arrange-Act-Assert**: Structure tests clearly
   ```python
   def test_example():
       # Arrange
       service = create_service()
       
       # Act
       result = service.do_something()
       
       # Assert
       assert result == expected
   ```

3. **One Assertion Per Test**: Focus on single behavior

4. **Use Fixtures**: Reuse common setup

5. **Mock External Dependencies**: Keep tests fast and reliable

6. **Test Edge Cases**: Not just happy path

---

*Last Updated: December 4, 2025*
