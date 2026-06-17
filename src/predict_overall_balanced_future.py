import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from build_overall_balanced_composite import (  # noqa: E402
    OUTPUT_COL,
    build_overall_balanced,
    missing_overall_balanced_columns,
    overall_balanced_required_columns,
)
from prediction_limits import MIN_MARKET_PRICE, clip_price_forecast  # noqa: E402


def parse_target_date(value):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return pd.Timestamp(pd.to_datetime(value, format=fmt).date())
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}. Use DD.MM.YYYY or YYYY-MM-DD.")


def default_target_input(output_dir, date_iso):
    candidates = [
        Path(output_dir) / f"prediction_{date_iso}_overall_balanced_filled.csv",
        Path(output_dir) / f"prediction_{date_iso}_overall_balanced_draft.csv",
        Path(output_dir) / f"prediction_{date_iso}_overall_input_probe.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        f"No target input found for {date_iso}. Pass --target-input-csv, or create one of: "
        + ", ".join(os.fspath(path) for path in candidates)
    )


def load_history(path, target_day):
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    if "datetime" not in frame.columns:
        raise ValueError(f"{path} does not contain datetime.")
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} contains duplicate datetimes.")
    return frame[frame["datetime"].dt.normalize() < target_day].copy()


def load_extra_history(paths, target_day):
    if not paths:
        return pd.DataFrame()

    frames = []
    for path in paths:
        extra_path = Path(path)
        frame = pd.read_csv(extra_path, parse_dates=["datetime"], low_memory=False)
        if "datetime" not in frame.columns:
            raise ValueError(f"{extra_path} does not contain datetime.")
        frame = frame[frame["datetime"].dt.normalize() < target_day].copy()
        frame = frame.sort_values("datetime").reset_index(drop=True)
        if frame["datetime"].duplicated().any():
            duplicate_count = int(frame["datetime"].duplicated().sum())
            raise ValueError(f"{extra_path} contains duplicate extra-history datetimes: {duplicate_count}")
        if not frame.empty:
            frames.append(frame)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False).sort_values("datetime").reset_index(drop=True)


def load_target_rows(path, target_day):
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    if "datetime" not in frame.columns:
        raise ValueError(f"{path} does not contain datetime.")
    frame = frame[frame["datetime"].dt.normalize() == target_day].copy()
    frame = frame.sort_values("datetime").reset_index(drop=True)
    if len(frame) != 24:
        raise ValueError(f"Expected 24 target rows for {target_day.date()}, found {len(frame)} in {path}.")
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} contains duplicate target datetimes.")
    if "actual" not in frame.columns:
        frame["actual"] = np.nan
    return frame


def load_actuals_from_data(path, target_day):
    if path is None:
        return pd.Series(dtype="float64")
    data_path = Path(path)
    if not data_path.exists():
        return pd.Series(dtype="float64")

    frame = pd.read_csv(data_path, decimal=",", low_memory=False)
    frame.columns = [str(col).strip().lower() for col in frame.columns]
    if frame.empty or "hour" not in frame.columns or "rdn_price" not in frame.columns:
        return pd.Series(dtype="float64")

    date_col = frame.columns[0]
    parsed_date = pd.to_datetime(frame[date_col], errors="coerce", dayfirst=True).dt.normalize()
    hour = pd.to_numeric(frame["hour"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    if hour.dropna().empty:
        return pd.Series(dtype="float64")
    offset = 1 if hour.min() == 1 and hour.max() == 24 else 0
    datetimes = parsed_date + pd.to_timedelta(hour - offset, unit="h")
    actual = pd.to_numeric(frame["rdn_price"], errors="coerce")
    result = pd.Series(actual.to_numpy(dtype="float64"), index=datetimes)
    result = result[result.index.notna()]
    result = result[result.index.normalize() == target_day]
    return result[~result.index.duplicated(keep="last")].sort_index()


def validate_target_readiness(target_rows):
    required = sorted(overall_balanced_required_columns())
    missing = missing_overall_balanced_columns(target_rows.columns)
    nullable = {"actual"}
    null_required = []
    for col in required:
        if col in nullable or col not in target_rows.columns:
            continue
        values = pd.to_numeric(target_rows[col], errors="coerce") if col != "datetime" else target_rows[col]
        if values.isna().any():
            null_required.append(col)
    return missing, null_required


def wmape(actual, pred):
    actual = pd.to_numeric(actual, errors="coerce")
    pred = pd.to_numeric(pred, errors="coerce")
    mask = actual.notna() & pred.notna()
    if not mask.any():
        return np.nan
    denom = actual[mask].abs().sum()
    if denom <= 0:
        return np.nan
    return float((pred[mask] - actual[mask]).abs().sum() / denom * 100.0)


def save_forecast(day_frame, output_dir, date_iso, pred_col):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    day_frame = day_frame.copy()
    day_frame[pred_col] = clip_price_forecast(day_frame[pred_col], day_frame["price_cap"])

    public = pd.DataFrame(
        {
            "Hour": day_frame["datetime"].dt.hour + 1,
            "Predicted_Price": day_frame[pred_col].round(2),
            "Price_Cap": pd.to_numeric(day_frame["price_cap"], errors="coerce").round(2),
        }
    )
    forecast_csv = output_dir / f"prediction_{date_iso}_overall_balanced.csv"
    public.to_csv(forecast_csv, index=False)

    debug_csv = output_dir / f"prediction_{date_iso}_overall_balanced_debug.csv"
    day_frame.to_csv(debug_csv, index=False)

    plot_png = output_dir / f"prediction_{date_iso}_overall_balanced.png"
    plt.figure(figsize=(13, 6))
    plt.plot(public["Hour"], public["Predicted_Price"], marker="o", label=pred_col)
    plt.plot(public["Hour"], public["Price_Cap"], linestyle="--", alpha=0.5, label="Price cap")
    plt.axhline(MIN_MARKET_PRICE, linestyle=":", alpha=0.5, color="gray", label="Price floor")
    plt.xticks(range(1, 25))
    plt.grid(True, alpha=0.25)
    plt.title(f"Overall-balanced forecast for {date_iso}")
    plt.xlabel("Hour")
    plt.ylabel("UAH/MWh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_png, dpi=140)
    plt.close()
    return public, forecast_csv, debug_csv, plot_png


def save_comparison(day_frame, output_dir, date_iso, pred_col):
    actual_rows = day_frame.dropna(subset=["actual", pred_col]).copy()
    if actual_rows.empty:
        return None

    comparison = pd.DataFrame(
        {
            "Hour": actual_rows["datetime"].dt.hour + 1,
            "Actual_Price": pd.to_numeric(actual_rows["actual"], errors="coerce"),
            "Predicted_Price": pd.to_numeric(actual_rows[pred_col], errors="coerce"),
            "Price_Cap": pd.to_numeric(actual_rows["price_cap"], errors="coerce"),
        }
    )
    comparison["Abs_Error"] = (comparison["Predicted_Price"] - comparison["Actual_Price"]).abs()
    comparison["APE_pct"] = np.where(
        comparison["Actual_Price"].abs() > 1e-9,
        comparison["Abs_Error"] / comparison["Actual_Price"].abs() * 100.0,
        np.nan,
    )
    metrics = {
        "date": date_iso,
        "prediction_column": pred_col,
        "rows": int(len(comparison)),
        "wmape": wmape(comparison["Actual_Price"], comparison["Predicted_Price"]),
        "mae": float(comparison["Abs_Error"].mean()),
        "bias": float((comparison["Predicted_Price"] - comparison["Actual_Price"]).mean()),
    }

    rounded = comparison.copy()
    for col in ["Actual_Price", "Predicted_Price", "Price_Cap", "Abs_Error", "APE_pct"]:
        rounded[col] = rounded[col].round(2)

    output_dir = Path(output_dir)
    comparison_csv = output_dir / f"comparison_{date_iso}_overall_balanced.csv"
    metrics_json = output_dir / f"comparison_{date_iso}_overall_balanced_metrics.json"
    plot_png = output_dir / f"comparison_{date_iso}_overall_balanced.png"
    rounded.to_csv(comparison_csv, index=False)
    with open(metrics_json, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    plt.figure(figsize=(13, 6))
    plt.plot(comparison["Hour"], comparison["Actual_Price"], marker="o", label="Actual")
    plt.plot(comparison["Hour"], comparison["Predicted_Price"], marker="x", linestyle="--", label=pred_col)
    plt.xticks(range(1, 25))
    plt.grid(True, alpha=0.25)
    plt.title(f"{date_iso} overall-balanced vs actual, WMAPE={metrics['wmape']:.2f}%")
    plt.xlabel("Hour")
    plt.ylabel("UAH/MWh")
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_png, dpi=140)
    plt.close()
    return metrics, comparison_csv, metrics_json, plot_png


def main():
    parser = argparse.ArgumentParser(
        description="Build a canonical overall-balanced forecast for one date from a ready forecast-time input CSV."
    )
    parser.add_argument("target_date")
    parser.add_argument("--target-input-csv", default=None)
    parser.add_argument("--history-csv", default=os.path.join(ROOT_DIR, "output", "neural_best_predictions.csv"))
    parser.add_argument(
        "--extra-history-csv",
        action="append",
        default=[],
        help=(
            "Append an already-known pre-target debug/history CSV before building the target day. "
            "Rows on or after the target day are ignored, and target-day actual is still hidden."
        ),
    )
    parser.add_argument("--actual-data-csv", default=os.path.join(ROOT_DIR, "data", "ready_for_train.csv"))
    parser.add_argument("--output-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--output-col", default=OUTPUT_COL)
    parser.add_argument(
        "--strict-non-null-required",
        action="store_true",
        help="Fail when any required candidate column contains nulls in target rows.",
    )
    args = parser.parse_args()

    target_day = parse_target_date(args.target_date)
    date_iso = target_day.strftime("%Y-%m-%d")
    output_dir = Path(args.output_dir)
    default_input_dir = Path(ROOT_DIR) / "output"
    target_input = Path(args.target_input_csv) if args.target_input_csv else default_target_input(default_input_dir, date_iso)

    history = load_history(args.history_csv, target_day)
    extra_history = load_extra_history(args.extra_history_csv, target_day)
    if not extra_history.empty:
        history = pd.concat([history, extra_history], ignore_index=True, sort=False)
        history = history.sort_values("datetime").reset_index(drop=True)
        if history["datetime"].duplicated().any():
            duplicates = history.loc[history["datetime"].duplicated(), "datetime"].head(5).tolist()
            raise ValueError(
                "History and extra-history contain duplicate datetimes. "
                f"Pass only pre-target rows that are not already in --history-csv. examples={duplicates}"
            )

    target_rows = load_target_rows(target_input, target_day)
    missing, null_required = validate_target_readiness(target_rows)
    if missing or (args.strict_non_null_required and null_required):
        raise ValueError(
            f"Target input is not ready for overall-balanced build. "
            f"missing={missing} null_required={null_required}"
        )

    actuals = load_actuals_from_data(args.actual_data_csv, target_day)
    target_for_build = target_rows.copy()
    target_for_build["actual"] = np.nan
    combined = pd.concat([history, target_for_build], ignore_index=True, sort=False)
    combined = combined.sort_values("datetime").reset_index(drop=True)
    if combined["datetime"].duplicated().any():
        raise ValueError("Combined history + target input contains duplicate datetimes.")

    built, *summaries = build_overall_balanced(combined, output_col=args.output_col)
    day_frame = built[built["datetime"].dt.normalize() == target_day].copy().sort_values("datetime")
    if len(day_frame) != 24:
        raise ValueError(f"Expected 24 built rows for {date_iso}, found {len(day_frame)}")

    if not actuals.empty:
        day_frame["actual"] = day_frame["datetime"].map(actuals)

    public, forecast_csv, debug_csv, plot_png = save_forecast(day_frame, output_dir, date_iso, args.output_col)
    comparison = save_comparison(day_frame, output_dir, date_iso, args.output_col)

    readiness_payload = {
        "date": date_iso,
        "target_input_csv": os.fspath(target_input),
        "history_csv": args.history_csv,
        "extra_history_csv": [os.fspath(path) for path in args.extra_history_csv],
        "extra_history_rows": int(len(extra_history)),
        "output_column": args.output_col,
        "target_rows": int(len(target_rows)),
        "history_rows_before_target": int(len(history)),
        "missing_required_columns": missing,
        "null_required_columns": null_required,
        "forecast_csv": os.fspath(forecast_csv),
        "debug_csv": os.fspath(debug_csv),
        "plot_png": os.fspath(plot_png),
        "comparison_available": comparison is not None,
    }
    if comparison is not None:
        metrics, comparison_csv, metrics_json, comparison_plot = comparison
        readiness_payload.update(
            {
                "comparison_csv": os.fspath(comparison_csv),
                "comparison_metrics_json": os.fspath(metrics_json),
                "comparison_plot_png": os.fspath(comparison_plot),
                "metrics": metrics,
            }
        )
    readiness_payload["repair_summary_counts"] = {
        "fixed": len(summaries[0]),
        "shifted": len(summaries[1]),
        "candidate_blend": len(summaries[2]),
        "final_shifted": len(summaries[3]),
        "final_gated_blend": len(summaries[4]),
    }
    readiness_json = output_dir / f"prediction_{date_iso}_overall_balanced_readiness.json"
    with open(readiness_json, "w", encoding="utf-8") as f:
        json.dump(readiness_payload, f, indent=2, ensure_ascii=False)

    print(public.to_string(index=False))
    print(f"prediction_column={args.output_col}")
    print(f"target_input_csv={target_input}")
    if null_required:
        print(f"null_required_columns={','.join(null_required)}")
    if args.extra_history_csv:
        print(f"extra_history_rows={len(extra_history)}")
    print(f"forecast_csv={forecast_csv}")
    print(f"debug_csv={debug_csv}")
    print(f"plot_png={plot_png}")
    print(f"readiness_json={readiness_json}")
    if comparison is not None:
        metrics = comparison[0]
        print(f"comparison_csv={comparison[1]}")
        print(f"comparison_metrics_json={comparison[2]}")
        print(f"comparison_plot_png={comparison[3]}")
        print(f"wmape={metrics['wmape']:.4f}% mae={metrics['mae']:.2f} bias={metrics['bias']:.2f}")


if __name__ == "__main__":
    main()
