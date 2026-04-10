import sys
from pathlib import Path
import json
import csv
import argparse

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulator.conv import (
    CONV_parameter_breakdown,
    CONV_reconfiguration_latency,
    CONV_send_filter_latency,
    CONV_send_ifmap_latency_HT,
    CONV_send_ifmap_latency_Normal,
)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_one_layer(cfg, layer):
    noc_x = cfg["noc_size_x"]
    noc_y = cfg["noc_size_y"]
    node_latency = cfg["node_latency"]
    num_pixels_per_packet = cfg["num_pixels_per_packet"]

    kernel_side = layer["kernel_side"]
    kernel_number = layer["kernel_number"]
    ifmap_side = layer["ifmap_side"]
    ifmap_side_original = layer["ifmap_side_original"]
    ifmap_depth = layer["ifmap_depth"]

    num_ifmap_per_node, num_filter_per_node, ifmap_ratio, filter_ratio = CONV_parameter_breakdown(
        Kernel_side=kernel_side,
        Kernel_number=kernel_number,
        ifmap_side=ifmap_side,
        ifmap_side_original=ifmap_side_original,
        ifmap_depth=ifmap_depth,
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
    )

    filter_latency = CONV_send_filter_latency(
        Kernel_side=kernel_side,
        kernel_number=kernel_number,
        ifmap_depth=ifmap_depth,
        num_pixels_per_packet=num_pixels_per_packet,
        node_latency=node_latency,
        NOC_SIZE_X=noc_x,
    )

    ifmap_latency_baseline = CONV_send_ifmap_latency_Normal(
        Kernel_side=kernel_side,
        ifmap_side=ifmap_side,
        ifmap_depth=ifmap_depth,
        num_pixels_per_packet=num_pixels_per_packet,
        node_latency=node_latency,
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
    )

    ifmap_latency_htnoc = CONV_send_ifmap_latency_HT(
        Kernel_side=kernel_side,
        ifmap_side=ifmap_side,
        ifmap_depth=ifmap_depth,
        num_pixels_per_packet=num_pixels_per_packet,
        node_latency=node_latency,
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
    )

    reconfiguration_latency = CONV_reconfiguration_latency(
        Kernel_side=kernel_side,
        ifmap_side=ifmap_side,
        NOC_SIZE_X=noc_x,
        NOC_SIZE_Y=noc_y,
    )

    baseline_total_latency = filter_latency + ifmap_latency_baseline
    htnoc_total_latency = filter_latency + ifmap_latency_htnoc + reconfiguration_latency
    speedup = baseline_total_latency / htnoc_total_latency

    return {
        "label": layer["label"],
        "network": layer["network"],
        "ifmap_side": ifmap_side,
        "ifmap_side_original": ifmap_side_original,
        "ifmap_depth": ifmap_depth,
        "kernel_side": kernel_side,
        "kernel_number": kernel_number,
        "ofmap_side": layer["ofmap_side"],
        "ofmap_depth": layer["ofmap_depth"],
        "num_ifmap_per_node": num_ifmap_per_node,
        "num_filter_per_node": num_filter_per_node,
        "ifmap_ratio": ifmap_ratio,
        "filter_ratio": filter_ratio,
        "filter_latency": int(filter_latency),
        "ifmap_latency_baseline": int(ifmap_latency_baseline),
        "ifmap_latency_htnoc": int(ifmap_latency_htnoc),
        "reconfiguration_latency": int(reconfiguration_latency),
        "baseline_total_latency": int(baseline_total_latency),
        "htnoc_total_latency": int(htnoc_total_latency),
        "speedup_vs_baseline": float(speedup),
    }


def save_csv(rows, out_csv):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(payload, out_json):
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description="Run CONV experiments.")
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
        help="Directory where results will be written. Defaults to outputs/section_6_2_3.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_3" / "conv_layers_12x12.json"
    else:
        config_path = Path(args.config)

    if args.output_dir is None:
        out_dir = root / "outputs" / "section_6_2_3"
    else:
        out_dir = Path(args.output_dir)

    tables_dir = out_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(config_path)
    results = [run_one_layer(cfg, layer) for layer in cfg["layers"]]

    experiment_name = cfg.get("experiment_name", "conv_results")

    save_csv(results, tables_dir / f"{experiment_name}.csv")
    save_json(
        {
            "experiment_name": experiment_name,
            "noc_size_x": cfg["noc_size_x"],
            "noc_size_y": cfg["noc_size_y"],
            "node_latency": cfg["node_latency"],
            "num_pixels_per_packet": cfg["num_pixels_per_packet"],
            "results": results,
        },
        tables_dir / f"{experiment_name}.json",
    )

    print("Generated:")
    print(tables_dir / f"{experiment_name}.csv")
    print(tables_dir / f"{experiment_name}.json")


if __name__ == "__main__":
    main()