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

from check_overall_balanced_readiness import build_readiness_payload  # noqa: E402


FEATURE_ALIASES = {
    "price_lag_24": "f_price_lag_24",
    "price_lag_48": "f_price_lag_48",
    "price_lag_168": "f_price_lag_168",
    "rolling_mean_hour_3d": "f_rolling_mean_hour_3d",
    "rolling_mean_hour_7d": "f_rolling_mean_hour_7d",
    "rolling_mean_hour_14d": "f_rolling_mean_hour_14d",
    "rolling_mean_24": "f_rolling_mean_24",
    "rolling_min_24": "f_rolling_min_24",
    "rolling_std_24": "f_rolling_std_24",
    "windspeed": "f_windspeed",
    "windgust": "f_windgust",
    "cloudcover": "f_cloudcover",
    "solarradiation": "f_solarradiation",
    "solarenergy": "f_solarenergy",
}


def load_debug_csv(path):
    frame = pd.read_csv(path, parse_dates=["datetime"], low_memory=False)
    if "datetime" not in frame.columns:
        raise ValueError(f"{path} does not contain datetime.")
    if frame["datetime"].duplicated().any():
        raise ValueError(f"{path} contains duplicate datetime rows.")
    for source_col, alias_col in FEATURE_ALIASES.items():
        if source_col in frame.columns and alias_col not in frame.columns:
            frame[alias_col] = frame[source_col]
    return frame.sort_values("datetime").reset_index(drop=True)


def merge_candidate_columns(base, candidate_paths, prefer_candidate=False, fill_null_candidate=False):
    if prefer_candidate and fill_null_candidate:
        raise ValueError("--prefer-candidate and --fill-null-candidate are mutually exclusive.")

    merged = base.copy()
    merge_summary = []
    for candidate_path in candidate_paths:
        candidate = load_debug_csv(candidate_path)
        value_cols = [col for col in candidate.columns if col != "datetime"]
        new_cols = []
        replaced_cols = []
        fill_null_cols = []
        fill_null_cells = {}
        skipped_cols = []

        candidate_by_datetime = candidate.set_index("datetime")
        for col in value_cols:
            candidate_values = merged["datetime"].map(candidate_by_datetime[col])
            if col not in merged.columns:
                merged[col] = candidate_values
                new_cols.append(col)
                continue

            if prefer_candidate:
                merged[col] = candidate_values
                replaced_cols.append(col)
                continue

            if fill_null_candidate:
                fill_mask = merged[col].isna() & candidate_values.notna()
                fill_count = int(fill_mask.sum())
                if fill_count > 0:
                    merged.loc[fill_mask, col] = candidate_values.loc[fill_mask]
                    fill_null_cols.append(col)
                    fill_null_cells[col] = fill_count
                else:
                    skipped_cols.append(col)
                continue

            skipped_cols.append(col)

        merge_summary.append(
            {
                "candidate_csv": os.fspath(candidate_path),
                "added_columns": sorted(new_cols),
                "replaced_columns": sorted(replaced_cols),
                "fill_null_columns": sorted(fill_null_cols),
                "fill_null_cells": fill_null_cells,
                "skipped_existing_columns": sorted(skipped_cols),
            }
        )
    return merged, merge_summary


def main():
    parser = argparse.ArgumentParser(
        description="Assemble a future-date debug CSV with extra candidate columns for overall-balanced readiness checks."
    )
    parser.add_argument("--base-debug-csv", required=True)
    parser.add_argument("--candidate-csv", action="append", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--prefer-candidate", action="store_true")
    parser.add_argument(
        "--fill-null-candidate",
        action="store_true",
        help="For overlapping candidate columns, fill only null base values instead of replacing the whole column.",
    )
    args = parser.parse_args()

    base = load_debug_csv(Path(args.base_debug_csv))
    merged, merge_summary = merge_candidate_columns(
        base,
        [Path(path) for path in args.candidate_csv],
        prefer_candidate=args.prefer_candidate,
        fill_null_candidate=args.fill_null_candidate,
    )
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_csv, index=False)

    readiness = build_readiness_payload(output_csv, pred_col="overall_balanced_low_regime_pred")
    payload = {
        "base_debug_csv": args.base_debug_csv,
        "output_csv": os.fspath(output_csv),
        "merge_summary": merge_summary,
        "readiness": readiness,
    }
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    print(
        f"assembled={output_csv} "
        f"required={readiness['present_required_columns']}/{readiness['required_columns']} "
        f"missing={readiness['missing_required_columns']} "
        f"null_required={readiness['null_required_columns']}"
    )
    if readiness["missing"]:
        print("missing:")
        for col in readiness["missing"]:
            print(f"- {col}")
    if args.output_json:
        print(f"json={args.output_json}")


if __name__ == "__main__":
    main()
