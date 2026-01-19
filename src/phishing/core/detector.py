"""Main phishing detection logic."""

import numpy as np
from typing import Optional, Tuple

from src.phishing.config.settings import settings
from src.phishing.core.feature_extractor import (
    extract_features_from_url,
    FeatureExtractionError,
)
from src.phishing.core.model_loader import load_model_and_scaler_safe, ModelLoadError
from src.phishing.utils.logging_config import get_logger, SafeErrorHandler
from src.phishing.utils.validators import URLValidationError, validate_url

logger = get_logger(__name__)


class DetectionError(Exception):
    """Raised when detection fails."""

    pass


class PhishingDetector:
    """Main phishing detection engine."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        scaler_path: Optional[str] = None,
        model_checksum: Optional[str] = None,
        scaler_checksum: Optional[str] = None,
        auto_load: bool = True,
    ):
        """
        Initialize detector.

        Args:
            model_path: Path to model file
            scaler_path: Path to scaler file
            model_checksum: Model checksum for validation
            scaler_checksum: Scaler checksum for validation
            auto_load: Automatically load model on init
        """
        self.model_path = model_path or settings.model_path
        self.scaler_path = scaler_path or settings.scaler_path
        self.model_checksum = model_checksum or settings.model_checksum
        self.scaler_checksum = scaler_checksum or settings.scaler_checksum

        self.model = None
        self.scaler = None
        self.is_ready = False

        if auto_load:
            self.load()

    def load(self) -> None:
        """Load model and scaler."""
        with SafeErrorHandler(logger, "model loading"):
            self.model, self.scaler = load_model_and_scaler_safe(
                self.model_path,
                self.scaler_path,
                self.model_checksum,
                self.scaler_checksum,
            )
            self.is_ready = True
            logger.info("Detector ready for predictions")

    def predict(self, url: str) -> Tuple[int, float, str]:
        """
        Predict if URL is phishing.

        Args:
            url: URL to analyze

        Returns:
            Tuple of (prediction, confidence, label)
                - prediction: 0 (legitimate) or 1 (phishing)
                - confidence: Confidence score (0.0-1.0)
                - label: Human-readable label

        Raises:
            DetectionError: If prediction fails
        """
        if not self.is_ready:
            raise DetectionError("Detector not ready. Call load() first.")

        with SafeErrorHandler(logger, "URL prediction"):
            try:
                # Validate URL
                validated_url = validate_url(url)

                # Extract features
                features = extract_features_from_url(validated_url)
                features_array = np.array(features).reshape(1, -1)

                # Scale features
                scaled = self.scaler.transform(features_array)

                # Get raw model prediction (dataset labels likely: 0=phishing, 1=legitimate)
                raw_prediction = int(self.model.predict(scaled)[0])
                probabilities = self.model.predict_proba(scaled)[0]

                # Map to expected output: 0=Legitimate, 1=Phishing
                # If model was trained with 1=Legitimate, flip here
                prediction = 0 if raw_prediction == 1 else 1

                # Confidence for the mapped class
                confidence = float(probabilities[0]) if prediction == 1 else float(probabilities[1])

                # Human-readable label
                label = "🚨 Phishing" if prediction == 1 else "✅ Legitimate"

                logger.info(
                    f"Prediction: {label}, Confidence: {confidence:.2%}",
                    extra={
                        "url": validated_url,
                        "prediction": prediction,
                        "raw_prediction": raw_prediction,
                        "confidence": confidence,
                    },
                )

                return prediction, confidence, label

            except URLValidationError as e:
                raise DetectionError(f"Invalid URL: {str(e)}") from e
            except FeatureExtractionError as e:
                raise DetectionError(f"Feature extraction failed: {str(e)}") from e
            except Exception as e:
                raise DetectionError(f"Prediction failed: {str(e)}") from e

    def predict_batch(self, urls: list) -> list:
        """
        Predict multiple URLs.

        Args:
            urls: List of URLs

        Returns:
            List of prediction tuples

        Raises:
            DetectionError: If batch prediction fails
        """
        if not self.is_ready:
            raise DetectionError("Detector not ready. Call load() first.")

        results = []
        failed_count = 0

        for url in urls:
            try:
                prediction, confidence, label = self.predict(url)
                results.append({
                    "url": url,
                    "prediction": prediction,
                    "confidence": confidence,
                    "label": label,
                    "status": "success",
                })
            except DetectionError as e:
                failed_count += 1
                results.append({
                    "url": url,
                    "error": str(e),
                    "status": "failed",
                })
                logger.warning(f"Batch prediction failed for {url}: {str(e)}")

        logger.info(
            f"Batch prediction complete: {len(urls) - failed_count}/{len(urls)} successful",
            extra={"total": len(urls), "failed": failed_count},
        )

        return results

    def get_info(self) -> dict:
        """Get detector information."""
        return {
            "is_ready": self.is_ready,
            "model_path": self.model_path,
            "scaler_path": self.scaler_path,
            "model_type": type(self.model).__name__ if self.model else None,
            "scaler_type": type(self.scaler).__name__ if self.scaler else None,
        }
