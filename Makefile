.PHONY: help install dev test lint format clean build run docker-up docker-down deploy

help:
	@echo "🛡️  Phishing Detection System - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
	@echo "  make install-mlops - Install MLOps dependencies"
	@echo "  make dev           - Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  make run-api       - Run API server"
	@echo "  make run-ui        - Run Streamlit UI"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run all linters"
	@echo "  make format        - Format code"
	@echo "  make type-check    - Type checking"
	@echo ""
	@echo "MLOps Pipeline:"
	@echo "  make mlops-setup   - Initialize DVC & MLflow"
	@echo "  make validate-data - Validate training data"
	@echo "  make train         - Train model (MLflow tracked)"
	@echo "  make evaluate      - Evaluate model quality gates"
	@echo "  make monitor       - Run drift monitoring"
	@echo "  make pipeline      - Run full ML pipeline (DVC)"
	@echo "  make mlflow-ui     - Launch MLflow dashboard"
	@echo "  make compare       - Compare experiment runs"
	@echo "  make promote       - Promote model to Production"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose"
	@echo "  make docker-logs   - View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Remove build artifacts"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

install-mlops:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-mlops.txt

dev:
	pip install -r requirements.txt
	pip install -r requirements-mlops.txt
	pre-commit install

run-api:
	python run_api.py

run-ui:
	python run_ui.py

test:
	pytest

test-cov:
	pytest --cov=src/phishing --cov-report=html --cov-report=term-missing

lint:
	black --check src tests
	isort --check-only src tests
	flake8 src tests
	mypy src
	ruff check src tests

format:
	black src tests
	isort src tests
	ruff check --fix src tests

type-check:
	mypy src

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov .coverage
	rm -rf reports/plots reports/evaluation_plots
	rm -f reports/*.json reports/*.html

train:
	python -m src.phishing.mlops.train

# === MLOps Commands ===
mlops-setup:
	dvc init || true
	@echo "✅ DVC initialized"
	@echo "✅ MLflow tracking configured (local)"
	@echo "Run 'make train' to start training with full tracking"

validate-data:
	python -m src.phishing.mlops.data_validation

evaluate:
	python -m src.phishing.mlops.evaluate

monitor:
	python -m src.phishing.mlops.monitor

pipeline:
	dvc repro

mlflow-ui:
	mlflow ui --host 0.0.0.0 --port 5000

compare:
	python -m src.phishing.mlops.promote --action compare

promote:
	python -m src.phishing.mlops.promote --action promote --stage Production

promote-staging:
	python -m src.phishing.mlops.promote --action promote --stage Staging

list-models:
	python -m src.phishing.mlops.promote --action list

docker-build:
	docker build -t phishing-detector:latest .

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

pre-commit:
	pre-commit run --all-files

security-check:
	bandit -r src
	safety check

all: clean lint test
	@echo "✅ All checks passed!"
