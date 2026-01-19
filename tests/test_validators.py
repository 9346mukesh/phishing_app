"""Tests for URL validation module."""

import pytest

from src.phishing.utils.validators import (
    validate_url,
    validate_batch_urls,
    URLValidationError,
)


class TestURLValidation:
    """Test URL validation functions."""

    def test_validate_url_valid_https(self):
        """Test validation of valid HTTPS URL."""
        url = "https://www.example.com"
        result = validate_url(url)
        assert result is not None
        assert "example.com" in result

    def test_validate_url_valid_http(self):
        """Test validation of valid HTTP URL."""
        url = "http://example.com"
        result = validate_url(url)
        assert result is not None
        assert "example.com" in result

    def test_validate_url_auto_prefix(self):
        """Test automatic protocol prefix."""
        url = "example.com"
        result = validate_url(url)
        assert result is not None
        assert result.startswith("http://")

    def test_validate_url_invalid_empty(self):
        """Test validation of empty URL."""
        with pytest.raises(URLValidationError):
            validate_url("")

    def test_validate_url_invalid_none(self):
        """Test validation of None URL."""
        with pytest.raises(URLValidationError):
            validate_url(None)

    def test_validate_url_invalid_short(self):
        """Test validation of too-short URL."""
        with pytest.raises(URLValidationError):
            validate_url("url")

    def test_validate_url_invalid_long(self):
        """Test validation of too-long URL."""
        long_url = "https://example.com/" + "a" * 2500
        with pytest.raises(URLValidationError):
            validate_url(long_url)

    def test_validate_url_normalize(self):
        """Test URL normalization."""
        url = "HTTPS://WWW.EXAMPLE.COM/PATH"
        result = validate_url(url)
        assert result is not None

    def test_validate_batch_urls_valid(self):
        """Test batch URL validation with valid URLs."""
        urls = [
            "https://example.com",
            "https://google.com",
            "https://github.com",
        ]
        valid, invalid = validate_batch_urls(urls)

        assert len(valid) == 3
        assert len(invalid) == 0

    def test_validate_batch_urls_mixed(self):
        """Test batch URL validation with mixed valid/invalid URLs."""
        urls = [
            "https://example.com",
            "",
            "https://google.com",
            "invalid",
        ]
        valid, invalid = validate_batch_urls(urls)

        assert len(valid) >= 2
        assert len(invalid) >= 1

    def test_validate_batch_urls_exceeds_limit(self):
        """Test batch size limit."""
        urls = [f"https://example{i}.com" for i in range(150)]

        with pytest.raises(URLValidationError):
            validate_batch_urls(urls, max_batch_size=100)

    def test_validate_batch_urls_not_list(self):
        """Test batch validation with non-list input."""
        with pytest.raises(URLValidationError):
            validate_batch_urls("not a list")
