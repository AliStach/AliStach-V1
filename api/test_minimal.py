"""Absolute minimal FastAPI app for Vercel testing."""

from fastapi import FastAPI

app = FastAPI(title="Minimal Test")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Minimal app works"}

@app.get("/health")
async def health():
    return {"status": "healthy", "test": "minimal"}

# Export for Vercel
handler = app
