import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PRICE_BINS = [
    (0.0, 500.0, "lt_500"),
    (500.0, 1000.0, "500_1000"),
    (1000.0, 3000.0, "1000_3000"),
    (3000.0, 7000.0, "3000_7000"),
    (7000.0, 12000.0, "7000_12000"),
    (12000.0, np.inf, "gt_12000"),
]


def wmape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype="float64")
    y_pred = np.asarray(y_pred, dtype="float64")
    denom = np.nansum(np.abs(y_true))
    if denom <= 0:
        return None
    return float(np.nansum(np.abs(y_true - y_pred)) / denom * 100.0)


def _metric_block(frame, pred_col):
    if frame.empty:
        return {"n": 0, "wmape": None, "mae": None, "bias": None}
    error = frame[pred_col].astype("float64") - frame["actual"].astype("float64")
    return {
        "n": int(len(frame)),
        "wmape": wmape(frame["actual"], frame[pred_col]),
        "mae": float(np.nanmean(np.abs(error))),
        "bias": float(np.nanmean(error)),
    }


def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if np.isnan(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def validate_hourly_predictions(predictions):
    required = {"datetime", "actual", "price_cap"}
    missing = required.difference(predictions.columns)
    if missing:
        raise ValueError(f"Missing required prediction columns: {sorted(missing)}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    duplicate_count = int(frame["datetime"].duplicated().sum())
    if duplicate_count:
        duplicates = frame.loc[frame["datetime"].duplicated(), "datetime"].head(5).tolist()
        raise ValueError(
            "Each factual hour must be evaluated once. "
            f"Found {duplicate_count} duplicate datetime rows, examples={duplicates}"
        )

    frame = frame.sort_values("datetime").reset_index(drop=True)
    frame = frame.dropna(subset=["actual"])
    return frame


def calculate_metrics(predictions, pred_col="hybrid_pred"):
    frame = validate_hourly_predictions(predictions)
    if pred_col not in frame.columns:
        raise ValueError(f"Prediction column not found: {pred_col}")

    frame = frame.dropna(subset=[pred_col]).copy()
    if frame.empty:
        raise ValueError(f"No non-null predictions for column: {pred_col}")

    end_ts = frame["datetime"].max()
    start_3m = end_ts - pd.DateOffset(months=3)
    start_14d = end_ts - pd.Timedelta(days=14)
    start_13d = end_ts - pd.Timedelta(days=13)

    metrics = {
        "prediction_column": pred_col,
        "period": {
            "start": frame["datetime"].min(),
            "end": end_ts,
            "rows": int(len(frame)),
        },
        "all_available": _metric_block(frame, pred_col),
        "last_3m": _metric_block(frame[frame["datetime"] >= start_3m], pred_col),
        "last_14d": _metric_block(frame[frame["datetime"] >= start_14d], pred_col),
        "last_13d": _metric_block(frame[frame["datetime"] >= start_13d], pred_col),
        "by_hour": {},
        "by_price_bin": {},
        "regimes": {},
    }

    for hour, group in frame.groupby(frame["datetime"].dt.hour):
        metrics["by_hour"][int(hour)] = _metric_block(group, pred_col)

    actual = frame["actual"].astype("float64")
    for low, high, name in PRICE_BINS:
        mask = (actual >= low) & (actual < high)
        metrics["by_price_bin"][name] = _metric_block(frame[mask], pred_col)

    hour = frame["datetime"].dt.hour
    date_key = frame["datetime"].dt.normalize()
    day_min = frame.groupby(date_key)["actual"].transform("min")
    metrics["regimes"]["summer_daytime_low"] = _metric_block(
        frame[(frame["datetime"].dt.month.isin([6, 7, 8])) & hour.between(10, 16) & (day_min < 1000.0)],
        pred_col,
    )
    metrics["regimes"]["daytime_low_lt_1000"] = _metric_block(
        frame[hour.between(10, 16) & (actual < 1000.0)],
        pred_col,
    )
    metrics["regimes"]["cap_spike_evening"] = _metric_block(
        frame[hour.between(19, 23) & (actual > 14000.0)],
        pred_col,
    )
    metrics["regimes"]["evening_19_23"] = _metric_block(frame[hour.between(19, 23)], pred_col)
    return _json_safe(metrics)


def save_prediction_plot(predictions, pred_col, output_path):
    frame = validate_hourly_predictions(predictions)
    frame = frame.dropna(subset=[pred_col]).copy()
    if frame.empty:
        return

    end_ts = frame["datetime"].max()
    start_3m = end_ts - pd.DateOffset(months=3)
    start_14d = end_ts - pd.Timedelta(days=14)
    frame_3m = frame[frame["datetime"] >= start_3m]
    frame_14d = frame[frame["datetime"] >= start_14d]

    fig, axes = plt.subplots(2, 1, figsize=(16, 9), sharex=False)
    axes[0].plot(frame_3m["datetime"], frame_3m["actual"], color="black", linewidth=1.0, alpha=0.65, label="Actual")
    axes[0].plot(frame_3m["datetime"], frame_3m[pred_col], color="#d62728", linewidth=1.0, alpha=0.85, label=pred_col)
    axes[0].set_title(f"Last 3 months WMAPE: {wmape(frame_3m['actual'], frame_3m[pred_col]):.2f}%")
    axes[0].grid(True, alpha=0.25)
    axes[0].legend()

    axes[1].plot(frame_14d["datetime"], frame_14d["actual"], color="black", linewidth=1.2, label="Actual")
    axes[1].plot(frame_14d["datetime"], frame_14d[pred_col], color="#1f77b4", linewidth=1.2, label=pred_col)
    axes[1].set_title(f"Last 14 days WMAPE: {wmape(frame_14d['actual'], frame_14d[pred_col]):.2f}%")
    axes[1].grid(True, alpha=0.25)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)
    plt.close(fig)


def save_evaluation_artifacts(predictions, experiment_id, output_dir, pred_col="hybrid_pred"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics = calculate_metrics(predictions, pred_col=pred_col)
    csv_path = output_dir / f"neural_experiment_{experiment_id}_predictions.csv"
    metrics_path = output_dir / f"neural_experiment_{experiment_id}_metrics.json"
    plot_path = output_dir / f"neural_experiment_{experiment_id}_plot.png"

    predictions.sort_values("datetime").to_csv(csv_path, index=False)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    save_prediction_plot(predictions, pred_col, plot_path)

    return {
        "predictions_csv": os.fspath(csv_path),
        "metrics_json": os.fspath(metrics_path),
        "plot_png": os.fspath(plot_path),
        "metrics": metrics,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate one hourly prediction CSV without duplicate factual hours.")
    parser.add_argument("predictions_csv")
    parser.add_argument("--pred-col", default="hybrid_pred")
    parser.add_argument("--experiment-id", default="manual_eval")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    args = parser.parse_args()

    predictions = pd.read_csv(args.predictions_csv, low_memory=False)
    artifacts = save_evaluation_artifacts(
        predictions,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.pred_col,
    )
    last_3m = artifacts["metrics"]["last_3m"]["wmape"]
    last_14d = artifacts["metrics"]["last_14d"]["wmape"]
    print(f"{args.pred_col}: 3m={last_3m:.2f}% 14d={last_14d:.2f}%")


if __name__ == "__main__":
    main()
