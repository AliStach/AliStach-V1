"""Vercel entry point for the FastAPI application."""

import sys
import os

# Add project root to Python path FIRST (before any imports)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import - but wrap in comprehensive error handling
try:
    # Try to import the main app
    from src.api.main import app
    
except Exception as e:
    # If ANYTHING fails during import, create a minimal diagnostic app
    # This ensures Vercel always gets a valid ASGI app
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import traceback
    
    # Create minimal app that reports the error
    app = FastAPI(title="AliExpress API - Initialization Error")
    
    # Capture the full error for debugging
    error_details = {
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc(),
        "python_path": sys.path[:3],
        "current_dir": current_dir,
        "project_root": project_root
    }
    
    @app.get("/health")
    async def health():
        """Health check that reports initialization failure."""
        return JSONResponse(
            status_code=503,
            content={
                "status": "initialization_failed",
                "message": "The application failed to initialize. Check environment variables and dependencies.",
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
    
    @app.get("/debug")
    async def debug():
        """Debug endpoint with full error details."""
        return JSONResponse(
            status_code=503,
            content=error_details
        )
    
    @app.get("/{path:path}")
    async def catch_all(path: str):
        """Catch all other routes and report error."""
        return JSONResponse(
            status_code=503,
            content={
                "status": "service_unavailable",
                "message": f"Service initialization failed: {str(e)}",
                "path_requested": path
            }
        )

# Export for Vercel (works whether app loaded successfully or not)
handler = app