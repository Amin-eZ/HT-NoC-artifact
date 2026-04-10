import csv
import json
import argparse
from pathlib import Path

import matplotlib.pyplot as plt


def load_rows(csv_path):
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = dict(row)
            parsed["input_size"] = int(row["input_size"])
            parsed["output_size"] = int(row["output_size"])
            parsed["baseline_weight_latency"] = float(row["baseline_weight_latency"])
            parsed["htnoc_weight_latency"] = float(row["htnoc_weight_latency"])
            parsed["reconfiguration_latency"] = float(row["reconfiguration_latency"])
            parsed["htnoc_total_latency"] = float(row["htnoc_total_latency"])
            parsed["speedup_vs_baseline"] = float(row["speedup_vs_baseline"])
            rows.append(parsed)
    return rows


def plot(rows, out_path):
    labels = [row["label"] for row in rows]

    baseline = [row["baseline_weight_latency"] for row in rows]
    htnoc_weight = [row["htnoc_weight_latency"] for row in rows]
    reconfig = [row["reconfiguration_latency"] for row in rows]

    x = list(range(len(labels)))
    width = 0.38

    fig, ax = plt.subplots(figsize=(14, 6))

    baseline_x = [i - width / 2 for i in x]
    htnoc_x = [i + width / 2 for i in x]

    ax.bar(baseline_x, baseline, width, label="Baseline NoC")
    ax.bar(htnoc_x, htnoc_weight, width, label="HT-NoC")
    ax.bar(htnoc_x, reconfig, width, bottom=htnoc_weight, label="Reconfiguration", color="black")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Latency (cycles)")
    ax.set_title("Section 6.2.2 – FC weight propagation latency on 12x12 NoC")
    ax.legend()

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Plot FC latency results.")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration JSON file. Defaults to the paper config.",
    )
    parser.add_argument(
        "--input-csv",
        type=str,
        default=None,
        help="Path to input CSV file. If omitted, it is inferred from the config.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory where the figure will be written. Defaults to outputs/section_6_2_2/figures.",
    )
    return parser.parse_args()


def load_experiment_name_from_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("experiment_name", "fc_results")


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_2" / "fc_layers_12x12.json"
    else:
        config_path = Path(args.config)

    experiment_name = load_experiment_name_from_config(config_path)

    if args.input_csv is None:
        csv_path = root / "outputs" / "section_6_2_2" / "tables" / f"{experiment_name}.csv"
    else:
        csv_path = Path(args.input_csv)

    if args.output_dir is None:
        fig_dir = root / "outputs" / "section_6_2_2" / "figures"
    else:
        fig_dir = Path(args.output_dir)

    fig_dir.mkdir(parents=True, exist_ok=True)
    out_path = fig_dir / f"{experiment_name}.png"

    rows = load_rows(csv_path)
    plot(rows, out_path)

    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()