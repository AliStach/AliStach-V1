# Contributing Guidelines

## Welcome!

Thank you for considering contributing to the AliExpress Affiliate API Service. This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Maintain professional communication

## Getting Started

### 1. Fork and Clone
```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AliStach-V1.git
cd AliStach-V1
```

### 2. Create Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Set Up Development Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
```

## Development Workflow

### 1. Make Changes
- Write clean, readable code
- Follow existing code style
- Add type hints
- Write docstrings

### 2. Add Tests
```bash
# Write tests for new features
# Ensure tests pass
python -m pytest
```

### 3. Format Code
```bash
# Format with Black
black src tests

# Lint with Ruff
ruff check --fix src tests

# Type check with mypy
mypy src
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add new feature"
```

### Commit Message Format
```
<type>: <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Examples**:
```
feat: add image search endpoint
fix: resolve cache expiration issue
docs: update API documentation
test: add unit tests for cache service
```

### 5. Push Changes
```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request
1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template
5. Submit for review

## Pull Request Guidelines

### PR Title
Use same format as commit messages:
```
feat: add image search functionality
```

### PR Description
Include:
- What changes were made
- Why changes were needed
- How to test changes
- Related issues (if any)

### PR Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (Black)
- [ ] Linting passed (Ruff)
- [ ] Type checking passed (mypy)
- [ ] All tests passing
- [ ] No breaking changes (or documented)

## Code Style

### Python Style Guide
- Follow PEP 8
- Use Black for formatting
- Use Ruff for linting
- Add type hints to all functions
- Write docstrings for public APIs

### Example
```python
from typing import List, Optional

def search_products(
    keywords: str,
    page_size: int = 10,
    category_id: Optional[str] = None
) -> List[Product]:
    """
    Search for products with given keywords.
    
    Args:
        keywords: Search keywords
        page_size: Number of results per page
        category_id: Optional category filter
    
    Returns:
        List of matching products
    
    Raises:
        ValidationError: If keywords are invalid
    """
    # Implementation
    pass
```

## Testing Requirements

### Test Coverage
- Minimum 85% overall coverage
- 100% coverage for critical paths
- Unit tests for all new functions
- Integration tests for new endpoints

### Test Structure
```python
class TestFeature:
    """Test feature functionality."""
    
    def test_happy_path(self):
        """Test normal operation."""
        pass
    
    def test_edge_case(self):
        """Test edge case."""
        pass
    
    def test_error_handling(self):
        """Test error handling."""
        pass
```

## Documentation

### Update Documentation
- Update README.md if needed
- Add/update API documentation
- Update architecture docs if needed
- Add examples for new features

### Docstring Format
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain what the function does,
    any important details, and usage examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
        TypeError: When param2 is wrong type
    
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

## Review Process

### What Reviewers Look For
1. Code quality and style
2. Test coverage
3. Documentation completeness
4. Performance implications
5. Security considerations
6. Breaking changes

### Addressing Feedback
- Respond to all comments
- Make requested changes
- Push updates to same branch
- Request re-review when ready

## Release Process

### Version Numbering
Follow Semantic Versioning (semver):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Changelog
Update CHANGELOG.md with:
- Added features
- Changed behavior
- Fixed bugs
- Removed features

## Questions?

- Check existing issues
- Review documentation
- Ask in discussions
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

*Last Updated: December 4, 2025*
