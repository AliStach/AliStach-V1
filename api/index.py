"""Vercel entry point for the FastAPI application."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the FastAPI app
from api.main import app

# Export the app for Vercel
handler = app