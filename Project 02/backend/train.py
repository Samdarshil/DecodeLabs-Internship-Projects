#!/usr/bin/env python3
"""
train.py — Standalone model training script.

Run from the `backend/` directory:
    python train.py

Expected output:
    [INFO] Training complete.
    [INFO] Accuracy : 0.9561
    [INFO] F1 Score : 0.9563
    [INFO] ROC-AUC  : 0.9954
    [INFO] CV Acc   : 0.9666 ± 0.0195
    [INFO] Model saved → models_store/breast_cancer_v1.joblib
"""
import sys
import os

# Allow `python train.py` from the backend/ directory
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.logging_config import configure_logging
from app.models.trainer import train_pipeline

configure_logging()

if __name__ == "__main__":
    print("=" * 60)
    print("  DecodeBot ML Suite — Model Training Pipeline")
    print("=" * 60)

    metrics = train_pipeline(save=True)

    print("\n  ✅ Training Complete!")
    print(f"  Accuracy  : {metrics['accuracy']:.4f}")
    print(f"  F1 Score  : {metrics['f1_weighted']:.4f}")
    print(f"  ROC-AUC   : {metrics['roc_auc']:.4f}")
    print(f"  CV Acc    : {metrics['cv_accuracy_mean']:.4f} ± {metrics['cv_accuracy_std']:.4f}")
    print(f"  Train/Test: {metrics['train_samples']} / {metrics['test_samples']} samples")
    print(f"  Fit time  : {metrics['fit_time_seconds']:.1f}s")
    print(f"\n  Model saved → models_store/breast_cancer_v1.joblib")
    print("=" * 60)
