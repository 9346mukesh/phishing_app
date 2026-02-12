"""MLOps configuration and utilities."""

import os
from pathlib import Path

import yaml


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent.parent


def load_params(params_path: str = None) -> dict:
    """Load parameters from params.yaml.

    Args:
        params_path: Path to params.yaml (default: project root)

    Returns:
        Dictionary of parameters
    """
    if params_path is None:
        params_path = str(get_project_root() / "params.yaml")

    with open(params_path) as f:
        return yaml.safe_load(f)


# Standard paths
PROJECT_ROOT = get_project_root()
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
PLOTS_DIR = REPORTS_DIR / "plots"
EVAL_PLOTS_DIR = REPORTS_DIR / "evaluation_plots"
MLFLOW_DIR = PROJECT_ROOT / "mlruns"

# Ensure directories exist
for d in [DATA_DIR, MODELS_DIR, REPORTS_DIR, PLOTS_DIR, EVAL_PLOTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"file://{MLFLOW_DIR}")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "phishing-detection")
