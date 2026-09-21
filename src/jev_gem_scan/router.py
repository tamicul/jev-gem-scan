"""
Router / policy gate — "jev_gem_router".

Sits between "a new launch appeared" and "an action happens". In this MVP the
only action is surfacing an alert (a printed/logged line) — there is no real
trading action anywhere.

Config is read from a small YAML file (config.yaml, falling back to
config.example.yaml). Parsing uses a tiny stdlib-only reader for the flat
schema below — no third-party YAML dependency is required.
"""

import os

from .jev_stub import call_jev_api, GEM_CONFIDENCE_THRESHOLD

# repo root = two levels up from this file (src/jev_gem_scan/router.py)
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_PKG_DIR, "..", ".."))

DEFAULTS = {
    "enabled": True,
    "bypass_jev": False,
    "mode": "shadow",
    "gem_confidence_threshold": GEM_CONFIDENCE_THRESHOLD,
}


def _coerce(value):
    """Cast a raw YAML scalar string to bool/int/float/str."""
    v = value.strip().strip('"').strip("'")
    low = v.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _parse_flat_yaml(text):
    """Minimal flat `key: value` YAML reader (comments and blanks ignored)."""
    out = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].rstrip()
        if not line.strip() or ":" not in line:
            continue
        key, _, raw = line.partition(":")
        out[key.strip()] = _coerce(raw)
    return out


def load_config(path=None):
    """
    Load router config. Order of preference:
      explicit `path` -> config.yaml -> config.example.yaml -> DEFAULTS.
    """
    cfg = dict(DEFAULTS)
    candidates = [path] if path else [
        os.path.join(REPO_ROOT, "config.yaml"),
        os.path.join(REPO_ROOT, "config.example.yaml"),
    ]
    for cand in candidates:
        if cand and os.path.exists(cand):
            with open(cand, encoding="utf-8") as f:
                cfg.update(_parse_flat_yaml(f.read()))
            break
    return cfg


def route_launch(features, config, rng):
    """
    Decide what happens to one launch.

    Returns (result_or_None, action) where action is one of:
        'bypass'   kill switch fired, no Jev call at all
        'shadow'   scored + logged, but never surfaced
        'alert'    active mode, high-confidence GEM -> surface it
        'suppress' active mode, did not clear the gate -> stay quiet
    """
    # Kill switch: enabled:false OR bypass_jev:true -> no Jev call.
    if not config.get("enabled", True) or config.get("bypass_jev", False):
        return None, "bypass"

    result = call_jev_api(features, rng)
    mode = config.get("mode", "shadow")

    if mode == "shadow":
        # Record what WOULD have happened; never surface an alert.
        return result, "shadow"

    # active: only surface high-confidence GEM verdicts.
    threshold = config.get("gem_confidence_threshold", GEM_CONFIDENCE_THRESHOLD)
    if result["verdict"] == "GEM" and result["confidence"] > threshold:
        return result, "alert"
    return result, "suppress"
