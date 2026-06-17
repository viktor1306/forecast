import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from build_overall_balanced_composite import (  # noqa: E402
    OUTPUT_COL,
    missing_overall_balanced_columns,
    overall_balanced_required_columns,
)
from evaluate_neural_hybrid import calculate_metrics  # noqa: E402


NULLABLE_REQUIRED_COLUMNS = {"actual"}


def _datetime_summary(frame):
    if "datetime" not in frame.columns:
        return {}

    dt = pd.to_datetime(frame["datetime"], errors="coerce")
    return {
        "datetime_min": None if dt.dropna().empty else str(dt.min()),
        "datetime_max": None if dt.dropna().empty else str(dt.max()),
        "duplicate_datetimes": int(dt.duplicated().sum()),
        "invalid_datetimes": int(dt.isna().sum()),
    }


def _metrics_summary(frame, pred_col):
    required = {"datetime", "actual", "price_cap", pred_col}
    if not required.issubset(frame.columns):
        return None

    metric_frame = frame.copy()
    metric_frame["datetime"] = pd.to_datetime(metric_frame["datetime"], errors="coerce")
    metric_frame["actual"] = pd.to_numeric(metric_frame["actual"], errors="coerce")
    metric_frame[pred_col] = pd.to_numeric(metric_frame[pred_col], errors="coerce")
    metric_frame = metric_frame.dropna(subset=["datetime", "actual", pred_col])
    if metric_frame.empty:
        return None

    return calculate_metrics(metric_frame, pred_col=pred_col)


def build_readiness_payload(input_csv, pred_col):
    frame = pd.read_csv(input_csv, low_memory=False)
    required = sorted(overall_balanced_required_columns())
    missing = missing_overall_balanced_columns(frame.columns)
    present = sorted(set(required).intersection(frame.columns))
    null_required = []
    for col in present:
        if col in NULLABLE_REQUIRED_COLUMNS:
            continue
        values = pd.to_datetime(frame[col], errors="coerce") if col == "datetime" else pd.to_numeric(frame[col], errors="coerce")
        if values.isna().any():
            null_required.append(col)

    payload = {
        "input_csv": os.fspath(input_csv),
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "required_columns": len(required),
        "present_required_columns": len(present),
        "missing_required_columns": len(missing),
        "null_required_columns": len(null_required),
        "ready_for_overall_balanced_build": len(missing) == 0,
        "ready_for_strict_non_null_build": len(missing) == 0 and len(null_required) == 0,
        "missing": missing,
        "null_required": null_required,
        "present": present,
        "prediction_column_checked": pred_col,
        "prediction_column_present": pred_col in frame.columns,
    }
    payload.update(_datetime_summary(frame))
    metrics = _metrics_summary(frame, pred_col)
    if metrics is not None:
        payload["metrics"] = metrics
    return payload


def main():
    parser = argparse.ArgumentParser(
        description="Check whether a prediction/debug CSV can build the unified overall-balanced forecast."
    )
    parser.add_argument("input_csv")
    parser.add_argument("--pred-col", default=OUTPUT_COL)
    parser.add_argument("--output-json", default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 2 when required columns are missing.",
    )
    parser.add_argument(
        "--strict-non-null-required",
        action="store_true",
        help="Exit with code 2 when required columns are missing or non-null required columns contain nulls.",
    )
    args = parser.parse_args()

    payload = build_readiness_payload(Path(args.input_csv), args.pred_col)
    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    status = "READY" if payload["ready_for_overall_balanced_build"] else "NOT_READY"
    print(
        f"{status}: {payload['present_required_columns']}/{payload['required_columns']} "
        f"required columns present in {payload['input_csv']}"
    )
    if payload["missing"]:
        print("missing:")
        for col in payload["missing"]:
            print(f"- {col}")
    if payload["null_required"]:
        print("null_required:")
        for col in payload["null_required"]:
            print(f"- {col}")
    if "metrics" in payload:
        metrics = payload["metrics"]
        print(
            f"metrics {args.pred_col}: "
            f"all={metrics['all_available']['wmape']:.4f}% "
            f"3m={metrics['last_3m']['wmape']:.4f}% "
            f"14d={metrics['last_14d']['wmape']:.4f}% "
            f"13d={metrics['last_13d']['wmape']:.4f}%"
        )
    if args.output_json:
        print(f"json={args.output_json}")
    if args.strict and payload["missing"]:
        raise SystemExit(2)
    if args.strict_non_null_required and (payload["missing"] or payload["null_required"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
