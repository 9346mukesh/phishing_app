"""Model monitoring and data drift detection using Evidently.

Detects feature drift and model performance degradation.
Run: python -m src.phishing.mlops.monitor
Or:  dvc repro monitor
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split

from src.phishing.mlops.config import DATA_DIR, MODELS_DIR, REPORTS_DIR, load_params
from src.phishing.core.feature_extractor import extract_features_from_url, NUM_FEATURES
from src.phishing.utils.logging_config import get_logger

logger = get_logger("model_monitor")


class DriftDetector:
    """Statistical drift detection for features and predictions."""

    def __init__(self, threshold: float = 0.05):
        """
        Args:
            threshold: p-value threshold for drift detection
        """
        self.threshold = threshold
        self.drift_results = []

    def detect_feature_drift(
        self,
        reference: pd.DataFrame,
        current: pd.DataFrame,
        feature_names: list = None,
    ) -> dict:
        """Detect feature drift using Kolmogorov-Smirnov test.

        Args:
            reference: Reference (training) data
            current: Current (production) data
            feature_names: Column names to check

        Returns:
            Drift detection results
        """
        if feature_names is None:
            feature_names = list(reference.columns)

        results = {
            "drift_detected": False,
            "drifted_features": [],
            "feature_results": {},
            "summary": {},
        }

        drifted_count = 0

        for col in feature_names:
            if col not in reference.columns or col not in current.columns:
                continue

            ref_data = reference[col].dropna().values
            cur_data = current[col].dropna().values

            if len(ref_data) == 0 or len(cur_data) == 0:
                continue

            # KS test
            ks_stat, p_value = stats.ks_2samp(ref_data, cur_data)
            is_drifted = p_value < self.threshold

            results["feature_results"][col] = {
                "ks_statistic": round(float(ks_stat), 6),
                "p_value": round(float(p_value), 6),
                "drift_detected": is_drifted,
                "reference_mean": round(float(np.mean(ref_data)), 4),
                "current_mean": round(float(np.mean(cur_data)), 4),
                "reference_std": round(float(np.std(ref_data)), 4),
                "current_std": round(float(np.std(cur_data)), 4),
            }

            if is_drifted:
                drifted_count += 1
                results["drifted_features"].append(col)
                logger.warning(
                    f"DRIFT detected in {col}: KS={ks_stat:.4f}, p={p_value:.6f}"
                )

        results["drift_detected"] = drifted_count > 0
        results["summary"] = {
            "total_features": len(feature_names),
            "drifted_features": drifted_count,
            "drift_ratio": drifted_count / len(feature_names) if feature_names else 0,
            "threshold": self.threshold,
        }

        return results

    def detect_prediction_drift(
        self,
        reference_predictions: np.ndarray,
        current_predictions: np.ndarray,
    ) -> dict:
        """Detect drift in model predictions.

        Args:
            reference_predictions: Predictions on reference data
            current_predictions: Predictions on current data

        Returns:
            Prediction drift results
        """
        ks_stat, p_value = stats.ks_2samp(reference_predictions, current_predictions)

        return {
            "drift_detected": p_value < self.threshold,
            "ks_statistic": round(float(ks_stat), 6),
            "p_value": round(float(p_value), 6),
            "reference_mean": round(float(np.mean(reference_predictions)), 4),
            "current_mean": round(float(np.mean(current_predictions)), 4),
        }


def generate_drift_html_report(drift_results: dict, output_path: Path) -> None:
    """Generate an HTML drift report.

    Args:
        drift_results: Results from drift detection
        output_path: Where to save the HTML report
    """
    feature_results = drift_results.get("feature_drift", {}).get("feature_results", {})
    summary = drift_results.get("feature_drift", {}).get("summary", {})
    drift_detected = drift_results.get("feature_drift", {}).get("drift_detected", False)
    drifted_count = summary.get("drifted_features", 0)
    total_features = summary.get("total_features", 0)
    drift_ratio = summary.get("drift_ratio", 0)

    drift_status_class = "status-drift" if drifted_count > 0 else "status-ok"
    overall_class = "status-drift" if drift_detected else "status-ok"
    overall_text = "⚠️ DRIFT DETECTED" if drift_detected else "✅ NO DRIFT"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Drift Report</title>
    <style>
        body {{ font-family: 'Inter', Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #1a1a2e; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .status-ok {{ color: #10B981; font-weight: bold; }}
        .status-drift {{ color: #EF4444; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; }}
        .drift {{ background: #FEF2F2; }}
        .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
        .metric {{ text-align: center; padding: 16px; }}
        .metric-value {{ font-size: 2em; font-weight: 700; color: #1a1a2e; }}
        .metric-label {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Model Drift Report</h1>

        <div class="card">
            <h2>Summary</h2>
            <div class="summary">
                <div class="metric">
                    <div class="metric-value">{total_features}</div>
                    <div class="metric-label">Features Monitored</div>
                </div>
                <div class="metric">
                    <div class="metric-value {drift_status_class}">
                        {drifted_count}
                    </div>
                    <div class="metric-label">Features with Drift</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{drift_ratio:.1%}</div>
                    <div class="metric-label">Drift Ratio</div>
                </div>
            </div>
            <p>Overall Status:
                <span class="{overall_class}">
                    {overall_text}
                </span>
            </p>
        </div>

        <div class="card">
            <h2>Feature Details</h2>
            <table>
                <tr>
                    <th>Feature</th>
                    <th>KS Statistic</th>
                    <th>p-value</th>
                    <th>Ref Mean</th>
                    <th>Cur Mean</th>
                    <th>Status</th>
                </tr>"""

    for feature, result in feature_results.items():
        drift_class = 'drift' if result['drift_detected'] else ''
        status = '<span class="status-drift">DRIFT</span>' if result['drift_detected'] else '<span class="status-ok">OK</span>'
        html += f"""
                <tr class="{drift_class}">
                    <td>{feature}</td>
                    <td>{result['ks_statistic']:.4f}</td>
                    <td>{result['p_value']:.6f}</td>
                    <td>{result['reference_mean']:.4f}</td>
                    <td>{result['current_mean']:.4f}</td>
                    <td>{status}</td>
                </tr>"""

    html += """
            </table>
        </div>
    </div>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    logger.info(f"Drift report saved to {output_path}")


def main():
    """Run monitoring pipeline."""
    import joblib

    logger.info("=" * 60)
    logger.info("MODEL MONITORING PIPELINE")
    logger.info("=" * 60)

    params = load_params()
    monitor_params = params.get("monitoring", {})
    train_params = params.get("train", {})

    # Load data
    dataset_path = DATA_DIR / "phishing_dataset.csv"
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        sys.exit(1)

    df = pd.read_csv(dataset_path)

    # Auto-detect label column
    label_candidates = ["label", "Label", "target", "Target", "class", "Class", "Result"]
    label_col = None
    for col in label_candidates:
        if col in df.columns:
            label_col = col
            break
    if label_col is None:
        label_col = df.columns[-1]

    # Check if URL-based dataset and extract features
    non_label_cols = [c for c in df.columns if c != label_col]
    has_url_col = any(c.lower() == "url" for c in non_label_cols)

    if has_url_col:
        url_col = next(c for c in non_label_cols if c.lower() == "url")
        logger.info(f"URL-based dataset — extracting features from '{url_col}' column")
        feature_names = [f"feature_{i}" for i in range(NUM_FEATURES)]
        features_list = []
        for url in df[url_col]:
            try:
                features_list.append(extract_features_from_url(str(url)))
            except Exception:
                features_list.append([0] * NUM_FEATURES)
        feature_df = pd.DataFrame(features_list, columns=feature_names)
        feature_cols = feature_names
    else:
        feature_cols = [c for c in df.columns if c != label_col]
        feature_df = df[feature_cols]

    # Simulate reference/current split
    # In production, reference = training data, current = recent production data
    ref_size = monitor_params.get("reference_window_size", 5000)
    cur_size = monitor_params.get("current_window_size", 1000)

    # Use train/test split as proxy for reference/current
    X = feature_df
    y = df[label_col]

    X_ref, X_cur, y_ref, y_cur = train_test_split(
        X, y,
        test_size=min(cur_size / len(df), 0.3),
        random_state=train_params.get("random_state", 42),
        stratify=y,
    )

    # Drift detection
    threshold = monitor_params.get("drift_threshold", 0.05)
    detector = DriftDetector(threshold=threshold)

    feature_drift = detector.detect_feature_drift(X_ref, X_cur, feature_cols)

    # Prediction drift (if model available)
    prediction_drift = None
    model_path = MODELS_DIR / "phishing_rf_model.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"

    if model_path.exists() and scaler_path.exists():
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        ref_scaled = scaler.transform(X_ref)
        cur_scaled = scaler.transform(X_cur)

        ref_proba = model.predict_proba(ref_scaled)[:, 1]
        cur_proba = model.predict_proba(cur_scaled)[:, 1]

        prediction_drift = detector.detect_prediction_drift(ref_proba, cur_proba)

    # Build results
    results = {
        "feature_drift": feature_drift,
        "prediction_drift": prediction_drift,
        "config": {
            "threshold": threshold,
            "reference_samples": len(X_ref),
            "current_samples": len(X_cur),
        },
    }

    # Save JSON report
    json_path = REPORTS_DIR / "drift_metrics.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Save HTML report
    html_path = REPORTS_DIR / "drift_report.html"
    generate_drift_html_report(results, html_path)

    # Summary
    if feature_drift["drift_detected"]:
        drifted = feature_drift["drifted_features"]
        logger.warning(f"⚠️  Feature drift detected in {len(drifted)} features: {drifted}")
    else:
        logger.info("✅ No feature drift detected")

    if prediction_drift and prediction_drift["drift_detected"]:
        logger.warning("⚠️  Prediction drift detected!")
    elif prediction_drift:
        logger.info("✅ No prediction drift detected")

    logger.info("Monitoring pipeline complete")


if __name__ == "__main__":
    main()
