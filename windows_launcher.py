"""PyInstaller entry point for the Windows executable."""
import os, sys, webbrowser, threading, time

# When frozen, keep writable scanner data beside the executable.
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

from jev_gem_scan.service import run


def open_dashboard():
    time.sleep(2.0)
    try: webbrowser.open("http://127.0.0.1:8787")
    except Exception: pass

if __name__ == "__main__":
    threading.Thread(target=open_dashboard, daemon=True).start()
    run(db_path="data/gem_scan.db", chain="solana", scan_interval=30,
        outcome_interval=300, limit=30, dedupe_seconds=900,
        host="127.0.0.1", port=8787, mode="shadow")
