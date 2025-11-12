"""Vercel serverless function entry point for FastAPI.

Vercel's @vercel/python builder expects a module-level ASGI app.
For FastAPI, the app object itself is the ASGI application.
"""

import sys
import os

# Setup Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI application
try:
    from src.api.main import app
except Exception as e:
    # Fallback app if main import fails
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    @app.get("/health")
    def error():
        return {"error": str(e), "status": "initialization_failed"}

# ✅ Always add a root route for production health/info
try:
    from fastapi import Request

    @app.get("/")
    async def root(request: Request):
        return {
            "status": "ok",
            "message": "AliExpress API Proxy is live 🚀",
            "host": request.client.host
        }

    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "AliExpress API Proxy"}

except Exception:
    # Prevent crash if FastAPI import fails in fallback mode
    pass
