"""Model evaluation: overall + per-protocol metrics and visualisation."""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.config import ALL_PROTOCOLS, PROTOCOL_FEATURE_PREFIX, RESULTS_DIR
from src.preprocessing import get_input_feature_names


def _mape(y_true, y_pred):
    """Mean absolute percentage error, ignoring zeros in y_true."""
    mask = y_true > 0
    if mask.sum() == 0:
        return float("nan")
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def _get_protocol_labels(X_test):
    """Recover protocol name per row from one-hot columns."""
    proto_cols = [f"{PROTOCOL_FEATURE_PREFIX}{p}" for p in ALL_PROTOCOLS]
    proto_matrix = X_test[proto_cols].values
    indices = proto_matrix.argmax(axis=1)
    return np.array([ALL_PROTOCOLS[i] for i in indices])


def evaluate_model(model, X_test, y_test, encoders):
    """Print metrics and save plots to RESULTS_DIR."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    y_pred = model.predict(X_test)
    y_true = y_test.values

    # ── Overall metrics ──────────────────────────────────────────────────
    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = _mape(y_true, y_pred)

    print("\n======================  Overall Metrics  ======================")
    print(f"  R2 Score : {r2:.5f}")
    print(f"  MAE      : {mae:.5f}")
    print(f"  RMSE     : {rmse:.5f}")
    print(f"  MAPE     : {mape:.2f}%")
    print("===============================================================\n")

    # ── Per-protocol metrics ─────────────────────────────────────────────
    proto_labels = _get_protocol_labels(X_test)
    rows = []
    for name in sorted(set(proto_labels)):
        mask = proto_labels == name
        yt, yp = y_true[mask], y_pred[mask]
        rows.append({
            "Protocol": name,
            "N": int(mask.sum()),
            "R2": round(r2_score(yt, yp), 4),
            "MAE": round(mean_absolute_error(yt, yp), 5),
            "RMSE": round(np.sqrt(mean_squared_error(yt, yp)), 5),
            "MAPE(%)": round(_mape(yt, yp), 2),
        })
    metrics_df = pd.DataFrame(rows)
    print(metrics_df.to_string(index=False))

    # ── Plot 1: Actual vs Predicted ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(y_true, y_pred, alpha=0.15, s=8, c="steelblue")
    lims = [0, max(y_true.max(), y_pred.max()) * 1.05]
    ax.plot(lims, lims, "r--", linewidth=1)
    ax.set_xlabel("Actual Secure Key Rate")
    ax.set_ylabel("Predicted Secure Key Rate")
    ax.set_title(f"Actual vs Predicted  (R2={r2:.4f})")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "actual_vs_predicted.png"), dpi=150)
    plt.close(fig)

    # ── Plot 2: Feature Importance ───────────────────────────────────────
    feature_names = get_input_feature_names()
    importance = model.feature_importances_
    idx = np.argsort(importance)
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.barh(np.array(feature_names)[idx], importance[idx], color="teal")
    ax.set_xlabel("Importance (gain)")
    ax.set_title("Feature Importance")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "feature_importance.png"), dpi=150)
    plt.close(fig)

    # ── Plot 3: Per-Protocol MAE bar chart ───────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(metrics_df["Protocol"], metrics_df["MAE"], color="coral")
    ax.set_ylabel("MAE")
    ax.set_title("Mean Absolute Error by Protocol")
    plt.xticks(rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "per_protocol_mae.png"), dpi=150)
    plt.close(fig)

    print(f"\nPlots saved to {RESULTS_DIR}/")
    return {"r2": r2, "mae": mae, "rmse": rmse, "mape": mape}
