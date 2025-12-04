# Migration Guide - v1.0 to v2.0

## Overview

This guide helps you migrate from version 1.0 to version 2.0 of the AliExpress Affiliate API Service. Version 2.0 includes comprehensive modernization with improved structure, documentation, and quality.

## Breaking Changes

**Good News**: There are **NO breaking changes** in v2.0!

All API endpoints, configuration options, and functionality remain backward compatible. You can upgrade without modifying your existing code or configuration.

## What's New in v2.0

### 1. Enhanced Project Structure
- Reorganized documentation into dedicated directories
- Improved test organization mirroring src/ structure
- Cleaner root directory

### 2. Comprehensive Documentation
- 20+ new documentation files
- Architecture documentation with diagrams
- Deployment guides for multiple platforms
- Operations runbooks
- Development guidelines

### 3. Quality Improvements
- 100% type annotation coverage
- Standardized exception hierarchy
- Enhanced test fixtures
- Quality gate enforcement

### 4. CI/CD Ready
- GitHub Actions workflows configured
- Pre-commit hooks available
- Docker Compose support
- Quality gate script

## Migration Steps

### Step 1: Update Dependencies

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 2: Review New Configuration Options

New optional environment variables (all backward compatible):

```bash
# Optional: Enable pre-commit hooks
pip install pre-commit
pre-commit install

# Optional: Configure Redis caching
REDIS_URL=redis://localhost:6379
```

### Step 3: Update Development Workflow (Optional)

If you're a developer, consider adopting new tools:

```bash
# Install development tools
pip install -r requirements-dev.txt

# Run quality checks
python tools/quality_gate.py

# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src
```

### Step 4: Review Documentation

Explore the new documentation structure:

- [Architecture Documentation](architecture/) - System design
- [API Documentation](api/) - API reference
- [Deployment Guides](deployment/) - Platform-specific guides
- [Operations Documentation](operations/) - Monitoring and troubleshooting
- [Development Documentation](development/) - Development setup

## Configuration Changes

### Environment Variables

All existing environment variables work as before. New optional variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | None | Optional Redis cache URL |
| `LOG_LEVEL` | INFO | Logging level |
| `CACHE_ENABLED` | true | Enable/disable caching |

### No Changes Required

- API endpoints remain the same
- Request/response formats unchanged
- Authentication methods unchanged
- Rate limiting behavior unchanged

## Testing Your Migration

### 1. Verify Application Starts

```bash
python -m src.api.main
```

Expected output:
```
[ROUTER] Categories router loaded successfully
[ROUTER] Products router loaded successfully
[ROUTER] Affiliate router loaded successfully
[ROUTER] Admin router loaded successfully
```

### 2. Run Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-04T10:30:00Z",
  "version": "2.0.0"
}
```

### 3. Run Tests

```bash
python -m pytest
```

All tests should pass.

### 4. Test API Endpoints

```bash
# Test product search
curl -X POST http://localhost:8000/api/products/search \
  -H "Content-Type: application/json" \
  -d '{"keywords": "test", "page_size": 5}'

# Test categories
curl http://localhost:8000/api/categories
```

## Rollback Procedure

If you need to rollback to v1.0:

```bash
# Checkout previous version
git checkout v1.0.0

# Reinstall dependencies
pip install -r requirements.txt
```

Note: Since there are no breaking changes, rollback should rarely be necessary.

## New Features to Explore

### 1. Quality Gate Script

Run comprehensive quality checks:

```bash
python tools/quality_gate.py
```

### 2. Docker Compose

Run with Docker Compose:

```bash
docker-compose up -d
```

### 3. Pre-commit Hooks

Automatically check code quality before commits:

```bash
pre-commit install
```

### 4. Enhanced Test Fixtures

Use new test data generators:

```python
from tests.fixtures.test_data import generate_product_data

product = generate_product_data(title="Test Product", price=29.99)
```

### 5. Comprehensive Documentation

Access documentation at:
- Local: `docs/README.md`
- Online: https://alistach.vercel.app/docs

## Troubleshooting

### Issue: Import Errors

**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Issue: Tests Failing

**Solution**: Clear cache and reinstall
```bash
rm -rf .pytest_cache __pycache__
pip install -r requirements-dev.txt
pytest
```

### Issue: Application Won't Start

**Solution**: Check environment variables
```bash
# Verify .env file exists
cp .env.example .env
# Edit .env with your credentials
```

## Getting Help

- **Documentation**: Check [docs/README.md](README.md)
- **Troubleshooting**: See [operations/troubleshooting.md](operations/troubleshooting.md)
- **Issues**: Report on [GitHub Issues](https://github.com/AliStach/AliStach-V1/issues)

## Summary

Version 2.0 is a **non-breaking upgrade** that adds:
- ✅ Enhanced documentation
- ✅ Better project structure
- ✅ Quality improvements
- ✅ CI/CD readiness
- ✅ Development tools

**No code changes required** - just pull and enjoy the improvements!

---

**Migration Difficulty**: ⭐ Easy (No breaking changes)  
**Estimated Time**: 5-10 minutes  
**Recommended**: Yes - Significant improvements with zero risk

*Last Updated: December 4, 2025*
