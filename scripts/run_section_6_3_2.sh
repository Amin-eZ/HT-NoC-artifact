#!/usr/bin/env bash
set -e

echo "Running Section 6.3.2 experiments..."
python3 src/experiments/run_section_6_3_2.py
echo "Generating plots..."
python3 src/plotting/plot_section_6_3_2.py
echo "Done. Outputs in ./outputs/section_6_3_2"