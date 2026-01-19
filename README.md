<div align="center">

# 🛡️ Phishing Detection System

[![CI](https://github.com/mukeshkumarreddy/phishing_app/actions/workflows/ci.yml/badge.svg)](https://github.com/mukeshkumarreddy/phishing_app/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Real-time phishing URL detection with FastAPI, Streamlit UI, and a production-ready ML pipeline.

</div>

## Overview
- **ML Classifier**: Random Forest model using 30 lexical URL features
- **Dual Interfaces**: FastAPI for production use, Streamlit for interactive demo
- **Security-First**: Strict input validation, structured logging, safe error handling
- **Production Ready**: Docker, CI/CD pipeline, comprehensive tests, type checking, linting
- **Clean Deployment**: Repository optimized for GitHub and cloud deployment

## Quickstart

### Prerequisites
- Python 3.8+
- pip or conda

### Installation
```bash
git clone https://github.com/mukeshkumarreddy/phishing_app.git
cd phishing_app
python -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run API (FastAPI)
```bash
python run_api.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Run UI (Streamlit)
```bash
python run_ui.py
# UI: http://localhost:8501
```

### Run Tests
```bash
PYTHONPATH=. pytest tests/ -v --override-ini="addopts="
```

## Project Structure
```
phishing_app/
├── src/phishing/                   # Main package
│   ├── api/
│   │   └── server.py              # FastAPI application and endpoints
│   ├── core/
│   │   ├── detector.py            # Prediction pipeline
│   │   ├── feature_extractor.py   # URL feature extraction
│   │   └── model_loader.py        # Safe model and scaler loading
│   ├── config/
│   │   └── settings.py            # Configuration management
│   ├── models/
│   │   └── schemas.py             # Pydantic request/response schemas
│   ├── ui/
│   │   └── app.py                 # Streamlit web interface
│   └── utils/
│       ├── logging_config.py      # Logging setup
│       └── validators.py          # Input validation utilities
├── tests/                          # Pytest test suite
│   ├── test_api.py
│   ├── test_feature_extraction.py
│   ├── test_model_loader.py
│   └── test_validators.py
├── models/
│   ├── phishing_rf_model.pkl      # Trained Random Forest model
│   └── scaler.pkl                 # Feature scaler
├── docker-compose.yml             # Multi-container setup
├── Dockerfile                      # API deployment container
├── Dockerfile.streamlit            # UI deployment container
├── Makefile                        # Common development commands
├── DEPLOYMENT.md                   # Deployment guide
├── AWS_DEPLOYMENT_GUIDE.md         # AWS-specific setup
├── SECURITY.md                     # Security best practices
├── ARCHITECTURE.md                 # Architecture documentation
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
└── README.md                       # This file
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Single URL Prediction
```bash
curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.google.com"}'
```

### Batch Prediction
```bash
curl -X POST http://localhost:8000/predict-batch \
    -H "Content-Type: application/json" \
    -d '{"urls": ["https://www.google.com", "http://example.com"]}'
```

## Docker Deployment

### Build and Run
```bash
docker build -t phishing-app .
docker run -p 8000:8000 phishing-app
```

### Docker Compose (API + UI)
```bash
docker-compose up -d
# API: http://localhost:8000
# UI: http://localhost:8501
```

## Performance Metrics
- **Single Prediction**: ~50–100ms
- **Batch (3 URLs)**: ~100–150ms
- **Model Startup**: ~2.2s



## Deployment

### Free Deployment Options ✅
Deploy at zero cost:
- **Railway** - API + UI with $5/month free credits (covers both services)
- **Streamlit Cloud** - Free UI hosting (no backend)
- **Oracle Cloud** - Always-free tier with VM instances
- **Render** - Free tier for FastAPI apps
- **Docker locally** - Run on your machine

📖 **See [FREE_DEPLOYMENT_STEPS.md](FREE_DEPLOYMENT_STEPS.md)** for complete step-by-step guides for each platform!

### AWS Deployment (Paid Option)
For production with auto-scaling:
- See [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) for ECR, ECS, ALB setup
- Quick deploy: `./deploy-to-aws.sh`

### Local Docker Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed procedures.

## Contributing
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- All pull requests must pass tests: `pytest tests/ -v`
- Code formatting: `black src/ tests/`
- Linting: `pylint src/`

## Security
Please review [SECURITY.md](SECURITY.md) for security best practices and vulnerability reporting procedures.

## License
MIT — see [LICENSE](LICENSE).
