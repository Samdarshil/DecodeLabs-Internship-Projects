"""
app/services/validation.py — Input/output schemas without pydantic.
Uses Python dataclasses + manual field validation for portability.
"""
from __future__ import annotations
from dataclasses import dataclass, field, fields, asdict
from typing import Optional, List


# ── Feature order (must match sklearn breast cancer feature order) ─────────
FEATURE_ORDER = [
    "radius_mean", "texture_mean", "perimeter_mean", "area_mean",
    "smoothness_mean", "compactness_mean", "concavity_mean",
    "concave_points_mean", "symmetry_mean", "fractal_dimension_mean",
    "radius_se", "texture_se", "perimeter_se", "area_se",
    "smoothness_se", "compactness_se", "concavity_se",
    "concave_points_se", "symmetry_se", "fractal_dimension_se",
    "radius_worst", "texture_worst", "perimeter_worst", "area_worst",
    "smoothness_worst", "compactness_worst", "concavity_worst",
    "concave_points_worst", "symmetry_worst", "fractal_dimension_worst",
]

# ── Validation ranges (min, max) ─────────────────────────────────────────────
FEATURE_RANGES = {
    "radius_mean":             (0.0, 30.0),
    "texture_mean":            (0.0, 40.0),
    "perimeter_mean":          (0.0, 200.0),
    "area_mean":               (0.0, 2600.0),
    "smoothness_mean":         (0.0, 0.25),
    "compactness_mean":        (0.0, 0.40),
    "concavity_mean":          (0.0, 0.45),
    "concave_points_mean":     (0.0, 0.22),
    "symmetry_mean":           (0.0, 0.35),
    "fractal_dimension_mean":  (0.0, 0.10),
    "radius_se":               (0.0, 3.0),
    "texture_se":              (0.0, 5.0),
    "perimeter_se":            (0.0, 22.0),
    "area_se":                 (0.0, 550.0),
    "smoothness_se":           (0.0, 0.02),
    "compactness_se":          (0.0, 0.14),
    "concavity_se":            (0.0, 0.40),
    "concave_points_se":       (0.0, 0.06),
    "symmetry_se":             (0.0, 0.08),
    "fractal_dimension_se":    (0.0, 0.03),
    "radius_worst":            (0.0, 40.0),
    "texture_worst":           (0.0, 52.0),
    "perimeter_worst":         (0.0, 260.0),
    "area_worst":              (0.0, 4300.0),
    "smoothness_worst":        (0.0, 0.24),
    "compactness_worst":       (0.0, 1.10),
    "concavity_worst":         (0.0, 1.30),
    "concave_points_worst":    (0.0, 0.32),
    "symmetry_worst":          (0.0, 0.70),
    "fractal_dimension_worst": (0.0, 0.22),
}

EXAMPLE_MALIGNANT = {
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


def validate_prediction_input(data: dict) -> tuple[list[float], list[str]]:
    """
    Validate a prediction input dict.
    Returns (feature_array, errors). If errors is non-empty, input is invalid.
    """
    errors = []
    features = []

    for fname in FEATURE_ORDER:
        if fname not in data:
            errors.append(f"Missing required feature: {fname}")
            features.append(0.0)
            continue

        try:
            val = float(data[fname])
        except (TypeError, ValueError):
            errors.append(f"{fname}: must be a number")
            features.append(0.0)
            continue

        lo, hi = FEATURE_RANGES[fname]
        if val < lo or val > hi:
            errors.append(f"{fname}={val} outside valid range [{lo}, {hi}]")

        features.append(val)

    return features, errors
