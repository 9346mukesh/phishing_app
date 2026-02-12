"""Model promotion and registry management.

Handles promoting models through stages:
  Development → Staging → Production

Run: python -m src.phishing.mlops.promote --action promote --version 1
"""

import argparse
import json
import sys
from pathlib import Path

import joblib

from src.phishing.mlops.config import MODELS_DIR, REPORTS_DIR, load_params
from src.phishing.mlops.experiment_tracker import ExperimentTracker
from src.phishing.utils.logging_config import get_logger

logger = get_logger("model_promotion")

MODEL_NAME = "phishing-detector"


def check_model_quality(evaluation_report: Path, params: dict) -> bool:
    """Check if model passes quality gates from evaluation report.

    Args:
        evaluation_report: Path to evaluation_metrics.json
        params: Parameters with evaluation thresholds

    Returns:
        True if model passes all gates
    """
    if not evaluation_report.exists():
        logger.error(f"Evaluation report not found: {evaluation_report}")
        return False

    with open(evaluation_report) as f:
        results = json.load(f)

    return results.get("quality_gate", {}).get("all_passed", False)


def promote_latest(stage: str = "Production") -> None:
    """Promote the latest model version to the given stage.

    Args:
        stage: Target stage (Staging or Production)
    """
    tracker = ExperimentTracker()

    # Check evaluation results
    eval_report = REPORTS_DIR / "evaluation_metrics.json"
    params = load_params()

    if stage == "Production" and not check_model_quality(eval_report, params):
        logger.error("Cannot promote to Production — quality gates not passed")
        logger.info("Run 'dvc repro evaluate' first")
        sys.exit(1)

    # Get latest model version
    try:
        from mlflow.tracking import MlflowClient

        client = MlflowClient(tracker.tracking_uri)
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")

        if not versions:
            logger.error(f"No registered models found with name '{MODEL_NAME}'")
            logger.info("Run training pipeline first: python -m src.phishing.mlops.train")
            sys.exit(1)

        # Get latest version
        latest = max(versions, key=lambda v: int(v.version))
        logger.info(f"Latest version: {MODEL_NAME} v{latest.version}")

        # Promote
        tracker.promote_model(MODEL_NAME, latest.version, stage)
        logger.info(f"Model {MODEL_NAME} v{latest.version} promoted to {stage}")

    except Exception as e:
        logger.error(f"Promotion failed: {e}")
        sys.exit(1)


def list_models() -> None:
    """List all registered model versions."""
    tracker = ExperimentTracker()

    try:
        from mlflow.tracking import MlflowClient

        client = MlflowClient(tracker.tracking_uri)
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")

        if not versions:
            logger.info("No registered models found")
            return

        logger.info(f"\nRegistered Models: {MODEL_NAME}")
        logger.info("-" * 60)

        for v in sorted(versions, key=lambda x: int(x.version)):
            logger.info(
                f"  v{v.version} | Stage: {v.current_stage} | "
                f"Status: {v.status} | Run: {v.run_id[:8]}..."
            )

    except Exception as e:
        logger.error(f"Failed to list models: {e}")


def compare_models() -> None:
    """Compare recent experiment runs."""
    tracker = ExperimentTracker()
    history = tracker.get_run_history(max_results=10)

    if not history:
        logger.info("No runs found")
        return

    logger.info("\nRecent Experiment Runs:")
    logger.info("-" * 80)
    logger.info(f"{'Run ID':<12} {'Name':<20} {'Status':<10} {'Accuracy':<10} {'F1':<10} {'AUC':<10}")
    logger.info("-" * 80)

    for run in history:
        m = run.get("metrics", {})
        logger.info(
            f"{run['run_id'][:10]:<12} "
            f"{(run.get('run_name') or 'unnamed')[:18]:<20} "
            f"{run['status']:<10} "
            f"{m.get('accuracy', 0):<10.4f} "
            f"{m.get('f1_score', 0):<10.4f} "
            f"{m.get('roc_auc', 0):<10.4f}"
        )

    # Show best run
    best = tracker.get_best_run(metric="f1_score")
    if best:
        logger.info(f"\nBest run by F1: {best['run_id'][:10]} (F1={best['metrics'].get('f1_score', 0):.4f})")


def main():
    parser = argparse.ArgumentParser(description="Model promotion and registry management")
    parser.add_argument(
        "--action",
        choices=["promote", "list", "compare"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument(
        "--stage",
        choices=["Staging", "Production"],
        default="Staging",
        help="Target stage for promotion",
    )
    parser.add_argument("--version", type=str, help="Specific version to promote")

    args = parser.parse_args()

    if args.action == "promote":
        promote_latest(stage=args.stage)
    elif args.action == "list":
        list_models()
    elif args.action == "compare":
        compare_models()


if __name__ == "__main__":
    main()
