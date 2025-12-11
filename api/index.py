import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.api.main import app
except Exception as e:
    import traceback
    traceback.print_exc()
    
    from fastapi import FastAPI
    
    app = FastAPI(title="AliExpress API - Initialization Error")
    
    @app.get("/")
    @app.get("/health")
    def error():
        return {
            "error": str(e),
            "status": "initialization_failed",
            "error_type": type(e).__name__,
            "env_check": {
                "VERCEL": os.getenv("VERCEL"),
                "ALIEXPRESS_APP_KEY": bool(os.getenv("ALIEXPRESS_APP_KEY")),
                "ALIEXPRESS_APP_SECRET": bool(os.getenv("ALIEXPRESS_APP_SECRET")),
                "python_version": sys.version,
                "cwd": os.getcwd()
            }
        }
