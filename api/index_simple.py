"""Simplified Vercel entry point for debugging."""

import sys
import os

# Setup Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"[SIMPLE] Starting import")
print(f"[SIMPLE] Python: {sys.version}")
print(f"[SIMPLE] Path: {sys.path[:2]}")

try:
    # Try absolute minimal import first
    print("[SIMPLE] Step 1: Import FastAPI...")
    from fastapi import FastAPI
    print("[SIMPLE] ✓ FastAPI OK")
    
    print("[SIMPLE] Step 2: Create minimal app...")
    app = FastAPI(title="Simple Test")
    
    @app.get("/")
    async def root():
        return {"status": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "simple"}
    
    print("[SIMPLE] ✓ App created")
    
    # Now try importing main
    print("[SIMPLE] Step 3: Try importing src.api.main...")
    from src.api.main import app as main_app
    app = main_app
    print("[SIMPLE] ✓ Main app imported successfully")
    
except Exception as e:
    print(f"[SIMPLE] ✗ FAILED: {e}")
    import traceback
    print(f"[SIMPLE] Traceback:")
    traceback.print_exc()
    
    # Create fallback app
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Error Debug")
    
    @app.get("/")
    async def root():
        return JSONResponse(
            status_code=503,
            content={
                "error": str(e),
                "type": type(e).__name__,
                "message": "Import failed - check logs"
            }
        )
    
    @app.get("/health")
    async def health():
        return JSONResponse(
            status_code=503,
            content={
                "status": "failed",
                "error": str(e),
                "type": type(e).__name__
            }
        )

print(f"[SIMPLE] Final app: {type(app)}")

handler = app
__all__ = ['app', 'handler']
