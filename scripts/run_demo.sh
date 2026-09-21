#!/usr/bin/env bash
# Convenience wrapper: run the shadow demo then the active demo, seed 1.
# From the repo root:  ./scripts/run_demo.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/src"

echo "===== SHADOW (default) ====="
python3 -m jev_gem_scan --launches 12 --seed 1 --mode shadow

echo
echo "===== ACTIVE ====="
python3 -m jev_gem_scan --launches 12 --seed 1 --mode active
