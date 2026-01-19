.PHONY: help install dev test lint format clean build run docker-up docker-down deploy

help:
	@echo "🛡️  Phishing Detection System - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
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
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose"
	@echo "  make docker-logs   - View Docker logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Remove build artifacts"
	@echo "  make train         - Train model"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
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

train:
	python train_model.py --data phishing_dataset.csv

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
