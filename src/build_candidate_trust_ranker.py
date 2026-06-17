import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from evaluate_neural_hybrid import calculate_metrics, wmape
from evaluate_target_days import fill_actuals_from_comparisons, parse_target_days
from prediction_limits import clip_price_forecast


SOURCE_COL = "overall_balanced_low_regime_pred"
OUTPUT_COL = "candidate_trust_ranker_pred"

DEFAULT_CANDIDATES = [
    "f_price_lag_24",
    "f_price_lag_48",
    "f_price_lag_168",
    "f_rolling_mean_hour_3d",
    "f_rolling_mean_hour_7d",
    "f_rolling_mean_hour_14d",
    "ensemble_neural_pred",
    "ensemble_hybrid_pred",
    "tree_base_pred",
    "tree_recent_calibrated_pred",
    "daybias31_hb22_midday_d8_b050_abs250_pred",
    "lag24blend9_db21_hourall_r3_mean_an005_advn500_pred",
    "high_profile_lag168_day_down_weather_lowcollapse_cap00_lag48eve_capnight_pred",
    "low_regime_postdeep_selector_target15_pred",
    "sourcebin_daytime_bias_after_lowrepair_pred",
    "hourbias17_gb12_midday_r21_med_bn050_abs250_pred",
    "hourbias22_hb21_peakerr_r8_bn020_wmape40_pred",
    "hourbias15_lag10_evening_r8_mean_bn030_abs300_pred",
    "hourbias16_h15_evening_then_morning_pred",
    "day14_16_ratio_lowrepair_after_morning_pred",
    "daybias23_h789_then_evening_pred",
    "lag24blend11_db23_hour21_all_an020_advn250_pred",
    "anomaly_hgb_ratio_b0025_q85w025_pred",
    "groupbias4_hourweekend12_med_bn025_all_abs400_pred",
    "ensemble_hybrid_recent_calibrated_pred",
]

OPTIONAL_FEATURES = [
    "price_cap",
    "f_price_lag_24",
    "f_price_lag_48",
    "f_price_lag_168",
    "f_rolling_mean_hour_3d",
    "f_rolling_mean_hour_7d",
    "f_rolling_mean_hour_14d",
    "f_rolling_mean_24",
    "f_rolling_min_24",
    "f_rolling_std_24",
    "f_renewable_pressure_index",
    "f_cloudcover",
    "f_solarradiation",
    "f_windspeed",
    "f_windgust",
    "f_feelslike",
    "f_uvindex",
]

LAG_FEATURES = [
    "f_price_lag_24",
    "f_price_lag_48",
    "f_price_lag_168",
    "f_rolling_mean_hour_3d",
    "f_rolling_mean_hour_7d",
    "f_rolling_mean_hour_14d",
]

BAD_CANDIDATE_TOKENS = [
    "actual",
    "signed_error",
    "abs_error",
    "ape",
    "wmape_signal",
    "bias_signal",
    "_applied",
]


def parse_csv_list(text, cast=str):
    values = [part.strip() for part in str(text).split(",") if part.strip()]
    return [cast(value) for value in values]


def parse_hours(text):
    text = str(text).strip().lower()
    aliases = {
        "all": set(range(24)),
        "peakerr": {0, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 23},
        "day": set(range(9, 18)),
        "lowday": set(range(9, 17)),
        "morning": set(range(6, 10)),
        "evening": set(range(17, 24)),
        "target18": {7, 10, 11, 12, 13, 14, 15, 16, 17, 20, 23},
    }
    if text in aliases:
        return aliases[text]
    hours = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(value) for value in part.split("-", 1)]
            hours.update(range(start, end + 1))
        else:
            hours.add(int(part))
    unknown = sorted(hour for hour in hours if hour < 0 or hour > 23)
    if unknown:
        raise ValueError(f"Hours must be 0-23, got: {unknown}")
    return hours


def load_target_frame(day, output_dir, input_pattern, comparison_suffix):
    day_text = pd.Timestamp(day).strftime("%Y-%m-%d")
    path = Path(output_dir) / input_pattern.format(date=day_text)
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    frame = fill_actuals_from_comparisons(
        frame,
        target_days=[pd.Timestamp(day_text).normalize()],
        actuals_dir=output_dir,
        comparison_suffix=comparison_suffix,
    )
    frame["__split"] = "target"
    return frame


def load_frames(args):
    history = pd.read_csv(args.history_csv, parse_dates=["datetime"], low_memory=False)
    history["__split"] = "history"
    target_days = parse_target_days(args.target_days)
    targets = [
        load_target_frame(
            day,
            output_dir=args.output_dir,
            input_pattern=args.target_input_pattern,
            comparison_suffix=args.comparison_suffix,
        )
        for day in target_days
    ]
    frame = pd.concat([history, *targets], ignore_index=True, sort=False)
    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        dupes = int(frame["datetime"].duplicated().sum())
        raise ValueError(f"Duplicate datetimes are not allowed: {dupes}")
    return frame, target_days


def is_candidate_like(column):
    lower = column.lower()
    if any(token in lower for token in BAD_CANDIDATE_TOKENS):
        return False
    return column.startswith("f_price_lag") or column.startswith("f_rolling_mean_hour") or column.endswith("_pred")


def historical_wmape(frame, col):
    hist = frame[(frame["__split"] == "history") & frame["actual"].notna() & frame[col].notna()]
    if hist.empty:
        return np.inf
    return wmape(hist["actual"], hist[col])


def select_candidate_columns(frame, args):
    common = set(frame.columns)
    candidates = []
    if args.candidate_pool in {"default", "wide"}:
        candidates.extend([col for col in DEFAULT_CANDIDATES if col in common])
    if args.extra_candidate_cols:
        candidates.extend([col for col in parse_csv_list(args.extra_candidate_cols) if col in common])
    if args.candidate_pool == "wide":
        auto_cols = [
            col
            for col in frame.columns
            if col not in {SOURCE_COL, "datetime", "actual", "price_cap"}
            and is_candidate_like(col)
            and pd.api.types.is_numeric_dtype(frame[col])
            and frame.loc[frame["__split"] == "target", col].notna().any()
        ]
        ranked = sorted(auto_cols, key=lambda col: historical_wmape(frame, col))
        candidates.extend(ranked[: args.max_auto_candidates])
    candidates = list(dict.fromkeys(col for col in candidates if col != args.source_col))
    missing = [col for col in [args.source_col, *candidates] if col not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if not candidates:
        raise ValueError("No candidate columns selected")
    return candidates


def _hour_block_mean(values, hours, day_key):
    masked = values.where(hours)
    return masked.groupby(day_key).transform("mean").groupby(day_key).transform("max")


def build_base_features(frame, source_col, candidate_cols):
    dt = pd.to_datetime(frame["datetime"])
    hour = dt.dt.hour
    day_key = dt.dt.normalize()
    source = pd.to_numeric(frame[source_col], errors="coerce")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce")

    feature_series = [
        hour.astype("float64"),
        np.sin(2.0 * np.pi * hour.astype("float64") / 24.0),
        np.cos(2.0 * np.pi * hour.astype("float64") / 24.0),
        dt.dt.dayofweek.astype("float64"),
        dt.dt.dayofweek.isin([5, 6]).astype("float64"),
        dt.dt.month.astype("float64"),
        dt.dt.month.isin([6, 7, 8]).astype("float64"),
        source,
        source / cap.clip(lower=1.0),
        source.groupby(day_key).transform("min"),
        source.groupby(day_key).transform("max"),
        source.groupby(day_key).transform("mean"),
        _hour_block_mean(source, hour.between(6, 8), day_key),
        _hour_block_mean(source, hour.between(9, 16), day_key),
        _hour_block_mean(source, hour.between(17, 20), day_key),
    ]

    for col in OPTIONAL_FEATURES:
        if col in frame.columns and col != source_col:
            feature_series.append(pd.to_numeric(frame[col], errors="coerce"))

    for col in LAG_FEATURES:
        if col in frame.columns:
            lag = pd.to_numeric(frame[col], errors="coerce")
            feature_series.append(source - lag)
            feature_series.append(source / lag.clip(lower=10.0))

    candidate_matrix = np.column_stack(
        [pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64") for col in candidate_cols]
    )
    feature_series.extend(
        [
            pd.Series(np.nanstd(candidate_matrix, axis=1), index=frame.index),
            pd.Series(np.nanmin(candidate_matrix, axis=1), index=frame.index),
            pd.Series(np.nanmax(candidate_matrix, axis=1), index=frame.index),
        ]
    )

    base = np.column_stack([pd.to_numeric(series, errors="coerce") for series in feature_series])
    return np.nan_to_num(base, nan=0.0, posinf=0.0, neginf=0.0)


def expanded_features(base_features, frame, source_col, candidate_cols, row_indices, candidate_matrix):
    row_indices = np.asarray(row_indices, dtype="int64")
    candidate_indices = np.tile(np.arange(len(candidate_cols), dtype="int64"), len(row_indices))
    expanded_rows = np.repeat(row_indices, len(candidate_cols))
    source = pd.to_numeric(frame[source_col], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    source_values = source[expanded_rows]
    cap_values = np.clip(cap[expanded_rows], 1.0, None)
    candidate_values = candidate_matrix[expanded_rows, candidate_indices]

    extras = [
        candidate_values,
        candidate_values / cap_values,
        candidate_values - source_values,
        np.abs(candidate_values - source_values),
        np.abs(candidate_values - source_values) / cap_values,
    ]
    for col in LAG_FEATURES:
        if col in frame.columns:
            lag = pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64")[expanded_rows]
            extras.append(candidate_values - lag)
            extras.append(candidate_values / np.clip(lag, 10.0, None))

    one_hot = np.eye(len(candidate_cols), dtype="float64")[candidate_indices]
    features = np.column_stack([base_features[expanded_rows], *extras, one_hot])
    return (
        np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0),
        expanded_rows,
        candidate_indices,
    )


def make_model(args):
    if args.model == "ridge":
        return make_pipeline(StandardScaler(), Ridge(alpha=args.ridge_alpha))
    if args.model == "hgb":
        return HistGradientBoostingRegressor(
            max_iter=args.hgb_iter,
            learning_rate=args.hgb_learning_rate,
            max_leaf_nodes=args.hgb_leaf_nodes,
            l2_regularization=args.hgb_l2,
            random_state=args.random_state,
        )
    if args.model == "et":
        return ExtraTreesRegressor(
            n_estimators=args.et_estimators,
            max_depth=args.et_max_depth,
            min_samples_leaf=args.et_min_samples_leaf,
            random_state=args.random_state,
            n_jobs=-1,
        )
    raise ValueError(f"Unsupported model: {args.model}")


def fit_model(model, features, target, sample_weight, model_name):
    if model_name == "ridge":
        model.fit(features, target, ridge__sample_weight=sample_weight)
    else:
        model.fit(features, target, sample_weight=sample_weight)
    return model


def row_weights(frame, row_indices, day, source, actual, args):
    row_indices = np.asarray(row_indices, dtype="int64")
    dt = pd.to_datetime(frame.loc[row_indices, "datetime"])
    age_days = (pd.Timestamp(day) - dt).dt.total_seconds().to_numpy(dtype="float64") / 86400.0
    if args.half_life_days > 0:
        weights = np.power(0.5, age_days / args.half_life_days)
    else:
        weights = np.ones(len(row_indices), dtype="float64")
    source_error = np.abs(source[row_indices] - actual[row_indices])
    scale = np.nanmedian(source_error[np.isfinite(source_error)])
    if not np.isfinite(scale) or scale <= 0.0:
        scale = 300.0
    weights *= np.clip(0.5 + source_error / scale, 0.5, 8.0)
    hour = dt.dt.hour.to_numpy()
    weights[actual[row_indices] < 1000.0] *= args.low_weight
    weights[(actual[row_indices] < 1000.0) & (hour >= 9) & (hour <= 16)] *= args.daytime_low_weight
    return np.clip(weights, 0.05, 30.0)


def rolling_candidate_signals(frame, candidate_cols, args, target_days):
    base_features = build_base_features(frame, args.source_col, candidate_cols)
    source = pd.to_numeric(frame[args.source_col], errors="coerce").to_numpy(dtype="float64")
    actual = pd.to_numeric(frame["actual"], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    candidate_matrix = np.column_stack(
        [
            clip_price_forecast(pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype="float64"), cap)
            for col in candidate_cols
        ]
    )

    chosen_signal = np.full(len(frame), np.nan, dtype="float64")
    chosen_idx = np.full(len(frame), -1, dtype="int64")
    day_key = frame["datetime"].dt.normalize()
    history_end = frame.loc[frame["__split"] == "history", "datetime"].max()
    recent_start = history_end - pd.Timedelta(days=args.apply_history_days)
    target_day_set = set(pd.Timestamp(day).normalize() for day in target_days)
    apply_days = [
        day
        for day in pd.DatetimeIndex(day_key.unique()).sort_values()
        if day in target_day_set or (args.apply_history_days > 0 and day >= recent_start.normalize() and day <= history_end.normalize())
    ]

    for day in apply_days:
        train_start = pd.Timestamp(day) - pd.Timedelta(days=args.lookback_days)
        train_mask = (
            (frame["datetime"] < pd.Timestamp(day))
            & (frame["datetime"] >= train_start)
            & np.isfinite(actual)
            & np.isfinite(source)
        ).to_numpy()
        train_rows = np.flatnonzero(train_mask)
        target_rows = np.flatnonzero((day_key == day).to_numpy())
        if len(target_rows) == 0 or len(train_rows) < args.min_train_days * 24:
            continue

        x_train, expanded_rows, candidate_indices = expanded_features(
            base_features,
            frame,
            args.source_col,
            candidate_cols,
            train_rows,
            candidate_matrix,
        )
        source_error = np.abs(source[expanded_rows] - actual[expanded_rows])
        candidate_error = np.abs(candidate_matrix[expanded_rows, candidate_indices] - actual[expanded_rows])
        y_train = source_error - candidate_error
        finite = np.isfinite(y_train)
        if int(finite.sum()) < args.min_train_days * 24:
            continue

        weights = row_weights(frame, train_rows, day, source, actual, args)
        sample_weight = np.repeat(weights, len(candidate_cols))[finite]
        model = fit_model(make_model(args), x_train[finite], y_train[finite], sample_weight, args.model)

        x_target, expanded_target_rows, expanded_target_candidates = expanded_features(
            base_features,
            frame,
            args.source_col,
            candidate_cols,
            target_rows,
            candidate_matrix,
        )
        pred_gain = model.predict(x_target).reshape(len(target_rows), len(candidate_cols))
        finite_candidates = np.isfinite(candidate_matrix[target_rows])
        pred_gain = np.where(finite_candidates, pred_gain, -np.inf)
        best_idx = np.argmax(pred_gain, axis=1)
        best_signal = pred_gain[np.arange(len(target_rows)), best_idx]
        chosen_idx[target_rows] = best_idx
        chosen_signal[target_rows] = best_signal

    return chosen_signal, chosen_idx, candidate_matrix


def metric_value(metrics, path, default=np.inf):
    current = metrics
    for part in path:
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    if current is None:
        return default
    return float(current)


def evaluate_grid(frame, candidate_cols, signal, chosen_idx, candidate_matrix, args, target_days):
    source = pd.to_numeric(frame[args.source_col], errors="coerce").to_numpy(dtype="float64")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce").to_numpy(dtype="float64")
    hour = frame["datetime"].dt.hour.to_numpy(dtype="int64")
    hour_mask = np.isin(hour, sorted(parse_hours(args.hours)))
    target_mask = frame["__split"].eq("target").to_numpy()
    history_mask = frame["__split"].eq("history").to_numpy()
    selected_candidate = np.full(len(frame), np.nan, dtype="float64")
    valid_choice = chosen_idx >= 0
    selected_candidate[valid_choice] = candidate_matrix[np.arange(len(frame))[valid_choice], chosen_idx[valid_choice]]

    baseline_history = frame.loc[history_mask].copy()
    baseline_metrics = calculate_metrics(baseline_history, pred_col=args.source_col)
    baseline_all = baseline_metrics["all_available"]["wmape"]
    baseline_3m = baseline_metrics["last_3m"]["wmape"]
    baseline_14d = baseline_metrics["last_14d"]["wmape"]

    rows = []
    predictions_by_key = {}
    thresholds = parse_csv_list(args.thresholds, float)
    alphas = parse_csv_list(args.alphas, float)
    target_day_values = [day.strftime("%Y-%m-%d") for day in target_days]

    for threshold in thresholds:
        for alpha in alphas:
            pred = source.copy()
            apply_mask = hour_mask & valid_choice & np.isfinite(signal) & (signal >= threshold)
            blended = (1.0 - alpha) * source + alpha * selected_candidate
            pred[apply_mask] = blended[apply_mask]
            pred = clip_price_forecast(pred, cap)

            work = frame.copy()
            work[args.output_col] = pred
            history = work.loc[history_mask].copy()
            metrics = calculate_metrics(history, pred_col=args.output_col)
            dailies = {}
            for day in target_days:
                mask = work["datetime"].dt.normalize().eq(day)
                dailies[day.strftime("%Y-%m-%d")] = wmape(work.loc[mask, "actual"], work.loc[mask, args.output_col])

            all_w = metrics["all_available"]["wmape"]
            w3m = metrics["last_3m"]["wmape"]
            w14d = metrics["last_14d"]["wmape"]
            summer_low = metric_value(metrics, ["regimes", "summer_daytime_low", "wmape"])
            daytime_low = metric_value(metrics, ["regimes", "daytime_low_lt_1000", "wmape"])
            cap_evening = metric_value(metrics, ["regimes", "cap_spike_evening", "wmape"])
            below_10 = int((pd.Series(pred) < 10.0).sum())
            above_cap = int((pred > cap).sum())
            hist_ok = (
                all_w <= baseline_all + args.max_all_delta
                and w3m <= baseline_3m + args.max_3m_delta
                and w14d <= baseline_14d + args.max_14d_delta
            )
            regime_ok = (
                summer_low <= args.max_summer_daytime_low
                and daytime_low <= args.max_daytime_low_lt_1000
                and cap_evening <= args.max_cap_spike_evening
            )
            target_ok = all(value < args.target_wmape for value in dailies.values())
            integrity_ok = below_10 == 0 and above_cap == 0 and int(work["datetime"].duplicated().sum()) == 0
            key = (threshold, alpha)
            rows.append(
                {
                    "threshold": threshold,
                    "alpha": alpha,
                    "history_all": all_w,
                    "history_3m": w3m,
                    "history_14d": w14d,
                    "history_all_delta": all_w - baseline_all,
                    "history_3m_delta": w3m - baseline_3m,
                    "history_14d_delta": w14d - baseline_14d,
                    "summer_daytime_low": summer_low,
                    "daytime_low_lt_1000": daytime_low,
                    "cap_spike_evening": cap_evening,
                    **{f"d{day.replace('-', '')}": value for day, value in dailies.items()},
                    "max_target_wmape": max(dailies.values()),
                    "applied_history": int((apply_mask & history_mask).sum()),
                    "applied_target": int((apply_mask & target_mask).sum()),
                    "below_10": below_10,
                    "above_cap": above_cap,
                    "hist_ok": bool(hist_ok),
                    "regime_ok": bool(regime_ok),
                    "target_ok": bool(target_ok),
                    "objective_ok": bool(hist_ok and regime_ok and target_ok and integrity_ok),
                }
            )
            predictions_by_key[key] = (work, apply_mask)

    grid = pd.DataFrame(rows)
    grid = grid.sort_values(
        ["objective_ok", "hist_ok", "target_ok", "max_target_wmape", "history_14d_delta"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    best = grid.iloc[0]
    best_key = (float(best["threshold"]), float(best["alpha"]))
    best_frame, best_apply_mask = predictions_by_key[best_key]

    candidate_names = np.array(candidate_cols, dtype=object)
    chosen_names = np.full(len(frame), "", dtype=object)
    chosen = chosen_idx >= 0
    chosen_names[chosen] = candidate_names[chosen_idx[chosen]]
    best_frame[f"{args.output_col}_applied"] = best_apply_mask.astype("int64")
    best_frame[f"{args.output_col}_candidate"] = chosen_names
    best_frame[f"{args.output_col}_predicted_gain"] = signal
    best_frame[f"{args.output_col}_threshold"] = float(best["threshold"])
    best_frame[f"{args.output_col}_alpha"] = float(best["alpha"])
    return grid, best_frame, baseline_metrics


def write_summary(path, grid, candidate_cols, args, baseline_metrics, best_metrics):
    best = grid.iloc[0]
    lines = [
        "# Candidate Trust Ranker 17/18 Summary",
        "",
        f"- model: `{args.model}`",
        f"- source: `{args.source_col}`",
        f"- output: `{args.output_col}`",
        f"- candidate pool size: `{len(candidate_cols)}`",
        f"- candidates: `{', '.join(candidate_cols)}`",
        "",
        "## Baseline History",
        "",
        "| scope | WMAPE |",
        "|---|---:|",
        f"| all | {baseline_metrics['all_available']['wmape']:.4f}% |",
        f"| 3m | {baseline_metrics['last_3m']['wmape']:.4f}% |",
        f"| 14d | {baseline_metrics['last_14d']['wmape']:.4f}% |",
        "",
        "## Best Grid Row",
        "",
        "| field | value |",
        "|---|---:|",
    ]
    for col in grid.columns:
        value = best[col]
        if isinstance(value, (float, np.floating)):
            lines.append(f"| `{col}` | {float(value):.6f} |")
        else:
            lines.append(f"| `{col}` | {value} |")
    lines.extend(
        [
            "",
            "## Best Prediction History Metrics",
            "",
            "| scope | WMAPE |",
            "|---|---:|",
            f"| all | {best_metrics['all_available']['wmape']:.4f}% |",
            f"| 3m | {best_metrics['last_3m']['wmape']:.4f}% |",
            f"| 14d | {best_metrics['last_14d']['wmape']:.4f}% |",
            "",
            f"Objective passed: `{bool(best['objective_ok'])}`.",
            "",
        ]
    )
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Rolling-origin candidate trust ranker for 17/18 target days.")
    parser.add_argument("--history-csv", default=os.path.join(ROOT_DIR, "output", "neural_best_predictions.csv"))
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--target-input-pattern", default="prediction_{date}_overall_balanced_filled.csv")
    parser.add_argument("--comparison-suffix", default="overall_balanced")
    parser.add_argument("--target-days", default="2026-06-17,2026-06-18")
    parser.add_argument("--source-col", default=SOURCE_COL)
    parser.add_argument("--output-col", default=OUTPUT_COL)
    parser.add_argument("--candidate-pool", choices=["default", "wide"], default="default")
    parser.add_argument("--extra-candidate-cols", default="")
    parser.add_argument("--max-auto-candidates", type=int, default=48)
    parser.add_argument("--model", choices=["ridge", "hgb", "et"], default="hgb")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--min-train-days", type=int, default=21)
    parser.add_argument("--apply-history-days", type=int, default=14)
    parser.add_argument("--half-life-days", type=float, default=30.0)
    parser.add_argument("--low-weight", type=float, default=1.4)
    parser.add_argument("--daytime-low-weight", type=float, default=2.0)
    parser.add_argument("--hours", default="all")
    parser.add_argument("--thresholds", default="0,50,100,200,400,800")
    parser.add_argument("--alphas", default="0.25,0.5,0.75,1.0")
    parser.add_argument("--ridge-alpha", type=float, default=1000.0)
    parser.add_argument("--hgb-iter", type=int, default=120)
    parser.add_argument("--hgb-learning-rate", type=float, default=0.05)
    parser.add_argument("--hgb-leaf-nodes", type=int, default=15)
    parser.add_argument("--hgb-l2", type=float, default=10.0)
    parser.add_argument("--et-estimators", type=int, default=160)
    parser.add_argument("--et-max-depth", type=int, default=7)
    parser.add_argument("--et-min-samples-leaf", type=int, default=12)
    parser.add_argument("--random-state", type=int, default=17)
    parser.add_argument("--target-wmape", type=float, default=13.0)
    parser.add_argument("--max-all-delta", type=float, default=0.0)
    parser.add_argument("--max-3m-delta", type=float, default=0.05)
    parser.add_argument("--max-14d-delta", type=float, default=0.15)
    parser.add_argument("--max-summer-daytime-low", type=float, default=13.0)
    parser.add_argument("--max-daytime-low-lt-1000", type=float, default=15.0)
    parser.add_argument("--max-cap-spike-evening", type=float, default=2.0)
    parser.add_argument("--grid-csv", default=os.path.join(ROOT_DIR, "output", "candidate_trust_ranker_17_18_grid.csv"))
    parser.add_argument(
        "--predictions-csv",
        default=os.path.join(ROOT_DIR, "output", "candidate_trust_ranker_best_predictions.csv"),
    )
    parser.add_argument(
        "--summary-md",
        default=os.path.join(ROOT_DIR, "output", "candidate_trust_ranker_17_18_summary.md"),
    )
    args = parser.parse_args()

    frame, target_days = load_frames(args)
    candidate_cols = select_candidate_columns(frame, args)
    signal, chosen_idx, candidate_matrix = rolling_candidate_signals(frame, candidate_cols, args, target_days)
    grid, best_frame, baseline_metrics = evaluate_grid(
        frame,
        candidate_cols,
        signal,
        chosen_idx,
        candidate_matrix,
        args,
        target_days,
    )
    Path(args.grid_csv).parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(args.grid_csv, index=False)
    best_frame.to_csv(args.predictions_csv, index=False)

    history_best = best_frame.loc[best_frame["__split"] == "history"].copy()
    best_metrics = calculate_metrics(history_best, pred_col=args.output_col)
    write_summary(args.summary_md, grid, candidate_cols, args, baseline_metrics, best_metrics)

    best = grid.iloc[0].to_dict()
    metrics_payload = {
        "baseline_history_metrics": baseline_metrics,
        "best_history_metrics": best_metrics,
        "best_grid_row": best,
        "candidate_columns": candidate_cols,
        "grid_csv": args.grid_csv,
        "predictions_csv": args.predictions_csv,
        "summary_md": args.summary_md,
    }
    metrics_path = Path(args.summary_md).with_suffix(".json")
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"best: objective_ok={best['objective_ok']} "
        f"hist_ok={best['hist_ok']} target_ok={best['target_ok']} "
        f"max_target={best['max_target_wmape']:.4f}% "
        f"history_3m={best['history_3m']:.4f}% history_14d={best['history_14d']:.4f}% "
        f"threshold={best['threshold']} alpha={best['alpha']}"
    )
    for day in target_days:
        key = f"d{day.strftime('%Y%m%d')}"
        print(f"{day.strftime('%Y-%m-%d')}: {best[key]:.4f}%")
    print(f"grid_csv={args.grid_csv}")
    print(f"predictions_csv={args.predictions_csv}")
    print(f"summary_md={args.summary_md}")


if __name__ == "__main__":
    main()
