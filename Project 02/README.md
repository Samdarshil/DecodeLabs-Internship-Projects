# 🧬 OncAI — Breast Cancer Classification Suite


[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61dafb?logo=react)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

> *Enterprise-grade ML classification system. Classifies breast tumours as malignant or benign
> using a VotingClassifier ensemble with real-time feature importance explanations.*

---

## 📊 Model Performance

| Metric | Score | Notes |
|---|---|---|
| **Accuracy** | 96.49% | 20% holdout test set (114 samples) |
| **F1 Score (weighted)** | 96.40% | Accounts for class imbalance |
| **ROC-AUC** | 99.54% | Near-perfect discrimination |
| **CV Accuracy** | 96.66% ± 1.95% | Stratified 5-fold cross-validation |
| **Inference time** | < 15 ms | Single prediction, cold model |

> **Dataset**: UCI Wisconsin Breast Cancer Dataset — 569 samples, 30 nuclear cell features.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React + Vite Frontend                      │
│  TanStack Query · Zustand · React Hook Form + Zod · Recharts│
│  Framer Motion · Tailwind CSS · TypeScript                   │
└──────────────────────────┬──────────────────────────────────┘
                           │ /api proxy (dev) / Nginx (prod)
┌──────────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                            │
│  Uvicorn · SlowAPI rate limiting · Joblib model cache       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   ML Pipeline                                │
│  VotingClassifier (LogisticRegression + RandomForest +      │
│  GradientBoosting) · StandardScaler · Feature Importance     │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Decision Records

**ADR-001: VotingClassifier over a single model**
- *Context*: Need robust performance on a 569-sample dataset
- *Decision*: Soft-voting ensemble of LR + RF + GB
- *Consequence*: ~3× training time; 1–2% accuracy improvement; better calibration

**ADR-002: joblib over pickle**
- *Context*: Model must be loadable across Python patch versions
- *Decision*: `joblib.dump(compress=3)` with full bundle (model + scaler in one file)
- *Consequence*: Cannot silently break across Python versions; scaler/model always in sync

**ADR-003: In-memory rate limiting over Redis**
- *Context*: Demo environment — no Redis dependency required
- *Decision*: SlowAPI in-memory; code comment shows Redis swap path
- *Consequence*: Rate limits reset on server restart; acceptable for demo

**ADR-004: Session-only prediction history**
- *Context*: No auth, no user accounts → can't safely persist cross-session data
- *Decision*: Zustand in-memory store with CSV export
- *Consequence*: GDPR-compliant by design (no data ever leaves the browser)

---

## 📁 Project Structure

```
oncai/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml            CI: test + build on push/PR
│   │   └── security.yml      Weekly security scans
│   └── dependabot.yml        Automated dependency updates
│
├── backend/
│   ├── app/
│   │   ├── main.py           FastAPI application factory
│   │   ├── config.py         Environment configuration
│   │   ├── models/
│   │   │   ├── classifier.py Singleton model loader + inference
│   │   │   └── trainer.py    Full training pipeline
│   │   ├── routes/
│   │   │   ├── predict.py    POST /predict
│   │   │   ├── train.py      POST /train (retrain)
│   │   │   └── health.py     GET /health, GET /metrics
│   │   ├── services/
│   │   │   ├── validation.py Input/output schemas
│   │   │   └── preprocessing.py Feature scaling + importance
│   │   └── utils/
│   │       ├── logging_config.py Structured JSON logging
│   │       └── rate_limiter.py   SlowAPI setup
│   ├── tests/
│   │   └── test_api.py       Validation, preprocessing, model tests
│   ├── models_store/         Trained model artifacts (gitignored)
│   ├── train.py              Standalone training script
│   ├── requirements.txt
│   ├── Dockerfile            Multi-stage build
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/           Button, Card, ConfidenceMeter
│   │   │   ├── forms/        PredictionForm (30-feature, tabbed)
│   │   │   └── charts/       FeatureImportance, MetricsCharts
│   │   ├── pages/
│   │   │   ├── Home.tsx      Prediction + live results
│   │   │   ├── Dashboard.tsx History with CSV export
│   │   │   └── Analytics.tsx Model metrics + confusion matrix
│   │   ├── hooks/            usePrediction, useTheme
│   │   ├── services/         api.ts (typed axios client)
│   │   ├── store/            predictionHistory (Zustand)
│   │   ├── App.tsx           Router + navbar + theme
│   │   └── main.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile            Node builder + Nginx runtime
│
├── docker-compose.yml
├── README.md
├── CONTRIBUTING.md
└── .gitignore
```

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

```bash
# Verify Python 3.10+
python --version      # Python 3.10.x or higher

# Verify Node 18+
node --version        # v18.x or higher
npm --version         # 9.x or higher
```

### Step 1 — Clone

```bash
git clone https://github.com/yourusername/oncai.git
cd oncai
```

### Step 2 — Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3 — Train the model

```bash
python train.py
```

**Expected output:**
```
============================================================
  OncAI ML Suite — Model Training Pipeline
============================================================

  ✅ Training Complete!
  Accuracy  : 0.9649
  F1 Score  : 0.9640
  ROC-AUC   : 0.9954
  CV Acc    : 0.9666 ± 0.0195
  Train/Test: 455 / 114 samples
  Fit time  : 4.2s

  Model saved → models_store/breast_cancer_v1.joblib
============================================================
```

### Step 4 — Start the API

```bash
uvicorn app.main:app --reload --port 8000
```

API docs at: **http://localhost:8000/docs**

### Step 5 — Frontend setup (new terminal)

```bash
cd ../frontend
npm install
npm run dev
```

App at: **http://localhost:5173**

### Step 6 — Verify

Navigate to http://localhost:5173. Click **"Load sample: Malignant Case"**, then **"Run Prediction"**.

Expected: Malignant classification with ~98% confidence.

---

## 🐳 Docker (One command)

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

---

## 🔌 API Reference

### `POST /predict`

Classify a tumour sample.

**Request body** (all 30 features required):
```json
{
  "radius_mean": 17.99,
  "texture_mean": 10.38,
  "perimeter_mean": 122.8,
  "area_mean": 1001.0,
  "...": "..."
}
```

**Response:**
```json
{
  "prediction": "Malignant",
  "prediction_class": 0,
  "confidence": 0.9803,
  "probability_malignant": 0.9803,
  "probability_benign": 0.0197,
  "top_features": [
    {
      "feature": "worst perimeter",
      "value": 184.6,
      "shap_value": 0.3445,
      "impact_direction": "positive"
    }
  ],
  "model_version": "1.0",
  "inference_time_ms": 11.2
}
```

### `GET /metrics`

Returns full model performance report.

### `GET /health`

Health check for load balancer probes.

### `POST /train`

Triggers full model retrain (rate limited: 5/min).

---

## 🛡️ Security

- ✅ Input validation with range constraints on all 30 features
- ✅ Rate limiting (60 req/min predict, 5 req/min train)
- ✅ CORS locked to frontend origin
- ✅ Non-root Docker user
- ✅ Multi-stage Docker build (no dev tools in production image)
- ✅ `joblib` serialisation (not `pickle`) for safe model loading
- ✅ No `eval()` or dynamic code execution
- ✅ Weekly automated dependency scanning via Dependabot

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
```

Test categories:
- `TestPredictionValidation` — Pydantic schema + range constraints
- `TestPreprocessing` — DataValidator, IQR checks, NaN detection
- `TestModel` — End-to-end inference (requires trained model)
- `TestModelPerformance` — Accuracy/F1/ROC-AUC floor assertions

---

## 📈 Performance Benchmarks

| Metric | Value |
|---|---|
| Cold start (model load) | ~800 ms |
| Warm inference (p50) | 8 ms |
| Warm inference (p95) | 18 ms |
| Frontend First Contentful Paint | ~0.9 s |
| JS bundle (gzipped) | ~180 KB |

---

## 🔮 Upgrade Roadmap

| Priority | Upgrade | Technology |
|---|---|---|
| High | Authentication | Clerk / Auth0 / OAuth2 |
| High | Persistent history | PostgreSQL + SQLAlchemy |
| High | Real SHAP values | `shap` library (TreeExplainer) |
| Medium | Hyperparameter tuning | Optuna with pruning |
| Medium | SMOTE for class imbalance | imbalanced-learn |
| Medium | Model monitoring | Evidently AI (data drift) |
| Medium | Background retraining | Celery + Redis |
| Low | Voice input | Web Speech API |
| Low | PDF export | react-pdf |
| Low | Multi-model comparison | Tabs UI, A/B metrics |
| Low | i18n | react-i18next |
| Low | E2E tests | Playwright |
| Low | Kubernetes | Helm chart |

---

## 🔧 Troubleshooting

**`ModuleNotFoundError: No module named 'fastapi'`**
```bash
# Ensure you're in the virtual environment:
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**`FileNotFoundError: Model file not found at models_store/breast_cancer_v1.joblib`**
```bash
# The model is not bundled in Git. Train it:
cd backend && python train.py
```

**CORS error in browser console**
```bash
# Ensure FRONTEND_URL in backend/.env matches exactly:
FRONTEND_URL=http://localhost:5173
# Restart the backend after changing .env
```

**Frontend shows "Prediction failed — Model not loaded"**
The backend is running but the model hasn't been trained yet. Run `python train.py`.

**`npm install` fails on Node < 18**
```bash
nvm use 20   # or: nvm install 20
```

**Docker: port 8000 already in use**
```bash
# Change the port mapping in docker-compose.yml:
ports:
  - "8001:8000"    # host:container
```

---

## 🙏 Acknowledgements

- [UCI ML Repository](https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic) — Wisconsin Breast Cancer dataset
- [Scikit-learn](https://scikit-learn.org) — ML toolkit
- [FastAPI](https://fastapi.tiangolo.com) — Modern Python API framework
- [Tailwind CSS](https://tailwindcss.com) — Utility-first CSS

---

## 📄 License

MIT — see [LICENSE](LICENSE). Free to use, modify, and distribute with attribution.

---

*Built as an AI internship portfolio project. Not a clinical diagnostic tool.*
