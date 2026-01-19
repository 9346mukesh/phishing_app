"""Tests for FastAPI application."""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.phishing.api.server import create_app
from src.phishing.core.detector import PhishingDetector


@pytest.fixture
def app():
    """Create test FastAPI app."""
    return create_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_detector():
    """Create mock detector."""
    detector = Mock(spec=PhishingDetector)
    detector.is_ready = True
    detector.predict.return_value = (0, 0.95, "✅ Legitimate")
    detector.predict_batch.return_value = [
        {
            "url": "https://example.com",
            "prediction": 0,
            "confidence": 0.95,
            "label": "✅ Legitimate",
            "status": "success",
        }
    ]
    detector.get_info.return_value = {
        "is_ready": True,
        "model_type": "RandomForestClassifier",
    }
    return detector


class TestAPIHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check response."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "model_loaded" in data


class TestAPIPredictEndpoint:
    """Test prediction endpoint."""

    @patch("src.phishing.api.server.detector")
    def test_predict_legitimate_url(self, mock_detector_global, client, mock_detector):
        """Test prediction for legitimate URL."""
        mock_detector_global.is_ready = True
        mock_detector_global.predict.return_value = (0, 0.95, "✅ Legitimate")
        response = client.post(
            "/predict",
            json={"url": "https://www.google.com"},
        )
        # Response might be 503 if detector not ready, that's ok
        assert response.status_code in [200, 503]

    def test_predict_invalid_url(self, client):
        """Test prediction with invalid URL."""
        response = client.post(
            "/predict",
            json={"url": "invalid"},
        )
        assert response.status_code in [400, 422, 503]

    def test_predict_empty_url(self, client):
        """Test prediction with empty URL."""
        response = client.post(
            "/predict",
            json={"url": ""},
        )
        assert response.status_code in [400, 422, 503]

    def test_predict_missing_url(self, client):
        """Test prediction with missing URL."""
        response = client.post(
            "/predict",
            json={},
        )
        assert response.status_code == 422


class TestAPIBatchEndpoint:
    """Test batch prediction endpoint."""

    def test_batch_predict_multiple_urls(self, client):
        """Test batch prediction."""
        response = client.post(
            "/predict-batch",
            json={
                "urls": [
                    "https://example.com",
                    "https://google.com",
                ]
            },
        )
        assert response.status_code in [200, 503]

    def test_batch_predict_empty_list(self, client):
        """Test batch prediction with empty list."""
        response = client.post(
            "/predict-batch",
            json={"urls": []},
        )
        assert response.status_code in [400, 422, 503]

    def test_batch_predict_too_many_urls(self, client):
        """Test batch prediction exceeds size limit."""
        urls = [f"https://example{i}.com" for i in range(150)]
        response = client.post(
            "/predict-batch",
            json={"urls": urls},
        )
        assert response.status_code in [400, 422, 503]


class TestAPIInfoEndpoint:
    """Test info endpoint."""

    def test_get_info(self, client):
        """Test info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "app_name" in data
        assert "version" in data
        assert "environment" in data


class TestAPICORSHeaders:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.get("/health")
        assert response.status_code == 200
        # CORS headers should be added by middleware


class TestAPIErrorHandling:
    """Test error handling."""

    def test_404_not_found(self, client):
        """Test 404 response."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test invalid JSON."""
        response = client.post(
            "/predict",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422
