# Convenience wrapper (Windows PowerShell): shadow demo then active demo, seed 1.
# From the repo root:  .\scripts\run_demo.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "src"

Write-Host "===== SHADOW (default) ====="
python -m jev_gem_scan --launches 12 --seed 1 --mode shadow

Write-Host ""
Write-Host "===== ACTIVE ====="
python -m jev_gem_scan --launches 12 --seed 1 --mode active
