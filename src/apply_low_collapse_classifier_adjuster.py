import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts
from prediction_limits import MIN_MARKET_PRICE, clip_price_forecast
from rolling_origin_stacker import build_stacker_frame
from train_neural_hybrid import finite_frame


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def parse_hours(text):
    text = str(text).strip().lower()
    if text in {"all", "0-23"}:
        return set(range(24))

    selected = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(value) for value in part.split("-", 1)]
            selected.update(range(start, end + 1))
        else:
            selected.add(int(part))
    return selected


def numeric_feature_columns(frame, output_col):
    excluded = {"datetime", "actual", output_col}
    cols = []
    for col in frame.columns:
        if col in excluded or col.endswith("_applied"):
            continue
        if frame[col].dtype.kind in "fi":
            cols.append(col)
    return cols


def make_classifier(args):
    if args.classifier == "et":
        return ExtraTreesClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth if args.max_depth > 0 else None,
            min_samples_leaf=args.min_samples_leaf,
            class_weight={0: 1.0, 1: args.positive_weight},
            random_state=args.seed,
            n_jobs=-1,
        )
    if args.classifier == "rf":
        return RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth if args.max_depth > 0 else None,
            min_samples_leaf=args.min_samples_leaf,
            class_weight={0: 1.0, 1: args.positive_weight},
            random_state=args.seed,
            n_jobs=-1,
        )
    if args.classifier == "hgb":
        return HistGradientBoostingClassifier(
            max_iter=args.max_iter,
            learning_rate=args.learning_rate,
            max_leaf_nodes=args.max_leaf_nodes,
            min_samples_leaf=args.min_samples_leaf,
            l2_regularization=args.l2_regularization,
            random_state=args.seed,
        )
    raise ValueError(f"Unsupported classifier: {args.classifier}")


def target_labels(actual, target):
    actual = np.asarray(actual, dtype="float64")
    if target == "collapse100":
        return (actual <= 100.0).astype("int64")
    if target == "low500":
        return (actual < 500.0).astype("int64")
    if target == "low1000":
        return (actual < 1000.0).astype("int64")
    raise ValueError(f"Unsupported target: {target}")


def anchor_values(frame, source, args):
    cap = frame["price_cap"].to_numpy(dtype="float64")
    if args.anchor == "floor10":
        anchor = np.full(len(frame), MIN_MARKET_PRICE, dtype="float64")
    elif args.anchor == "min_lag24_48":
        anchor = np.nanmin(
            np.vstack([
                source,
                pd.to_numeric(frame.get("f_price_lag_24"), errors="coerce").to_numpy(dtype="float64"),
                pd.to_numeric(frame.get("f_price_lag_48"), errors="coerce").to_numpy(dtype="float64"),
            ]),
            axis=0,
        )
    elif args.anchor == "min_lag24_48_roll7":
        anchor = np.nanmin(
            np.vstack([
                source,
                pd.to_numeric(frame.get("f_price_lag_24"), errors="coerce").to_numpy(dtype="float64"),
                pd.to_numeric(frame.get("f_price_lag_48"), errors="coerce").to_numpy(dtype="float64"),
                pd.to_numeric(frame.get("f_rolling_mean_hour_7d"), errors="coerce").to_numpy(dtype="float64"),
            ]),
            axis=0,
        )
    elif args.anchor == "rolling_min_24":
        anchor = pd.to_numeric(frame.get("f_rolling_min_24"), errors="coerce").to_numpy(dtype="float64")
    else:
        raise ValueError(f"Unsupported anchor: {args.anchor}")

    anchor = np.where(np.isfinite(anchor), anchor, source)
    return clip_price_forecast(anchor, cap)


def bounded_mask(values, min_value, max_value):
    series = pd.to_numeric(values, errors="coerce")
    arr = series.to_numpy(dtype="float64")
    mask = np.isfinite(arr)
    if min_value > 0.0:
        mask &= arr >= min_value
    if max_value > 0.0:
        mask &= arr <= max_value
    return mask


def apply_low_collapse_classifier_adjustment(predictions, args):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = build_stacker_frame(predictions, args.source_col)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    cap = frame["price_cap"].to_numpy(dtype="float64")
    source = clip_price_forecast(frame[args.source_col].to_numpy(dtype="float64"), cap)
    frame[args.source_col] = source
    anchor = anchor_values(frame, source, args)
    feature_cols = numeric_feature_columns(frame, args.output_col)

    adjusted = source.copy()
    probabilities = np.full(len(frame), np.nan, dtype="float64")
    applied = np.zeros(len(frame), dtype="int64")
    hours = parse_hours(args.hours)
    day_key = frame["datetime"].dt.normalize()
    unique_days = pd.DatetimeIndex(day_key.unique()).sort_values()

    for day in unique_days:
        target_mask = (day_key == day).to_numpy()
        train_start = pd.Timestamp(day) - pd.Timedelta(days=args.lookback_days)
        train_mask = ((frame["datetime"] < day) & (frame["datetime"] >= train_start)).to_numpy()
        if train_mask.sum() < args.min_train_days * 24:
            continue

        y_actual = frame.loc[train_mask, "actual"].to_numpy(dtype="float64")
        labels = target_labels(y_actual, args.target)
        if labels.sum() < args.min_positive_rows or labels.min() == labels.max():
            continue

        X_train = finite_frame(frame.loc[train_mask, feature_cols])
        X_target = finite_frame(frame.loc[target_mask, feature_cols])
        classifier = make_classifier(args)
        if args.classifier == "hgb":
            sample_weight = np.ones(len(labels), dtype="float64")
            sample_weight[labels == 1] = args.positive_weight
            classifier.fit(X_train, labels, sample_weight=sample_weight)
        else:
            classifier.fit(X_train, labels)

        day_prob = classifier.predict_proba(X_target)[:, 1]
        probabilities[target_mask] = day_prob

        selected = target_mask.copy()
        selected &= np.isfinite(probabilities)
        selected &= probabilities >= args.prob_threshold
        selected &= frame["datetime"].dt.hour.isin(hours).to_numpy()
        if args.source_min > 0.0 or args.source_max > 0.0:
            selected &= bounded_mask(source, args.source_min, args.source_max)
        if args.rolling7_min > 0.0 or args.rolling7_max > 0.0:
            selected &= bounded_mask(frame.get("f_rolling_mean_hour_7d"), args.rolling7_min, args.rolling7_max)

        adjusted[selected] = (1.0 - args.alpha) * source[selected] + args.alpha * anchor[selected]
        applied[selected] = 1

    if args.apply_recent_days > 0:
        recent_start = frame["datetime"].max() - pd.Timedelta(days=args.apply_recent_days)
        recent_mask = (frame["datetime"] >= recent_start).to_numpy()
        adjusted = np.where(recent_mask, adjusted, source)
        applied = np.where(recent_mask, applied, 0)

    frame[args.output_col] = clip_price_forecast(adjusted, cap)
    frame[f"{args.output_col}_probability"] = probabilities
    frame[f"{args.output_col}_applied"] = applied
    return frame, feature_cols


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Rolling-origin low-collapse classifier adjuster: "
            f"classifier `{params['classifier']}`, target `{params['target']}`, source `{params['source_col']}`, "
            f"anchor `{params['anchor']}`, probability threshold `{params['prob_threshold']}`, "
            f"alpha `{params['alpha']}`, hours `{params['hours']}`.\n"
        )
        f.write(
            "- For each delivery day, classifier training rows are strictly earlier than that day; "
            "current-row actual is not exposed as a feature.\n"
        )
        f.write(f"- Adjusted rows: `{applied_rows}`.\n\n")
        f.write("| variant | 3m WMAPE | 14d WMAPE | 3m rows |\n")
        f.write("|---|---:|---:|---:|\n")
        for col, metrics in variant_metrics.items():
            f.write(
                f"| `{col}` | {metrics['last_3m']['wmape']:.4f}% | "
                f"{metrics['last_14d']['wmape']:.4f}% | {metrics['last_3m']['n']} |\n"
            )
        f.write(f"\n- Predictions: `{artifacts['predictions_csv']}`\n")
        f.write(f"- Metrics: `{artifacts['metrics_json']}`\n")
        f.write(f"- Plot: `{artifacts['plot_png']}`\n")
    return os.fspath(log_path)


def main():
    parser = argparse.ArgumentParser(description="Leakage-safe rolling low-collapse classifier adjustment.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", default="low_collapse_classifier_pred")
    parser.add_argument("--classifier", choices=["et", "rf", "hgb"], default="et")
    parser.add_argument("--target", choices=["collapse100", "low500", "low1000"], default="collapse100")
    parser.add_argument("--anchor", choices=["floor10", "min_lag24_48", "min_lag24_48_roll7", "rolling_min_24"], default="floor10")
    parser.add_argument("--prob-threshold", type=float, default=0.7)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--hours", default="10-16")
    parser.add_argument("--lookback-days", type=int, default=75)
    parser.add_argument("--min-train-days", type=int, default=24)
    parser.add_argument("--min-positive-rows", type=int, default=8)
    parser.add_argument("--apply-recent-days", type=int, default=0)
    parser.add_argument("--source-min", type=float, default=0.0)
    parser.add_argument("--source-max", type=float, default=0.0)
    parser.add_argument("--rolling7-min", type=float, default=0.0)
    parser.add_argument("--rolling7-max", type=float, default=0.0)
    parser.add_argument("--n-estimators", type=int, default=260)
    parser.add_argument("--max-depth", type=int, default=9)
    parser.add_argument("--min-samples-leaf", type=int, default=4)
    parser.add_argument("--positive-weight", type=float, default=4.0)
    parser.add_argument("--max-iter", type=int, default=90)
    parser.add_argument("--learning-rate", type=float, default=0.04)
    parser.add_argument("--max-leaf-nodes", type=int, default=15)
    parser.add_argument("--l2-regularization", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted, feature_cols = apply_low_collapse_classifier_adjustment(predictions, args)
    variant_cols = [
        "tree_recent_calibrated_pred",
        args.source_col,
        args.output_col,
    ]
    variant_metrics = {
        col: calculate_metrics(adjusted, pred_col=col)
        for col in variant_cols
        if col in adjusted.columns
    }
    artifacts = save_evaluation_artifacts(
        adjusted,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )

    applied_col = f"{args.output_col}_applied"
    applied_rows = int(adjusted[applied_col].sum())
    params = vars(args).copy()
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["low_collapse_classifier_params"] = params
    payload["low_collapse_classifier_feature_count"] = len(feature_cols)
    payload["low_collapse_classifier_applied_rows"] = applied_rows
    payload["low_collapse_classifier_applied_days"] = int(
        adjusted.loc[adjusted[applied_col] == 1, "datetime"].dt.normalize().nunique()
    )
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    append_log(
        output_dir=args.output_dir,
        experiment_id=args.experiment_id,
        input_experiment=args.input_experiment,
        params=params,
        artifacts=artifacts,
        variant_metrics=variant_metrics,
        applied_rows=applied_rows,
    )

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.4f}% "
            f"14d={metrics['last_14d']['wmape']:.4f}%"
        )
    print(f"adjusted_rows={applied_rows}")


if __name__ == "__main__":
    main()
