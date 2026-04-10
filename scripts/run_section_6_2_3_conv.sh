#!/usr/bin/env bash
set -e

echo "Running CONV layers Section 6.2.3 experiments..."
python3 src/experiments/run_section_6_2_3_conv.py
echo "Generating plots..."
python3 src/plotting/plot_section_6_2_3_conv.py
echo "Done. Outputs in ./outputs/section_6_2_3"