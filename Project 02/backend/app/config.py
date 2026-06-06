"""app/config.py — Simple config via os.environ with sensible defaults."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/


class Settings:
    APP_NAME    = "Breast Cancer Prediction API"
    APP_VERSION = "1.0.0"
    DEBUG       = os.getenv("DEBUG", "false").lower() == "true"

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    ALLOWED_ORIGINS = [
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:3000",
    ]

    MODEL_DIR  = Path(os.getenv("MODEL_DIR",  str(BASE_DIR / "models_store")))
    MODEL_FILE = os.getenv("MODEL_FILE", "breast_cancer_v1.joblib")
    META_FILE  = os.getenv("META_FILE",  "metadata.json")

    @property
    def MODEL_PATH(self): return self.MODEL_DIR / self.MODEL_FILE
    @property
    def METADATA_PATH(self): return self.MODEL_DIR / self.META_FILE

    RATE_LIMIT_PREDICT = "60/minute"
    RATE_LIMIT_TRAIN   = "5/minute"
    LOG_LEVEL          = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
