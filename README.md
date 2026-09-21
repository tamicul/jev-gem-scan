<!-- JEV + GEM SCAN -->
<h1 align="center">💎 JEV &nbsp;<code>+</code>&nbsp; GEM SCAN</h1>

<p align="center">
  <b>Score new token launches <code>GEM</code> or <code>RUG</code> before you open a chart.</b><br>
  A tiny, offline, <b>educational</b> router that streams simulated launches through a
  mocked <b>TypeSafe Jev</b> decision model — into <b>Grok Bot</b>.
</p>

<p align="center">
  <img alt="mode: shadow default" src="https://img.shields.io/badge/mode-shadow%20(default)-1fdd7a?style=flat-square">
  <img alt="python 3.8+" src="https://img.shields.io/badge/python-3.8%2B-0a0a0a?style=flat-square">
  <img alt="deps: none" src="https://img.shields.io/badge/runtime%20deps-none-ff2fa0?style=flat-square">
  <img alt="license MIT" src="https://img.shields.io/badge/license-MIT-ffc93b?style=flat-square">
  <img alt="no real trades" src="https://img.shields.io/badge/real%20trades-never-ff3b3b?style=flat-square">
</p>

---

> ## ⚠️ Read this first
> This is a **DEMO / EDUCATIONAL MVP**, not a production trading system and **not
> financial advice**. It runs entirely offline: **no real wallet, no real
> execution, no real API keys, no network calls of any kind.** The "Jev" call is a
> **mocked stand-in** — a rule-based stub — for a real decision-model API that
> does not ship here. The only "action" the tool ever takes is **printing and
> logging a line.** It never places an order, transfer, or trade.

---

## What it does

`jev_gem_scan` simulates the moment a fresh token launch hits a chain and asks a
fast decision model — **Jev** — a single question: *gem, or rug?* A **policy
gate** (`jev_gem_router`) sits between "a launch appeared" and "an action
happens" and decides, per your config, whether that verdict should ever be
surfaced.

It ships **in shadow mode**: it scores and logs everything but surfaces nothing,
so a human can review the log before trusting the model. Flip to **active** and
it will surface only high-confidence `GEM` verdicts — still just as printed
lines.

```
[shadow] $GIGA582 -> GEM (0.92, lock=391d, top10=6%, social=97d) 414ms $0.00024
[ALERT]  $GIGA582 -> GEM (0.92, lock=391d, top10=6%, social=97d) 414ms $0.00024
```

## The visualization

The [`media/`](media/) folder holds [`jev_gem_scan_1.html`](media/jev_gem_scan_1.html) —
the pink/black halftone **JEV + GEM SCAN** HUD. It is a **work visualization, not
a demo**: a stylized concept render of what a Jev desk *could* look like, with
hard-coded feed/chat/latency loops. It does **not** run the scanner and is **not**
a recording of real activity. The real tool's output is the plain text above.
See [`media/README.md`](media/README.md).

## Quick start

No install, no dependencies — just Python 3.8+.

```bash
git clone <this-repo>
cd jev

# default: SHADOW mode (scores + logs, surfaces nothing)
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1

# ACTIVE mode (surfaces only high-confidence GEM alerts)
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1 --mode active
```

Or use the wrappers:

```bash
./scripts/run_demo.sh        # macOS / Linux
.\scripts\run_demo.ps1       # Windows PowerShell
```

Runs are **deterministic** for a given `--seed`, so a demo is reproducible.

## Example output

Both captured in [`examples/`](examples/) ([shadow](examples/shadow_run.txt) ·
[active](examples/active_run.txt)).

<details open>
<summary><b>shadow</b> — score + log everything, surface nothing</summary>

```
== Jev Gem Scan v1.0.0 (DEMO - mocked decision model, no real trades) ==
mode=shadow enabled=True bypass_jev=False seed=1

[shadow] $GIGA582 -> GEM (0.92, lock=391d, top10=6%, social=97d) 414ms $0.00024
[shadow] $ZAPX540 -> RUG (0.79, dev_wallet=94%, top10=76%, social=173d) 424ms $0.00050
[shadow] $BONK948 -> RUG (0.99, honeypot=true, dev_wallet=92%, top10=42%, lock=11d, social=161d) 503ms $0.00025
...
-- summary --
scanned: 12   GEM: 5   RUG: 7   avg confidence: 0.788   avg latency: 513 ms   total sim cost: $0.00451
```
</details>

<details>
<summary><b>active</b> — surface only GEM above the confidence gate</summary>

```
== Jev Gem Scan v1.0.0 (DEMO - mocked decision model, no real trades) ==
mode=active enabled=True bypass_jev=False seed=1

[ALERT]  $GIGA582 -> GEM (0.92, lock=391d, top10=6%, social=97d) 414ms $0.00024
[active] (suppressed) $PEPE9923 -> GEM (0.72, top10=3%, social=97d) 421ms $0.00059
[active] (suppressed) $ZAPX540 -> RUG (0.79, dev_wallet=94%, top10=76%, social=173d) 424ms $0.00050
...
-- summary --
scanned: 12   GEM: 5   RUG: 7   alerts fired: 1   avg confidence: 0.788 ...
```
</details>

## How the score works (the stub)

There is no public TypeSafe Jev API, so
[`call_jev_api()`](src/jev_gem_scan/jev_stub.py) is a **clearly labeled stub**: a
weighted rule-based scorer over seven mock signals, with fabricated latency
(200–900 ms) and cost ($0.0002–$0.0006) to demo the UX.

| pushes toward `RUG`               | pushes toward `GEM`                 |
|-----------------------------------|-------------------------------------|
| honeypot flag                     | liquidity locked ≥ 180 days         |
| dev wallet > 15%                  | contract renounced                  |
| top-10 holders > 40%              | top-10 holders < 20%                |
| liquidity unlocked (< 30 days)    | socials older than 90 days          |

```python
# swap this for a real Jev/TypeSafe API call when available.
```

Swapping in a real model means replacing that one function body with an HTTP
call and mapping the response onto the same
`{verdict, confidence, reason, latency_ms, cost_usd}` shape. Nothing else
changes. See [`docs/architecture.md`](docs/architecture.md).

## Modes & the kill switch

Config is [`config.example.yaml`](config.example.yaml) → copy to `config.yaml`.

| setting                          | behavior                                                         |
|----------------------------------|-----------------------------------------------------------------|
| `enabled: false` / `bypass_jev: true` | **kill switch** — pass launches through, no Jev call at all |
| `mode: shadow` *(default)*       | call Jev, log the verdict, **never** surface an alert           |
| `mode: active`                   | call Jev, surface an alert only for `GEM` confidence > `0.85`   |

`--mode shadow|active` overrides config for one run. Full detail in
[`docs/modes.md`](docs/modes.md).

## Logging

Every scored launch is appended as one JSON line to `gem_scan_log.jsonl`:

```json
{"timestamp":"...","symbol":"$GIGA582","features":{...},"verdict":"GEM",
 "confidence":0.92,"reason":"lock=391d, top10=6%, social=97d",
 "latency_ms":414,"cost_usd":0.00024,"mode":"shadow"}
```

**That log is the point of shadow mode** — review it before you ever trust
`mode: active`. It's git-ignored; delete the file to reset.

## Project layout

```
jev/
├── src/jev_gem_scan/      # the package
│   ├── generator.py       #  1. mock launch generator (seeded)
│   ├── jev_stub.py        #  2. call_jev_api()  <- the mocked decision model
│   ├── router.py          #  3. jev_gem_router  <- policy gate + config
│   ├── logbook.py         #  5. JSONL logging
│   └── cli.py             #  4. CLI entrypoint
├── docs/                  # architecture.md, modes.md
├── examples/              # captured shadow_run.txt / active_run.txt
├── media/                 # the HUD work visualization (NOT a demo)
├── scripts/               # run_demo.sh / run_demo.ps1
├── skill/                 # optional agent skill wrapper
├── config.example.yaml
└── requirements.txt       # empty on purpose — stdlib only
```

## CLI reference

```
python3 -m jev_gem_scan [options]

  --launches N     how many launches to simulate      (default 20)
  --seed N         PRNG seed for reproducible runs     (default 1)
  --mode M         shadow | active (overrides config)
  --config PATH    path to a config.yaml
  --sleep S        seconds between launches            (default 0.15)
  --no-log         do not append to gem_scan_log.jsonl
  --version
```

## Scope & safety (non-negotiable)

- ❌ No real trading, order execution, transfers, or swaps.
- ❌ No wallet, private keys, exchange, or on-chain integration.
- ❌ No network calls, no API keys, no third-party dependencies.
- ✅ Deterministic, offline, standard-library-only, readable end to end.

The tables and verdicts here are entirely synthetic. **Nothing in this repo
should be used to make real trading decisions.**

## License

[MIT](LICENSE) © 2026 st1ne. `JEV v1.0 · HIGHER INTELLIGENCE. LOWER COST.` is
flavor text for the demo, not a product claim.
