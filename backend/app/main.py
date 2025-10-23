"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Realtime Quality Inspection API")


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Simple health endpoint for availability checks."""

    return {"status": "ok"}
