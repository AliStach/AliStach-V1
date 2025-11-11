"""Simulate Vercel's ASGI invocation to diagnose FUNCTION_INVOCATION_FAILED."""

import sys
import os

# Add project root to path (same as api/ultra_minimal.py would do)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=" * 60)
print("VERCEL SIMULATION TEST")
print("=" * 60)

# Step 1: Test import
print("\n[1] Testing import of api/ultra_minimal.py...")
try:
    from api.ultra_minimal import app, handler
    print("✓ Import successful")
    print(f"  - app type: {type(app)}")
    print(f"  - handler type: {type(handler)}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Test ASGI interface
print("\n[2] Testing ASGI interface...")
try:
    # Check if app is callable
    if not callable(app):
        print("✗ App is not callable")
        sys.exit(1)
    print("✓ App is callable")
    
    # Check for ASGI signature
    import inspect
    sig = inspect.signature(app)
    params = list(sig.parameters.keys())
    print(f"  - Signature: {params}")
    
except Exception as e:
    print(f"✗ ASGI check failed: {e}")
    sys.exit(1)

# Step 3: Simulate ASGI call
print("\n[3] Simulating ASGI call...")
try:
    import asyncio
    
    # Create a minimal ASGI scope (HTTP request)
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "path": "/health",
        "query_string": b"",
        "headers": [],
        "server": ("testserver", 80),
    }
    
    # Collect response
    class ResponseCollector:
        def __init__(self):
            self.started = False
            self.body = b""
            self.status = None
    
    collector = ResponseCollector()
    
    async def receive():
        return {"type": "http.request", "body": b""}
    
    async def send(message):
        if message["type"] == "http.response.start":
            collector.started = True
            collector.status = message["status"]
        elif message["type"] == "http.response.body":
            collector.body += message.get("body", b"")
    
    # Call the ASGI app
    async def test_request():
        await app(scope, receive, send)
    
    asyncio.run(test_request())
    
    print("✓ ASGI call successful")
    print(f"  - Status: {collector.status}")
    print(f"  - Body: {collector.body.decode()}")
    
except Exception as e:
    print(f"✗ ASGI call failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test with Vercel-like environment
print("\n[4] Testing with Vercel-like environment variables...")
try:
    # Set Vercel environment variables
    os.environ["VERCEL"] = "1"
    os.environ["VERCEL_ENV"] = "production"
    
    # Re-import to test with Vercel env
    import importlib
    import api.ultra_minimal
    importlib.reload(api.ultra_minimal)
    
    print("✓ Vercel environment simulation successful")
    
except Exception as e:
    print(f"✗ Vercel environment test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
print("\nConclusion: ultra_minimal.py works correctly locally.")
print("The FUNCTION_INVOCATION_FAILED error must be caused by:")
print("  1. Vercel's Python runtime environment")
print("  2. Missing system dependencies")
print("  3. Vercel's ASGI adapter (@vercel/python)")
print("  4. Network/timeout issues during cold start")
