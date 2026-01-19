"""Tests for model loader module."""

import hashlib
import os
import tempfile
from unittest import mock

import pytest
import joblib

from src.phishing.core.model_loader import (
    calculate_checksum,
    validate_checksum,
    load_model_and_scaler_safe,
    ModelLoadError,
)


class TestModelLoader:
    """Test model loading functions."""

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            checksum = calculate_checksum(temp_path)
            assert isinstance(checksum, str)
            assert len(checksum) == 64  # SHA256 hex length

            # Verify consistency
            checksum2 = calculate_checksum(temp_path)
            assert checksum == checksum2
        finally:
            os.unlink(temp_path)

    def test_validate_checksum_valid(self):
        """Test checksum validation with valid checksum."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            checksum = calculate_checksum(temp_path)
            assert validate_checksum(temp_path, checksum) is True
        finally:
            os.unlink(temp_path)

    def test_validate_checksum_invalid(self):
        """Test checksum validation with invalid checksum."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            invalid_checksum = "0" * 64
            assert validate_checksum(temp_path, invalid_checksum) is False
        finally:
            os.unlink(temp_path)

    def test_validate_checksum_case_insensitive(self):
        """Test that checksum validation is case-insensitive."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            checksum = calculate_checksum(temp_path)
            assert validate_checksum(temp_path, checksum.lower()) is True
            assert validate_checksum(temp_path, checksum.upper()) is True
        finally:
            os.unlink(temp_path)

    def test_load_model_and_scaler_file_not_found(self):
        """Test loading with missing files."""
        with pytest.raises(ModelLoadError):
            load_model_and_scaler_safe(
                model_path="/nonexistent/model.pkl",
                scaler_path="/nonexistent/scaler.pkl",
            )

    @mock.patch("src.phishing.core.model_loader.joblib.load")
    def test_load_model_and_scaler_checksum_mismatch(self, mock_load):
        """Test loading with checksum mismatch."""
        with tempfile.NamedTemporaryFile(delete=False) as f_model:
            model_path = f_model.name
        with tempfile.NamedTemporaryFile(delete=False) as f_scaler:
            scaler_path = f_scaler.name

        try:
            with pytest.raises(ModelLoadError):
                load_model_and_scaler_safe(
                    model_path=model_path,
                    scaler_path=scaler_path,
                    model_checksum="invalid_checksum",
                )
        finally:
            os.unlink(model_path)
            os.unlink(scaler_path)

    def test_load_model_from_settings(self):
        """Test loading model with settings defaults."""
        # This test requires actual model files to exist
        # Skip if models don't exist
        pytest.skip("Requires actual model files")
