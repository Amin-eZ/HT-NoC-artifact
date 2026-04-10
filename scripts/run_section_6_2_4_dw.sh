#!/usr/bin/env bash
set -e

echo "Running DW layers Section 6.2.4 experiments..."
python3 src/experiments/run_section_6_2_4_dw.py
echo "Generating plots..."
python3 src/plotting/plot_section_6_2_4_dw.py
echo "Done. Outputs in ./outputs/section_6_2_4"