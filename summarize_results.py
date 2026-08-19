from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import _bootstrap  # noqa: F401
from src.config import load_config, resolve_workspace_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge experiment metric CSV files.")
    parser.add_argument("--config", default="configs/project.yaml")
    parser.add_argument("--method", default="patchcore")
    parser.add_argument("--include-toy", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    results_root = resolve_workspace_path(config, config["experiment"]["output_dir"]) / args.method
    rows = []
    categories = set(config["data"]["categories"])
    for metrics_path in sorted(results_root.glob("*/ratio_*/metrics.csv")):
        category = metrics_path.parents[1].name
        if not args.include_toy and category not in categories:
            continue
        df = pd.read_csv(metrics_path)
        row = df.iloc[0].to_dict()
        row["category"] = category
        row["run"] = metrics_path.parent.name
        rows.append(row)
    if not rows:
        print(f"No metrics found under {results_root}")
        return
    summary = pd.DataFrame(rows)
    output_path = results_root / "summary.csv"
    summary.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(summary.to_string(index=False))
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
