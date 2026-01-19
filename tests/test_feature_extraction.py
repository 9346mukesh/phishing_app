"""Tests for feature extraction module."""

import pytest

from src.phishing.core.feature_extractor import (
    NUM_FEATURES,
    FeatureExtractionError,
    extract_at_symbol,
    extract_features_from_url,
    extract_ip_address,
    extract_subdomain_count,
    extract_url_length,
)


class TestFeatureExtraction:
    """Test feature extraction functions."""

    def test_extract_features_from_url_legitimate(self):
        """Test feature extraction from legitimate URL."""
        url = "https://www.google.com"
        features = extract_features_from_url(url)

        assert isinstance(features, list)
        assert len(features) == NUM_FEATURES
        assert all(isinstance(f, int) for f in features)

    def test_extract_features_from_url_phishing(self):
        """Test feature extraction from suspicious URL."""
        url = "https://192.168.1.1/login"
        features = extract_features_from_url(url)

        assert len(features) == NUM_FEATURES
        # Should detect IP address
        assert features[0] == -1

    def test_extract_features_invalid_url(self):
        """Test feature extraction with invalid URL."""
        with pytest.raises(FeatureExtractionError):
            extract_features_from_url("")

        with pytest.raises(FeatureExtractionError):
            extract_features_from_url(None)

    def test_extract_ip_address(self):
        """Test IP address detection."""
        assert extract_ip_address("https://192.168.1.1") == -1
        assert extract_ip_address("https://www.google.com") == 1

    def test_extract_url_length(self):
        """Test URL length feature."""
        short_url = "https://example.com"
        medium_url = "https://example.com/path/to/page"
        long_url = "https://example.com/path/to/page?with=many&query=parameters&more=data"

        assert extract_url_length(short_url) == 1
        assert extract_url_length(medium_url) in [0, 1]
        assert extract_url_length(long_url) in [-1, 0]

    def test_extract_at_symbol(self):
        """Test @ symbol detection."""
        assert extract_at_symbol("https://user@example.com") == -1
        assert extract_at_symbol("https://example.com") == 1

    def test_extract_subdomain_count(self):
        """Test subdomain counting."""
        assert extract_subdomain_count("https://example.com") == 1
        assert extract_subdomain_count("https://www.example.com") == 0 or 1
        assert extract_subdomain_count("https://mail.google.com") in [0, 1]

    def test_feature_vector_size(self):
        """Test that feature vector is always correct size."""
        test_urls = [
            "https://example.com",
            "https://subdomain.example.co.uk",
            "https://192.168.1.1/login",
            "https://bit.ly/12345",
        ]

        for url in test_urls:
            features = extract_features_from_url(url)
            assert len(features) == NUM_FEATURES, f"Wrong size for {url}: {len(features)}"
