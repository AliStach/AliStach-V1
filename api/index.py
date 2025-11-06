"""Vercel entry point for the FastAPI application."""

# Import the FastAPI app directly from the api directory
from .main import app

# Export the app for Vercel
handler = app