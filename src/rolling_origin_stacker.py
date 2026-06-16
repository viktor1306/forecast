import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts
from prediction_limits import clip_price_forecast
from train_neural_hybrid import finite_frame, prepare_dataframe


BASE_FEATURES = [
    "hour",
    "price_cap",
    "month",
    "day_of_week_num",
    "is_weekend",
    "is_off_day",
    "is_summer",
    "hour_sin",
    "hour_cos",
    "day_sin",
    "day_cos",
    "week_sin",
    "week_cos",
    "price_lag_24",
    "price_lag_48",
    "price_lag_168",
    "ratio_lag_24",
    "ratio_lag_48",
    "ratio_lag_168",
    "rolling_mean_hour_3d",
    "rolling_mean_hour_7d",
    "rolling_mean_hour_14d",
    "rolling_min_24",
    "rolling_mean_24",
    "rolling_std_24",
    "feelslike",
    "humidity",
    "windspeed",
    "windgust",
    "cloudcover",
    "solarradiation",
    "uvindex",
    "renewable_pressure_index",
    "wind_cloud_interaction",
]


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def build_stacker_frame(predictions, source_col):
    feature_frame = prepare_dataframe()
    dt_index = pd.DatetimeIndex(pd.to_datetime(predictions["datetime"]))
    features = feature_frame.reindex(dt_index)
    existing = [col for col in BASE_FEATURES if col in features.columns]
    frame = predictions.copy().reset_index(drop=True)
    prefixed_features = features[existing].reset_index(drop=True).add_prefix("f_")
    stale_prefixed = [col for col in prefixed_features.columns if col in frame.columns]
    if stale_prefixed:
        frame = frame.drop(columns=stale_prefixed)
    if len(prefixed_features.columns) > 0:
        frame = pd.concat([frame, prefixed_features], axis=1)
    frame = frame.loc[:, ~frame.columns.duplicated()]

    prediction_cols = [
        source_col,
        "hybrid_guarded_pred",
        "hybrid_low_profile_pred",
        "tree_recent_calibrated_pred",
        "tree_base_pred",
        "ensemble_hybrid_pred",
        "ensemble_hybrid_recent_calibrated_pred",
        "ensemble_neural_pred",
    ]
    for col in prediction_cols:
        if col in frame.columns:
            cap = frame["price_cap"].replace(0, np.nan)
            frame[f"{col}_ratio"] = frame[col] / cap

    for lag_col in [
        "f_price_lag_24",
        "f_price_lag_48",
        "f_price_lag_168",
        "f_rolling_mean_hour_7d",
        "f_rolling_min_24",
    ]:
        if lag_col in frame.columns and source_col in frame.columns:
            frame[f"{source_col}_minus_{lag_col[2:]}"] = frame[source_col] - frame[lag_col]

    if source_col in frame.columns and "actual" in frame.columns:
        source = pd.to_numeric(frame[source_col], errors="coerce")
        actual = pd.to_numeric(frame["actual"], errors="coerce")
        signed_error = source - actual
        abs_error = signed_error.abs()
        ape = abs_error / actual.abs().clip(lower=1.0)

        # Only lagged source-error features are exposed. The current row error is
        # deliberately not kept in the frame, because target-day actuals are not
        # known at forecast time.
        for lag in (24, 48, 168):
            frame[f"{source_col}_signed_error_lag_{lag}"] = signed_error.shift(lag)
            frame[f"{source_col}_abs_error_lag_{lag}"] = abs_error.shift(lag)
            frame[f"{source_col}_ape_lag_{lag}"] = ape.shift(lag)

        day_key = pd.to_datetime(frame["datetime"]).dt.normalize()
        daily = pd.DataFrame({
            "day": day_key,
            "abs_error": abs_error,
            "signed_error": signed_error,
            "actual_abs": actual.abs(),
        }).groupby("day").agg(
            abs_error_sum=("abs_error", "sum"),
            signed_error_mean=("signed_error", "mean"),
            actual_abs_sum=("actual_abs", "sum"),
        )
        daily[f"{source_col}_day_wmape"] = (
            daily["abs_error_sum"] / daily["actual_abs_sum"].clip(lower=1.0) * 100.0
        )
        shifted_wmape = daily[f"{source_col}_day_wmape"].shift(1)
        shifted_bias = daily["signed_error_mean"].shift(1)
        frame[f"{source_col}_day_wmape_lag_1"] = day_key.map(shifted_wmape)
        frame[f"{source_col}_day_wmape_roll_7"] = day_key.map(
            shifted_wmape.rolling(7, min_periods=1).mean()
        )
        frame[f"{source_col}_day_wmape_std_7"] = day_key.map(
            shifted_wmape.rolling(7, min_periods=2).std()
        )
        frame[f"{source_col}_day_bias_lag_1"] = day_key.map(shifted_bias)
        frame[f"{source_col}_day_bias_roll_7"] = day_key.map(
            shifted_bias.rolling(7, min_periods=1).mean()
        )

    return frame


def numeric_feature_columns(frame):
    excluded = {"datetime", "actual"}
    feature_cols = [
        col
        for col in frame.columns
        if col not in excluded and frame[col].dtype.kind in "fi"
    ]
    return [col for col in feature_cols if not col.startswith("rolling_stack")]


def fit_predict_day(frame, feature_cols, source_col, target_mask, train_mask, target, alpha):
    X_train = finite_frame(frame.loc[train_mask, feature_cols])
    X_target = finite_frame(frame.loc[target_mask, feature_cols])
    y_actual = frame.loc[train_mask, "actual"].to_numpy(dtype="float64")
    y_source = frame.loc[train_mask, source_col].to_numpy(dtype="float64")

    day_start = frame.loc[target_mask, "datetime"].min().normalize()
    age_days = (day_start - frame.loc[train_mask, "datetime"]).dt.total_seconds().to_numpy(dtype="float64") / 86400.0
    lookback_span = max(float(np.nanmax(age_days)), 1.0)
    weights = np.clip(1.4 - age_days / lookback_span, 0.5, 1.4)
    hours = frame.loc[train_mask, "datetime"].dt.hour.to_numpy()
    weights[(hours >= 10) & (hours <= 16)] *= 1.25
    weights[y_actual < 1000.0] *= 1.5

    model = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
    if target == "resid":
        y_train = y_actual - y_source
        model.fit(X_train, y_train, ridge__sample_weight=weights)
        pred = frame.loc[target_mask, source_col].to_numpy(dtype="float64") + model.predict(X_target)
    elif target == "logresid":
        y_train = np.log1p(np.clip(y_actual, 0.0, None)) - np.log1p(np.clip(y_source, 0.0, None))
        model.fit(X_train, y_train, ridge__sample_weight=weights)
        pred = np.expm1(
            np.log1p(np.clip(frame.loc[target_mask, source_col].to_numpy(dtype="float64"), 0.0, None))
            + model.predict(X_target)
        )
    elif target == "log":
        y_train = np.log1p(np.clip(y_actual, 0.0, None))
        model.fit(X_train, y_train, ridge__sample_weight=weights)
        pred = np.expm1(model.predict(X_target))
    else:
        raise ValueError(f"Unsupported target: {target}")

    caps = frame.loc[target_mask, "price_cap"].to_numpy(dtype="float64")
    return clip_price_forecast(pred, caps)


def apply_rolling_stacker(
    predictions,
    source_col="hybrid_low_profile_pred",
    output_col="rolling_stack_pred",
    target="resid",
    lookback_days=30,
    min_train_days=14,
    alpha=1000.0,
    blend=0.25,
    apply_recent_days=None,
):
    if source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {source_col}")

    frame = build_stacker_frame(predictions, source_col)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    feature_cols = numeric_feature_columns(frame)
    source = frame[source_col].to_numpy(dtype="float64")
    stacked = source.copy()
    applied = np.zeros(len(frame), dtype="int64")

    for day in sorted(frame["datetime"].dt.normalize().unique()):
        target_mask = (frame["datetime"].dt.normalize() == day).to_numpy()
        train_start = pd.Timestamp(day) - pd.Timedelta(days=lookback_days)
        train_mask = ((frame["datetime"] < day) & (frame["datetime"] >= train_start)).to_numpy()
        if train_mask.sum() < min_train_days * 24:
            continue

        day_pred = fit_predict_day(
            frame=frame,
            feature_cols=feature_cols,
            source_col=source_col,
            target_mask=target_mask,
            train_mask=train_mask,
            target=target,
            alpha=alpha,
        )
        day_source = source[target_mask]
        stacked[target_mask] = (1.0 - blend) * day_source + blend * day_pred
        applied[target_mask] = 1

    if apply_recent_days is not None and apply_recent_days > 0:
        recent_start = frame["datetime"].max() - pd.Timedelta(days=apply_recent_days)
        recent_mask = (frame["datetime"] >= recent_start).to_numpy()
        stacked = np.where(recent_mask, stacked, source)
        applied = np.where(recent_mask, applied, 0)

    frame[output_col] = clip_price_forecast(stacked, frame["price_cap"].to_numpy(dtype="float64"))
    frame["rolling_stack_applied"] = applied
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_days):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Rolling-origin stacker: "
            f"source `{params['source_col']}`, target `{params['target']}`, "
            f"lookback `{params['lookback_days']}` days, min train `{params['min_train_days']}` days, "
            f"alpha `{params['alpha']}`, blend `{params['blend']}`, "
            f"apply recent days `{params.get('apply_recent_days')}`.\n"
        )
        f.write(f"- Applied target days: `{applied_days}`.\n")
        f.write("- For each target day, training rows are strictly earlier than that day.\n\n")
        f.write("| variant | 3m WMAPE | 14d WMAPE | 3m rows |\n")
        f.write("|---|---:|---:|---:|\n")
        for col, metrics in variant_metrics.items():
            f.write(
                f"| `{col}` | {metrics['last_3m']['wmape']:.2f}% | "
                f"{metrics['last_14d']['wmape']:.2f}% | {metrics['last_3m']['n']} |\n"
            )
        f.write(f"\n- Predictions: `{artifacts['predictions_csv']}`\n")
        f.write(f"- Metrics: `{artifacts['metrics_json']}`\n")
        f.write(f"- Plot: `{artifacts['plot_png']}`\n")
    return os.fspath(log_path)


def main():
    parser = argparse.ArgumentParser(description="Apply leakage-safe rolling-origin residual stacker.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", default="hybrid_low_profile_pred")
    parser.add_argument("--output-col", default="rolling_stack_pred")
    parser.add_argument("--target", choices=["resid", "logresid", "log"], default="resid")
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--min-train-days", type=int, default=14)
    parser.add_argument("--alpha", type=float, default=1000.0)
    parser.add_argument("--blend", type=float, default=0.25)
    parser.add_argument("--apply-recent-days", type=int, default=0)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    stacked = apply_rolling_stacker(
        predictions=predictions,
        source_col=args.source_col,
        output_col=args.output_col,
        target=args.target,
        lookback_days=args.lookback_days,
        min_train_days=args.min_train_days,
        alpha=args.alpha,
        blend=args.blend,
        apply_recent_days=args.apply_recent_days if args.apply_recent_days > 0 else None,
    )

    variant_cols = [
        "tree_recent_calibrated_pred",
        args.source_col,
        args.output_col,
    ]
    variant_metrics = {
        col: calculate_metrics(stacked, pred_col=col)
        for col in variant_cols
        if col in stacked.columns
    }
    artifacts = save_evaluation_artifacts(
        stacked,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )
    applied_days = int(stacked.loc[stacked["rolling_stack_applied"] == 1, "datetime"].dt.normalize().nunique())

    params = {
        "source_col": args.source_col,
        "target": args.target,
        "lookback_days": args.lookback_days,
        "min_train_days": args.min_train_days,
        "alpha": args.alpha,
        "blend": args.blend,
        "apply_recent_days": args.apply_recent_days if args.apply_recent_days > 0 else None,
    }
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["rolling_origin_params"] = params
    payload["rolling_stack_applied_days"] = applied_days
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    append_log(args.output_dir, args.experiment_id, args.input_experiment, params, artifacts, variant_metrics, applied_days)

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.3f}% "
            f"14d={metrics['last_14d']['wmape']:.3f}%"
        )
    print(f"applied_days={applied_days}")


if __name__ == "__main__":
    main()
