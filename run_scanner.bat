@echo off
setlocal
cd /d "%~dp0"
if not exist data mkdir data
set "PYTHONPATH=%CD%\src"
echo Starting Jev Gem Scan...
echo Dashboard will be available at http://127.0.0.1:8787
python -m jev_gem_scan.service --chain solana --mode shadow
if errorlevel 1 (
  echo.
  echo Scanner stopped with an error. Make sure Python 3.10+ is installed and available as python.
  pause
)
