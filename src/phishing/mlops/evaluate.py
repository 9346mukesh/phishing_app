"""Model evaluation pipeline with quality gates.

Evaluates model against thresholds before promotion.
Run: python -m src.phishing.mlops.evaluate
Or:  dvc repro evaluate
"""

import json
import sys
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

from src.phishing.mlops.config import (
    DATA_DIR,
    EVAL_PLOTS_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    load_params,
)
from src.phishing.mlops.experiment_tracker import ExperimentTracker
from src.phishing.core.feature_extractor import extract_features_from_url, NUM_FEATURES
from src.phishing.utils.logging_config import get_logger

logger = get_logger("model_evaluation")


class ModelQualityGate:
    """Checks if a model meets minimum quality thresholds."""

    def __init__(self, thresholds: dict):
        self.thresholds = thresholds
        self.results = []

    def check(self, metric_name: str, value: float) -> bool:
        """Check if a metric meets its threshold.

        Args:
            metric_name: Metric name (must match thresholds key)
            value: Actual metric value

        Returns:
            True if metric passes
        """
        threshold_key = f"min_{metric_name}"
        threshold = self.thresholds.get(threshold_key)

        if threshold is None:
            self.results.append({
                "metric": metric_name,
                "value": value,
                "threshold": None,
                "passed": True,
                "message": "No threshold defined",
            })
            return True

        passed = value >= threshold
        self.results.append({
            "metric": metric_name,
            "value": round(value, 4),
            "threshold": threshold,
            "passed": passed,
            "message": f"{'PASS' if passed else 'FAIL'}: {value:.4f} {'≥' if passed else '<'} {threshold}",
        })

        if passed:
            logger.info(f"✓ {metric_name}: {value:.4f} >= {threshold}")
        else:
            logger.warning(f"✗ {metric_name}: {value:.4f} < {threshold}")

        return passed

    def all_passed(self) -> bool:
        """Check if all quality gates passed."""
        return all(r["passed"] for r in self.results)

    def summary(self) -> dict:
        """Get quality gate summary."""
        return {
            "all_passed": self.all_passed(),
            "total_checks": len(self.results),
            "passed": sum(1 for r in self.results if r["passed"]),
            "failed": sum(1 for r in self.results if not r["passed"]),
            "details": self.results,
        }


def evaluate_model(model, scaler, data_path: Path, params: dict) -> dict:
    """Full model evaluation.

    Args:
        model: Trained model
        scaler: Feature scaler
        data_path: Path to dataset
        params: All params

    Returns:
        Evaluation results dictionary
    """
    train_params = params.get("train", {})
    eval_thresholds = params.get("evaluation", {})

    # Load data
    df = pd.read_csv(data_path)
    label_candidates = ["label", "Label", "target", "Target", "class", "Class", "Result"]
    label_col = None
    for col in label_candidates:
        if col in df.columns:
            label_col = col
            break
    if label_col is None:
        label_col = df.columns[-1]

    # Check if URL-based dataset
    non_label_cols = [c for c in df.columns if c != label_col]
    has_url_col = any(c.lower() == "url" for c in non_label_cols)

    if has_url_col:
        url_col = next(c for c in non_label_cols if c.lower() == "url")
        logger.info(f"URL-based dataset — extracting features from '{url_col}' column")
        features_list = []
        for url in df[url_col]:
            try:
                features_list.append(extract_features_from_url(str(url)))
            except Exception:
                features_list.append([0] * NUM_FEATURES)
        X = np.array(features_list)
    else:
        feature_cols = [c for c in df.columns if c != label_col]
        X = df[feature_cols].values

    y = df[label_col].values

    # Same split as training (reproducible)
    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=train_params.get("test_size", 0.2),
        random_state=train_params.get("random_state", 42),
        stratify=y,
    )

    X_test_scaled = scaler.transform(X_test)

    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    # Compute metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
    }

    # Quality gates
    gate = ModelQualityGate(eval_thresholds)
    gate.check("accuracy", metrics["accuracy"])
    gate.check("precision", metrics["precision"])
    gate.check("recall", metrics["recall"])
    gate.check("f1", metrics["f1_score"])
    gate.check("roc_auc", metrics["roc_auc"])

    # Generate evaluation plots
    generate_evaluation_plots(y_test, y_pred, y_proba, EVAL_PLOTS_DIR)

    return {
        "metrics": metrics,
        "quality_gate": gate.summary(),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }


def generate_evaluation_plots(y_test, y_pred, y_proba, output_dir: Path):
    """Generate evaluation-specific plots."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Precision-Recall Curve
    fig, ax = plt.subplots(figsize=(8, 6))
    precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_proba)
    ax.plot(recall_vals, precision_vals, linewidth=2)
    ax.set(xlabel="Recall", ylabel="Precision", title="Precision-Recall Curve")
    ax.fill_between(recall_vals, precision_vals, alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_dir / "precision_recall_curve.png", dpi=150)
    plt.close(fig)

    # Prediction Distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(y_proba[y_test == 0], bins=50, alpha=0.5, label="Legitimate", color="green")
    ax.hist(y_proba[y_test == 1], bins=50, alpha=0.5, label="Phishing", color="red")
    ax.set(xlabel="Predicted Probability", ylabel="Count", title="Prediction Distribution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "prediction_distribution.png", dpi=150)
    plt.close(fig)

    # Calibration Curve
    fig, ax = plt.subplots(figsize=(8, 6))
    fraction_of_positives, mean_predicted_value = calibration_curve(y_test, y_proba, n_bins=10)
    ax.plot(mean_predicted_value, fraction_of_positives, "s-", label="Model")
    ax.plot([0, 1], [0, 1], "k--", label="Perfectly Calibrated")
    ax.set(xlabel="Mean Predicted Probability", ylabel="Fraction of Positives", title="Calibration Curve")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "calibration_curve.png", dpi=150)
    plt.close(fig)

    logger.info(f"Evaluation plots saved to {output_dir}")


def main():
    """Run model evaluation pipeline."""
    logger.info("=" * 60)
    logger.info("MODEL EVALUATION PIPELINE")
    logger.info("=" * 60)

    params = load_params()

    # Load model and scaler
    model_path = MODELS_DIR / "phishing_rf_model.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    dataset_path = DATA_DIR / "phishing_dataset.csv"

    for p in [model_path, scaler_path, dataset_path]:
        if not p.exists():
            logger.error(f"File not found: {p}")
            sys.exit(1)

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Evaluate
    results = evaluate_model(model, scaler, dataset_path, params)

    # Save results
    report_path = REPORTS_DIR / "evaluation_metrics.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    logger.info(f"Evaluation report saved to {report_path}")

    # Log to MLflow
    try:
        tracker = ExperimentTracker()
        with tracker.start_run(
            run_name="model_evaluation",
            tags={"pipeline": "evaluation", "stage": "evaluate"},
        ):
            tracker.log_metrics(results["metrics"])
            tracker.log_artifact(str(report_path))

            # Log evaluation plots
            for plot_file in EVAL_PLOTS_DIR.glob("*.png"):
                tracker.log_artifact(str(plot_file), "evaluation_plots")
    except Exception as e:
        logger.warning(f"MLflow logging skipped: {e}")

    # Check quality gates
    if results["quality_gate"]["all_passed"]:
        logger.info("✓ All quality gates PASSED — model ready for deployment")
    else:
        logger.warning("✗ Quality gates FAILED — model needs improvement")
        failed = [d for d in results["quality_gate"]["details"] if not d["passed"]]
        for f in failed:
            logger.warning(f"  FAILED: {f['metric']}: {f['value']} < {f['threshold']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
