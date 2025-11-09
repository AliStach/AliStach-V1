#!/usr/bin/env python3
"""Test script to verify api/index.py can be imported without crashes."""

import sys
import os

# Set up path like api/index.py does
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=" * 60)
print("Testing api/index.py import")
print("=" * 60)
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")
print()

# Simulate Vercel environment
os.environ['VERCEL'] = '1'

try:
    # Change to api directory to simulate Vercel
    api_dir = os.path.join(project_root, 'api')
    original_dir = os.getcwd()
    
    try:
        os.chdir(api_dir)
        print(f"Changed to: {api_dir}")
        
        # Import handler (this is what Vercel does)
        print("\nImporting handler from api.index...")
        from index import handler
        print(f"✓ Handler imported successfully: {type(handler)}")
        print(f"✓ Handler is FastAPI app: {hasattr(handler, 'title')}")
        if hasattr(handler, 'title'):
            print(f"✓ App title: {handler.title}")
        
        print("\n" + "=" * 60)
        print("SUCCESS: api/index.py imported without errors!")
        print("=" * 60)
        
    finally:
        os.chdir(original_dir)
        
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

