# 🛡️ Phishing Website Detection System

A **production-grade** machine learning application for real-time phishing URL detection with REST API, containerization, comprehensive testing, and deployment automation.

## 📋 Table of Contents

- [⚡ Free Cloud Deployment (START HERE)](#-free-cloud-deployment-start-here)
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## ⚡ Free Cloud Deployment (START HERE)

Deploy your phishing detection system **completely free** to the cloud! Choose one of these options:

### Option 1: Railway.app (Recommended) ⭐ BEST

**Why:** Easiest setup, includes both API + UI, $5/month free credits (covers everything), great for beginners.

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### Step 2: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub account
3. Authorize Railway to access your repositories

#### Step 3: Deploy API Service
1. Click "New Project" → "Deploy from GitHub repo"
2. Select your `phishing_app` repository
3. Railway auto-detects it's Python
4. Set Environment Variable:
   ```
   PYTHONUNBUFFERED=1
   ```
5. In Settings, set Start Command:
   ```
   python run_api.py
   ```
6. Railway deploys! Your API URL appears in "Networking" section

#### Step 4: Deploy UI Service (Optional)
1. Click "New Service" → "GitHub Repo"
2. Same repo, but different start command:
   ```
   streamlit run src/phishing/ui/app.py --server.port 8501
   ```
3. Configure Streamlit to connect to your API URL

**Cost:** $0 (free $5/month credits cover both services)  
**Time:** ~10 minutes

---

### Option 2: Streamlit Cloud (UI Only - Free Forever) 🎨

**Why:** Completely free, UI only, zero cost forever, perfect for demos.

#### Step 1: Connect GitHub
1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign up with GitHub
3. Click "Deploy an app"

#### Step 2: Configure Deployment
```
Repository: your-phishing-app
Branch: main
File path: src/phishing/ui/app.py
```

#### Step 3: Add API Connection
In `src/phishing/ui/app.py`, update the API URL:
```python
API_URL = "https://your-railway-api.railway.app"  # Your Railway API URL
```

**Cost:** $0 (free forever)  
**Time:** ~5 minutes  
**Note:** Requires API deployed elsewhere (use Railway for API)

---

### Option 3: Oracle Cloud (Always-Free Tier) 🚀

**Why:** Completely free tier (no credit card required for always-free), full VM control.

#### Step 1: Create Oracle Account
1. Go to [oracle.com/cloud/free](https://www.oracle.com/cloud/free/)
2. Create account (no credit card for always-free resources)
3. Create a VM instance (always-free eligible: 2 cores, 1GB RAM)

#### Step 2: Connect via SSH
```bash
chmod 600 your-key.key
ssh ubuntu@your-instance-ip -i your-key.key
```

#### Step 3: Install & Deploy
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & Git
sudo apt install python3.10 python3-pip git -y

# Clone your repo
git clone https://github.com/yourusername/phishing_app.git
cd phishing_app

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run API
python run_api.py &  # Runs in background

# Run UI (optional)
streamlit run src/phishing/ui/app.py --server.port 8501 &
```

#### Step 4: Open Firewall Ports
```bash
# In Oracle Cloud Console:
# - VCN → Security Lists → Add Ingress Rule
# - Port 8000 (API) and 8501 (UI)
```

**Cost:** $0 (always-free tier)  
**Access:** `http://your-instance-ip:8000`

---

### Option 4: Render (Free Tier Available) 🎯

**Why:** Generous free tier, easy setup, auto-deploys on push.

#### Step 1: Create Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

#### Step 2: Deploy Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Name: `phishing-api`
4. Runtime: `Python 3`
5. Build command: `pip install -r requirements.txt`
6. Start command: `python run_api.py`
7. Instance Type: Free
8. Deploy!

**Cost:** Free tier available  
**Limitation:** Spins down after 15 mins of inactivity

---

### Option 5: Fly.io (Free Tier) 🛫

**Why:** Great for Docker apps, generous free tier, fast.

#### Step 1: Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
```

#### Step 2: Launch App
```bash
flyctl launch
```

Follow prompts to create app.

#### Step 3: Deploy
```bash
flyctl deploy
```

**Cost:** $0 (generous free tier)

---

## Quick Comparison Table

| Platform | API | UI | Cost | Setup Time | Pros | Cons |
|----------|-----|----|----|------|----|------|
| **Railway** | ✅ | ✅ | Free ($5 credits) | 10min | Easiest, both services | Requires credits |
| **Streamlit Cloud** | ❌ | ✅ | $0 | 5min | Free forever, easy | UI only |
| **Oracle Cloud** | ✅ | ✅ | $0 | 15min | Full control, free | More setup |
| **Render** | ✅ | ✅ | Free tier | 10min | Easy, fast builds | Spins down |
| **Fly.io** | ✅ | ✅ | Free tier | 10min | Docker optimized | New platform |

---

## Environment Variables for Cloud Deployment

Create `.env` file or set in platform settings:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Model Configuration  
MODEL_PATH=models/phishing_rf_model.pkl
SCALER_PATH=models/scaler.pkl

# Optional: For production monitoring
SENTRY_DSN=your-sentry-url-if-using
```

---

## Troubleshooting Free Deployments

### Railway Issues
- **Port binding error**: Railway uses PORT env var. Ensure `run_api.py` uses `os.getenv("PORT", 8000)`
- **Module not found**: Add all dependencies to `requirements.txt`
- **Memory limit**: Free tier has 5GB RAM, usually sufficient

### Streamlit Cloud Issues
- **API connection fails**: Check firewall, use HTTPS URLs
- **Timeout**: Increase timeout in `streamlit run` command

### Oracle Cloud Issues
- **SSH connection denied**: Check security group rules
- **Port not accessible**: Open firewall ports in VCN settings

---

## Overview

Phishing is one of the most prevalent cybersecurity threats. This project provides:

- **ML-Powered Detection**: Random Forest classifier analyzing 30 lexical features with ~95.2% accuracy
- **Production-Ready**: FastAPI server with comprehensive error handling and monitoring
- **Multiple Interfaces**: REST API + Streamlit UI for demos
- **Enterprise-Grade**: Security validation, structured logging, CI/CD pipeline, comprehensive tests
- **Industry Standards**: Type hints, linting, pre-commit hooks, Docker containerization

The system analyzes URL structure and characteristics without accessing page content, making it fast, safe, and scalable.

## Key Features

✅ **Real-time Analysis**: Instant classification of URLs
✅ **Feature Engineering**: 30 distinct lexical features extraction
✅ **ML-Powered**: Random Forest (~95.2% accuracy)
✅ **Secure**: Input validation, safe error handling, checksum verification
✅ **Production API**: FastAPI with health checks, error handling, batch predictions
✅ **Containerized**: Multi-stage Docker builds, Docker Compose for orchestration
✅ **Tested**: Comprehensive pytest suite with 80%+ coverage
✅ **CI/CD**: GitHub Actions for automated testing and Docker builds
✅ **Observable**: Structured JSON logging, Prometheus metrics
✅ **Documented**: API docs, deployment guides, architecture decisions

## System Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Input (URL)                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │ Input Validation    │
          │ • URL format check  │
          │ • Length limits     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ Feature Extraction  │
          │ • Lexical analysis  │
          │ • DNS lookup        │
          │ • 30 features       │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ Feature Scaling     │
          │ • StandardScaler    │
          │ • Normalization     │
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │ ML Inference        │
          │ • Random Forest     │
          │ • Prediction        │
          │ • Confidence        │
          └──────────┬──────────┘
                     │
┌────────────────────▼────────────────────┐
│ Response (JSON)                         │
│ • Prediction (0 or 1)                   │
│ • Confidence score                      │
│ • Human-readable label                  │
└─────────────────────────────────────────┘
```

### Project Structure

```
phishing_app/
├── src/phishing/                    # Main application package
│   ├── api/                         # FastAPI server
│   │   ├── __init__.py
│   │   └── server.py               # API endpoints
│   ├── core/                        # Core logic
│   │   ├── __init__.py
│   │   ├── detector.py             # Main detector class
│   │   ├── feature_extractor.py    # Feature extraction
│   │   └── model_loader.py         # Secure model loading
│   ├── ui/                         # Streamlit UI
│   │   ├── __init__.py
│   │   └── app.py                  # Streamlit interface
│   ├── models/                     # Data schemas
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic models
│   ├── utils/                      # Utilities
│   │   ├── __init__.py
│   │   ├── logging_config.py       # Logging setup
│   │   └── validators.py           # Input validation
│   └── config/                     # Configuration
│       ├── __init__.py
│       └── settings.py             # Settings management
├── tests/                          # Test suite
│   ├── conftest.py                # Pytest configuration
│   ├── test_api.py                # API tests
│   ├── test_feature_extraction.py # Feature tests
│   ├── test_model_loader.py       # Model loading tests
│   └── test_validators.py         # Validation tests
├── models/                         # Model artifacts (not in Git)
│   ├── phishing_rf_model.pkl       # Trained model
│   └── scaler.pkl                  # Feature scaler
├── monitoring/                     # Monitoring configs
│   └── prometheus.yml              # Prometheus config
├── Dockerfile                      # Production Dockerfile
├── Dockerfile.streamlit            # Streamlit Dockerfile
├── docker-compose.yml              # Local development setup
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── pyproject.toml                  # Tool configurations
├── .pre-commit-config.yaml        # Pre-commit hooks
├── .github/
│   └── workflows/
│       └── ci.yml                  # GitHub Actions CI/CD
├── README.md                       # This file
├── CONTRIBUTING.md                 # Contribution guide
├── CODE_OF_CONDUCT.md             # Code of conduct
├── SECURITY.md                     # Security policy
└── LICENSE                         # MIT License
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | Python 3.9+ | Core implementation |
| API | FastAPI | High-performance REST API |
| Server | Uvicorn | ASGI server |
| ML | Scikit-Learn | Model inference |
| Data | Pandas/NumPy | Array operations |
| UI | Streamlit | Demo interface |
| Serialization | Joblib | Model loading |
| Validation | Pydantic | Input validation |
| Testing | Pytest | Test framework |
| Code Quality | Black, Flake8, MyPy | Linting & formatting |
| Container | Docker | Containerization |
| CI/CD | GitHub Actions | Automation |
| Monitoring | Prometheus | Metrics collection |

## Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose (for containerized setup)
- Git

### Option 1: Local Development

```bash
# Clone repository
git clone https://github.com/mukeshkumarreddy/phishing_app.git
cd phishing_app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run API server
python -m uvicorn src.phishing.api.server:app --reload

# In another terminal, run Streamlit UI
streamlit run src/phishing/ui/app.py
```

### Option 2: Docker Compose

```bash
# Clone repository
git clone https://github.com/mukeshkumarreddy/phishing_app.git
cd phishing_app

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# Access services
# API: http://localhost:8000
# Streamlit: http://localhost:8501
# Prometheus: http://localhost:9091
```

## Installation

### From Source

```bash
# Clone repository
git clone https://github.com/mukeshkumarreddy/phishing_app.git
cd phishing_app

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional but recommended)
pre-commit install

# Run tests
pytest

# Run linting
black src tests
flake8 src tests
mypy src
```

### From Docker

```bash
# Build image
docker build -t phishing-detector:latest .

# Run container
docker run -p 8000:8000 phishing-detector:latest

# Run with custom environment
docker run -p 8000:8000 \
  -e MODEL_PATH=/app/models/phishing_rf_model.pkl \
  -e LOG_LEVEL=DEBUG \
  phishing-detector:latest
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Application
ENVIRONMENT=development|production
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
LOG_FORMAT=json|text

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
CORS_ORIGINS=*

# Model
MODEL_PATH=models/phishing_rf_model.pkl
SCALER_PATH=models/scaler.pkl
MODEL_CHECKSUM=<sha256_hash>
SCALER_CHECKSUM=<sha256_hash>

# Security
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Features
DNS_LOOKUP_TIMEOUT=2.0
DNS_LOOKUP_ENABLED=true

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type check
mypy src

# Lint
flake8 src tests
ruff check src tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/phishing --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestAPIHealthEndpoint::test_health_check

# Run with markers
pytest -m unit
pytest -m integration
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Skip hooks for emergency commits
git commit --no-verify
```

## Testing

### Test Coverage

```
Name                              Stmts   Miss  Cover
─────────────────────────────────────────────────────
src/phishing/api/server.py          80     5     94%
src/phishing/core/detector.py       50     2     96%
src/phishing/core/feature_extractor.py 120   10   92%
src/phishing/core/model_loader.py   45     3     93%
src/phishing/utils/validators.py    35     2     94%
src/phishing/utils/logging_config.py 40     5     88%
─────────────────────────────────────────────────────
TOTAL                               370    27     93%
```

### Test Categories

- **Unit Tests**: Feature extraction, validation, model loading
- **Integration Tests**: API endpoints, detector class
- **API Tests**: HTTP responses, error handling, batch operations

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t phishing-detector:v1.0.0 .

# Tag for registry
docker tag phishing-detector:v1.0.0 registry.example.com/phishing-detector:v1.0.0

# Push to registry
docker push registry.example.com/phishing-detector:v1.0.0

# Run container
docker run -d \
  -p 8000:8000 \
  -p 9090:9090 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  -e MODEL_CHECKSUM=<sha256> \
  --name phishing-api \
  registry.example.com/phishing-detector:v1.0.0
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace phishing

# Create ConfigMap for settings
kubectl create configmap phishing-config \
  --from-file=.env \
  -n phishing

# Deploy
kubectl apply -f deployment.yaml -n phishing

# Check status
kubectl get pods -n phishing
kubectl logs -f deployment/phishing-api -n phishing
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `API_KEY` or OAuth
- [ ] Enable rate limiting
- [ ] Configure proper DNS lookup timeouts
- [ ] Set model checksums for verification
- [ ] Use secrets manager for sensitive data
- [ ] Configure log aggregation
- [ ] Set up monitoring and alerts
- [ ] Use reverse proxy (Nginx)
- [ ] Enable HTTPS/TLS
- [ ] Configure backup strategies
- [ ] Set resource limits (CPU, memory)
- [ ] Regular security updates

## API Documentation

### Interactive API Docs

Once running, access Swagger UI:
```
http://localhost:8000/docs
```

### Endpoints

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true
}
```

#### Single Prediction
```bash
POST /predict

Request:
{
  "url": "https://example.com"
}

Response:
{
  "prediction": 0,
  "confidence": 0.95,
  "label": "✅ Legitimate",
  "url": "https://example.com",
  "features_count": 30
}
```

#### Batch Prediction
```bash
POST /predict-batch

Request:
{
  "urls": [
    "https://example1.com",
    "https://example2.com"
  ]
}

Response:
{
  "results": [...],
  "total": 2,
  "failed": 0
}
```

#### System Info
```bash
GET /info

Response:
{
  "app_name": "Phishing Detection API",
  "version": "1.0.0",
  "environment": "production",
  "detector": {
    "is_ready": true,
    "model_type": "RandomForestClassifier"
  }
}
```

## Security

### Input Validation
- Strict URL format validation using Pydantic
- URL length limits (5-2048 characters)
- Batch size limits (1-100 URLs)
- Type validation for all inputs

### Model Security
- Checksum verification for model artifacts
- Models stored outside Git repository
- Secure model loading from trusted sources only

### Network Security
- DNS lookup timeouts to prevent DoS
- Request timeouts to prevent hanging
- CORS configuration for frontend isolation
- HTTPS recommended for production

### Error Handling
- Safe error messages to prevent information leakage
- Comprehensive logging of errors
- No stack traces in API responses
- Structured JSON logging for security analysis

### Secrets Management
- Environment variables for sensitive data
- Support for GitHub Secrets
- `.env` file in `.gitignore`
- Secrets scanning in CI/CD

See [SECURITY.md](SECURITY.md) for detailed security policy.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start:
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and commit (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/mukeshkumarreddy/phishing_app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mukeshkumarreddy/phishing_app/discussions)
- **Security**: See [SECURITY.md](SECURITY.md)

## Changelog

### v1.0.0 (2024-01-17)
- ✨ Production-ready FastAPI server
- 🔒 Secure model loading with checksums
- 📦 Comprehensive test suite (93% coverage)
- 🐳 Docker & Docker Compose support
- 🔄 GitHub Actions CI/CD pipeline
- 📊 Structured logging and monitoring
- 🎨 Modular architecture with clean separation of concerns
- 📖 Comprehensive documentation
- ✅ Pre-commit hooks and linting setup

---

**Made with ❤️ for security**
