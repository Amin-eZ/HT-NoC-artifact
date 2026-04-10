import csv
from pathlib import Path

import matplotlib.pyplot as plt


def load_rows(csv_path):
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = dict(row)
            for key in [
                "weight",
                "activation",
                "compute",
                "sum_collection",
                "reconfiguration",
                "total",
                "speedup_vs_baseline",
            ]:
                parsed[key] = float(parsed[key])
            rows.append(parsed)
    return rows


def plot(rows, out_path):
    experiments = [
        ("vit_base", "32x32"),
        ("transformer", "64x64"),
    ]

    labels = []
    baseline_weight = []
    baseline_activation = []
    baseline_compute = []
    baseline_sum = []

    ht_weight = []
    ht_activation = []
    ht_compute = []
    ht_sum = []
    ht_reconfig = []

    for model, noc in experiments:
        labels.append(f"{model}\n{noc}")

        baseline_row = next(
            r for r in rows
            if r["model"] == model and r["noc"] == noc and r["architecture"] == "baseline"
        )
        ht_row = next(
            r for r in rows
            if r["model"] == model and r["noc"] == noc and r["architecture"] == "htnoc"
        )

        baseline_weight.append(baseline_row["weight"])
        baseline_activation.append(baseline_row["activation"])
        baseline_compute.append(baseline_row["compute"])
        baseline_sum.append(baseline_row["sum_collection"])

        ht_weight.append(ht_row["weight"])
        ht_activation.append(ht_row["activation"])
        ht_compute.append(ht_row["compute"])
        ht_sum.append(ht_row["sum_collection"])
        ht_reconfig.append(ht_row["reconfiguration"])

    x = list(range(len(labels)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    baseline_x = [i - width / 2 for i in x]
    ht_x = [i + width / 2 for i in x]

    ax.bar(baseline_x, baseline_weight, width, label="Weight (Baseline)")
    ax.bar(
        baseline_x,
        baseline_activation,
        width,
        bottom=baseline_weight,
        label="Ifmap (Baseline)"
    )
    ax.bar(
        baseline_x,
        baseline_compute,
        width,
        bottom=[a + b for a, b in zip(baseline_weight, baseline_activation)],
        label="Compute (Baseline)",
    )
    ax.bar(
        baseline_x,
        baseline_sum,
        width,
        bottom=[a + b + c for a, b, c in zip(baseline_weight, baseline_activation, baseline_compute)],
        label="Ofmap collection (Baseline)",
    )

    ax.bar(ht_x, ht_weight, width, label="Weight (HT-NoC)")
    ax.bar(
        ht_x,
        ht_activation,
        width,
        bottom=ht_weight,
        label="Ifmap (HT-NoC)"
    )
    ax.bar(
        ht_x,
        ht_compute,
        width,
        bottom=[a + b for a, b in zip(ht_weight, ht_activation)],
        label="Compute (HT-NoC)",
    )
    ax.bar(
        ht_x,
        ht_sum,
        width,
        bottom=[a + b + c for a, b, c in zip(ht_weight, ht_activation, ht_compute)],
        label="Ofmap collection (HT-NoC)",
    )
    ax.bar(
        ht_x,
        ht_reconfig,
        width,
        bottom=[a + b + c + d for a, b, c, d in zip(ht_weight, ht_activation, ht_compute, ht_sum)],
        label="Reconfiguration (HT-NoC)",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Latency (cycles)")
    ax.set_title("Section 6.3.2 – FFN execution time breakdown")
    ax.legend(fontsize=8, ncol=2)

    plt.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def main():
    root = Path(__file__).resolve().parents[2]
    csv_path = root / "outputs" / "section_6_3_2" / "tables" / "section_6_3_2_breakdown.csv"
    fig_dir = root / "outputs" /  "section_6_3_2" / "figures" 
    fig_dir.mkdir(parents=True, exist_ok=True)
    out_path = fig_dir / "section_6_3_2_breakdown.png"

    rows = load_rows(csv_path)
    plot(rows, out_path)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()