"""Test script to simulate api/index.py import in isolation."""

import sys
import os
import traceback

print("=" * 60)
print("TESTING: api/index.py import simulation")
print("=" * 60)
print()

# Step 1: Simulate the path setup from api/index.py
print("Step 1: Setting up Python path...")
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added project root to sys.path")
else:
    print(f"Project root already in sys.path")

print(f"Python path (first 5): {sys.path[:5]}")
print()

# Step 2: Check __init__.py files
print("Step 2: Checking __init__.py files...")
init_files = [
    os.path.join(project_root, "src", "__init__.py"),
    os.path.join(project_root, "src", "api", "__init__.py"),
    os.path.join(project_root, "src", "middleware", "__init__.py"),
]

for init_file in init_files:
    if os.path.exists(init_file):
        print(f"  ✓ {init_file} exists")
    else:
        print(f"  ✗ {init_file} MISSING")
print()

# Step 3: Test import of audit_logger in isolation
print("Step 3: Testing audit_logger import...")
try:
    print("  Importing audit_logger...")
    from src.middleware.audit_logger import audit_logger
    print(f"  ✓ audit_logger imported: {type(audit_logger)}")
    
    # Check if it tries to access database
    print("  Checking if audit_logger tries to access database on import...")
    # The proxy should not instantiate yet
    print(f"  audit_logger type: {type(audit_logger)}")
    print(f"  Has log_event method: {hasattr(audit_logger, 'log_event')}")
    
    # Try to access an attribute (this should trigger lazy init if proxy works)
    print("  Accessing audit_logger.log_event (should trigger lazy init if needed)...")
    log_method = getattr(audit_logger, 'log_event', None)
    print(f"  ✓ Got log_event method: {log_method is not None}")
    
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    traceback.print_exc()
print()

# Step 4: Test import of security middleware
print("Step 4: Testing security middleware import...")
try:
    print("  Importing security middleware...")
    from src.middleware.security import get_security_manager
    print("  ✓ Security middleware imported")
    
    # Check if this triggers audit_logger instantiation
    print("  Getting security manager...")
    security_manager = get_security_manager()
    print("  ✓ Security manager obtained")
    
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    traceback.print_exc()
print()

# Step 5: Test import of main app
print("Step 5: Testing main app import...")
try:
    print("  Importing from src.api.main...")
    from src.api.main import app
    print(f"  ✓ App imported: {app.title}")
    print(f"  ✓ App version: {app.version}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    traceback.print_exc()
    print()
    print("Full traceback:")
    traceback.print_exc()
print()

# Step 6: Test import of api/index handler
print("Step 6: Testing api/index.py handler import...")
try:
    print("  Importing handler from api.index...")
    # Change to api directory to simulate Vercel
    api_dir = os.path.join(project_root, "api")
    if api_dir not in sys.path:
        sys.path.insert(0, api_dir)
    
    from index import handler
    print(f"  ✓ Handler imported: {type(handler)}")
except Exception as e:
    print(f"  ✗ FAILED: {e}")
    traceback.print_exc()
print()

print("=" * 60)
print("IMPORT TEST COMPLETE")
print("=" * 60)

