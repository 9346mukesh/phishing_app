"""MLflow experiment tracking wrapper.

Provides a clean interface for logging experiments, parameters,
metrics, and artifacts to MLflow — all running locally for free.
"""

import os
from contextlib import contextmanager
from typing import Any, Dict, Optional

import mlflow
from mlflow.tracking import MlflowClient

from src.phishing.mlops.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI
from src.phishing.utils.logging_config import get_logger

logger = get_logger("experiment_tracker")


class ExperimentTracker:
    """MLflow-based experiment tracking."""

    def __init__(
        self,
        experiment_name: str = None,
        tracking_uri: str = None,
    ):
        self.experiment_name = experiment_name or MLFLOW_EXPERIMENT_NAME
        self.tracking_uri = tracking_uri or MLFLOW_TRACKING_URI

        # Configure MLflow
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient(self.tracking_uri)

        # Create or get experiment
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            self.experiment_id = mlflow.create_experiment(self.experiment_name)
            logger.info(f"Created experiment: {self.experiment_name}")
        else:
            self.experiment_id = experiment.experiment_id
            logger.info(f"Using experiment: {self.experiment_name} (id={self.experiment_id})")

        mlflow.set_experiment(self.experiment_name)

    @contextmanager
    def start_run(self, run_name: str = None, tags: Dict[str, str] = None):
        """Start an MLflow run as a context manager.

        Args:
            run_name: Name for the run
            tags: Tags to attach to the run

        Yields:
            MLflow run object
        """
        with mlflow.start_run(run_name=run_name) as run:
            if tags:
                for key, value in tags.items():
                    mlflow.set_tag(key, value)
            logger.info(f"Started run: {run.info.run_id} ({run_name})")
            yield run
            logger.info(f"Finished run: {run.info.run_id}")

    def log_params(self, params: Dict[str, Any]) -> None:
        """Log parameters to current run."""
        mlflow.log_params(params)
        logger.debug(f"Logged {len(params)} parameters")

    def log_metrics(self, metrics: Dict[str, float], step: int = None) -> None:
        """Log metrics to current run."""
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
        logger.debug(f"Logged {len(metrics)} metrics")

    def log_artifact(self, local_path: str, artifact_path: str = None) -> None:
        """Log an artifact file to current run."""
        mlflow.log_artifact(local_path, artifact_path)
        logger.debug(f"Logged artifact: {local_path}")

    def log_model(self, model, artifact_path: str = "model", **kwargs) -> None:
        """Log a scikit-learn model to current run."""
        mlflow.sklearn.log_model(model, artifact_path, **kwargs)
        logger.info(f"Logged model to {artifact_path}")

    def log_figure(self, figure, artifact_file: str) -> None:
        """Log a matplotlib figure to current run."""
        mlflow.log_figure(figure, artifact_file)
        logger.debug(f"Logged figure: {artifact_file}")

    def register_model(self, run_id: str, model_name: str) -> str:
        """Register a model from a run in the model registry.

        Args:
            run_id: MLflow run ID
            model_name: Name for the registered model

        Returns:
            Model version string
        """
        model_uri = f"runs:/{run_id}/model"
        result = mlflow.register_model(model_uri, model_name)
        logger.info(f"Registered model: {model_name} v{result.version}")
        return result.version

    def promote_model(
        self,
        model_name: str,
        version: str,
        stage: str = "Production",
    ) -> None:
        """Promote a model version to a stage.

        Args:
            model_name: Registered model name
            version: Version to promote
            stage: Target stage (Staging, Production, Archived)
        """
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
        )
        logger.info(f"Promoted {model_name} v{version} to {stage}")

    def get_best_run(self, metric: str = "f1_score", ascending: bool = False) -> Optional[dict]:
        """Get the best run by a metric.

        Args:
            metric: Metric name to sort by
            ascending: Sort ascending (True for loss metrics)

        Returns:
            Best run info dict or None
        """
        order = "ASC" if ascending else "DESC"
        runs = self.client.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=[f"metrics.{metric} {order}"],
            max_results=1,
        )
        if runs:
            best = runs[0]
            return {
                "run_id": best.info.run_id,
                "metrics": best.data.metrics,
                "params": best.data.params,
            }
        return None

    def get_run_history(self, max_results: int = 20) -> list:
        """Get recent run history.

        Returns:
            List of run info dicts
        """
        runs = self.client.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=["start_time DESC"],
            max_results=max_results,
        )
        return [
            {
                "run_id": r.info.run_id,
                "run_name": r.info.run_name,
                "status": r.info.status,
                "start_time": r.info.start_time,
                "metrics": r.data.metrics,
            }
            for r in runs
        ]
