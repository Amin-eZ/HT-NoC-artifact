#!/usr/bin/env bash
set -e

echo "Running FC layers Section 6.2.2 experiments..."
python3 src/experiments/run_section_6_2_2_fc.py
echo "Generating plots..."
python3 src/plotting/plot_section_6_2_2_fc.py
echo "Done. Outputs in ./outputs/section_6_2_2"