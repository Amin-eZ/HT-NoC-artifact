import sys
import json
import csv
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


def main():
    root = Path(__file__).resolve().parents[2]
    config_dir = root / "configs" / "section_6_3_1"
    out_dir = root / "outputs" / "section_6_3_1"/ "tables"
    out_dir.mkdir(parents=True, exist_ok=True)

    config_files = [
        config_dir / "gpt2_small_16x16.json",
        config_dir / "gpt2_small_64x64.json",
        config_dir / "gpt2_medium_16x16.json",
        config_dir / "gpt2_medium_64x64.json",
    ]

    all_results = []
    all_rows = []

    for cfg_path in config_files:
        cfg = load_config(cfg_path)
        result = run_one_experiment(cfg)
        all_results.append(result)
        all_rows.extend(flatten_results(result))

    save_csv(all_rows, out_dir / "section_6_3_1_breakdown.csv")
    save_json(all_results, out_dir / "section_6_3_1_breakdown.json")

    print("Generated:")
    print(out_dir / "section_6_3_1_breakdown.csv")
    print(out_dir / "section_6_3_1_breakdown.json")


if __name__ == "__main__":
    main()