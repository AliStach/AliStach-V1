#!/usr/bin/env python3
"""Simple import test to identify crash point."""

import sys
import os
import traceback

# Simulate api/index.py setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Testing imports step by step...")
print(f"Project root: {project_root}")
print()

# Test 1: Import audit_logger
print("1. Testing audit_logger import...")
try:
    from src.middleware.audit_logger import audit_logger
    print(f"   ✓ audit_logger imported: {type(audit_logger)}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check if proxy prevents instantiation
print("\n2. Checking if proxy prevents instantiation...")
try:
    # Access an attribute - this should trigger lazy init
    has_log = hasattr(audit_logger, 'log_event')
    print(f"   ✓ hasattr check: {has_log}")
    if has_log:
        # Try to get the method - this WILL trigger instantiation
        print("   Accessing log_event method (this triggers lazy init)...")
        log_event = getattr(audit_logger, 'log_event')
        print(f"   ✓ Got log_event method: {log_event}")
        print("   ⚠️  This triggered AuditLogger instantiation!")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Import security
print("\n3. Testing security middleware import...")
try:
    from src.middleware.security import get_security_manager
    print("   ✓ Security middleware imported")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Import main app
print("\n4. Testing main app import...")
try:
    from src.api.main import app
    print(f"   ✓ App imported: {app.title}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Import handler
print("\n5. Testing handler import...")
try:
    sys.path.insert(0, os.path.join(project_root, 'api'))
    from index import handler
    print(f"   ✓ Handler imported: {type(handler)}")
except Exception as e:
    print(f"   ✗ FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("ALL IMPORTS SUCCESSFUL!")
print("="*60)

