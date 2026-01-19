"""Phishing Detection System - Production-Ready ML Application."""

__version__ = "1.0.0"
__author__ = "Phishing Detection Team"

from src.phishing.core.detector import PhishingDetector  # noqa: F401
from src.phishing.utils.logging_config import get_logger  # noqa: F401

__all__ = ["PhishingDetector", "get_logger"]
