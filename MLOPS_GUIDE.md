# MLOps Guide — Phishing Detection System

> **All tools are 100% free & open-source.** No paid services required.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MLOps Pipeline                           │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐ │
│  │  Data     │──▶│ Training │──▶│ Evaluate │──▶│ Deploy  │ │
│  │ Validate  │   │ + Track  │   │ + Gates  │   │ + Serve │ │
│  └──────────┘   └──────────┘   └──────────┘   └─────────┘ │
│       │              │              │              │        │
│       ▼              ▼              ▼              ▼        │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐ │
│  │  Great    │   │  MLflow  │   │ Quality  │   │ Model   │ │
│  │ Expect.   │   │ Tracking │   │  Gates   │   │Registry │ │
│  └──────────┘   └──────────┘   └──────────┘   └─────────┘ │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────────────┐│
│  │   DVC    │   │ Evidently│   │   GitHub Actions CI/CD   ││
│  │ Version  │   │   Drift  │   │                          ││
│  └──────────┘   └──────────┘   └──────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Tools Used (All Free)

| Tool | Purpose | Cost |
|------|---------|------|
| **DVC** | Data & model versioning, pipeline orchestration | Free |
| **MLflow** | Experiment tracking, model registry | Free |
| **Evidently/SciPy** | Drift detection & monitoring | Free |
| **GitHub Actions** | CI/CD automation | Free (public repos) |
| **Matplotlib** | Training & evaluation plots | Free |

---

## Quick Start

### 1. Install MLOps Dependencies

```bash
make install-mlops
# or
pip install -r requirements-mlops.txt
```

### 2. Initialize DVC

```bash
make mlops-setup
# or
dvc init
```

### 3. Place Your Dataset

```bash
mkdir -p data
cp /path/to/phishing_dataset.csv data/phishing_dataset.csv
```

### 4. Run the Full Pipeline

```bash
# Option A: DVC pipeline (recommended)
dvc repro

# Option B: Individual steps
make validate-data   # Validate data quality
make train           # Train with MLflow tracking
make evaluate        # Run quality gates
make monitor         # Check for drift
```

---

## Pipeline Stages

### Stage 1: Data Validation

Validates your dataset before training:
- Minimum sample count (default: 1,000)
- Null value ratio (max 5%)
- Label value checks (binary: 0/1)
- Class balance (min 20% minority class)
- No constant features, no infinite values

```bash
make validate-data
# Output: reports/data_validation_report.json
```

### Stage 2: Model Training

Trains a Random Forest with full MLflow tracking:
- All hyperparameters logged
- Metrics (accuracy, F1, AUC, etc.) tracked
- Confusion matrix, ROC curve, feature importance plots
- Model artifact saved and registered

```bash
make train
# Output: models/phishing_rf_model.pkl, models/scaler.pkl
# MLflow: experiment run logged with all artifacts
```

### Stage 3: Model Evaluation

Evaluates the trained model against quality gates:
- Minimum accuracy ≥ 0.85
- Minimum precision ≥ 0.85
- Minimum recall ≥ 0.85
- Minimum F1 ≥ 0.85
- Minimum ROC-AUC ≥ 0.90

```bash
make evaluate
# Output: reports/evaluation_metrics.json
# Plots: reports/evaluation_plots/
```

### Stage 4: Drift Monitoring

Detects feature and prediction drift using KS tests:
- Feature distribution shifts
- Prediction distribution changes
- HTML report for visual inspection

```bash
make monitor
# Output: reports/drift_report.html, reports/drift_metrics.json
```

---

## MLflow Dashboard

View all experiments, compare runs, and manage models:

```bash
make mlflow-ui
# Open http://localhost:5000
```

### Compare Experiment Runs

```bash
make compare
```

### List Registered Models

```bash
make list-models
```

---

## Model Promotion

### Promote to Staging

```bash
make promote-staging
```

### Promote to Production (requires quality gate pass)

```bash
make promote
```

---

## Configuration

All parameters are in `params.yaml`:

```yaml
train:
  n_estimators: 200     # Number of trees
  max_depth: 20         # Max tree depth
  min_samples_split: 5  # Min samples to split
  test_size: 0.2        # Test split ratio
  cv_folds: 5           # Cross-validation folds

evaluation:
  min_accuracy: 0.85    # Quality gate thresholds
  min_f1: 0.85
  min_roc_auc: 0.90

monitoring:
  drift_threshold: 0.05 # p-value for drift detection
```

To modify parameters:

```bash
# Edit params.yaml, then re-run
dvc repro
```

DVC automatically detects parameter changes and re-runs only affected stages.

---

## CI/CD (GitHub Actions)

### CI Pipeline (`.github/workflows/ci.yml`)
- Runs on every push/PR
- Lint → Test → Security scan → Docker build

### ML Pipeline (`.github/workflows/ml-pipeline.yml`)
- Triggered manually or on training code changes
- Data validation → Train → Evaluate → Monitor → Deploy
- Quality gates must pass before production deployment

---

## Project Structure (MLOps additions)

```
phishing_app/
├── params.yaml                    # Hyperparameters & thresholds
├── dvc.yaml                       # Pipeline definition
├── requirements-mlops.txt         # MLOps dependencies
├── data/
│   └── phishing_dataset.csv       # Training data (DVC tracked)
├── models/
│   ├── phishing_rf_model.pkl      # Trained model (DVC tracked)
│   ├── scaler.pkl                 # Feature scaler (DVC tracked)
│   └── metrics.json               # Training metrics
├── reports/
│   ├── data_validation_report.json
│   ├── evaluation_metrics.json
│   ├── drift_report.html
│   ├── drift_metrics.json
│   ├── plots/                     # Training plots
│   └── evaluation_plots/          # Evaluation plots
├── mlruns/                        # MLflow tracking (local)
├── src/phishing/mlops/
│   ├── __init__.py
│   ├── config.py                  # MLOps configuration
│   ├── data_validation.py         # Data quality checks
│   ├── experiment_tracker.py      # MLflow wrapper
│   ├── train.py                   # Training pipeline
│   ├── evaluate.py                # Evaluation + quality gates
│   ├── monitor.py                 # Drift detection
│   └── promote.py                 # Model promotion
├── tests/
│   └── test_mlops.py              # MLOps tests
└── .github/workflows/
    ├── ci.yml                     # CI pipeline
    └── ml-pipeline.yml            # ML pipeline
```

---

## Workflow Summary

```
Developer makes changes
        │
        ▼
   Git Push / PR ──────────▶ CI Pipeline (auto)
        │                      ├── Lint
        │                      ├── Test
        │                      └── Security
        │
        ▼
   Data/Model changes ─────▶ ML Pipeline (manual/auto)
        │                      ├── Validate Data
        │                      ├── Train Model
        │                      ├── Evaluate (Quality Gates)
        │                      ├── Monitor Drift
        │                      └── Deploy (if gates pass)
        │
        ▼
   MLflow Dashboard ────────▶ Compare, Analyze, Promote
```
