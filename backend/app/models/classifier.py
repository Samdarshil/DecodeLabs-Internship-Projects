"""
app/models/classifier.py — Singleton model loader with in-process caching.

Design decisions:
  - Joblib (not pickle) for cross-Python-version safety
  - Single cache dict avoids repeated disk I/O after cold start
  - Model bundle contains both model + scaler to guarantee version sync
"""
from __future__ import annotations

import json
import time
import joblib
import numpy as np
from pathlib import Path
from typing import Optional
from app.config import settings
from app.utils.logging_config import get_logger

log = get_logger(__name__)

# ── Module-level cache (shared across requests in same process) ──────────────
_cache: dict = {}


def load_model() -> dict:
    """
    Load model bundle from disk into module cache.

    Bundle structure (as saved by train.py):
        {
          'model':         VotingClassifier,
          'scaler':        StandardScaler,
          'feature_names': list[str],
          'target_names':  list[str],   # ['malignant', 'benign']
        }

    Returns:
        The cached bundle dict.

    Raises:
        FileNotFoundError if model file does not exist.
        RuntimeError if bundle is malformed.
    """
    global _cache

    if "bundle" in _cache:
        return _cache["bundle"]

    model_path = settings.MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Run `python train.py` from the backend directory first."
        )

    log.info(f"loading_model path={model_path}")
    t0 = time.perf_counter()
    bundle = joblib.load(model_path)
    elapsed = (time.perf_counter() - t0) * 1000

    required_keys = {"model", "scaler", "feature_names", "target_names"}
    if not required_keys.issubset(bundle.keys()):
        raise RuntimeError(
            f"Model bundle missing keys: {required_keys - bundle.keys()}"
        )

    _cache["bundle"] = bundle
    log.info(f"model_loaded load_time_ms={round(elapsed, 2)}")
    return bundle


def load_metadata() -> Optional[dict]:
    """Load and return the model metadata JSON, or None if not found."""
    meta_path = settings.METADATA_PATH
    if not meta_path.exists():
        log.warning(f"metadata_not_found path=str(meta_path)")
        return None
    with open(meta_path, "r") as f:
        return json.load(f)


def predict(features_scaled: np.ndarray) -> dict:
    """
    Run inference on a pre-scaled (1×30) feature array.

    Returns:
        {
          'prediction':            str   ('Malignant' | 'Benign'),
          'prediction_class':      int,
          'confidence':            float,
          'probability_malignant': float,
          'probability_benign':    float,
        }
    """
    bundle = load_model()
    clf    = bundle["model"]
    target = bundle["target_names"]   # index 0 = malignant, 1 = benign

    t0     = time.perf_counter()
    proba  = clf.predict_proba(features_scaled)[0]
    pred   = int(clf.predict(features_scaled)[0])
    elapsed = (time.perf_counter() - t0) * 1000

    # VotingClassifier class order matches training label encoding:
    # class 0 → malignant, class 1 → benign
    prob_malignant = float(proba[0])
    prob_benign    = float(proba[1])
    confidence     = float(proba[pred])

    result = {
        "prediction":            target[pred].capitalize(),
        "prediction_class":      pred,
        "confidence":            round(confidence, 4),
        "probability_malignant": round(prob_malignant, 4),
        "probability_benign":    round(prob_benign, 4),
        "inference_time_ms":     round(elapsed, 3),
    }

    log.info(
        f'prediction={result["prediction"]}, '
        f'confidence={result["confidence"]}, '
        f'inference_ms={result["inference_time_ms"]}'
    )
    return result


def get_rf_estimator():
    """Return the RandomForest sub-estimator for feature importance."""
    bundle = load_model()
    clf    = bundle["model"]
    # estimators_ are in the order passed to VotingClassifier:
    # index 0 = LR, index 1 = RF, index 2 = GB
    return clf.estimators_[1]


def is_loaded() -> bool:
    """Return True if model is cached in memory."""
    return "bundle" in _cache


def evict_cache() -> None:
    """Clear the in-process model cache (used when retraining)."""
    global _cache
    _cache.clear()
    log.info(f"model_cache_evicted")
