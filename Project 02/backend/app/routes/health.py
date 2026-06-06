"""
app/routes/health.py — /health endpoint for load balancer probes.
"""
import time
from fastapi import APIRouter
from app.models.classifier import is_loaded, load_metadata
from app.services.validation import HealthResponse
from app.config import settings

router = APIRouter()
_start_time = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns service status and whether the ML model is loaded.",
)
async def health() -> HealthResponse:
    meta    = load_metadata()
    version = meta.get("version") if meta else None
    return HealthResponse(
        status="ok",
        model_loaded=is_loaded(),
        model_version=version,
        uptime_seconds=round(time.time() - _start_time, 1),
    )


@router.get("/metrics", summary="Model performance metrics")
async def get_metrics():
    """Return the latest saved model metrics."""
    meta = load_metadata()
    if meta is None:
        return {"error": "Metadata not found. Train the model first."}
    return meta
