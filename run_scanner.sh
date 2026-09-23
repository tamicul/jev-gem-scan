#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p data
export PYTHONPATH="$(pwd)/src${PYTHONPATH:+:$PYTHONPATH}"
echo "Starting Jev Gem Scan..."
echo "Dashboard: http://127.0.0.1:8787"
exec python3 -m jev_gem_scan.service --chain solana --mode shadow
