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

from evaluate_neural_hybrid import calculate_metrics, wmape


def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if not np.isfinite(value):
            return None
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def parse_target_days(text):
    days = [part.strip() for part in str(text).split(",") if part.strip()]
    if not days:
        raise ValueError("--target-days must contain at least one YYYY-MM-DD value")
    return [pd.Timestamp(day).normalize() for day in days]


def fill_actuals_from_comparisons(frame, target_days, actuals_dir, comparison_suffix):
    if "datetime" not in frame.columns:
        return frame
    result = frame.copy()
    result["datetime"] = pd.to_datetime(result["datetime"])
    if "actual" not in result.columns:
        result["actual"] = np.nan
    if "price_cap" not in result.columns:
        result["price_cap"] = np.nan

    actuals_dir = Path(actuals_dir)
    for day in target_days:
        day_text = day.strftime("%Y-%m-%d")
        path = actuals_dir / f"comparison_{day_text}_{comparison_suffix}.csv"
        if not path.exists():
            continue
        comp = pd.read_csv(path)
        if not {"Hour", "Actual_Price", "Price_Cap"}.issubset(comp.columns):
            continue
        comp = comp.sort_values("Hour").reset_index(drop=True)
        datetimes = [day + pd.Timedelta(hours=int(hour) - 1) for hour in comp["Hour"]]
        actual_map = dict(zip(datetimes, pd.to_numeric(comp["Actual_Price"], errors="coerce")))
        cap_map = dict(zip(datetimes, pd.to_numeric(comp["Price_Cap"], errors="coerce")))
        mask = result["datetime"].dt.normalize() == day
        missing_actual = mask & result["actual"].isna()
        missing_cap = mask & result["price_cap"].isna()
        result.loc[missing_actual, "actual"] = result.loc[missing_actual, "datetime"].map(actual_map)
        result.loc[missing_cap, "price_cap"] = result.loc[missing_cap, "datetime"].map(cap_map)
    return result


def metric_block(frame, pred_col):
    if frame.empty:
        return {"n": 0, "wmape": None, "mae": None, "bias": None}
    actual = pd.to_numeric(frame["actual"], errors="coerce")
    pred = pd.to_numeric(frame[pred_col], errors="coerce")
    mask = actual.notna() & pred.notna()
    if not mask.any():
        return {"n": 0, "wmape": None, "mae": None, "bias": None}
    error = pred[mask] - actual[mask]
    return {
        "n": int(mask.sum()),
        "wmape": wmape(actual[mask], pred[mask]),
        "mae": float(error.abs().mean()),
        "bias": float(error.mean()),
    }


def top_errors(frame, pred_col, limit):
    if frame.empty:
        return []
    work = frame.copy()
    work["hour"] = work["datetime"].dt.hour + 1
    work["signed_error"] = pd.to_numeric(work[pred_col], errors="coerce") - pd.to_numeric(
        work["actual"], errors="coerce"
    )
    work["abs_error"] = work["signed_error"].abs()
    actual_abs = pd.to_numeric(work["actual"], errors="coerce").abs()
    work["ape_pct"] = np.where(actual_abs > 0.0, work["abs_error"] / actual_abs * 100.0, np.nan)
    cols = ["datetime", "hour", "actual", pred_col, "signed_error", "abs_error", "ape_pct"]
    return _json_safe(
        work.sort_values("abs_error", ascending=False)
        .head(limit)[cols]
        .rename(columns={pred_col: "prediction"})
        .to_dict(orient="records")
    )


def evaluate(predictions, pred_col, target_days):
    frame = predictions.copy()
    if "datetime" not in frame.columns:
        raise ValueError("predictions CSV must contain a datetime column")
    if pred_col not in frame.columns:
        raise ValueError(f"Prediction column not found: {pred_col}")
    if "actual" not in frame.columns:
        raise ValueError("predictions CSV must contain or be fillable with an actual column")
    if "price_cap" not in frame.columns:
        raise ValueError("predictions CSV must contain or be fillable with a price_cap column")

    frame["datetime"] = pd.to_datetime(frame["datetime"])
    frame = frame.sort_values("datetime").reset_index(drop=True)
    duplicate_count = int(frame["datetime"].duplicated().sum())
    usable = frame.dropna(subset=["actual", pred_col]).copy()
    metric_frame = usable
    if "__split" in usable.columns and (usable["__split"] == "history").any():
        metric_frame = usable[usable["__split"] == "history"].copy()

    payload = {
        "prediction_column": pred_col,
        "rows": int(len(frame)),
        "usable_rows": int(len(usable)),
        "metric_rows": int(len(metric_frame)),
        "duplicate_datetimes": duplicate_count,
        "period": {
            "start": usable["datetime"].min() if not usable.empty else None,
            "end": usable["datetime"].max() if not usable.empty else None,
        },
        "target_days": {},
        "top_errors": {},
        "cap_floor": {},
        "metrics": None,
    }

    pred = pd.to_numeric(frame[pred_col], errors="coerce")
    cap = pd.to_numeric(frame["price_cap"], errors="coerce")
    payload["cap_floor"] = {
        "below_10": int((pred < 10.0).sum()),
        "above_cap": int((pred > cap).sum()),
        "nan_predictions": int(pred.isna().sum()),
    }

    for day in target_days:
        day_mask = usable["datetime"].dt.normalize() == day
        day_frame = usable[day_mask]
        day_key = day.strftime("%Y-%m-%d")
        payload["target_days"][day_key] = metric_block(day_frame, pred_col)
        payload["top_errors"][day_key] = top_errors(day_frame, pred_col, limit=8)

    if not metric_frame.empty:
        payload["metrics"] = calculate_metrics(metric_frame, pred_col=pred_col)
    return _json_safe(payload)


def write_markdown(payload, path):
    pred_col = payload["prediction_column"]
    lines = [f"# Target Day Evaluation: `{pred_col}`", ""]
    if payload["metrics"]:
        metrics = payload["metrics"]
        lines.extend(
            [
                "## Historical Metrics",
                "",
                "| scope | WMAPE | rows |",
                "|---|---:|---:|",
                f"| all | {metrics['all_available']['wmape']:.4f}% | {metrics['all_available']['n']} |",
                f"| 3m | {metrics['last_3m']['wmape']:.4f}% | {metrics['last_3m']['n']} |",
                f"| 14d | {metrics['last_14d']['wmape']:.4f}% | {metrics['last_14d']['n']} |",
                f"| 13d | {metrics['last_13d']['wmape']:.4f}% | {metrics['last_13d']['n']} |",
                "",
            ]
        )
    lines.extend(["## Target Days", "", "| date | WMAPE | MAE | bias | rows |", "|---|---:|---:|---:|---:|"])
    for day, block in payload["target_days"].items():
        wmape_value = block["wmape"]
        wmape_text = "" if wmape_value is None else f"{wmape_value:.4f}%"
        mae_text = "" if block["mae"] is None else f"{block['mae']:.2f}"
        bias_text = "" if block["bias"] is None else f"{block['bias']:.2f}"
        lines.append(f"| {day} | {wmape_text} | {mae_text} | {bias_text} | {block['n']} |")
    lines.extend(
        [
            "",
            "## Integrity",
            "",
            f"- duplicate datetimes: `{payload['duplicate_datetimes']}`",
            f"- predictions below 10: `{payload['cap_floor']['below_10']}`",
            f"- predictions above cap: `{payload['cap_floor']['above_cap']}`",
            f"- NaN predictions: `{payload['cap_floor']['nan_predictions']}`",
            "",
        ]
    )
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Evaluate target-day WMAPE and promotion guardrails.")
    parser.add_argument("--predictions-csv", required=True)
    parser.add_argument("--pred-col", required=True)
    parser.add_argument("--target-days", default="2026-06-17,2026-06-18")
    parser.add_argument("--history-csv", default=None)
    parser.add_argument("--actuals-dir", default=os.path.join(ROOT_DIR, "output"))
    parser.add_argument("--comparison-suffix", default="overall_balanced")
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--output-md", default=None)
    args = parser.parse_args()

    target_days = parse_target_days(args.target_days)
    predictions = pd.read_csv(args.predictions_csv, low_memory=False)
    if "__split" not in predictions.columns:
        predictions["__split"] = "prediction"
    if args.history_csv:
        history = pd.read_csv(args.history_csv, low_memory=False)
        if "__split" not in history.columns:
            history["__split"] = "history"
        predictions["__split"] = "target"
        predictions = pd.concat([history, predictions], ignore_index=True, sort=False)
    predictions = fill_actuals_from_comparisons(
        predictions,
        target_days=target_days,
        actuals_dir=args.actuals_dir,
        comparison_suffix=args.comparison_suffix,
    )

    payload = evaluate(predictions, pred_col=args.pred_col, target_days=target_days)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.output_md:
        write_markdown(payload, args.output_md)

    if payload["metrics"]:
        metrics = payload["metrics"]
        print(
            f"{args.pred_col}: "
            f"all={metrics['all_available']['wmape']:.4f}% "
            f"3m={metrics['last_3m']['wmape']:.4f}% "
            f"14d={metrics['last_14d']['wmape']:.4f}% "
            f"13d={metrics['last_13d']['wmape']:.4f}%"
        )
    for day, block in payload["target_days"].items():
        print(
            f"{day}: wmape={block['wmape']:.4f}% "
            f"mae={block['mae']:.2f} bias={block['bias']:.2f} rows={block['n']}"
        )
    print(
        "integrity: "
        f"duplicates={payload['duplicate_datetimes']} "
        f"below_10={payload['cap_floor']['below_10']} "
        f"above_cap={payload['cap_floor']['above_cap']} "
        f"nan_pred={payload['cap_floor']['nan_predictions']}"
    )


if __name__ == "__main__":
    main()
