import sys
from pathlib import Path
import json
import csv
import argparse

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulator.fc import (
    FC_reconfiguration_latency,
    weight_latency_phase_Normal_mode,
    weight_latency_phase_HT_mode,
)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_one_layer(noc_size_x, noc_size_y, node_latency, layer_cfg):
    input_size = layer_cfg["input_size"]
    output_size = layer_cfg["output_size"]

    baseline_weight_latency = weight_latency_phase_Normal_mode(
        noc_size_x, noc_size_y, input_size, output_size, node_latency
    )

    htnoc_weight_latency = weight_latency_phase_HT_mode(
        noc_size_x, noc_size_y, input_size, output_size, node_latency
    )

    reconfiguration_latency = FC_reconfiguration_latency(
        noc_size_x, noc_size_y, output_size
    )

    htnoc_total_latency = htnoc_weight_latency + reconfiguration_latency
    speedup = baseline_weight_latency / htnoc_total_latency

    return {
        "label": layer_cfg["label"],
        "network": layer_cfg["network"],
        "input_size": input_size,
        "output_size": output_size,
        "baseline_weight_latency": int(baseline_weight_latency),
        "htnoc_weight_latency": int(htnoc_weight_latency),
        "reconfiguration_latency": int(reconfiguration_latency),
        "htnoc_total_latency": int(htnoc_total_latency),
        "speedup_vs_baseline": float(speedup),
    }


def save_csv(rows, out_csv):
    fieldnames = [
        "label",
        "network",
        "input_size",
        "output_size",
        "baseline_weight_latency",
        "htnoc_weight_latency",
        "reconfiguration_latency",
        "htnoc_total_latency",
        "speedup_vs_baseline",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(results, out_json):
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description="Run FC latency experiments.")
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
        help="Directory where results will be written. Defaults to outputs/section_6_2_2.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_2" / "fc_layers_12x12.json"
    else:
        config_path = Path(args.config)

    if args.output_dir is None:
        out_dir = root / "outputs" / "section_6_2_2"
    else:
        out_dir = Path(args.output_dir)

    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(config_path)

    noc_size_x = cfg["noc_size_x"]
    noc_size_y = cfg["noc_size_y"]
    node_latency = cfg["node_latency"]

    results = []
    for layer_cfg in cfg["layers"]:
        layer_result = run_one_layer(
            noc_size_x=noc_size_x,
            noc_size_y=noc_size_y,
            node_latency=node_latency,
            layer_cfg=layer_cfg,
        )
        results.append(layer_result)

    experiment_name = cfg.get("experiment_name", "fc_results")

    save_csv(results, tables_dir / f"{experiment_name}.csv")
    save_json(
        {
            "experiment_name": experiment_name,
            "noc_size_x": noc_size_x,
            "noc_size_y": noc_size_y,
            "node_latency": node_latency,
            "results": results,
        },
        tables_dir / f"{experiment_name}.json",
    )

    print("Generated:")
    print(tables_dir / f"{experiment_name}.csv")
    print(tables_dir / f"{experiment_name}.json")


if __name__ == "__main__":
    main()