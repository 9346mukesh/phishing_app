"""Secure model loading with checksum validation."""

import hashlib
import os
from typing import Optional, Tuple

import joblib

from src.phishing.config.settings import settings
from src.phishing.utils.logging_config import get_logger

logger = get_logger(__name__)


class ModelLoadError(Exception):
    """Raised when model loading fails."""

    pass


def calculate_checksum(file_path: str, algorithm: str = "sha256") -> str:
    """
    Calculate file checksum.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm (sha256, md5)

    Returns:
        Hexadecimal checksum string
    """
    hash_obj = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def validate_checksum(
    file_path: str,
    expected_checksum: str,
    algorithm: str = "sha256",
) -> bool:
    """
    Validate file checksum.

    Args:
        file_path: Path to file
        expected_checksum: Expected checksum value
        algorithm: Hash algorithm

    Returns:
        True if checksum matches
    """
    actual_checksum = calculate_checksum(file_path, algorithm)
    return actual_checksum.lower() == expected_checksum.lower()


def load_model_and_scaler_safe(
    model_path: Optional[str] = None,
    scaler_path: Optional[str] = None,
    model_checksum: Optional[str] = None,
    scaler_checksum: Optional[str] = None,
) -> Tuple:
    """
    Load model and scaler with checksum validation.

    Args:
        model_path: Path to model file (default from settings)
        scaler_path: Path to scaler file (default from settings)
        model_checksum: Expected model checksum (default from settings)
        scaler_checksum: Expected scaler checksum (default from settings)

    Returns:
        Tuple of (model, scaler)

    Raises:
        ModelLoadError: If loading or validation fails
    """
    # Use defaults from settings if not provided
    if model_path is None:
        model_path = settings.model_path
    if scaler_path is None:
        scaler_path = settings.scaler_path
    if model_checksum is None:
        model_checksum = settings.model_checksum
    if scaler_checksum is None:
        scaler_checksum = settings.scaler_checksum

    try:
        # Validate file existence
        if not os.path.exists(model_path):
            raise ModelLoadError(f"Model file not found: {model_path}")

        if not os.path.exists(scaler_path):
            raise ModelLoadError(f"Scaler file not found: {scaler_path}")

        # Validate checksums if provided
        if model_checksum:
            logger.info("Validating model checksum...")
            if not validate_checksum(model_path, model_checksum):
                raise ModelLoadError(
                    f"Model checksum validation failed. Expected {model_checksum}, "
                    f"got {calculate_checksum(model_path)}"
                )
            logger.info("Model checksum validated successfully")

        if scaler_checksum:
            logger.info("Validating scaler checksum...")
            if not validate_checksum(scaler_path, scaler_checksum):
                raise ModelLoadError(
                    f"Scaler checksum validation failed. Expected {scaler_checksum}, "
                    f"got {calculate_checksum(scaler_path)}"
                )
            logger.info("Scaler checksum validated successfully")

        # Load model
        logger.info(f"Loading model from {model_path}")
        model = joblib.load(model_path)

        # Load scaler
        logger.info(f"Loading scaler from {scaler_path}")
        scaler = joblib.load(scaler_path)

        logger.info("Model and scaler loaded successfully")

        return model, scaler

    except ModelLoadError:
        raise
    except Exception as e:
        raise ModelLoadError(f"Failed to load model/scaler: {str(e)}") from e


def get_model_info(model_path: Optional[str] = None) -> dict:
    """
    Get information about a model file.

    Args:
        model_path: Path to model file

    Returns:
        Dictionary with model info
    """
    if model_path is None:
        model_path = settings.model_path

    try:
        file_size = os.path.getsize(model_path)
        file_checksum = calculate_checksum(model_path)
        model = joblib.load(model_path)

        return {
            "path": model_path,
            "exists": True,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "checksum": file_checksum,
            "type": type(model).__name__,
            "model_class": str(type(model)),
        }
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        return {
            "path": model_path,
            "exists": False,
            "error": str(e),
        }
