"""Vercel serverless function entry point for FastAPI.

Vercel's @vercel/python builder expects a module-level ASGI app.
For FastAPI, the app object itself is the ASGI application.
"""

import sys
import os

# Setup Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Debug: Print environment info
print(f"[VERCEL] Python path: {sys.path[0]}")
print(f"[VERCEL] CWD: {os.getcwd()}")
print(f"[VERCEL] VERCEL env: {os.getenv('VERCEL', 'not_set')}")
print(f"[VERCEL] ALIEXPRESS_APP_KEY present: {bool(os.getenv('ALIEXPRESS_APP_KEY'))}")

# Import the FastAPI application
try:
    from src.api.main import app
    print(f"[VERCEL] Successfully imported main app")
    print(f"[VERCEL] App routes: {[route.path for route in app.routes]}")
    # Successfully imported the main app - all routes are already defined
except Exception as e:
    print(f"[VERCEL ERROR] Failed to import main app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create fallback diagnostic app if main app fails to import
    from fastapi import FastAPI
    
    app = FastAPI(title="AliExpress API - Initialization Error")
    
    @app.get("/")
    @app.get("/health")
    def error():
        return {
            "error": str(e),
            "status": "initialization_failed",
            "hint": "Check Vercel function logs and environment variables",
            "env_check": {
                "ALIEXPRESS_APP_KEY": bool(os.getenv("ALIEXPRESS_APP_KEY")),
                "ALIEXPRESS_APP_SECRET": bool(os.getenv("ALIEXPRESS_APP_SECRET")),
                "VERCEL": os.getenv("VERCEL", "not_set")
            }
        }
