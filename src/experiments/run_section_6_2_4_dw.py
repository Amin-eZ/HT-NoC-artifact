import sys
import json
import csv
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulator.dw import (
    DW_send_filter_latency,
    DW_send_ifmap_latency_HT,
    DW_send_ifmap_latency_Normal,
    DW_parameter_breakdown,
    DW_reconfiguration_latency,
)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_layer_config(common_config, layer_config):
    return {
        "experiment_name": common_config["experiment_name"],
        "model": common_config.get("model", "dw"),
        "noc_size_x": common_config["noc_size_x"],
        "noc_size_y": common_config["noc_size_y"],
        "num_pixels_per_packet": common_config["num_pixels_per_packet"],
        "node_latency": common_config["node_latency"],
        "label": layer_config["label"],
        "kernel_side": layer_config["kernel_side"],
        "ifmap_side_original": layer_config["ifmap_side_original"],
        "ifmap_side": layer_config["ifmap_side"],
        "ifmap_depth": layer_config["ifmap_depth"],
        "ofmap_side": layer_config.get("ofmap_side", layer_config["ifmap_side_original"]),
        "ofmap_depth": layer_config.get("ofmap_depth", layer_config["ifmap_depth"]),
    }


def run_one_experiment(config):
    baseline_filter_latency = DW_send_filter_latency(
        Kernel_side=config["kernel_side"],
        ifmap_depth=config["ifmap_depth"],
        num_pixels_per_packet=config["num_pixels_per_packet"],
        node_latency=config["node_latency"],
        NOC_SIZE_X=config["noc_size_x"],
    )

    baseline_ifmap_latency = DW_send_ifmap_latency_Normal(
        Kernel_side=config["kernel_side"],
        ifmap_side=config["ifmap_side"],
        ifmap_depth=config["ifmap_depth"],
        num_pixels_per_packet=config["num_pixels_per_packet"],
        node_latency=config["node_latency"],
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
    )

    htnoc_ifmap_latency = DW_send_ifmap_latency_HT(
        Kernel_side=config["kernel_side"],
        ifmap_side=config["ifmap_side"],
        ifmap_depth=config["ifmap_depth"],
        num_pixels_per_packet=config["num_pixels_per_packet"],
        node_latency=config["node_latency"],
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
    )

    reconfiguration_latency = DW_reconfiguration_latency(
        Kernel_side=config["kernel_side"],
        ifmap_side=config["ifmap_side"],
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
    )

    (
        num_ifmap_per_node,
        num_filter_per_node,
        ifmap_per_node_ratio,
        filter_per_node_ratio,
    ) = DW_parameter_breakdown(
        Kernel_side=config["kernel_side"],
        ifmap_side=config["ifmap_side"],
        ifmap_side_original=config["ifmap_side_original"],
        ifmap_depth=config["ifmap_depth"],
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
    )

    baseline_total_latency = baseline_filter_latency + baseline_ifmap_latency
    htnoc_total_latency = baseline_filter_latency + htnoc_ifmap_latency + reconfiguration_latency
    speedup_vs_baseline = baseline_total_latency / htnoc_total_latency

    return {
        "config": config,
        "baseline": {
            "filter_latency": baseline_filter_latency,
            "ifmap_latency": baseline_ifmap_latency,
            "total_latency": baseline_total_latency,
        },
        "htnoc": {
            "filter_latency": baseline_filter_latency,
            "ifmap_latency": htnoc_ifmap_latency,
            "reconfiguration_latency": reconfiguration_latency,
            "total_latency": htnoc_total_latency,
        },
        "parameters": {
            "num_ifmap_per_node": num_ifmap_per_node,
            "num_filter_per_node": num_filter_per_node,
            "ifmap_per_node_ratio": ifmap_per_node_ratio,
            "filter_per_node_ratio": filter_per_node_ratio,
        },
        "speedup": {
            "speedup_vs_baseline": speedup_vs_baseline,
        },
    }


def flatten_results(result):
    cfg = result["config"]
    baseline = result["baseline"]
    htnoc = result["htnoc"]
    params = result["parameters"]
    speedup = result["speedup"]

    return {
        "experiment_name": cfg["experiment_name"],
        "model": cfg["model"],
        "label": cfg["label"],
        "noc": f'{cfg["noc_size_x"]}x{cfg["noc_size_y"]}',
        "kernel_side": cfg["kernel_side"],
        "ifmap_side_original": cfg["ifmap_side_original"],
        "ifmap_side": cfg["ifmap_side"],
        "ifmap_depth": cfg["ifmap_depth"],
        "ofmap_side": cfg["ofmap_side"],
        "ofmap_depth": cfg["ofmap_depth"],
        "num_pixels_per_packet": cfg["num_pixels_per_packet"],
        "node_latency": cfg["node_latency"],
        "baseline_filter_latency": baseline["filter_latency"],
        "baseline_ifmap_latency": baseline["ifmap_latency"],
        "baseline_total_latency": baseline["total_latency"],
        "htnoc_filter_latency": htnoc["filter_latency"],
        "htnoc_ifmap_latency": htnoc["ifmap_latency"],
        "reconfiguration_latency": htnoc["reconfiguration_latency"],
        "htnoc_total_latency": htnoc["total_latency"],
        "num_ifmap_per_node": params["num_ifmap_per_node"],
        "num_filter_per_node": params["num_filter_per_node"],
        "ifmap_ratio": params["ifmap_per_node_ratio"],
        "filter_ratio": params["filter_per_node_ratio"],
        "speedup_vs_baseline": speedup["speedup_vs_baseline"],
    }


def save_csv(rows, out_csv):
    fieldnames = [
        "experiment_name",
        "model",
        "label",
        "noc",
        "kernel_side",
        "ifmap_side_original",
        "ifmap_side",
        "ifmap_depth",
        "ofmap_side",
        "ofmap_depth",
        "num_pixels_per_packet",
        "node_latency",
        "baseline_filter_latency",
        "baseline_ifmap_latency",
        "baseline_total_latency",
        "htnoc_filter_latency",
        "htnoc_ifmap_latency",
        "reconfiguration_latency",
        "htnoc_total_latency",
        "num_ifmap_per_node",
        "num_filter_per_node",
        "ifmap_ratio",
        "filter_ratio",
        "speedup_vs_baseline",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(all_results, out_json):
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(description="Run DW experiments.")
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
        help="Directory where results will be written. Defaults to outputs/section_6_2_4.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    if args.config is None:
        config_path = root / "configs" / "section_6_2_4" / "dw_layers_12x12.json"
    else:
        config_path = Path(args.config)

    if args.output_dir is None:
        out_root = root / "outputs" / "section_6_2_4"
    else:
        out_root = Path(args.output_dir)

    tables_dir = out_root / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    config = load_config(config_path)

    all_results = []
    all_rows = []

    for layer_cfg in config["layers"]:
        merged_config = build_layer_config(config, layer_cfg)
        result = run_one_experiment(merged_config)
        all_results.append(result)
        all_rows.append(flatten_results(result))

    experiment_name = config.get("experiment_name", "dw_results")

    save_csv(all_rows, tables_dir / f"{experiment_name}.csv")
    save_json(all_results, tables_dir / f"{experiment_name}.json")

    print("Generated:")
    print(tables_dir / f"{experiment_name}.csv")
    print(tables_dir / f"{experiment_name}.json")


if __name__ == "__main__":
    main()