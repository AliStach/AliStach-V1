#!/usr/bin/env python3
"""Test script to simulate Vercel import environment."""

import sys
import os

# Simulate Vercel environment
os.environ['VERCEL'] = '1'
os.environ['VERCEL_ENV'] = 'production'

# Setup path like Vercel does
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=" * 60)
print("SIMULATING VERCEL IMPORT")
print("=" * 60)
print(f"VERCEL={os.getenv('VERCEL')}")
print(f"Python: {sys.version}")
print(f"Path: {sys.path[:3]}")
print()

try:
    print("Step 1: Importing api.index...")
    from api.index import app
    print("✅ SUCCESS: api.index imported")
    print(f"App type: {type(app)}")
    print()
    
    print("Step 2: Checking app attributes...")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    print()
    
    print("Step 3: Listing routes...")
    for route in app.routes[:5]:
        if hasattr(route, 'path'):
            print(f"  - {route.path}")
    print()
    
    print("=" * 60)
    print("✅ ALL IMPORTS SUCCESSFUL")
    print("=" * 60)
    
except Exception as e:
    print("=" * 60)
    print("❌ IMPORT FAILED")
    print("=" * 60)
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
    print()
    
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
    
    sys.exit(1)
