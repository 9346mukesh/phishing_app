"""Reproducible model training pipeline with MLflow tracking.

This is the main training script that:
1. Loads and validates data
2. Extracts features
3. Trains a Random Forest model
4. Logs everything to MLflow
5. Saves model artifacts for DVC tracking

Run: python -m src.phishing.mlops.train
Or:  dvc repro train
"""

import json
import os
import sys
import time
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for CI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from src.phishing.mlops.config import (
    DATA_DIR,
    MODELS_DIR,
    PLOTS_DIR,
    REPORTS_DIR,
    load_params,
)
from src.phishing.mlops.experiment_tracker import ExperimentTracker
from src.phishing.core.feature_extractor import extract_features_from_url, NUM_FEATURES
from src.phishing.utils.logging_config import get_logger

logger = get_logger("training_pipeline")


def load_dataset(data_path: Path) -> pd.DataFrame:
    """Load the phishing dataset.

    Args:
        data_path: Path to CSV dataset

    Returns:
        DataFrame with features and labels
    """
    logger.info(f"Loading dataset from {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")
    return df


def prepare_data(df: pd.DataFrame, params: dict) -> tuple:
    """Prepare training and test data.

    Supports both URL-based datasets (url, label) and pre-extracted feature datasets.
    For URL-based datasets, features are extracted using the project's feature extractor.

    Args:
        df: Raw dataset
        params: Training parameters

    Returns:
        Tuple of (X_train, X_test, y_train, y_test, scaler, feature_names)
    """
    # Auto-detect label column
    label_candidates = ["label", "Label", "target", "Target", "class", "Class", "Result"]
    label_col = None
    for col in label_candidates:
        if col in df.columns:
            label_col = col
            break
    if label_col is None:
        label_col = df.columns[-1]

    logger.info(f"Using label column: {label_col}")

    # Check if this is a URL-based dataset
    non_label_cols = [c for c in df.columns if c != label_col]
    has_url_col = any(c.lower() == "url" for c in non_label_cols)

    if has_url_col:
        url_col = next(c for c in non_label_cols if c.lower() == "url")
        logger.info(f"URL-based dataset detected — extracting {NUM_FEATURES} features from '{url_col}' column")

        feature_names = [f"feature_{i}" for i in range(NUM_FEATURES)]
        features_list = []
        failed_count = 0

        for idx, url in enumerate(df[url_col]):
            try:
                features = extract_features_from_url(str(url))
                features_list.append(features)
            except Exception as e:
                logger.debug(f"Feature extraction failed for row {idx}: {e}")
                features_list.append([0] * NUM_FEATURES)
                failed_count += 1

        if failed_count > 0:
            logger.warning(f"Feature extraction failed for {failed_count}/{len(df)} URLs")

        X = np.array(features_list)
        y = df[label_col].values
    else:
        # Pre-extracted numeric features
        feature_names = [c for c in df.columns if c != label_col]
        X = df[feature_names].values
        y = df[label_col].values

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=params.get("test_size", 0.2),
        random_state=params.get("random_state", 42),
        stratify=y,
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logger.info(f"Train: {X_train_scaled.shape}, Test: {X_test_scaled.shape}")

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names


def train_model(X_train, y_train, params: dict) -> RandomForestClassifier:
    """Train a Random Forest classifier.

    Args:
        X_train: Training features
        y_train: Training labels
        params: Model hyperparameters

    Returns:
        Trained model
    """
    logger.info("Training Random Forest model...")

    model = RandomForestClassifier(
        n_estimators=params.get("n_estimators", 200),
        max_depth=params.get("max_depth", 20),
        min_samples_split=params.get("min_samples_split", 5),
        min_samples_leaf=params.get("min_samples_leaf", 2),
        max_features=params.get("max_features", "sqrt"),
        class_weight=params.get("class_weight", "balanced"),
        random_state=params.get("random_state", 42),
        n_jobs=-1,
    )

    start_time = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - start_time

    logger.info(f"Training complete in {training_time:.2f}s")

    return model


def evaluate_model(model, X_test, y_test, cv_folds: int = 5, X_train=None, y_train=None) -> dict:
    """Evaluate model and compute metrics.

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        cv_folds: Number of cross-validation folds
        X_train: Training features (for CV)
        y_train: Training labels (for CV)

    Returns:
        Dictionary of metrics
    """
    logger.info("Evaluating model...")

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Core metrics
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "test_samples": int(len(y_test)),
    }

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics["true_negatives"] = int(cm[0, 0])
    metrics["false_positives"] = int(cm[0, 1])
    metrics["false_negatives"] = int(cm[1, 0])
    metrics["true_positives"] = int(cm[1, 1])

    # Specificity
    if (cm[0, 0] + cm[0, 1]) > 0:
        metrics["specificity"] = float(cm[0, 0] / (cm[0, 0] + cm[0, 1]))
    else:
        metrics["specificity"] = 0.0

    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics["classification_report"] = report

    # Cross-validation
    if X_train is not None and y_train is not None:
        cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring="accuracy")
        metrics["cv_scores"] = cv_scores.tolist()
        metrics["mean_cv_score"] = float(cv_scores.mean())
        metrics["std_cv_score"] = float(cv_scores.std())
        metrics["folds"] = cv_folds

    logger.info(
        f"Metrics — Acc: {metrics['accuracy']:.4f}, "
        f"F1: {metrics['f1_score']:.4f}, "
        f"AUC: {metrics['roc_auc']:.4f}"
    )

    return metrics


def generate_plots(model, X_test, y_test, feature_names: list, output_dir: Path) -> list:
    """Generate training plots and save to disk.

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        feature_names: Feature column names
        output_dir: Directory to save plots

    Returns:
        List of plot file paths
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_files = []

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # 1. Confusion Matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=[0, 1],
        yticks=[0, 1],
        xticklabels=["Legitimate", "Phishing"],
        yticklabels=["Legitimate", "Phishing"],
        xlabel="Predicted",
        ylabel="Actual",
        title="Confusion Matrix",
    )
    for i in range(2):
        for j in range(2):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14)
    fig.tight_layout()
    cm_path = output_dir / "confusion_matrix.png"
    fig.savefig(cm_path, dpi=150)
    plt.close(fig)
    plot_files.append(str(cm_path))

    # 2. ROC Curve
    fig, ax = plt.subplots(figsize=(8, 6))
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)
    ax.plot(fpr, tpr, label=f"ROC (AUC = {auc:.4f})", linewidth=2)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
    ax.set(xlabel="False Positive Rate", ylabel="True Positive Rate", title="ROC Curve")
    ax.legend(loc="lower right")
    fig.tight_layout()
    roc_path = output_dir / "roc_curve.png"
    fig.savefig(roc_path, dpi=150)
    plt.close(fig)
    plot_files.append(str(roc_path))

    # 3. Feature Importance
    fig, ax = plt.subplots(figsize=(10, 8))
    importances = model.feature_importances_
    n_features = min(len(feature_names), len(importances))
    indices = np.argsort(importances[:n_features])[-15:]  # Top 15
    names = [feature_names[i] if i < len(feature_names) else f"Feature_{i}" for i in indices]
    ax.barh(range(len(indices)), importances[indices], align="center")
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels(names)
    ax.set(xlabel="Feature Importance", title="Top 15 Feature Importances")
    fig.tight_layout()
    fi_path = output_dir / "feature_importance.png"
    fig.savefig(fi_path, dpi=150)
    plt.close(fig)
    plot_files.append(str(fi_path))

    logger.info(f"Generated {len(plot_files)} plots")
    return plot_files


def main():
    """Run the full training pipeline."""
    logger.info("=" * 60)
    logger.info("PHISHING DETECTION MODEL TRAINING PIPELINE")
    logger.info("=" * 60)

    # Load params
    params = load_params()
    train_params = params.get("train", {})

    # Paths
    dataset_path = DATA_DIR / "phishing_dataset.csv"

    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.info("Place your dataset at data/phishing_dataset.csv")
        sys.exit(1)

    # Initialize experiment tracker
    tracker = ExperimentTracker()

    with tracker.start_run(
        run_name="rf_training",
        tags={
            "model_type": "RandomForest",
            "pipeline": "training",
            "stage": "train",
        },
    ) as run:
        # Log all parameters
        tracker.log_params({
            "n_estimators": train_params.get("n_estimators", 200),
            "max_depth": train_params.get("max_depth", 20),
            "min_samples_split": train_params.get("min_samples_split", 5),
            "min_samples_leaf": train_params.get("min_samples_leaf", 2),
            "max_features": train_params.get("max_features", "sqrt"),
            "test_size": train_params.get("test_size", 0.2),
            "random_state": train_params.get("random_state", 42),
            "cv_folds": train_params.get("cv_folds", 5),
        })

        # 1. Load data
        df = load_dataset(dataset_path)
        tracker.log_params({"dataset_rows": len(df), "dataset_cols": len(df.columns)})

        # 2. Prepare data
        X_train, X_test, y_train, y_test, scaler, feature_names = prepare_data(df, train_params)

        # 3. Train model
        model = train_model(X_train, y_train, train_params)

        # 4. Evaluate
        metrics = evaluate_model(
            model,
            X_test,
            y_test,
            cv_folds=train_params.get("cv_folds", 5),
            X_train=X_train,
            y_train=y_train,
        )

        # Log metrics to MLflow
        tracker.log_metrics({
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1_score"],
            "roc_auc": metrics["roc_auc"],
            "specificity": metrics["specificity"],
            "mean_cv_score": metrics.get("mean_cv_score", 0),
        })

        # 5. Generate plots
        plot_files = generate_plots(model, X_test, y_test, feature_names, PLOTS_DIR)
        for pf in plot_files:
            tracker.log_artifact(pf, "plots")

        # 6. Save model artifacts
        model_path = MODELS_DIR / "phishing_rf_model.pkl"
        scaler_path = MODELS_DIR / "scaler.pkl"
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Scaler saved to {scaler_path}")

        # Log model to MLflow
        tracker.log_model(model, artifact_path="model")
        tracker.log_artifact(str(model_path))
        tracker.log_artifact(str(scaler_path))

        # 7. Save metrics JSON (for DVC tracking)
        metrics_for_json = {k: v for k, v in metrics.items()}
        metrics_for_json["confusion_matrix"] = confusion_matrix(y_test, model.predict(X_test)).tolist()
        metrics_path = MODELS_DIR / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics_for_json, f, indent=2, default=str)
        tracker.log_artifact(str(metrics_path))

        logger.info(f"Run ID: {run.info.run_id}")
        logger.info("Training pipeline complete!")

        # 8. Register model in MLflow registry
        try:
            version = tracker.register_model(run.info.run_id, "phishing-detector")
            logger.info(f"Model registered as v{version}")
        except Exception as e:
            logger.warning(f"Model registration skipped: {e}")

    return metrics


if __name__ == "__main__":
    main()
