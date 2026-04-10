import sys
from pathlib import Path
import json
import csv
import argparse

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulator.pw import (
    PW_parameter_breakdown,
    PW_reconfiguration_latency,
    PW_ifmap_latency_HT_mode,
    PW_ifmap_latency_Normal_mode,
    PW_filter_latency,
)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_one_case(cfg, layer, alpha):
    noc_x = cfg["noc_size_x"]
    noc_y = cfg["noc_size_y"]
    node_latency = cfg["node_latency"]

    ifmap_side = layer["ifmap_side"]
    ifmap_depth = layer["ifmap_depth"]
    number_filters = layer["number_filters"]

    num_ifmap_per_node, num_filter_per_node, ifmap_ratio, filter_ratio = PW_parameter_breakdown(
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
        ifmap_side_original=ifmap_side,
        ifmap_depth=ifmap_depth,
        number_filters=number_filters,
        alpha=alpha,
    )

    filter_latency = PW_filter_latency(
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
        ifmap_depth=ifmap_depth,
        number_filters=number_filters,
        alpha=alpha,
        Node_latency=node_latency,
    )

    ifmap_latency_baseline = PW_ifmap_latency_Normal_mode(
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
        ifmap_side=ifmap_side,
        ifmap_depth=ifmap_depth,
        alpha=alpha,
        Node_latency=node_latency,
    )

    ifmap_latency_htnoc = PW_ifmap_latency_HT_mode(
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
        ifmap_side=ifmap_side,
        ifmap_depth=ifmap_depth,
        alpha=alpha,
        Node_latency=node_latency,
    )

    reconfiguration_latency = PW_reconfiguration_latency(
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
        ifmap_side=ifmap_side,
    )

    baseline_total_latency = filter_latency + ifmap_latency_baseline
    htnoc_total_latency = filter_latency + ifmap_latency_htnoc + reconfiguration_latency
    speedup = baseline_total_latency / htnoc_total_latency

    return {
        "experiment_name": cfg["experiment_name"],
        "model": cfg.get("model", "pw"),
        "label": layer["label"],
        "ifmap_side": ifmap_side,
        "ifmap_depth": ifmap_depth,
        "number_filters": number_filters,
        "alpha": float(alpha),
        "num_ifmap_per_node": int(num_ifmap_per_node),
        "num_filter_per_node": int(num_filter_per_node),
        "ifmap_ratio": float(ifmap_ratio),
        "filter_ratio": float(filter_ratio),
        "filter_latency": int(filter_latency),
        "ifmap_latency_baseline": int(ifmap_latency_baseline),
        "ifmap_latency_htnoc": int(ifmap_latency_htnoc),
        "reconfiguration_latency": int(reconfiguration_latency),
        "baseline_total_latency": int(baseline_total_latency),
        "htnoc_total_latency": int(htnoc_total_latency),
        "speedup_vs_baseline": float(speedup),
    }


def save_csv(rows, out_csv):
    fieldnames = [
        "experiment_name",
        "model",
        "label",
        "ifmap_side",
        "ifmap_depth",
        "number_filters",
        "alpha",
        "num_ifmap_per_node",
        "num_filter_per_node",
        "ifmap_ratio",
        "filter_ratio",
        "filter_latency",
        "ifmap_latency_baseline",
        "ifmap_latency_htnoc",
        "reconfiguration_latency",
        "baseline_total_latency",
        "htnoc_total_latency",
        "speedup_vs_baseline",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(payload, out_json):
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description="Run PW experiments.")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration JSON file. Defaults to the paper config.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory where results will be written. Defaults to outputs/section_6_2_5.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_5" / "pw_layers_12x12.json"
    else:
        config_path = Path(args.config)

    if args.output_dir is None:
        out_dir = root / "outputs" / "section_6_2_5"
    else:
        out_dir = Path(args.output_dir)

    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(config_path)

    results = []
    for layer in cfg["layers"]:
        for alpha in cfg["alpha_values"]:
            results.append(run_one_case(cfg, layer, alpha))

    experiment_name = cfg.get("experiment_name", "pw_results")

    save_csv(results, tables_dir / f"{experiment_name}.csv")
    save_json(
        {
            "experiment_name": experiment_name,
            "results": results,
        },
        tables_dir / f"{experiment_name}.json",
    )

    print("Generated:")
    print(tables_dir / f"{experiment_name}.csv")
    print(tables_dir / f"{experiment_name}.json")


if __name__ == "__main__":
    main()