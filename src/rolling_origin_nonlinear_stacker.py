import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler

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


def numeric_feature_columns(frame, output_col):
    excluded = {"datetime", "actual", output_col}
    feature_cols = []
    for col in frame.columns:
        if col in excluded:
            continue
        if col.endswith("_pred") and col == output_col:
            continue
        if frame[col].dtype.kind in "fi":
            feature_cols.append(col)
    return feature_cols


def make_model(model_type, random_state, args):
    if model_type == "hgb":
        return HistGradientBoostingRegressor(
            loss=args.loss,
            learning_rate=args.learning_rate,
            max_iter=args.max_iter,
            max_leaf_nodes=args.max_leaf_nodes,
            min_samples_leaf=args.min_samples_leaf,
            l2_regularization=args.l2_regularization,
            random_state=random_state,
        )
    if model_type == "rf":
        return RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth if args.max_depth > 0 else None,
            min_samples_leaf=args.min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,
        )
    if model_type == "et":
        return ExtraTreesRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth if args.max_depth > 0 else None,
            min_samples_leaf=args.min_samples_leaf,
            random_state=random_state,
            n_jobs=-1,
        )
    if model_type == "mlp":
        return MLPRegressor(
            hidden_layer_sizes=parse_hidden_layers(args.hidden_layers),
            activation=args.activation,
            solver="adam",
            alpha=args.mlp_alpha,
            learning_rate_init=args.learning_rate,
            max_iter=args.max_iter,
            early_stopping=args.mlp_early_stopping,
            validation_fraction=args.mlp_validation_fraction,
            n_iter_no_change=args.mlp_n_iter_no_change,
            random_state=random_state,
        )
    raise ValueError(f"Unsupported model type: {model_type}")


def target_values(actual, source, target):
    if target == "resid":
        return actual - source
    if target == "ratio":
        return np.maximum(actual, MIN_MARKET_PRICE) / np.maximum(source, MIN_MARKET_PRICE)
    if target == "logresid":
        return np.log1p(np.clip(actual, MIN_MARKET_PRICE, None)) - np.log1p(np.clip(source, MIN_MARKET_PRICE, None))
    if target == "log":
        return np.log1p(np.clip(actual, MIN_MARKET_PRICE, None))
    raise ValueError(f"Unsupported target: {target}")


def invert_prediction(source, raw_pred, target):
    if target == "resid":
        return source + raw_pred
    if target == "ratio":
        return np.maximum(source, MIN_MARKET_PRICE) * np.clip(raw_pred, 0.0, 3.0)
    if target == "logresid":
        return np.expm1(np.log1p(np.clip(source, MIN_MARKET_PRICE, None)) + raw_pred)
    if target == "log":
        return np.expm1(raw_pred)
    raise ValueError(f"Unsupported target: {target}")


def parse_hidden_layers(text):
    values = [int(part.strip()) for part in str(text).split(",") if part.strip()]
    if not values or any(value <= 0 for value in values):
        raise ValueError(f"Unsupported hidden layer sizes: {text}")
    return tuple(values)


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


def sample_weights(
    frame,
    train_mask,
    day,
    half_life_days,
    low_weight,
    high_weight,
    daytime_weight,
    evening_weight,
    daytime_low_weight,
):
    train_dt = frame.loc[train_mask, "datetime"]
    age_days = (pd.Timestamp(day) - train_dt).dt.total_seconds().to_numpy(dtype="float64") / 86400.0
    if half_life_days > 0:
        weights = np.power(0.5, age_days / half_life_days)
    else:
        weights = np.ones(train_mask.sum(), dtype="float64")
    actual = frame.loc[train_mask, "actual"].to_numpy(dtype="float64")
    hour = train_dt.dt.hour.to_numpy()
    weights[actual < 1000.0] *= low_weight
    weights[actual >= 12000.0] *= high_weight
    weights[(hour >= 10) & (hour <= 16)] *= daytime_weight
    weights[(actual < 1000.0) & (hour >= 10) & (hour <= 16)] *= daytime_low_weight
    weights[(hour >= 19) & (hour <= 23)] *= evening_weight
    return np.clip(weights, 0.05, 20.0)


def bounded_numeric_mask(values, min_value, max_value):
    series = pd.to_numeric(values, errors="coerce")
    mask = np.isfinite(series.to_numpy(dtype="float64"))
    if min_value is not None:
        mask &= series.to_numpy(dtype="float64") >= float(min_value)
    if max_value is not None:
        mask &= series.to_numpy(dtype="float64") <= float(max_value)
    return mask


def apply_gate_mask(frame, target_mask, source, args):
    selected = target_mask.copy()
    hours = parse_hours(args.apply_hours)
    if hours != set(range(24)):
        selected &= frame["datetime"].dt.hour.isin(hours).to_numpy()
    if args.apply_source_min > 0.0:
        selected &= source >= args.apply_source_min
    if args.apply_source_max > 0.0:
        selected &= source <= args.apply_source_max

    gate_columns = [
        ("f_price_lag_24", args.apply_lag24_min, args.apply_lag24_max),
        ("f_price_lag_48", args.apply_lag48_min, args.apply_lag48_max),
        ("f_rolling_mean_hour_7d", args.apply_rolling7_min, args.apply_rolling7_max),
    ]
    for col, min_value, max_value in gate_columns:
        if col not in frame.columns:
            continue
        has_min = min_value > 0.0
        has_max = max_value > 0.0
        if has_min or has_max:
            selected &= bounded_numeric_mask(
                frame[col],
                min_value if has_min else None,
                max_value if has_max else None,
            )
    return selected


def source_day_error_scores(frame, source_col):
    day_key = pd.to_datetime(frame["datetime"]).dt.normalize()
    source = pd.to_numeric(frame[source_col], errors="coerce")
    actual = pd.to_numeric(frame["actual"], errors="coerce")
    score_frame = pd.DataFrame({
        "day": day_key,
        "abs_error": (source - actual).abs(),
        "actual_abs": actual.abs(),
    })
    daily = score_frame.groupby("day").agg(
        abs_error_sum=("abs_error", "sum"),
        actual_abs_sum=("actual_abs", "sum"),
    )
    return daily["abs_error_sum"] / daily["actual_abs_sum"].clip(lower=1.0) * 100.0


def apply_source_error_outlier_weights(frame, train_mask, source_col, weights, quantile, outlier_weight):
    if quantile <= 0.0 or quantile >= 1.0 or outlier_weight >= 1.0:
        return weights

    scores = source_day_error_scores(frame, source_col)
    train_days = pd.to_datetime(frame.loc[train_mask, "datetime"]).dt.normalize()
    row_scores = train_days.map(scores).to_numpy(dtype="float64")
    finite = np.isfinite(row_scores)
    if finite.sum() < 24:
        return weights

    threshold = np.nanquantile(row_scores[finite], quantile)
    outlier_rows = finite & (row_scores >= threshold)
    adjusted = weights.copy()
    adjusted[outlier_rows] *= max(float(outlier_weight), 0.02)
    return adjusted


def apply_nonlinear_stacker(
    predictions,
    args,
):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")

    frame = build_stacker_frame(predictions, args.source_col)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    feature_cols = numeric_feature_columns(frame, args.output_col)

    source = clip_price_forecast(
        frame[args.source_col].to_numpy(dtype="float64"),
        frame["price_cap"].to_numpy(dtype="float64"),
    )
    stacked = source.copy()
    applied = np.zeros(len(frame), dtype="int64")

    for day in sorted(frame["datetime"].dt.normalize().unique()):
        target_mask = (frame["datetime"].dt.normalize() == day).to_numpy()
        train_start = pd.Timestamp(day) - pd.Timedelta(days=args.lookback_days)
        train_mask = ((frame["datetime"] < day) & (frame["datetime"] >= train_start)).to_numpy()
        if train_mask.sum() < args.min_train_days * 24:
            continue

        X_train = finite_frame(frame.loc[train_mask, feature_cols])
        X_target = finite_frame(frame.loc[target_mask, feature_cols])
        if args.model_type == "mlp":
            scaler = RobustScaler(quantile_range=(5.0, 95.0))
            X_train = scaler.fit_transform(X_train)
            X_target = scaler.transform(X_target)
        y_actual = frame.loc[train_mask, "actual"].to_numpy(dtype="float64")
        y_source = frame.loc[train_mask, args.source_col].to_numpy(dtype="float64")
        y_train = target_values(y_actual, y_source, args.target)
        weights = sample_weights(
            frame=frame,
            train_mask=train_mask,
            day=day,
            half_life_days=args.half_life_days,
            low_weight=args.low_weight,
            high_weight=args.high_weight,
            daytime_weight=args.daytime_weight,
            evening_weight=args.evening_weight,
            daytime_low_weight=args.daytime_low_weight,
        )
        weights = apply_source_error_outlier_weights(
            frame=frame,
            train_mask=train_mask,
            source_col=args.source_col,
            weights=weights,
            quantile=args.source_error_outlier_quantile,
            outlier_weight=args.source_error_outlier_weight,
        )

        model = make_model(args.model_type, args.seed, args)
        model.fit(X_train, y_train, sample_weight=weights)
        raw_pred = model.predict(X_target)
        day_source = source[target_mask]
        day_pred = invert_prediction(day_source, raw_pred, args.target)
        candidate = source.copy()
        candidate[target_mask] = (1.0 - args.blend) * day_source + args.blend * day_pred
        selected_mask = apply_gate_mask(frame, target_mask, source, args)
        stacked[selected_mask] = candidate[selected_mask]
        applied[selected_mask] = 1

    if args.apply_recent_days > 0:
        recent_start = frame["datetime"].max() - pd.Timedelta(days=args.apply_recent_days)
        recent_mask = (frame["datetime"] >= recent_start).to_numpy()
        stacked = np.where(recent_mask, stacked, source)
        applied = np.where(recent_mask, applied, 0)

    frame[args.output_col] = clip_price_forecast(stacked, frame["price_cap"].to_numpy(dtype="float64"))
    frame[f"{args.output_col}_applied"] = applied
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_days):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Nonlinear rolling-origin stacker: "
            f"model `{params['model_type']}`, source `{params['source_col']}`, target `{params['target']}`, "
            f"lookback `{params['lookback_days']}` days, min train `{params['min_train_days']}` days, "
            f"blend `{params['blend']}`, apply recent days `{params['apply_recent_days']}`.\n"
        )
        f.write(
            "- Focus weights/gate: "
            f"low `{params['low_weight']}`, daytime-low `{params.get('daytime_low_weight', 1.0)}`, "
            f"daytime `{params['daytime_weight']}`, evening `{params['evening_weight']}`, "
            f"apply hours `{params.get('apply_hours', 'all')}`, source range "
            f"`{params.get('apply_source_min', 0.0)}`-`{params.get('apply_source_max', 0.0)}`.\n"
        )
        if params.get("source_error_outlier_quantile", 0.0) > 0.0:
            f.write(
                "- Source-error anomaly weighting: "
                f"train-day WMAPE quantile `{params['source_error_outlier_quantile']}`, "
                f"outlier weight `{params['source_error_outlier_weight']}`.\n"
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
    parser = argparse.ArgumentParser(description="Apply leakage-safe nonlinear rolling-origin stacker.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", default="nonlinear_stack_pred")
    parser.add_argument("--model-type", choices=["hgb", "rf", "et", "mlp"], default="hgb")
    parser.add_argument("--target", choices=["resid", "ratio", "logresid", "log"], default="resid")
    parser.add_argument("--lookback-days", type=int, default=45)
    parser.add_argument("--min-train-days", type=int, default=21)
    parser.add_argument("--apply-recent-days", type=int, default=0)
    parser.add_argument("--blend", type=float, default=0.2)
    parser.add_argument("--half-life-days", type=float, default=21.0)
    parser.add_argument("--low-weight", type=float, default=1.2)
    parser.add_argument("--high-weight", type=float, default=1.2)
    parser.add_argument("--daytime-weight", type=float, default=1.1)
    parser.add_argument("--daytime-low-weight", type=float, default=1.0)
    parser.add_argument("--evening-weight", type=float, default=1.1)
    parser.add_argument("--apply-hours", default="all")
    parser.add_argument("--apply-source-min", type=float, default=0.0)
    parser.add_argument("--apply-source-max", type=float, default=0.0)
    parser.add_argument("--apply-lag24-min", type=float, default=0.0)
    parser.add_argument("--apply-lag24-max", type=float, default=0.0)
    parser.add_argument("--apply-lag48-min", type=float, default=0.0)
    parser.add_argument("--apply-lag48-max", type=float, default=0.0)
    parser.add_argument("--apply-rolling7-min", type=float, default=0.0)
    parser.add_argument("--apply-rolling7-max", type=float, default=0.0)
    parser.add_argument("--source-error-outlier-quantile", type=float, default=0.0)
    parser.add_argument("--source-error-outlier-weight", type=float, default=1.0)
    parser.add_argument("--loss", default="squared_error")
    parser.add_argument("--learning-rate", type=float, default=0.04)
    parser.add_argument("--max-iter", type=int, default=80)
    parser.add_argument("--max-leaf-nodes", type=int, default=15)
    parser.add_argument("--min-samples-leaf", type=int, default=20)
    parser.add_argument("--l2-regularization", type=float, default=1.0)
    parser.add_argument("--n-estimators", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--hidden-layers", default="64,32")
    parser.add_argument("--activation", choices=["identity", "logistic", "tanh", "relu"], default="relu")
    parser.add_argument("--mlp-alpha", type=float, default=0.001)
    parser.add_argument("--mlp-early-stopping", action="store_true")
    parser.add_argument("--mlp-validation-fraction", type=float, default=0.12)
    parser.add_argument("--mlp-n-iter-no-change", type=int, default=12)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    stacked = apply_nonlinear_stacker(predictions, args)
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

    applied_col = f"{args.output_col}_applied"
    applied_days = int(stacked.loc[stacked[applied_col] == 1, "datetime"].dt.normalize().nunique())
    params = vars(args).copy()
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["nonlinear_rolling_origin_params"] = params
    payload["nonlinear_stack_applied_days"] = applied_days
    payload["nonlinear_stack_applied_rows"] = int(stacked[applied_col].sum())
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    append_log(args.output_dir, args.experiment_id, args.input_experiment, params, artifacts, variant_metrics, applied_days)

    for col, metrics in variant_metrics.items():
        print(
            f"{col}: 3m={metrics['last_3m']['wmape']:.3f}% "
            f"14d={metrics['last_14d']['wmape']:.3f}%"
        )
    print(f"applied_days={applied_days}")
    print(f"applied_rows={int(stacked[applied_col].sum())}")


if __name__ == "__main__":
    main()
