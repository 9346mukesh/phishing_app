<div align="center">

# 🛡️ Phishing URL Detector — AI-Powered Cybersecurity Tool

### 🔍 Real-time Phishing URL Detection using Machine Learning

<p>
  <a href="https://phishingapp-hhdc4h28pyjxhvcwcdjqgc.streamlit.app/">
    <img src="https://img.shields.io/badge/🌐_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo">
  </a>
  <a href="https://github.com/9346mukesh/phishing_app">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/MLOps-DVC%20%2B%20MLflow-blue?style=flat-square" alt="MLOps">
</p>

<p><i>A production-grade ML system that analyzes URLs in real-time to detect phishing attempts using a Random Forest classifier trained on 30 engineered features.</i></p>

</div>

---

## 🌐 Live Demo

> **Try it now →** [https://phishingapp-hhdc4h28pyjxhvcwcdjqgc.streamlit.app](https://phishingapp-hhdc4h28pyjxhvcwcdjqgc.streamlit.app/)

Paste any URL and get instant phishing analysis with confidence scores — no installation required!

---

## 📌 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation & Setup](#-installation--setup)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [MLOps Pipeline](#-mlops-pipeline)
- [Project Structure](#-project-structure)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Model Performance](#-model-performance)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)
- [Contact](#-contact)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Real-Time Detection** | Instantly classify any URL as safe or phishing |
| 🧠 **30 Engineered Features** | URL length, special characters, domain analysis, IP detection, and more |
| 🌐 **Modern Web UI** | Beautiful Streamlit interface with gradient design and real-time feedback |
| ⚡ **REST API** | FastAPI backend with batch prediction, health checks, and OpenAPI docs |
| 📊 **MLOps Pipeline** | Automated training, evaluation, and monitoring with DVC + MLflow |
| 🔄 **Drift Detection** | Automatic data drift monitoring using statistical tests |
| 🧪 **Comprehensive Testing** | 62+ tests covering API, features, model loading, and MLOps |
| 🚀 **One-Click Deploy** | Ready for Streamlit Cloud, Render, or Docker deployment |
| 🔒 **Standalone Mode** | UI works independently without API — loads model directly |

---

## 🛠️ Tech Stack

<table>
  <tr>
    <th>Category</th>
    <th>Technology</th>
  </tr>
  <tr>
    <td>🤖 Machine Learning</td>
    <td>scikit-learn, Random Forest, StandardScaler</td>
  </tr>
  <tr>
    <td>🌐 Backend API</td>
    <td>FastAPI, Uvicorn, Pydantic</td>
  </tr>
  <tr>
    <td>🎨 Frontend UI</td>
    <td>Streamlit (with custom CSS)</td>
  </tr>
  <tr>
    <td>📦 MLOps</td>
    <td>DVC (pipeline), MLflow (experiment tracking)</td>
  </tr>
  <tr>
    <td>🧪 Testing</td>
    <td>pytest, pytest-cov, pytest-asyncio</td>
  </tr>
  <tr>
    <td>🐳 Containerization</td>
    <td>Docker</td>
  </tr>
  <tr>
    <td>⚙️ CI/CD</td>
    <td>GitHub Actions</td>
  </tr>
  <tr>
    <td>🔧 Feature Engineering</td>
    <td>tldextract, urllib, regex, socket</td>
  </tr>
  <tr>
    <td>🐍 Language</td>
    <td>Python 3.9+</td>
  </tr>
</table>

---

## 🏗️ Architecture

```
┌──────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│   URL Input  │────▶│  Feature Extraction  │────▶│  StandardScaler  │
│              │     │   (30 Features)      │     │                  │
└──────────────┘     └─────────────────────┘     └────────┬─────────┘
                                                          │
                     ┌─────────────────────┐              ▼
                     │    Prediction +      │◀────┌──────────────────┐
                     │    Confidence Score  │     │  Random Forest   │
                     └─────────────────────┘     │   Classifier     │
                                                 └──────────────────┘
```

### How It Works

1. **URL Input** — User submits a URL via Web UI or REST API
2. **Feature Extraction** — 30 features are engineered from the URL structure:
   - IP address detection, URL length, shortening service check
   - Special character counts (`@`, `-`, `//`, `.`)
   - Domain registration details, HTTPS usage, subdomain analysis
   - Suspicious keyword patterns, port analysis, path depth
3. **Preprocessing** — Features are scaled using a trained `StandardScaler`
4. **Classification** — Random Forest model predicts `Safe` or `Phishing`
5. **Response** — Returns prediction label with confidence percentage

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/9346mukesh/phishing_app.git
cd phishing_app
```

### Step 2: Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# For MLOps features (optional)
pip install -r requirements-mlops.txt
```

### Step 3: Run the Application

```bash
# Option A: Run Streamlit Web UI
python run_ui.py
# Opens at http://localhost:8501

# Option B: Run FastAPI Server
python run_api.py
# API at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## 💡 Usage

### Web Interface

1. Open the Streamlit app at `http://localhost:8501`
2. Paste any URL in the input field
3. Click **Analyze** to get instant results
4. View the prediction (Safe ✅ / Phishing 🚨) with confidence score

### Batch Analysis

Upload a text file with multiple URLs to analyze them all at once through the web UI.

---

## 📡 API Reference

### Health Check

```bash
curl http://localhost:8000/health
```

```json
{"status": "healthy", "model_loaded": true}
```

### Single URL Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

```json
{
  "url": "https://google.com",
  "is_phishing": false,
  "confidence": 0.98,
  "risk_level": "Low"
}
```

### Batch Prediction

```bash
curl -X POST http://localhost:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": [{"url": "https://google.com"}, {"url": "http://suspicious-login.xyz"}]}'
```

> 📖 Full API documentation available at `http://localhost:8000/docs` (Swagger UI)

---

## 🔬 MLOps Pipeline

This project includes a complete MLOps setup using **DVC** and **MLflow**.

### Pipeline Stages

```
validate_data  →  train  →  evaluate  →  monitor
     │               │          │            │
     ▼               ▼          ▼            ▼
  Data quality    Train RF    Metrics    Drift detection
  checks          model      & reports   (KS-test)
```

### Commands

```bash
# Run full ML pipeline
dvc repro

# View model metrics
dvc metrics show

# Start MLflow experiment tracking UI
mlflow ui
# Opens at http://localhost:5000

# Individual stages
make train          # Train model
make evaluate       # Evaluate model
make monitor        # Check data drift
make pipeline       # Run full DVC pipeline
```

### CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push / PR | Linting, testing, code quality |
| `ml-pipeline.yml` | Data/code changes | Automated model retraining |

---

## 📁 Project Structure

```
phishing_app/
│
├── 📄 app.py                       # Streamlit Cloud entry point
├── 📄 run_api.py                   # FastAPI launcher
├── 📄 run_ui.py                    # Streamlit launcher
│
├── 📂 src/phishing/                # Main source code
│   ├── 📂 api/
│   │   └── server.py              # FastAPI REST endpoints
│   ├── 📂 core/
│   │   ├── detector.py            # PhishingDetector engine
│   │   ├── feature_extractor.py   # 30 URL feature extraction
│   │   └── model_loader.py        # Model loading utilities
│   ├── 📂 config/
│   │   └── settings.py            # App configuration
│   ├── 📂 models/
│   │   └── schemas.py             # Pydantic request/response models
│   ├── 📂 ui/
│   │   └── app.py                 # Streamlit web interface
│   ├── 📂 utils/
│   │   ├── logging_config.py      # Structured logging
│   │   └── validators.py          # URL validation
│   └── 📂 mlops/
│       ├── train.py               # Training pipeline
│       ├── evaluate.py            # Model evaluation
│       ├── monitor.py             # Data drift detection
│       ├── data_validation.py     # Data quality checks
│       ├── experiment_tracker.py  # MLflow integration
│       └── promote.py             # Model promotion logic
│
├── 📂 models/                      # Trained model artifacts
│   ├── phishing_rf_model.pkl      # Random Forest model
│   └── scaler.pkl                 # Feature scaler
│
├── 📂 data/                        # Training dataset (DVC tracked)
├── 📂 tests/                       # Test suite (62+ tests)
├── 📂 .github/workflows/           # CI/CD pipelines
│
├── 📄 dvc.yaml                     # DVC pipeline definition
├── 📄 params.yaml                  # Model hyperparameters
├── 📄 requirements.txt             # Production dependencies
├── 📄 requirements-streamlit.txt   # Streamlit Cloud dependencies
├── 📄 requirements-mlops.txt       # MLOps dependencies
├── 📄 Dockerfile                   # Container config
├── 📄 render.yaml                  # Render.com deployment
├── 📄 Makefile                     # Dev commands
├── 📄 pyproject.toml               # Project metadata
└── 📄 LICENSE                      # MIT License
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/phishing --cov-report=html

# Run specific test modules
pytest tests/test_api.py                # API endpoint tests
pytest tests/test_feature_extraction.py # Feature extraction tests
pytest tests/test_model_loader.py       # Model loading tests
pytest tests/test_validators.py         # URL validation tests
pytest tests/test_mlops.py              # MLOps pipeline tests
```

---

## ☁️ Deployment

### Streamlit Community Cloud (Free — Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select repository → `app.py` → `requirements-streamlit.txt`
4. Deploy! 🚀

### Render.com

Automatically deploys the FastAPI backend using `render.yaml`.

### Docker

```bash
docker build -t phishing-api .
docker run -p 8000:8000 phishing-api
```

---

## 📊 Model Performance

| Metric | Score |
|--------|-------|
| **Accuracy** | 100% |
| **F1 Score** | 1.00 |
| **AUC-ROC** | 1.00 |
| **Features Used** | 30 |
| **Algorithm** | Random Forest |
| **Preprocessing** | StandardScaler |

---

## 🔮 Future Enhancements

- [ ] 🧠 Deep Learning model (LSTM/Transformer) for URL sequence analysis
- [ ] 📸 Screenshot-based visual phishing detection
- [ ] 🌍 Real-time threat intelligence API integration
- [ ] 📧 Email header analysis for phishing email detection
- [ ] 📱 Browser extension for real-time URL scanning
- [ ] 📊 Dashboard with historical analytics and trends
- [ ] 🔄 Active learning pipeline for continuous model improvement

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

<div align="center">

**Mukesh Kumar Reddy**

<a href="https://github.com/9346mukesh">
  <img src="https://img.shields.io/badge/GitHub-9346mukesh-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>

⭐ **If you found this project useful, please give it a star!** ⭐

</div>

---

<div align="center">
  <p><b>Built with ❤️ for Cybersecurity</b></p>
  <p><i>Protecting users from phishing attacks, one URL at a time.</i></p>
</div>
