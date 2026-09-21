# media/

## `jev_gem_scan_1.html` — a work visualization, **not** a demo

This file is a **stylized concept render** (a "work visualization") of what a
Jev-powered scanning desk *could look like* — the pink/black halftone
"JEV + GEM SCAN" HUD, a live token feed, a chat-with-Jev panel, and a decision
bar showing latency/cost.

It is **art, not the application**:

- The tokens, verdicts, chat messages, latencies and costs in the HTML are
  **hard-coded loops** for visual effect. Nothing in it calls the scanner.
- It does **not** connect to any chain, exchange, wallet, or API.
- It is **not** a screen recording of the real tool and should never be
  presented as a product demo, live dashboard, or proof of performance.

The actual, runnable tool is the CLI in [`../src/jev_gem_scan/`](../src/jev_gem_scan/).
Its real output is plain text — see [`../examples/`](../examples/).

Open the visualization locally in a browser:

```bash
# from the repo root
python3 -m http.server 8000
# then visit http://localhost:8000/media/jev_gem_scan_1.html
```

Design tokens (for anyone reskinning a real UI on top of the engine):
`--pink #ff2fa0`, `--black #0a0a0a`, `--green #1fdd7a` (GEM),
`--red #ff3b3b` (RUG), `--amber #ffc93b`.
