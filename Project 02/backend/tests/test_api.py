"""
tests/test_api.py — Integration tests for FastAPI endpoints.

Run: cd backend && pytest tests/ -v --tb=short
"""
import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.validation import FEATURE_ORDER

# ── Sample inputs ─────────────────────────────────────────────────────────────
MALIGNANT_SAMPLE = {
    "radius_mean": 17.99, "texture_mean": 10.38, "perimeter_mean": 122.8,
    "area_mean": 1001.0, "smoothness_mean": 0.1184, "compactness_mean": 0.2776,
    "concavity_mean": 0.3001, "concave_points_mean": 0.1471,
    "symmetry_mean": 0.2419, "fractal_dimension_mean": 0.07871,
    "radius_se": 1.095, "texture_se": 0.9053, "perimeter_se": 8.589,
    "area_se": 153.4, "smoothness_se": 0.006399, "compactness_se": 0.04904,
    "concavity_se": 0.05373, "concave_points_se": 0.01587,
    "symmetry_se": 0.03003, "fractal_dimension_se": 0.006193,
    "radius_worst": 25.38, "texture_worst": 17.33, "perimeter_worst": 184.6,
    "area_worst": 2019.0, "smoothness_worst": 0.1622,
    "compactness_worst": 0.6656, "concavity_worst": 0.7119,
    "concave_points_worst": 0.2654, "symmetry_worst": 0.4601,
    "fractal_dimension_worst": 0.1189,
}

BENIGN_SAMPLE = {
    "radius_mean": 11.42, "texture_mean": 20.38, "perimeter_mean": 77.58,
    "area_mean": 386.1, "smoothness_mean": 0.1425, "compactness_mean": 0.2839,
    "concavity_mean": 0.2414, "concave_points_mean": 0.1052,
    "symmetry_mean": 0.2597, "fractal_dimension_mean": 0.09744,
    "radius_se": 0.4956, "texture_se": 1.156, "perimeter_se": 3.445,
    "area_se": 27.23, "smoothness_se": 0.00911, "compactness_se": 0.07458,
    "concavity_se": 0.05661, "concave_points_se": 0.01867,
    "symmetry_se": 0.05963, "fractal_dimension_se": 0.009208,
    "radius_worst": 14.91, "texture_worst": 26.5, "perimeter_worst": 98.87,
    "area_worst": 567.7, "smoothness_worst": 0.2098,
    "compactness_worst": 0.8663, "concavity_worst": 0.6869,
    "concave_points_worst": 0.2575, "symmetry_worst": 0.6638,
    "fractal_dimension_worst": 0.173,
}


class TestPredictionValidation:
    """Test Pydantic validation without needing a running server."""

    def test_valid_input_parses(self):
        from app.services.validation import PredictionInput
        obj = PredictionInput(**MALIGNANT_SAMPLE)
        arr = obj.to_array()
        assert len(arr) == 30

    def test_feature_order_matches_sklearn(self):
        from app.services.validation import PredictionInput
        obj = PredictionInput(**MALIGNANT_SAMPLE)
        arr = obj.to_array()
        # First feature must be radius_mean
        assert arr[0] == pytest.approx(17.99, rel=1e-3)

    def test_negative_feature_raises(self):
        from pydantic import ValidationError
        from app.services.validation import PredictionInput
        bad = MALIGNANT_SAMPLE.copy()
        bad["radius_mean"] = -1.0
        with pytest.raises(ValidationError):
            PredictionInput(**bad)

    def test_out_of_range_feature_raises(self):
        from pydantic import ValidationError
        from app.services.validation import PredictionInput
        bad = MALIGNANT_SAMPLE.copy()
        bad["radius_mean"] = 999.0   # max is 30.0
        with pytest.raises(ValidationError):
            PredictionInput(**bad)

    def test_missing_feature_raises(self):
        from pydantic import ValidationError
        from app.services.validation import PredictionInput
        incomplete = {k: v for k, v in list(MALIGNANT_SAMPLE.items())[:15]}
        with pytest.raises(ValidationError):
            PredictionInput(**incomplete)


class TestPreprocessing:
    """Unit tests for the preprocessing pipeline."""

    def test_validate_clean_input(self):
        from app.services.preprocessing import DataValidator
        from app.services.validation import PredictionInput
        dv = DataValidator()
        obj = PredictionInput(**MALIGNANT_SAMPLE)
        result = dv.validate(obj.to_array())
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_wrong_length(self):
        from app.services.preprocessing import DataValidator
        dv = DataValidator()
        result = dv.validate([1.0, 2.0, 3.0])
        assert result["valid"] is False

    def test_validate_nan_detected(self):
        import math
        from app.services.preprocessing import DataValidator
        from app.services.validation import PredictionInput
        dv = DataValidator()
        arr = PredictionInput(**MALIGNANT_SAMPLE).to_array()
        arr[0] = float("nan")
        result = dv.validate(arr)
        assert result["valid"] is False


class TestModel:
    """Integration tests requiring the trained model."""

    @pytest.fixture(autouse=True, scope="class")
    def ensure_model(self):
        """Train model if not present."""
        import os
        from app.config import settings
        if not settings.MODEL_PATH.exists():
            from app.models.trainer import train_pipeline
            train_pipeline(save=True)

    def test_model_loads(self):
        from app.models.classifier import load_model
        bundle = load_model()
        assert "model" in bundle
        assert "scaler" in bundle

    def test_malignant_prediction(self):
        from app.services.validation import PredictionInput
        from app.services.preprocessing import preprocess
        from app.models import classifier

        bundle = classifier.load_model()
        obj = PredictionInput(**MALIGNANT_SAMPLE)
        scaled = preprocess(obj.to_array(), bundle["scaler"])
        result = classifier.predict(scaled)
        assert result["prediction"] == "Malignant"
        assert result["confidence"] > 0.5

    def test_prediction_response_structure(self):
        from app.services.validation import PredictionInput
        from app.services.preprocessing import preprocess
        from app.models import classifier

        bundle = classifier.load_model()
        obj = PredictionInput(**BENIGN_SAMPLE)
        scaled = preprocess(obj.to_array(), bundle["scaler"])
        result = classifier.predict(scaled)

        assert "prediction" in result
        assert "confidence" in result
        assert result["prediction"] in ("Malignant", "Benign")
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["inference_time_ms"] >= 0


class TestModelPerformance:
    """Performance threshold tests — ensures model meets minimum quality bar."""

    @pytest.fixture(autouse=True, scope="class")
    def ensure_model(self):
        from app.config import settings
        if not settings.MODEL_PATH.exists():
            from app.models.trainer import train_pipeline
            train_pipeline(save=True)

    def test_accuracy_above_floor(self):
        from app.models.classifier import load_metadata
        meta = load_metadata()
        assert meta is not None, "Run train.py first"
        assert meta["accuracy"] > 0.94, f"Accuracy {meta['accuracy']} below floor 0.94"

    def test_roc_auc_above_floor(self):
        from app.models.classifier import load_metadata
        meta = load_metadata()
        assert meta["roc_auc"] > 0.98, f"ROC-AUC {meta['roc_auc']} below floor 0.98"

    def test_f1_above_floor(self):
        from app.models.classifier import load_metadata
        meta = load_metadata()
        assert meta["f1_weighted"] > 0.93
