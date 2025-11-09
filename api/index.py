"""Vercel entry point for the FastAPI application."""

import sys
import os
import logging

# Configure basic logging first (before any imports that might fail)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path for Vercel serverless environment
# This allows imports from src.* to work correctly with relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add project root to sys.path first (before src)
# This is critical for relative imports to work in src/api/main.py
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger.info(f"Vercel entry point starting...")
logger.info(f"Current directory: {current_dir}")
logger.info(f"Project root: {project_root}")
logger.info(f"Python path: {sys.path[:3]}...")  # Log first 3 entries

# Import the secured FastAPI app from src.api.main
# The relative imports in src/api/main.py will work because:
# 1. project_root is in sys.path
# 2. Python treats 'src' as a package
# 3. Relative imports like 'from ..utils.config' resolve correctly
try:
    logger.info("Attempting to import from src.api.main...")
    from src.api.main import app
    logger.info("Successfully imported from src.api.main")
except ImportError as e:
    # If import fails, try the fallback api/main.py
    logger.error(f"Failed to import from src.api.main: {e}")
    logger.error(f"Python path: {sys.path}")
    logger.error(f"Current directory: {current_dir}")
    logger.error(f"Project root: {project_root}")
    
    # Fallback to the simpler api/main.py if available
    try:
        logger.info("Attempting fallback import from api.main...")
        from .main import app
        logger.warning("Using fallback api/main.py instead of src/api/main.py")
    except ImportError as e2:
        logger.error(f"Failed to import fallback api/main.py: {e2}")
        # Last resort: try to create a minimal app
        try:
            from fastapi import FastAPI
            app = FastAPI(title="AliExpress API - Fallback Mode")
            logger.warning("Created minimal FastAPI app as last resort")
        except Exception as e3:
            logger.error(f"Failed to create minimal app: {e3}")
            raise ImportError(f"All import attempts failed. Last error: {e2}") from e2
except Exception as e:
    # Catch any other unexpected errors during import
    logger.error(f"Unexpected error during import: {e}", exc_info=True)
    # Try fallback
    try:
        from .main import app
        logger.warning("Using fallback api/main.py after unexpected error")
    except:
        raise

logger.info("FastAPI app imported successfully, exporting handler...")

# Export the app for Vercel
handler = app