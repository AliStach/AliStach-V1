# Development Setup Guide

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- AliExpress API credentials

## Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/AliStach/AliStach-V1.git
cd AliStach-V1
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
ALIEXPRESS_APP_KEY=your_app_key
ALIEXPRESS_APP_SECRET=your_app_secret

# Optional:
ALIEXPRESS_TRACKING_ID=dev_tracking
LOG_LEVEL=DEBUG
```

### 5. Verify Setup
```bash
# Run tests
python -m pytest

# Start development server
python -m src.api.main
```

## Development Tools

### Code Formatting
```bash
# Format code with Black
black src tests

# Check formatting
black --check src tests
```

### Linting
```bash
# Lint with Ruff
ruff check src tests

# Auto-fix issues
ruff check --fix src tests
```

### Type Checking
```bash
# Check types with mypy
mypy src
```

### Testing
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_config.py

# Run with verbose output
python -m pytest -v
```

## IDE Setup

### VS Code

Install recommended extensions:
- Python
- Pylance
- Python Test Explorer
- GitLens

Settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Open project
2. Configure Python interpreter (venv)
3. Enable pytest as test runner
4. Configure Black as formatter

## Running the Application

### Development Server
```bash
# With auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python module
python -m src.api.main
```

### Access Points
- API: http://localhost:8000/api/
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Database Setup

### SQLite Databases
Automatically created on first run:
- `data/cache.db` - Cache storage
- `data/audit.db` - Audit logs

### Reset Databases
```bash
rm data/*.db
# Restart application to recreate
```

## Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001

# Or kill process using port 8000
# Windows: netstat -ano | findstr :8000
# Linux/Mac: lsof -ti:8000 | xargs kill
```

### Module Not Found
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

*Last Updated: December 4, 2025*
