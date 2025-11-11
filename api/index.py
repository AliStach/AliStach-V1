"""Vercel entry point for the FastAPI application.

This module MUST always succeed and return a valid ASGI app.
If initialization fails, it returns a diagnostic app that reports the error.
"""

import sys
import os

# Step 1: Setup Python path (must happen before any imports)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Step 2: Print diagnostics to Vercel logs (these appear in Function logs)
print(f"[INIT] Starting Vercel function initialization")
print(f"[INIT] Python version: {sys.version}")
print(f"[INIT] Current dir: {current_dir}")
print(f"[INIT] Project root: {project_root}")
print(f"[INIT] Python path: {sys.path[:3]}")

# Step 3: Try to import the main app with comprehensive error handling
app = None
initialization_error = None

try:
    print("[INIT] Attempting to import src.api.main...")
    from api.main import app as main_app
    app = main_app
    print("[INIT] ✓ Successfully imported main app")
    
except Exception as e:
    # Capture the error for reporting
    import traceback
    initialization_error = {
        "error": str(e),
        "error_type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    
    print(f"[INIT] ✗ Failed to import main app: {type(e).__name__}: {str(e)}")
    print(f"[INIT] Traceback:\n{traceback.format_exc()}")
    print("[INIT] Creating fallback diagnostic app...")
    
    # Step 4: Create a minimal fallback app that ALWAYS works
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI(
            title="AliExpress API - Initialization Error",
            description="The main application failed to initialize. Use /debug for details."
        )
        
        # Capture environment info for debugging
        env_info = {
            "ALIEXPRESS_APP_KEY": "SET" if os.getenv("ALIEXPRESS_APP_KEY") else "MISSING",
            "ALIEXPRESS_APP_SECRET": "SET" if os.getenv("ALIEXPRESS_APP_SECRET") else "MISSING",
            "INTERNAL_API_KEY": "SET" if os.getenv("INTERNAL_API_KEY") else "MISSING",
            "ADMIN_API_KEY": "SET" if os.getenv("ADMIN_API_KEY") else "MISSING",
            "JWT_SECRET_KEY": "SET" if os.getenv("JWT_SECRET_KEY") else "MISSING",
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "not set"),
            "VERCEL": os.getenv("VERCEL", "not set"),
            "VERCEL_ENV": os.getenv("VERCEL_ENV", "not set")
        }
        
        @app.get("/")
        async def root():
            """Root endpoint - reports initialization failure."""
            return JSONResponse(
                status_code=503,
                content={
                    "status": "service_unavailable",
                    "message": "Application failed to initialize",
                    "error": initialization_error["error"],
                    "error_type": initialization_error["error_type"],
                    "hint": "Check /debug endpoint for full details"
                }
            )
        
        @app.get("/health")
        async def health():
            """Health check - reports initialization failure."""
            return JSONResponse(
                status_code=503,
                content={
                    "status": "initialization_failed",
                    "message": "The application failed to initialize. Check environment variables and dependencies.",
                    "error": initialization_error["error"],
                    "error_type": initialization_error["error_type"],
                    "environment_variables": env_info
                }
            )
        
        @app.get("/debug")
        async def debug():
            """Debug endpoint - provides full error details."""
            return JSONResponse(
                status_code=503,
                content={
                    "status": "initialization_failed",
                    "error_details": initialization_error,
                    "environment_variables": env_info,
                    "python_info": {
                        "version": sys.version,
                        "path": sys.path[:5],
                        "current_dir": current_dir,
                        "project_root": project_root
                    },
                    "troubleshooting": {
                        "step_1": "Check that all environment variables are set in Vercel dashboard",
                        "step_2": "Verify all dependencies in requirements.txt are installed",
                        "step_3": "Check for import errors in the traceback above",
                        "step_4": "Look for module-level code that might fail (file I/O, network calls)"
                    }
                }
            )
        
        @app.get("/{path:path}")
        async def catch_all(path: str):
            """Catch all other routes."""
            return JSONResponse(
                status_code=503,
                content={
                    "status": "service_unavailable",
                    "message": f"Service initialization failed. Cannot serve: /{path}",
                    "error": initialization_error["error"],
                    "hint": "Visit /debug for full error details"
                }
            )
        
        print("[INIT] ✓ Fallback diagnostic app created successfully")
        
    except Exception as fallback_error:
        # If even the fallback fails, we're in serious trouble
        print(f"[INIT] ✗✗ CRITICAL: Fallback app creation failed: {fallback_error}")
        print(f"[INIT] This should never happen. FastAPI itself may not be installed.")
        
        # Last resort: create the absolute minimum ASGI app
        async def emergency_app(scope, receive, send):
            """Emergency ASGI app when everything else fails."""
            if scope["type"] == "http":
                await send({
                    "type": "http.response.start",
                    "status": 503,
                    "headers": [[b"content-type", b"application/json"]],
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"error": "Critical initialization failure", "message": "FastAPI could not be imported"}',
                })
        
        app = emergency_app
        print("[INIT] ✓ Emergency ASGI app created")

# Step 5: Verify we have a valid app
if app is None:
    print("[INIT] ✗✗ FATAL: No app object created!")
    raise RuntimeError("Failed to create any app object")

print(f"[INIT] Final app type: {type(app)}")
print("[INIT] Initialization complete, exporting handler")

# Step 6: Export for Vercel
# Vercel looks for 'app' or 'handler' in the module
handler = app

# Also export as 'app' for compatibility
__all__ = ['app', 'handler']
