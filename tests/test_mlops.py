"""Tests for MLOps pipeline components."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class TestDataValidator:
    """Tests for data validation pipeline."""

    def _make_dataset(self, n_samples=500, n_features=10, label_col="label"):
        """Create a synthetic phishing-like dataset."""
        np.random.seed(42)
        data = np.random.randint(-1, 2, size=(n_samples, n_features))
        labels = np.random.randint(0, 2, size=n_samples)
        columns = [f"feature_{i}" for i in range(n_features)]
        df = pd.DataFrame(data, columns=columns)
        df[label_col] = labels
        return df

    def test_validator_passes_good_data(self):
        """Validator should pass for well-formed data."""
        from src.phishing.mlops.data_validation import DataValidator

        df = self._make_dataset(n_samples=2000)
        validator = DataValidator(params={
            "min_samples": 1000,
            "max_null_ratio": 0.05,
            "expected_label_values": [0, 1],
            "min_class_ratio": 0.2,
        })
        results = validator.validate(df)
        assert results["passed"] is True

    def test_validator_fails_small_dataset(self):
        """Validator should fail if dataset is too small."""
        from src.phishing.mlops.data_validation import DataValidator

        df = self._make_dataset(n_samples=50)
        validator = DataValidator(params={"min_samples": 1000})
        results = validator.validate(df)
        # Should fail min_samples check
        failed = [c for c in results["checks"] if c["name"] == "min_samples"]
        assert len(failed) == 1
        assert failed[0]["passed"] is False

    def test_validator_detects_nulls(self):
        """Validator should detect high null ratio."""
        from src.phishing.mlops.data_validation import DataValidator

        df = self._make_dataset(n_samples=2000)
        # Introduce lots of nulls
        df.iloc[:1500, 0] = np.nan

        validator = DataValidator(params={"max_null_ratio": 0.05})
        results = validator.validate(df)
        failed = [c for c in results["checks"] if c["name"] == "null_ratio"]
        assert len(failed) == 1
        assert failed[0]["passed"] is False


class TestDriftDetector:
    """Tests for drift detection."""

    def test_no_drift_same_distribution(self):
        """No drift when distributions are identical."""
        from src.phishing.mlops.monitor import DriftDetector

        np.random.seed(42)
        ref = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})
        cur = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})

        detector = DriftDetector(threshold=0.05)
        results = detector.detect_feature_drift(ref, cur, ["f1"])
        assert results["drift_detected"] is False

    def test_drift_different_distribution(self):
        """Drift should be detected when distributions differ significantly."""
        from src.phishing.mlops.monitor import DriftDetector

        np.random.seed(42)
        ref = pd.DataFrame({"f1": np.random.normal(0, 1, 1000)})
        cur = pd.DataFrame({"f1": np.random.normal(5, 1, 1000)})  # Shifted mean

        detector = DriftDetector(threshold=0.05)
        results = detector.detect_feature_drift(ref, cur, ["f1"])
        assert results["drift_detected"] is True

    def test_prediction_drift(self):
        """Should detect drift in predictions."""
        from src.phishing.mlops.monitor import DriftDetector

        np.random.seed(42)
        ref_pred = np.random.uniform(0.3, 0.7, 500)
        cur_pred = np.random.uniform(0.7, 1.0, 500)  # Shifted predictions

        detector = DriftDetector(threshold=0.05)
        results = detector.detect_prediction_drift(ref_pred, cur_pred)
        assert results["drift_detected"] == True


class TestModelQualityGate:
    """Tests for model quality gates."""

    def test_quality_gate_passes(self):
        """Quality gate should pass when metrics exceed thresholds."""
        from src.phishing.mlops.evaluate import ModelQualityGate

        gate = ModelQualityGate({
            "min_accuracy": 0.85,
            "min_f1": 0.85,
        })
        gate.check("accuracy", 0.92)
        gate.check("f1", 0.90)
        assert gate.all_passed() is True

    def test_quality_gate_fails(self):
        """Quality gate should fail when metrics are below thresholds."""
        from src.phishing.mlops.evaluate import ModelQualityGate

        gate = ModelQualityGate({
            "min_accuracy": 0.90,
            "min_f1": 0.90,
        })
        gate.check("accuracy", 0.80)  # Below threshold
        gate.check("f1", 0.95)
        assert gate.all_passed() is False

    def test_quality_gate_no_threshold(self):
        """Metrics without thresholds should always pass."""
        from src.phishing.mlops.evaluate import ModelQualityGate

        gate = ModelQualityGate({})
        gate.check("accuracy", 0.50)
        assert gate.all_passed() is True


class TestExperimentTracker:
    """Tests for MLflow experiment tracking."""

    def test_tracker_initialization(self, tmp_path):
        """Tracker should initialize with a temp tracking URI."""
        from src.phishing.mlops.experiment_tracker import ExperimentTracker

        tracker = ExperimentTracker(
            experiment_name="test-experiment",
            tracking_uri=f"file://{tmp_path}/mlruns",
        )
        assert tracker.experiment_name == "test-experiment"
        assert tracker.experiment_id is not None

    def test_tracker_log_run(self, tmp_path):
        """Should log a run with params and metrics."""
        from src.phishing.mlops.experiment_tracker import ExperimentTracker

        tracker = ExperimentTracker(
            experiment_name="test-run",
            tracking_uri=f"file://{tmp_path}/mlruns",
        )
        with tracker.start_run(run_name="test"):
            tracker.log_params({"n_estimators": 100})
            tracker.log_metrics({"accuracy": 0.95, "f1_score": 0.93})

        history = tracker.get_run_history()
        assert len(history) >= 1
        assert history[0]["metrics"]["accuracy"] == 0.95


class TestMLOpsConfig:
    """Tests for MLOps configuration."""

    def test_load_params(self, tmp_path):
        """Should load params from YAML."""
        from src.phishing.mlops.config import load_params

        params_file = tmp_path / "params.yaml"
        params_file.write_text("train:\n  n_estimators: 100\n  max_depth: 10\n")

        params = load_params(str(params_file))
        assert params["train"]["n_estimators"] == 100
        assert params["train"]["max_depth"] == 10
