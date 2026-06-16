import argparse
import json
import os
from pathlib import Path

import pandas as pd

from evaluate_neural_hybrid import calculate_metrics, save_evaluation_artifacts
from prediction_limits import clip_price_series


def load_member(output_dir, experiment_id):
    path = Path(output_dir) / f"neural_experiment_{experiment_id}_predictions.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, parse_dates=["datetime"]).set_index("datetime").sort_index()


def build_ensemble(output_dir, members, experiment_id, recent_policy="tree"):
    frames = [load_member(output_dir, member) for member in members]
    common_index = frames[0].index
    for frame in frames[1:]:
        common_index = common_index.intersection(frame.index)
    if common_index.empty:
        raise ValueError("No overlapping prediction timestamps across ensemble members.")

    frames = [frame.loc[common_index] for frame in frames]
    base = frames[0][["actual", "price_cap", "tree_base_pred", "tree_recent_calibrated_pred"]].copy()

    for col in ["neural_pred", "hybrid_pred", "hybrid_recent_calibrated_pred", "hybrid_guarded_pred"]:
        if all(col in frame.columns for frame in frames):
            base[f"ensemble_{col}"] = sum(frame[col] for frame in frames) / len(frames)

    if "ensemble_hybrid_pred" not in base.columns:
        raise ValueError("Members do not contain hybrid_pred.")

    base["hybrid_guarded_pred"] = base["ensemble_hybrid_pred"]
    recent_start = base.index.max() - pd.Timedelta(days=14)
    recent_mask = base.index >= recent_start
    if recent_policy == "tree":
        base.loc[recent_mask, "hybrid_guarded_pred"] = base.loc[recent_mask, "tree_recent_calibrated_pred"]
    elif recent_policy == "hybrid_recent" and "ensemble_hybrid_recent_calibrated_pred" in base.columns:
        base.loc[recent_mask, "hybrid_guarded_pred"] = base.loc[
            recent_mask, "ensemble_hybrid_recent_calibrated_pred"
        ]
    else:
        raise ValueError(f"Unsupported recent policy: {recent_policy}")

    base["hybrid_guarded_pred"] = clip_price_series(base["hybrid_guarded_pred"], base["price_cap"])
    predictions = base.reset_index().rename(columns={"index": "datetime"})

    artifacts = save_evaluation_artifacts(
        predictions,
        experiment_id=experiment_id,
        output_dir=output_dir,
        pred_col="hybrid_guarded_pred",
    )
    variant_cols = [
        "tree_base_pred",
        "tree_recent_calibrated_pred",
        "ensemble_neural_pred",
        "ensemble_hybrid_pred",
        "ensemble_hybrid_recent_calibrated_pred",
        "hybrid_guarded_pred",
    ]
    variant_metrics = {
        col: calculate_metrics(predictions, pred_col=col)
        for col in variant_cols
        if col in predictions.columns
    }

    metrics_path = Path(artifacts["metrics_json"])
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_payload = json.load(f)
    metrics_payload["variant_metrics"] = variant_metrics
    metrics_payload["ensemble_members"] = members
    metrics_payload["recent_policy"] = recent_policy
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)

    log_path = Path(output_dir) / "neural_experiments_log.md"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n### {experiment_id}\n\n")
        f.write("- Ensemble members: " + ", ".join(f"`{member}`" for member in members) + ".\n")
        f.write(f"- Recent policy: `{recent_policy}`.\n")
        f.write("- Evaluator still has one row per factual hour.\n\n")
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

    return artifacts, variant_metrics


def main():
    parser = argparse.ArgumentParser(description="Average neural-hybrid experiment predictions.")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--members", nargs="+", required=True)
    parser.add_argument("--recent-policy", choices=["tree", "hybrid_recent"], default="tree")
    args = parser.parse_args()

    _, metrics = build_ensemble(args.output_dir, args.members, args.experiment_id, args.recent_policy)
    for col, metric in metrics.items():
        print(
            f"{col}: 3m={metric['last_3m']['wmape']:.2f}% "
            f"14d={metric['last_14d']['wmape']:.2f}%"
        )


if __name__ == "__main__":
    main()
