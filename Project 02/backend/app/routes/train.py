"""
app/routes/train.py — /train endpoint (triggers model retraining).

Security note: In production this would be protected by an API key or OAuth scope.
For this demo, it's rate-limited to 5 calls/min as a lightweight guard.
"""
from fastapi import APIRouter, Request
from app.models.trainer import train_pipeline
from app.models.classifier import evict_cache
from app.services.validation import ModelMetrics
from app.utils.rate_limiter import limiter
from app.utils.logging_config import get_logger
from app.config import settings

router = APIRouter()
log    = get_logger(__name__)


@router.post(
    "/train",
    response_model=ModelMetrics,
    summary="Retrain the classification model",
    description=(
        "Runs the full training pipeline on the Wisconsin Breast Cancer dataset "
        "and replaces the persisted model artifact. Rate-limited to 5 req/min."
    ),
)
@limiter.limit(settings.RATE_LIMIT_TRAIN)
async def retrain(request: Request) -> ModelMetrics:
    """Retrain model and reload cache."""
    log.info(f"retrain_requested")
    evict_cache()
    metrics = train_pipeline(save=True)
    return ModelMetrics(**{k: v for k, v in metrics.items() if k in ModelMetrics.model_fields})
