"""
CLI entrypoint.

    python -m jev_gem_scan --launches 20 --seed 1 --mode shadow
    python -m jev_gem_scan --launches 20 --seed 1 --mode active

Streams N simulated launches through the router one by one, prints one line
per launch, then a summary. Deterministic given --seed. No real trades.
"""

import argparse
import time

from .generator import generate_launch
from .router import route_launch, load_config
from .logbook import log_scan, LOG_PATH
from . import __version__

try:                                   # dedicated RNG so runs are reproducible
    from random import Random
except ImportError:                    # pragma: no cover
    Random = None


def build_parser():
    ap = argparse.ArgumentParser(
        prog="jev_gem_scan",
        description="Jev Gem Scan — DEMO MVP. Scores simulated token launches "
                    "GEM/RUG via a mocked decision model. No real trades.")
    ap.add_argument("--launches", type=int, default=20, help="how many launches to simulate")
    ap.add_argument("--seed", type=int, default=1, help="PRNG seed for reproducible runs")
    ap.add_argument("--mode", choices=["shadow", "active"], help="override config mode")
    ap.add_argument("--config", help="path to a config.yaml (default: repo config)")
    ap.add_argument("--sleep", type=float, default=0.15, help="seconds between launches")
    ap.add_argument("--no-log", action="store_true", help="do not append to gem_scan_log.jsonl")
    ap.add_argument("--version", action="version", version="jev_gem_scan " + __version__)
    return ap


def run(args):
    rng = Random(args.seed)   # one seeded stream drives features AND telemetry

    config = load_config(args.config)
    if args.mode:
        config["mode"] = args.mode
    mode = config.get("mode", "shadow")

    print("== Jev Gem Scan v%s (DEMO - mocked decision model, no real trades) ==" % __version__)
    print("mode=%s enabled=%s bypass_jev=%s seed=%d\n" %
          (mode, config.get("enabled", True), config.get("bypass_jev", False), args.seed))

    gems = rugs = alerts = 0
    conf_sum = lat_sum = cost_sum = 0.0
    scored = 0

    for _ in range(args.launches):
        features = generate_launch(rng)
        result, action = route_launch(features, config, rng)

        if action == "bypass":
            print("[bypass] %s -> (kill switch: no Jev call)" % features["symbol"])
            time.sleep(args.sleep)
            continue

        if not args.no_log:
            log_scan(features, result, mode)

        scored += 1
        conf_sum += result["confidence"]
        lat_sum += result["latency_ms"]
        cost_sum += result["cost_usd"]
        if result["verdict"] == "GEM":
            gems += 1
        else:
            rugs += 1

        line = "%s -> %s (%.2f, %s) %dms $%.5f" % (
            features["symbol"], result["verdict"], result["confidence"],
            result["reason"], result["latency_ms"], result["cost_usd"])

        if action == "shadow":
            print("[shadow] " + line)
        elif action == "alert":
            alerts += 1
            print("[ALERT]  " + line)
        elif action == "suppress":
            print("[active] (suppressed) " + line)

        time.sleep(args.sleep)

    print("\n-- summary --")
    print("scanned:        %d" % scored)
    print("GEM:            %d" % gems)
    print("RUG:            %d" % rugs)
    if mode == "active":
        print("alerts fired:   %d" % alerts)
    print("avg confidence: %.3f" % (conf_sum / scored if scored else 0))
    print("avg latency:    %.0f ms" % (lat_sum / scored if scored else 0))
    print("total sim cost: $%.5f" % cost_sum)
    if scored and not args.no_log:
        print("\nlog appended -> %s" % LOG_PATH)


def main(argv=None):
    run(build_parser().parse_args(argv))


if __name__ == "__main__":
    main()
