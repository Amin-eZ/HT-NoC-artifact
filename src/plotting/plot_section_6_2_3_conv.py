import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_rows(csv_path):
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = dict(row)
            int_keys = [
                "ifmap_side",
                "ifmap_depth",
                "kernel_side",
                "kernel_number",
                "ofmap_side",
                "ofmap_depth",
                "num_ifmap_per_node",
                "num_filter_per_node",
                "filter_latency",
                "ifmap_latency_baseline",
                "ifmap_latency_htnoc",
                "reconfiguration_latency",
                "baseline_total_latency",
                "htnoc_total_latency",
            ]
            float_keys = [
                "ifmap_ratio",
                "filter_ratio",
                "speedup_vs_baseline",
            ]

            for key in int_keys:
                parsed[key] = int(parsed[key])
            for key in float_keys:
                parsed[key] = float(parsed[key])

            rows.append(parsed)
    return rows


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
    ax.set_title("Parameter distribution")
    ax.set_ylim(0, 100)
    ax.legend()

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_latency(rows, out_path):
    labels = [row["label"] for row in rows]

    filter_latency = [row["filter_latency"] for row in rows]
    ifmap_latency_baseline = [row["ifmap_latency_baseline"] for row in rows]
    ifmap_latency_htnoc = [row["ifmap_latency_htnoc"] for row in rows]
    reconfiguration_latency = [row["reconfiguration_latency"] for row in rows]

    x = list(range(len(labels)))
    width = 0.38

    baseline_x = [i - width / 2 for i in x]
    htnoc_x = [i + width / 2 for i in x]

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.bar(baseline_x, filter_latency, width, label="Filter (Baseline)")
    ax.bar(
        baseline_x,
        ifmap_latency_baseline,
        width,
        bottom=filter_latency,
        label="Ifmap (Baseline)"
    )

    ax.bar(htnoc_x, filter_latency, width, label="Filter (HT-NoC)",  color="red")
    ax.bar(
        htnoc_x,
        ifmap_latency_htnoc,
        width,
        bottom=filter_latency,
        label="Ifmap (HT-NoC)", 
        color="yellow"
    )
    ax.bar(
        htnoc_x,
        reconfiguration_latency,
        width,
        bottom=[a + b for a, b in zip(filter_latency, ifmap_latency_htnoc)],
        label="Reconfiguration", 
        color="black"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Latency (cycles)")
    ax.set_title("Latency")
    ax.legend(fontsize=8, ncol=2)

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def main():
    root = Path(__file__).resolve().parents[2]
    csv_path = root / "outputs" / "section_6_2_3" / "tables" / "section_6_2_3_conv_12x12.csv"

    fig_dir = root / "outputs" / "section_6_2_3" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(csv_path)

    plot_parameter_distribution(rows, fig_dir / "conv_parameter_distribution_12x12.png")
    plot_latency(rows, fig_dir / "conv_latency_12x12.png")

    print("Generated:")
    print(fig_dir / "conv_parameter_distribution_12x12.png")
    print(fig_dir / "conv_latency_12x12.png")


if __name__ == "__main__":
    main()