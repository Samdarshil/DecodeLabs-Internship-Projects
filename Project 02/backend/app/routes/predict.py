"""
app/routes/predict.py — /predict endpoint.
"""
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException
from app.services.validation import PredictionInput, PredictionResponse, ShapContribution
from app.services.preprocessing import DataValidator, preprocess, compute_feature_importance_from_shap
from app.models import classifier
from app.utils.rate_limiter import limiter
from app.utils.logging_config import get_logger
from app.config import settings

router = APIRouter()
log    = get_logger(__name__)
dv     = DataValidator()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Run breast cancer classification",
    description=(
        "Accepts 30 Wisconsin breast cancer features and returns a binary "
        "classification (Malignant/Benign) with confidence score and top-10 "
        "feature importance contributions."
    ),
    responses={
        422: {"description": "Validation error — feature out of clinical range"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Model not loaded — run train.py first"},
    },
)
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(request: Request, body: PredictionInput) -> PredictionResponse:
    """Full prediction pipeline with feature importance."""

    # ── Ensure model is loaded ────────────────────────────────────────
    try:
        bundle = classifier.load_model()
    except FileNotFoundError as exc:
        log.error(f"model_not_found error=str(exc)")
        raise HTTPException(status_code=503, detail=str(exc))

    # ── Validate input ───────────────────────────────────────────────
    feature_list = body.to_array()
    validation   = dv.validate(feature_list)

    if not validation["valid"]:
        raise HTTPException(status_code=422, detail=validation["errors"])

    if validation["warnings"]:
        log.warning(f"input_warnings warnings=validation["warnings"]")

    # ── Preprocess ───────────────────────────────────────────────────
    scaled = preprocess(feature_list, bundle["scaler"])

    # ── Inference ────────────────────────────────────────────────────
    result = classifier.predict(scaled)

    # ── Feature importance ───────────────────────────────────────────
    rf_est        = classifier.get_rf_estimator()
    top_features  = compute_feature_importance_from_shap(
        bundle["feature_names"], feature_list, rf_est, scaled
    )
    shap_contrib  = [ShapContribution(**f) for f in top_features]

    # ── Load metadata for version string ────────────────────────────
    meta    = classifier.load_metadata()
    version = meta.get("version", "unknown") if meta else "unknown"

    return PredictionResponse(
        prediction=result["prediction"],
        prediction_class=result["prediction_class"],
        confidence=result["confidence"],
        probability_malignant=result["probability_malignant"],
        probability_benign=result["probability_benign"],
        top_features=shap_contrib,
        model_version=version,
        inference_time_ms=result["inference_time_ms"],
    )
