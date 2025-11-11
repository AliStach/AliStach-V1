"""Ultra minimal test - just FastAPI, no imports."""

from fastapi import FastAPI

app = FastAPI(title="Ultra Minimal")

@app.get("/")
def root():
    return {"status": "ok", "test": "ultra_minimal"}

@app.get("/health")
def health():
    return {"status": "healthy", "test": "ultra_minimal"}

handler = app
