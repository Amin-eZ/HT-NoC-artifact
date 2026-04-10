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
            parsed = {
                "experiment_name": row["experiment_name"],
                "model": row["model"],
                "label": row["label"],
                "ifmap_side": int(float(row["ifmap_side"])),
                "ifmap_depth": int(float(row["ifmap_depth"])),
                "number_filters": int(float(row["number_filters"])),
                "alpha": float(row["alpha"]),
                "num_ifmap_per_node": int(float(row["num_ifmap_per_node"])),
                "num_filter_per_node": int(float(row["num_filter_per_node"])),
                "ifmap_ratio": float(row["ifmap_ratio"]),
                "filter_ratio": float(row["filter_ratio"]),
                "filter_latency": int(float(row["filter_latency"])),
                "ifmap_latency_baseline": int(float(row["ifmap_latency_baseline"])),
                "ifmap_latency_htnoc": int(float(row["ifmap_latency_htnoc"])),
                "reconfiguration_latency": int(float(row["reconfiguration_latency"])),
                "baseline_total_latency": int(float(row["baseline_total_latency"])),
                "htnoc_total_latency": int(float(row["htnoc_total_latency"])),
                "speedup_vs_baseline": float(row["speedup_vs_baseline"]),
            }
            rows.append(parsed)
    return rows


def alpha_to_label(alpha):
    if alpha == 1.0:
        return "1.0"
    if alpha == 0.5:
        return "0.5"
    if alpha == 0.25:
        return "0.25"
    return str(alpha)


def sort_key(row):
    layer_order = {}
    seen = []
    for r in rows_global:
        if r["label"] not in seen:
            seen.append(r["label"])
    for idx, label in enumerate(seen, start=1):
        layer_order[label] = idx

    alpha_order = {1.0: 1, 0.5: 2, 0.25: 3}
    return (layer_order[row["label"]], alpha_order[row["alpha"]])


def plot_parameter_distribution(rows, out_path):
    rows_sorted = sorted(rows, key=sort_key)

    labels = [f'{row["label"]}\nα={alpha_to_label(row["alpha"])}' for row in rows_sorted]
    ifmap_ratio = [row["ifmap_ratio"] for row in rows_sorted]
    filter_ratio = [row["filter_ratio"] for row in rows_sorted]

    x = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.bar(x, ifmap_ratio, label="Ifmap")
    ax.bar(x, filter_ratio, bottom=ifmap_ratio, label="Filter")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Parameter distribution")
    ax.set_ylim(0, 100)
    ax.legend()

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_latency_one_layer(rows, layer_name, out_path):
    layer_rows = [r for r in rows if r["label"] == layer_name]
    alpha_order = {1.0: 1, 0.5: 2, 0.25: 3}
    layer_rows = sorted(layer_rows, key=lambda r: alpha_order[r["alpha"]])

    labels = [f'α={alpha_to_label(r["alpha"])}' for r in layer_rows]

    filter_latency = [r["filter_latency"] for r in layer_rows]
    ifmap_latency_baseline = [r["ifmap_latency_baseline"] for r in layer_rows]
    ifmap_latency_htnoc = [r["ifmap_latency_htnoc"] for r in layer_rows]
    reconfiguration_latency = [r["reconfiguration_latency"] for r in layer_rows]

    x = list(range(len(labels)))
    width = 0.38

    baseline_x = [i - width / 2 for i in x]
    htnoc_x = [i + width / 2 for i in x]

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(baseline_x, ifmap_latency_baseline, width, label="Ifmap (Baseline)")
    ax.bar(
        baseline_x,
        filter_latency,
        width,
        bottom=ifmap_latency_baseline,
        label="Filter (Baseline)"
    )

    ax.bar(htnoc_x, ifmap_latency_htnoc, width, label="Ifmap (HT-NoC)")
    ax.bar(
        htnoc_x,
        filter_latency,
        width,
        bottom=ifmap_latency_htnoc,
        label="Filter (HT-NoC)"
    )
    ax.bar(
        htnoc_x,
        reconfiguration_latency,
        width,
        bottom=[a + b for a, b in zip(ifmap_latency_htnoc, filter_latency)],
        label="Reconfiguration",
        color="black"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Latency (cycles)")
    ax.set_title(f"{layer_name} Latency")
    ax.legend(fontsize=8, ncol=2)

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def parse_args():
    parser = argparse.ArgumentParser(description="Plot PW results.")
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
        help="Directory where figures will be written. Defaults to outputs/section_6_2_5/figures.",
    )
    return parser.parse_args()


def load_experiment_name_from_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg.get("experiment_name", "pw_results")


def main():
    global rows_global

    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_5" / "pw_layers_12x12.json"
    else:
        config_path = Path(args.config)

    experiment_name = load_experiment_name_from_config(config_path)

    if args.input_csv is None:
        csv_path = root / "outputs" / "section_6_2_5" / "tables" / f"{experiment_name}.csv"
    else:
        csv_path = Path(args.input_csv)

    if args.output_dir is None:
        fig_dir = root / "outputs" / "section_6_2_5" / "figures"
    else:
        fig_dir = Path(args.output_dir)

    fig_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(csv_path)
    rows_global = rows

    plot_parameter_distribution(rows, fig_dir / f"{experiment_name}_parameter_distribution.png")

    unique_labels = []
    for row in rows:
        if row["label"] not in unique_labels:
            unique_labels.append(row["label"])

    for layer_name in unique_labels:
        plot_latency_one_layer(rows, layer_name, fig_dir / f"{experiment_name}_{layer_name.lower()}_latency.png")

    print("Generated:")
    print(fig_dir / f"{experiment_name}_parameter_distribution.png")
    for layer_name in unique_labels:
        print(fig_dir / f"{experiment_name}_{layer_name.lower()}_latency.png")


if __name__ == "__main__":
    main()