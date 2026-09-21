---
name: jev-gem-scan
description: Run the Jev Gem Scan educational demo — stream simulated token launches through the shadow/active router and score each GEM or RUG with the mocked TypeSafe Jev decision model. Use when the user asks to run a gem scan, demo the Jev router, or show shadow vs active mode. Never places real trades.
---

# Jev Gem Scan (demo skill)

A thin wrapper around the CLI in this repo. It runs a **simulation only** — no
chain, no wallet, no exchange, no real API. The "Jev" call is a mocked stub.

## Run it

From the repo root (with `PYTHONPATH=src`):

```bash
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1 --mode shadow
```

- `--mode shadow` (default): score + log every launch, surface nothing.
- `--mode active`: surface only GEM verdicts above the confidence threshold.
- `--seed N`: reproducible run.
- `--launches N`: how many simulated launches to stream.

## What to tell the user

1. Default is **shadow** — it only records to `gem_scan_log.jsonl`.
2. Flip to **active** to see the alert gate, but even then it just prints a
   line: it does **not** trade.
3. The verdicts come from a rule-based **stub**, not a real decision model.

## Do NOT

- Do not present `media/jev_gem_scan_1.html` as a live demo — it is a stylized
  work visualization.
- Do not wire this into any real trading, wallet, or payment tool.
