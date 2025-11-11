"""Minimal test to isolate the failing import."""

import sys
import os

# Setup path like Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Testing imports step by step...")
print("=" * 60)

try:
    print("1. Testing FastAPI import...")
    from fastapi import FastAPI
    print("   ✅ FastAPI OK")
except Exception as e:
    print(f"   ❌ FastAPI FAILED: {e}")
    sys.exit(1)

try:
    print("2. Testing src.utils.config...")
    from src.utils.config import Config
    print("   ✅ Config OK")
except Exception as e:
    print(f"   ❌ Config FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. Testing src.utils.logging_config...")
    from src.utils.logging_config import setup_production_logging
    print("   ✅ logging_config OK")
except Exception as e:
    print(f"   ❌ logging_config FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. Testing src.middleware.security...")
    from src.middleware.security import get_security_manager
    print("   ✅ security OK")
except Exception as e:
    print(f"   ❌ security FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. Testing src.middleware.csrf...")
    from src.middleware.csrf import csrf_middleware
    print("   ✅ csrf OK")
except Exception as e:
    print(f"   ❌ csrf FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("6. Testing src.services.aliexpress_service...")
    from src.services.aliexpress_service import AliExpressService
    print("   ✅ aliexpress_service OK")
except Exception as e:
    print(f"   ❌ aliexpress_service FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("7. Testing src.api.main...")
    from src.api.main import app
    print("   ✅ main OK")
    print(f"   App type: {type(app)}")
except Exception as e:
    print(f"   ❌ main FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
print("✅ ALL IMPORTS SUCCESSFUL")
