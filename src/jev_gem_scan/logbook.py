"""
Logging — append every scored launch as one JSON line to gem_scan_log.jsonl.

Shadow mode exists so this log can be reviewed by a human before anyone trusts
active mode. The log is append-only; delete the file to reset.
"""

import json
import os
from datetime import datetime, timezone

from .router import REPO_ROOT

LOG_PATH = os.path.join(REPO_ROOT, "gem_scan_log.jsonl")


def log_scan(features, result, mode, path=LOG_PATH):
    """Append one JSON-line record. No-op when the launch was bypassed."""
    if result is None:
        return
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": features["symbol"],
        "features": features,
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "reason": result["reason"],
        "latency_ms": result["latency_ms"],
        "cost_usd": result["cost_usd"],
        "mode": mode,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
