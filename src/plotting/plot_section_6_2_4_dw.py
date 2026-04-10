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
            parsed["baseline_filter_latency"] = float(row["baseline_filter_latency"])
            parsed["baseline_ifmap_latency"] = float(row["baseline_ifmap_latency"])
            parsed["baseline_total_latency"] = float(row["baseline_total_latency"])
            parsed["htnoc_filter_latency"] = float(row["htnoc_filter_latency"])
            parsed["htnoc_ifmap_latency"] = float(row["htnoc_ifmap_latency"])
            parsed["reconfiguration_latency"] = float(row["reconfiguration_latency"])
            parsed["htnoc_total_latency"] = float(row["htnoc_total_latency"])
            parsed["num_ifmap_per_node"] = float(row["num_ifmap_per_node"])
            parsed["num_filter_per_node"] = float(row["num_filter_per_node"])
            parsed["ifmap_ratio"] = float(row["ifmap_ratio"])
            parsed["filter_ratio"] = float(row["filter_ratio"])
            parsed["speedup_vs_baseline"] = float(row["speedup_vs_baseline"])
            rows.append(parsed)
    return rows


def plot_latency(rows, out_path):
    labels = [row["label"] for row in rows]

    baseline_filter = [row["baseline_filter_latency"] for row in rows]
    baseline_ifmap = [row["baseline_ifmap_latency"] for row in rows]

    htnoc_filter = [row["htnoc_filter_latency"] for row in rows]
    htnoc_ifmap = [row["htnoc_ifmap_latency"] for row in rows]
    reconfig = [row["reconfiguration_latency"] for row in rows]

    x = list(range(len(labels)))
    width = 0.38

    fig, ax = plt.subplots(figsize=(14, 6))

    baseline_x = [i - width / 2 for i in x]
    htnoc_x = [i + width / 2 for i in x]

    ax.bar(baseline_x, baseline_filter, width, label="Filter (Baseline)")
    ax.bar(
        baseline_x,
        baseline_ifmap,
        width,
        bottom=baseline_filter,
        label="Ifmap (Baseline)",
    )

    ax.bar(htnoc_x, htnoc_ifmap, width, label="Filter (HT-NoC)", color = "red")
    ax.bar(
        htnoc_x,
        htnoc_ifmap,
        width,
        bottom=htnoc_filter,
        label="Ifmap (HT-NoC)",
        color = "green",
    )
    ax.bar(
        htnoc_x,
        reconfig,
        width,
        bottom=[i + f for i, f in zip(htnoc_ifmap, htnoc_filter)],
        label="Reconfiguration",
        color="black",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Latency (cycles)")
    ax.set_title("DW latency")
    ax.legend()

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_parameter_distribution(rows, out_path):
    labels = [row["label"] for row in rows]
    filter_ratio = [row["filter_ratio"] for row in rows]
    ifmap_ratio = [row["ifmap_ratio"] for row in rows]

    x = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(x, ifmap_ratio, label="Ifmap")
    ax.bar(x, filter_ratio, bottom=ifmap_ratio, label="Filter")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("DW parameter distribution")
    ax.set_ylim(0, 100)
    ax.legend()

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Plot DW results.")
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
        help="Directory where figures will be written. Defaults to outputs/section_6_2_4/figures.",
    )
    return parser.parse_args()


def load_experiment_name_from_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("experiment_name", "dw_results")


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_4" / "dw_layers_12x12.json"
    else:
        config_path = Path(args.config)

    experiment_name = load_experiment_name_from_config(config_path)

    if args.input_csv is None:
        csv_path = root / "outputs" / "section_6_2_4" / "tables" / f"{experiment_name}.csv"
    else:
        csv_path = Path(args.input_csv)

    if args.output_dir is None:
        fig_dir = root / "outputs" / "section_6_2_4" / "figures"
    else:
        fig_dir = Path(args.output_dir)

    fig_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(csv_path)

    latency_out = fig_dir / f"{experiment_name}_latency.png"
    parameter_out = fig_dir / f"{experiment_name}_parameter_distribution.png"

    plot_latency(rows, latency_out)
    plot_parameter_distribution(rows, parameter_out)

    print("Generated:")
    print(latency_out)
    print(parameter_out)


if __name__ == "__main__":
    main()