"""
app/services/preprocessing.py — Feature engineering and data validation pipeline.

Design: Stateless functions that transform raw feature arrays.
The fitted scaler is stored inside the joblib bundle (not as a separate artifact)
so model + scaler version are always in sync.
"""
from __future__ import annotations

import numpy as np
from app.utils.logging_config import get_logger

log = get_logger(__name__)


class DataValidator:
    """
    Pre-model data quality checks.

    Checks:
      - No NaN / Inf values
      - IQR-based outlier detection (soft warning, not hard reject)
      - Feature count matches expected
    """

    # Approximate IQR bounds from Wisconsin dataset (used for drift detection)
    # Format: {feature_index: (Q1 - 1.5*IQR, Q3 + 1.5*IQR)}
    _IQR_BOUNDS: dict[int, tuple[float, float]] = {
        0:  (6.98, 22.0),   # radius_mean
        3:  (143.5, 1458.0), # area_mean
        # Add more bounds as needed; unspecified features skip outlier check
    }

    def validate(self, features: list[float]) -> dict:
        """
        Validate a feature vector and return a quality report.

        Returns:
            dict with keys: valid (bool), warnings (list[str]), errors (list[str])
        """
        result: dict = {"valid": True, "warnings": [], "errors": []}
        arr = np.array(features, dtype=np.float64)

        # ── Check for NaN / Inf ─────────────────────────────────────
        if not np.isfinite(arr).all():
            result["errors"].append("Feature vector contains NaN or Inf values.")
            result["valid"] = False
            return result

        # ── Check feature count ─────────────────────────────────────
        if len(features) != 30:
            result["errors"].append(f"Expected 30 features, got {len(features)}.")
            result["valid"] = False
            return result

        # ── IQR outlier warnings (non-blocking) ────────────────────
        for idx, (lo, hi) in self._IQR_BOUNDS.items():
            val = arr[idx]
            if val < lo or val > hi:
                result["warnings"].append(
                    f"Feature[{idx}] = {val:.4f} is outside expected IQR range [{lo}, {hi}]. "
                    "Possible outlier — prediction may be less reliable."
                )

        return result


def preprocess(features: list[float], scaler) -> np.ndarray:
    """
    Apply standard scaling to raw feature values.

    Args:
        features: Raw 30-element feature list.
        scaler:   Fitted sklearn StandardScaler from model bundle.

    Returns:
        Scaled (1, 30) numpy array ready for model inference.
    """
    arr = np.array(features, dtype=np.float64).reshape(1, -1)
    return scaler.transform(arr)


def compute_feature_importance_from_shap(
    feature_names: list[str],
    feature_values: list[float],
    rf_estimator,
    scaled_features: np.ndarray,
) -> list[dict]:
    """
    Compute per-prediction feature importance using the RandomForest
    sub-estimator's feature importances as a SHAP proxy.

    Why: shap.TreeExplainer is not available in this environment.
    We approximate SHAP by multiplying RF feature_importances_ by the
    standardized feature value direction — this gives a directional impact.

    Returns:
        List of {feature, value, shap_value, impact_direction} dicts,
        sorted by |shap_value| descending.
    """
    try:
        importances = rf_estimator.feature_importances_  # shape (30,)
        scaled_vals = scaled_features.flatten()          # shape (30,)

        # Directional pseudo-SHAP: importance × sign of scaled value
        pseudo_shap = importances * scaled_vals

        contributions = []
        for i, fname in enumerate(feature_names):
            sv = float(pseudo_shap[i])
            contributions.append({
                "feature": fname,
                "value": round(float(feature_values[i]), 6),
                "shap_value": round(sv, 6),
                "impact_direction": "positive" if sv > 0 else "negative",
            })

        # Sort by absolute impact descending, return top 10
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        return contributions[:10]

    except Exception as exc:
        log.warning(f"feature_importance_failed error=str(exc)")
        return []
