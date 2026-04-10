import sys
import json
import csv
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from simulator.ffn import (
    FFN_phase_breakdown_ht,
    FFN_phase_breakdown_normal,
    FFN_speedup,
)


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_one_experiment(config):
    baseline = FFN_phase_breakdown_normal(
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
        FC1_Input_size=config["fc1_input"],
        FC1_Output_size=config["fc1_output"],
        FC2_Input_size=config["fc2_input"],
        FC2_Output_size=config["fc2_output"],
        Node_latency=config["node_latency"],
    )

    ht = FFN_phase_breakdown_ht(
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
        FC1_Input_size=config["fc1_input"],
        FC1_Output_size=config["fc1_output"],
        FC2_Input_size=config["fc2_input"],
        FC2_Output_size=config["fc2_output"],
        Node_latency=config["node_latency"],
    )

    speed = FFN_speedup(
        NOC_SIZE_X=config["noc_size_x"],
        NOC_SIZE_Y=config["noc_size_y"],
        FC1_Input_size=config["fc1_input"],
        FC1_Output_size=config["fc1_output"],
        FC2_Input_size=config["fc2_input"],
        FC2_Output_size=config["fc2_output"],
        Node_latency=config["node_latency"],
    )

    return {
        "config": config,
        "baseline": baseline,
        "ht": ht,
        "speedup": speed,
    }


def flatten_results(result):
    cfg = result["config"]
    base = result["baseline"]["ffn_total"]
    ht = result["ht"]["ffn_total"]
    speed = result["speedup"]["speedup"]

    rows = []

    rows.append({
        "experiment_name": cfg["experiment_name"],
        "model": cfg["model"],
        "noc": f'{cfg["noc_size_x"]}x{cfg["noc_size_y"]}',
        "architecture": "baseline",
        "weight": base["weight"],
        "activation": base["activation"],
        "compute": base["compute"],
        "sum_collection": base["sum_collection"],
        "reconfiguration": base["reconfiguration"],
        "total": base["total"],
        "speedup_vs_baseline": 1.0,
    })

    rows.append({
        "experiment_name": cfg["experiment_name"],
        "model": cfg["model"],
        "noc": f'{cfg["noc_size_x"]}x{cfg["noc_size_y"]}',
        "architecture": "htnoc",
        "weight": ht["weight"],
        "activation": ht["activation"],
        "compute": ht["compute"],
        "sum_collection": ht["sum_collection"],
        "reconfiguration": ht["reconfiguration"],
        "total": ht["total"],
        "speedup_vs_baseline": speed,
    })

    return rows


def save_csv(rows, out_csv):
    fieldnames = [
        "experiment_name",
        "model",
        "noc",
        "architecture",
        "weight",
        "activation",
        "compute",
        "sum_collection",
        "reconfiguration",
        "total",
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
    parser = argparse.ArgumentParser(description="Run one custom FFN experiment.")
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to a custom FFN configuration JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory where results will be written. Defaults to outputs/custom_ffn.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = Path(__file__).resolve().parents[2]

    config_path = Path(args.config)

    if args.output_dir is None:
        out_root = root / "outputs" / "custom_ffn"
    else:
        out_root = Path(args.output_dir)

    tables_dir = out_root / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    cfg = load_config(config_path)

    if "experiment_name" not in cfg:
        cfg["experiment_name"] = "custom_ffn"

    result = run_one_experiment(cfg)
    rows = flatten_results(result)

    experiment_name = cfg.get("experiment_name", "custom_ffn")

    save_csv(rows, tables_dir / f"{experiment_name}.csv")
    save_json([result], tables_dir / f"{experiment_name}.json")

    print("Generated:")
    print(tables_dir / f"{experiment_name}.csv")
    print(tables_dir / f"{experiment_name}.json")


if __name__ == "__main__":
    main()