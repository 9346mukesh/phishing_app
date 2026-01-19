"""Configuration management using Pydantic Settings."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    app_name: str = "Phishing Detection API"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(
        os.getenv("PORT") or os.getenv("API_PORT", "8000")
    )  # Support Railway's PORT env var
    api_workers: int = int(os.getenv("API_WORKERS", "4"))
    cors_origins: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Model Configuration
    model_path: str = os.getenv("MODEL_PATH", "models/phishing_rf_model.pkl")
    scaler_path: str = os.getenv("SCALER_PATH", "models/scaler.pkl")
    model_checksum: Optional[str] = os.getenv("MODEL_CHECKSUM")
    scaler_checksum: Optional[str] = os.getenv("SCALER_CHECKSUM")

    # Security
    api_key: Optional[str] = os.getenv("API_KEY")
    enable_rate_limiting: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_period: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")

    # Feature Extraction
    url_validation_enabled: bool = True
    dns_lookup_timeout: float = float(os.getenv("DNS_LOOKUP_TIMEOUT", "2.0"))
    dns_lookup_enabled: bool = os.getenv("DNS_LOOKUP_ENABLED", "false").lower() == "true"

    # Monitoring
    enable_metrics: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))

    # Performance
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "30.0"))
    model_cache_enabled: bool = True

    class Config:
        """Pydantic config."""

        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
