import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts


def load_predictions(output_dir, input_experiment):
    path = Path(output_dir) / f"neural_experiment_{input_experiment}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"])


def parse_hours(text):
    text = str(text).strip().lower()
    aliases = {
        "all": set(range(24)),
        "peakerr": {0, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 21, 22},
        "day": set(range(10, 18)),
        "lowday": set(range(10, 17)),
        "midday": {11, 12, 13, 14, 15, 16},
        "morning": set(range(7, 11)),
        "evening": set(range(19, 24)),
        "night": {0, 1, 2, 3, 4, 5, 6, 23},
    }
    if text in aliases:
        return aliases[text]

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
    unknown = sorted(hour for hour in selected if hour < 0 or hour > 23)
    if unknown:
        raise ValueError(f"Hours must be 0-23, got: {unknown}")
    return selected


def add_lag24_from_history(frame, lag_col):
    if lag_col in frame.columns and frame[lag_col].notna().all():
        return frame

    enriched = frame.copy()
    if lag_col not in enriched.columns:
        enriched[lag_col] = np.nan

    history = enriched[["datetime", "actual"]].dropna(subset=["actual"]).copy()
    lag_lookup = history.assign(datetime=history["datetime"] + pd.Timedelta(hours=24))
    lag_lookup = lag_lookup.rename(columns={"actual": "_lag24_actual"})
    enriched = enriched.merge(lag_lookup[["datetime", "_lag24_actual"]], on="datetime", how="left")
    enriched[lag_col] = enriched[lag_col].fillna(enriched["_lag24_actual"])
    return enriched.drop(columns=["_lag24_actual"])


def shifted_daily_lag_advantage(frame, source_col, lag_col, rolling_days):
    source = frame[source_col].astype("float64")
    lag = frame[lag_col].astype("float64")
    actual = frame["actual"].astype("float64")
    valid = actual.notna() & lag.notna() & source.notna()

    daily = pd.DataFrame(
        {
            "date": frame["datetime"].dt.normalize(),
            "model_abs_error": (source - actual).abs(),
            "lag_abs_error": (lag - actual).abs(),
            "actual_abs": actual.abs(),
            "valid": valid,
        }
    )
    daily = daily[daily["valid"]].groupby("date").agg(
        model_abs_error=("model_abs_error", "sum"),
        lag_abs_error=("lag_abs_error", "sum"),
        actual_abs=("actual_abs", "sum"),
    )
    daily["lag_advantage_wmape"] = (
        (daily["model_abs_error"] - daily["lag_abs_error"]) / daily["actual_abs"].clip(lower=1.0) * 100.0
    )

    all_days = pd.DatetimeIndex(frame["datetime"].dt.normalize().unique()).sort_values()
    daily = daily.reindex(all_days)
    signal = daily["lag_advantage_wmape"].shift(1).rolling(rolling_days, min_periods=1).mean()
    return frame["datetime"].dt.normalize().map(signal).to_numpy(dtype="float64")


def shifted_hour_lag_advantage(frame, source_col, lag_col, rolling_hours, stat):
    source = frame[source_col].astype("float64")
    lag = frame[lag_col].astype("float64")
    actual = frame["actual"].astype("float64")
    advantage = (source - actual).abs() - (lag - actual).abs()
    hour = frame["datetime"].dt.hour

    def shifted_rolling(values):
        rolling = values.shift(1).rolling(rolling_hours, min_periods=1)
        if stat == "mean":
            return rolling.mean()
        if stat == "median":
            return rolling.median()
        raise ValueError(f"Unsupported stat: {stat}")

    return advantage.groupby(hour, sort=False, group_keys=False).transform(shifted_rolling).to_numpy(dtype="float64")


def lag24_similarity_signal(frame, signal_source_col, lag_col, metric):
    source = frame[signal_source_col].astype("float64")
    lag = frame[lag_col].astype("float64")
    cap = frame["price_cap"].astype("float64").clip(lower=1.0)

    absdiff = (source - lag).abs()
    if metric == "absdiff":
        return absdiff.to_numpy(dtype="float64")
    if metric == "reldiff":
        return (absdiff / cap).to_numpy(dtype="float64")
    if metric == "ratio":
        return ((source / lag.abs().clip(lower=1.0)) - 1.0).abs().to_numpy(dtype="float64")
    if metric == "profile_abs":
        daily = pd.DataFrame(
            {
                "date": frame["datetime"].dt.normalize(),
                "absdiff": absdiff,
            }
        )
        signal = daily.groupby("date")["absdiff"].mean()
        return frame["datetime"].dt.normalize().map(signal).to_numpy(dtype="float64")
    raise ValueError(f"Unsupported similarity metric: {metric}")


def apply_lag24_blend_adjustment(predictions, args):
    if args.source_col not in predictions.columns:
        raise ValueError(f"Missing source column: {args.source_col}")
    signal_source_col = getattr(args, "signal_source_col", None) or args.source_col
    if signal_source_col not in predictions.columns:
        raise ValueError(f"Missing signal source column: {signal_source_col}")

    frame = predictions.copy()
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        duplicate_count = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {duplicate_count}")

    frame = add_lag24_from_history(frame, args.lag_col)

    signal_op = getattr(args, "signal_op", "ge")
    if signal_op not in {"ge", "le"}:
        raise ValueError(f"Unsupported signal op: {signal_op}")

    if args.mode == "daily":
        signal = shifted_daily_lag_advantage(
            frame=frame,
            source_col=args.source_col,
            lag_col=args.lag_col,
            rolling_days=args.rolling_window,
        )
        selected_by_signal = signal >= args.advantage_threshold if signal_op == "ge" else signal <= args.advantage_threshold
    elif args.mode == "hour":
        signal = shifted_hour_lag_advantage(
            frame=frame,
            source_col=args.source_col,
            lag_col=args.lag_col,
            rolling_hours=args.rolling_window,
            stat=args.stat,
        )
        selected_by_signal = signal >= args.advantage_threshold if signal_op == "ge" else signal <= args.advantage_threshold
    elif args.mode == "similarity":
        signal = lag24_similarity_signal(
            frame=frame,
            signal_source_col=signal_source_col,
            lag_col=args.lag_col,
            metric=args.similarity_metric,
        )
        if args.similarity_op == "le":
            selected_by_signal = signal <= args.similarity_threshold
        elif args.similarity_op == "ge":
            selected_by_signal = signal >= args.similarity_threshold
        else:
            raise ValueError(f"Unsupported similarity op: {args.similarity_op}")
    else:
        raise ValueError(f"Unsupported mode: {args.mode}")

    hours = parse_hours(args.hours)
    hour_mask = frame["datetime"].dt.hour.isin(hours).to_numpy()
    lag = frame[args.lag_col].to_numpy(dtype="float64")
    source = frame[args.source_col].to_numpy(dtype="float64")
    finite_mask = np.isfinite(signal) & np.isfinite(lag) & np.isfinite(source)
    selected = finite_mask & hour_mask & selected_by_signal

    adjusted = source.copy()
    adjusted[selected] = (1.0 - args.alpha) * source[selected] + args.alpha * lag[selected]
    adjusted = np.clip(adjusted, 0.0, frame["price_cap"].to_numpy(dtype="float64"))

    frame[args.output_col] = adjusted
    frame[f"{args.output_col}_applied"] = selected.astype("int64")
    frame[f"{args.output_col}_lag24_signal"] = signal
    return frame


def append_log(output_dir, experiment_id, input_experiment, params, artifacts, variant_metrics, applied_rows):
    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write(f"- Input experiment: `{input_experiment}`.\n")
        f.write(
            "- Shifted lag24 blend adjuster: "
            f"source `{params['source_col']}`, lag `{params['lag_col']}`, mode `{params['mode']}`, "
            f"signal source `{params.get('signal_source_col') or params['source_col']}`, "
            f"signal op `{params.get('signal_op', 'ge')}`, "
            f"rolling window `{params['rolling_window']}`, stat `{params['stat']}`, "
            f"hours `{params['hours']}`, lag advantage threshold `{params['advantage_threshold']}`, "
            f"similarity `{params.get('similarity_metric')}` `{params.get('similarity_op')}` "
            f"`{params.get('similarity_threshold')}`, alpha `{params['alpha']}`.\n"
        )
        f.write(
            "- Formula: selected rows use `(1-alpha) * source + alpha * lag24`; "
            "daily/hour modes use shifted prior actual errors, while similarity mode uses only forecast-time source-vs-lag24 distance.\n"
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
    parser = argparse.ArgumentParser(description="Leakage-safe lag24 copy/blend fallback.")
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--input-experiment", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--source-col", required=True)
    parser.add_argument("--output-col", default="lag24_blend_pred")
    parser.add_argument("--lag-col", default="f_price_lag_24")
    parser.add_argument("--signal-source-col", default=None)
    parser.add_argument("--mode", choices=["daily", "hour", "similarity"], default="daily")
    parser.add_argument("--signal-op", choices=["ge", "le"], default="ge")
    parser.add_argument("--rolling-window", type=int, default=2)
    parser.add_argument("--stat", choices=["mean", "median"], default="mean")
    parser.add_argument("--hours", default="night")
    parser.add_argument("--advantage-threshold", type=float, default=0.0)
    parser.add_argument("--similarity-metric", choices=["absdiff", "reldiff", "ratio", "profile_abs"], default="ratio")
    parser.add_argument("--similarity-op", choices=["le", "ge"], default="le")
    parser.add_argument("--similarity-threshold", type=float, default=0.05)
    parser.add_argument("--alpha", type=float, default=1.0)
    args = parser.parse_args()

    predictions = load_predictions(args.output_dir, args.input_experiment)
    adjusted = apply_lag24_blend_adjustment(predictions, args)
    variant_cols = [
        "tree_recent_calibrated_pred",
        args.source_col,
        args.lag_col,
        args.output_col,
    ]
    variant_metrics = {
        col: calculate_metrics(adjusted, pred_col=col)
        for col in variant_cols
        if col in adjusted.columns and adjusted[col].notna().any()
    }
    artifacts = save_evaluation_artifacts(
        adjusted,
        experiment_id=args.experiment_id,
        output_dir=args.output_dir,
        pred_col=args.output_col,
    )

    applied_col = f"{args.output_col}_applied"
    applied_rows = int(adjusted[applied_col].fillna(0).astype(bool).sum())
    params = vars(args).copy()
    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    payload["variant_metrics"] = variant_metrics
    payload["input_experiment"] = args.input_experiment
    payload["lag24_blend_adjuster_params"] = params
    payload["lag24_blend_adjuster_applied_rows"] = applied_rows
    for flag_col in sorted(col for col in adjusted.columns if col.endswith("_applied")):
        payload[f"{flag_col}_rows"] = int(adjusted[flag_col].fillna(0).astype(bool).sum())
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
