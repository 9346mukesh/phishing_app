"""Data validation pipeline using Great Expectations patterns.

Validates the phishing dataset before training to ensure data quality.
Runs as a DVC stage: `dvc repro validate_data`
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.phishing.mlops.config import DATA_DIR, REPORTS_DIR, load_params
from src.phishing.utils.logging_config import get_logger

logger = get_logger("data_validation")


class DataValidationError(Exception):
    """Raised when data validation fails."""

    pass


class DataValidator:
    """Validates phishing dataset quality before training."""

    def __init__(self, params: dict = None):
        self.params = params or load_params().get("data_validation", {})
        self.results = {
            "checks": [],
            "passed": True,
            "summary": {},
        }

    def _add_check(self, name: str, passed: bool, details: str):
        """Record a validation check result."""
        self.results["checks"].append({
            "name": name,
            "passed": passed,
            "details": details,
        })
        if not passed:
            self.results["passed"] = False
            logger.warning(f"FAILED: {name} - {details}")
        else:
            logger.info(f"PASSED: {name} - {details}")

    def validate_schema(self, df: pd.DataFrame) -> None:
        """Validate dataset schema and column types."""
        # Check minimum columns
        if len(df.columns) < 2:
            self._add_check(
                "schema_columns",
                False,
                f"Expected at least 2 columns, got {len(df.columns)}",
            )
            return

        self._add_check(
            "schema_columns",
            True,
            f"Dataset has {len(df.columns)} columns",
        )

        # Support URL-based datasets (url + label columns)
        has_url_col = "url" in [c.lower() for c in df.columns]
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if has_url_col:
            self._add_check(
                "url_column",
                True,
                "URL-based dataset detected — features will be extracted at training time",
            )
        else:
            self._add_check(
                "numeric_features",
                len(numeric_cols) >= 2,
                f"{len(numeric_cols)} numeric columns found",
            )

    def validate_completeness(self, df: pd.DataFrame) -> None:
        """Validate data completeness (missing values, sample count)."""
        min_samples = self.params.get("min_samples", 1000)
        max_null_ratio = self.params.get("max_null_ratio", 0.05)

        # Check sample count
        self._add_check(
            "min_samples",
            len(df) >= min_samples,
            f"{len(df)} samples (min: {min_samples})",
        )

        # Check null ratios per column
        null_ratios = df.isnull().mean()
        max_null = null_ratios.max()
        worst_col = null_ratios.idxmax() if max_null > 0 else "none"

        self._add_check(
            "null_ratio",
            max_null <= max_null_ratio,
            f"Max null ratio: {max_null:.4f} (col: {worst_col}, threshold: {max_null_ratio})",
        )

    def validate_labels(self, df: pd.DataFrame, label_col: str = None) -> None:
        """Validate label column quality."""
        # Auto-detect label column
        if label_col is None:
            candidates = ["label", "Label", "target", "Target", "class", "Class", "Result"]
            for col in candidates:
                if col in df.columns:
                    label_col = col
                    break
            if label_col is None:
                label_col = df.columns[-1]  # assume last column

        expected_labels = self.params.get("expected_label_values", [0, 1])
        min_class_ratio = self.params.get("min_class_ratio", 0.2)

        # Check label values
        unique_labels = sorted(df[label_col].dropna().unique().tolist())
        self._add_check(
            "label_values",
            set(unique_labels).issubset(set(expected_labels)),
            f"Labels found: {unique_labels}, expected subset of: {expected_labels}",
        )

        # Check class balance
        if len(unique_labels) >= 2:
            class_counts = df[label_col].value_counts(normalize=True)
            minority_ratio = class_counts.min()
            self._add_check(
                "class_balance",
                minority_ratio >= min_class_ratio,
                f"Minority class ratio: {minority_ratio:.4f} (threshold: {min_class_ratio})",
            )

    def validate_features(self, df: pd.DataFrame, label_col: str = None) -> None:
        """Validate feature distributions and ranges."""
        if label_col is None:
            candidates = ["label", "Label", "target", "Target", "class", "Class", "Result"]
            for col in candidates:
                if col in df.columns:
                    label_col = col
                    break
            if label_col is None:
                label_col = df.columns[-1]

        feature_cols = [c for c in df.columns if c != label_col]

        # URL-based dataset: validate URL column instead of numeric features
        has_url_col = any(c.lower() == "url" for c in feature_cols)
        if has_url_col:
            url_col = next(c for c in feature_cols if c.lower() == "url")
            empty_urls = df[url_col].isna().sum() + (df[url_col].astype(str).str.strip() == "").sum()
            self._add_check(
                "no_empty_urls",
                empty_urls == 0,
                f"Empty/null URLs: {empty_urls}",
            )
            # Check for duplicate URLs
            dup_count = df[url_col].duplicated().sum()
            dup_ratio = dup_count / len(df)
            self._add_check(
                "low_duplicates",
                dup_ratio < 0.5,
                f"Duplicate URLs: {dup_count} ({dup_ratio:.2%})",
            )
            return

        numeric_features = df[feature_cols].select_dtypes(include=[np.number])

        # Check for constant features (zero variance)
        variances = numeric_features.var()
        constant_features = variances[variances == 0].index.tolist()
        self._add_check(
            "no_constant_features",
            len(constant_features) == 0,
            f"Constant features: {constant_features if constant_features else 'none'}",
        )

        # Check for infinite values
        inf_count = np.isinf(numeric_features.values).sum()
        self._add_check(
            "no_infinite_values",
            inf_count == 0,
            f"Infinite values: {inf_count}",
        )

        # Check for duplicate rows
        dup_count = df.duplicated().sum()
        dup_ratio = dup_count / len(df)
        self._add_check(
            "low_duplicates",
            dup_ratio < 0.5,
            f"Duplicate rows: {dup_count} ({dup_ratio:.2%})",
        )

    def validate(self, df: pd.DataFrame, label_col: str = None) -> dict:
        """Run all validation checks.

        Args:
            df: Dataset to validate
            label_col: Name of label column (auto-detected if None)

        Returns:
            Validation results dictionary
        """
        logger.info(f"Starting data validation on {len(df)} samples...")

        self.validate_schema(df)
        self.validate_completeness(df)
        self.validate_labels(df, label_col)
        self.validate_features(df, label_col)

        # Summary
        total = len(self.results["checks"])
        passed = sum(1 for c in self.results["checks"] if c["passed"])
        self.results["summary"] = {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
        }

        status = "PASSED" if self.results["passed"] else "FAILED"
        logger.info(f"Data validation {status}: {passed}/{total} checks passed")

        return self.results


def main():
    """Run data validation as DVC stage."""
    # Find dataset
    dataset_path = DATA_DIR / "phishing_dataset.csv"

    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.info("Place your dataset at data/phishing_dataset.csv")
        # Create a placeholder report
        report = {
            "checks": [{"name": "dataset_exists", "passed": False, "details": "Dataset not found"}],
            "passed": False,
            "summary": {"total_checks": 1, "passed": 0, "failed": 1, "pass_rate": 0.0},
        }
        report_path = REPORTS_DIR / "data_validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        sys.exit(1)

    # Load and validate
    df = pd.read_csv(dataset_path)

    validator = DataValidator()
    results = validator.validate(df)

    # Save report
    report_path = REPORTS_DIR / "data_validation_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Validation report saved to {report_path}")

    if not results["passed"]:
        logger.error("Data validation FAILED. Fix issues before training.")
        sys.exit(1)

    logger.info("Data validation PASSED. Ready for training.")


if __name__ == "__main__":
    main()
