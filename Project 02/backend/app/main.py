"""
app/main.py — FastAPI application.
Start: uvicorn app.main:app --reload --port 8000
Docs:  http://localhost:8000/docs
"""
import time
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, Request, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_OK = True
except ImportError:
    FASTAPI_OK = False
    print("\n[ERROR] FastAPI missing. Run: pip install fastapi uvicorn slowapi\n")
    raise

from app.config import settings
from app.utils.logging_config import configure_logging, get_logger
from app.models.classifier import load_model, load_metadata, predict as model_predict, get_rf_estimator, is_loaded, evict_cache
from app.services.validation import validate_prediction_input
from app.services.preprocessing import DataValidator, preprocess, compute_feature_importance_from_shap

configure_logging()
log = get_logger(__name__)
dv  = DataValidator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("startup: loading model")
    try:
        load_model()
        log.info("startup: model ready")
    except FileNotFoundError:
        log.warning("startup: model not found — run python train.py first")
    yield
    log.info("shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Breast cancer classification using a VotingClassifier ensemble. "
        "Trained on the Wisconsin Breast Cancer Dataset."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept"],
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    ms = round((time.perf_counter() - t0) * 1000, 2)
    response.headers["X-Response-Time"] = f"{ms}ms"
    return response


@app.get("/")
async def root():
    return {"service": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}


@app.get("/health")
async def health():
    meta = load_metadata()
    return {
        "status": "ok",
        "model_loaded": is_loaded(),
        "model_version": meta.get("version") if meta else None,
    }


@app.get("/metrics")
async def get_metrics():
    meta = load_metadata()
    if not meta:
        raise HTTPException(404, "No metadata. Run python train.py first.")
    return meta


@app.post("/predict")
async def predict(request: Request):
    body = await request.json()
    features, errors = validate_prediction_input(body)
    if errors:
        raise HTTPException(422, {"errors": errors})
    try:
        bundle = load_model()
    except FileNotFoundError as e:
        raise HTTPException(503, str(e))
    scaled = preprocess(features, bundle["scaler"])
    result = model_predict(scaled)
    rf_est = get_rf_estimator()
    top_features = compute_feature_importance_from_shap(
        bundle["feature_names"], features, rf_est, scaled
    )
    meta = load_metadata()
    return {
        "prediction":            result["prediction"],
        "prediction_class":      result["prediction_class"],
        "confidence":            result["confidence"],
        "probability_malignant": result["probability_malignant"],
        "probability_benign":    result["probability_benign"],
        "top_features":          top_features,
        "model_version":         meta.get("version", "1.0") if meta else "1.0",
        "inference_time_ms":     result["inference_time_ms"],
    }


@app.post("/train")
async def retrain():
    from app.models.trainer import train_pipeline
    evict_cache()
    metrics = train_pipeline(save=True)
    return {"status": "ok", "metrics": metrics}
