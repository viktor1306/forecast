import argparse
import os
import sys
from pathlib import Path

import pandas as pd

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
for import_path in (SRC_DIR, ROOT_DIR):
    if import_path not in sys.path:
        sys.path.append(import_path)

from apply_low_profile_adjuster import add_low_profile_adjustment  # noqa: E402


def add_feature_aliases(frame):
    frame = frame.copy()
    aliases = {
        "f_price_lag_24": "price_lag_24",
        "f_rolling_min_24": "rolling_min_24",
        "f_rolling_mean_hour_7d": "rolling_mean_hour_7d",
    }
    for source_col, alias_col in aliases.items():
        if alias_col not in frame.columns and source_col in frame.columns:
            frame[alias_col] = frame[source_col]
    return frame


def main():
    parser = argparse.ArgumentParser(description="Build the deterministic hybrid_low_profile candidate for a future-date CSV.")
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--source-col", default="hybrid_guarded_pred")
    parser.add_argument("--output-col", default="hybrid_low_profile_pred")
    parser.add_argument("--anchor-col", default="price_lag_24")
    parser.add_argument("--anchor-output-col", default="low_profile_anchor")
    parser.add_argument("--flag-col", default="low_profile_applied")
    args = parser.parse_args()

    frame = pd.read_csv(args.input_csv, parse_dates=["datetime"], low_memory=False)
    frame = add_feature_aliases(frame)
    if "datetime" not in frame.columns:
        raise ValueError("input CSV must contain datetime")
    if frame["datetime"].duplicated().any():
        raise ValueError("input CSV contains duplicate datetime rows")

    feature_frame = frame.set_index("datetime").sort_index()
    adjusted = add_low_profile_adjustment(
        predictions=frame,
        feature_frame=feature_frame,
        source_col=args.source_col,
        output_col=args.output_col,
        anchor_col=args.anchor_col,
        anchor_output_col=args.anchor_output_col,
        flag_col=args.flag_col,
        anchor_threshold=500.0,
        min_gap=1000.0,
        blend=0.15,
        start_month=5,
        end_month=8,
        hours="10-16",
    )
    output_cols = [
        "datetime",
        args.output_col,
        args.anchor_output_col,
        args.flag_col,
    ]
    output_cols = [col for col in output_cols if col in adjusted.columns]
    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    adjusted[output_cols].to_csv(output_csv, index=False)
    print(f"output_csv={output_csv}")
    print(f"applied_rows={int(adjusted[args.flag_col].sum())}")


if __name__ == "__main__":
    main()
