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
    # Successfully imported the main app - all routes are already defined
except Exception as e:
    # Create fallback diagnostic app if main app fails to import
    from fastapi import FastAPI
    
    app = FastAPI(title="AliExpress API - Initialization Error")
    
    @app.get("/")
    @app.get("/health")
    def error():
        return {
            "error": str(e),
            "status": "initialization_failed",
            "hint": "Check Vercel function logs and environment variables"
        }
