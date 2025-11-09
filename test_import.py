"""Test script to verify imports work correctly before deployment."""

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("Testing imports...")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}...")
print()

# Test 1: Import audit logger
print("1. Testing audit_logger import...")
try:
    from src.middleware.audit_logger import audit_logger
    print("   ✅ audit_logger imported successfully")
    print(f"   Type: {type(audit_logger)}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Import security manager
print("\n2. Testing security manager import...")
try:
    from src.middleware.security import get_security_manager
    security_manager = get_security_manager()
    print("   ✅ Security manager imported successfully")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Import main app
print("\n3. Testing main app import...")
try:
    from src.api.main import app
    print("   ✅ Main app imported successfully")
    print(f"   App title: {app.title}")
    print(f"   App version: {app.version}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Import Vercel handler
print("\n4. Testing Vercel handler import...")
try:
    from api.index import handler
    print("   ✅ Vercel handler imported successfully")
    print(f"   Handler type: {type(handler)}")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Import test complete!")
print("="*50)

