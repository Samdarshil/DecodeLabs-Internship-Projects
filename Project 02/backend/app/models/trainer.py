"""
app/models/trainer.py — Reusable training pipeline (imported by train.py and /train endpoint).

Architecture decision: VotingClassifier (soft voting) over a single model because:
  1. Diversity: LR (linear) + RF (trees) + GB (boosted trees) cover different inductive biases
  2. Soft voting averages probabilities → better calibration than hard voting
  3. Robustness: error of one sub-model mitigated by the others
  4. Trade-off: ~3× slower training vs single RF; acceptable for this dataset size (569 rows)
"""
from __future__ import annotations

import json
import time
import joblib
import numpy as np
from pathlib import Path
from typing import Optional

from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    roc_auc_score,
    classification_report,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from app.config import settings
from app.utils.logging_config import get_logger

log = get_logger(__name__)


def build_estimators() -> list[tuple]:
    """
    Build the three sub-estimators for the voting classifier.

    Hyperparameter notes:
      - LR: max_iter=1000 prevents ConvergenceWarning on this dataset
      - RF: 200 trees balances bias-variance; class_weight='balanced' for slight imbalance
      - GB: n_estimators=200, lr=0.05 (conservative) to avoid overfitting
    """
    lr = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42,
        C=1.0,
    )
    rf = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        max_features="sqrt",
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    gb = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        random_state=42,
    )
    return [("lr", lr), ("rf", rf), ("gb", gb)]


def train_pipeline(
    test_size: float = 0.20,
    random_state: int = 42,
    save: bool = True,
) -> dict:
    """
    Full training pipeline:
      load → split → scale → train VotingClassifier → evaluate → save

    Args:
        test_size:    Fraction of data held out for final evaluation.
        random_state: RNG seed for reproducibility.
        save:         Whether to persist the model artifact to disk.

    Returns:
        Metrics dict with accuracy, f1, roc_auc, cv scores, etc.
    """
    log.info("training_start test_size=test_size, random_state=random_state")
    t_total = time.perf_counter()

    # ── Load data ─────────────────────────────────────────────
    data = load_breast_cancer()
    X, y = data.data, data.target

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # ── Scale ──────────────────────────────────────────────────
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # ── Train ──────────────────────────────────────────────────
    clf = VotingClassifier(
        estimators=build_estimators(),
        voting="soft",
        n_jobs=-1,
    )
    t_fit = time.perf_counter()
    clf.fit(X_train_s, y_train)
    fit_time = time.perf_counter() - t_fit

    # ── Evaluate ───────────────────────────────────────────────
    y_pred  = clf.predict(X_test_s)
    y_proba = clf.predict_proba(X_test_s)[:, 1]

    # Cross-validation on full (scaled) dataset
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    cv_scores = cross_val_score(
        VotingClassifier(estimators=build_estimators(), voting="soft", n_jobs=-1),
        scaler.transform(X),
        y,
        cv=cv,
        scoring="accuracy",
    )

    metrics = {
        "version":          "1.0",
        "model_type":       "VotingClassifier",
        "sub_models":       ["LogisticRegression", "RandomForest", "GradientBoosting"],
        "accuracy":         round(float(accuracy_score(y_test, y_pred)), 4),
        "f1_weighted":      round(float(f1_score(y_test, y_pred, average="weighted")), 4),
        "f1_macro":         round(float(f1_score(y_test, y_pred, average="macro")), 4),
        "roc_auc":          round(float(roc_auc_score(y_test, y_proba)), 4),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "cv_accuracy_std":  round(float(cv_scores.std()), 4),
        "train_samples":    len(X_train),
        "test_samples":     len(X_test),
        "fit_time_seconds": round(fit_time, 2),
        "total_time_seconds": round(time.perf_counter() - t_total, 2),
        "feature_names":    list(data.feature_names),
        "target_names":     list(data.target_names),
        "classification_report": classification_report(
            y_test, y_pred, target_names=data.target_names, output_dict=True
        ),
    }

    log.info("training_complete")

    # ── Save ───────────────────────────────────────────────────
    if save:
        settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)

        bundle = {
            "model":        clf,
            "scaler":       scaler,
            "feature_names": list(data.feature_names),
            "target_names":  list(data.target_names),
        }
        joblib.dump(bundle, settings.MODEL_PATH, compress=3)

        meta_path = settings.METADATA_PATH
        with open(meta_path, "w") as f:
            json.dump(metrics, f, indent=2)

        log.info("model_saved path=str(settings.MODEL_PATH)")

    return metrics
