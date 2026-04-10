#!/usr/bin/env bash
set -e

echo "Running PW layers Section 6.2.5 experiments..."
python3 src/experiments/run_section_6_2_5_pw.py
echo "Generating plots..."
python3 src/plotting/plot_section_6_2_5_pw.py
echo "Done. Outputs in ./outputs/section_6_2_5"