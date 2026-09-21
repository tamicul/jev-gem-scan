# Architecture

Jev Gem Scan is four small pieces wired in a straight line. Nothing loops back
to a chain, an exchange, a wallet, or a network socket.

```
                +------------------+
                |  1. GENERATOR    |   fake "new token launch" events
                |  generator.py    |   (seeded PRNG -> reproducible)
                +---------+--------+
                          | features dict
                          v
        +-----------------------------------+
        |  3. ROUTER / POLICY GATE          |   reads config.yaml
        |  router.py  (jev_gem_router)      |
        |                                   |
        |  enabled:false / bypass_jev:true  |--> bypass (no Jev call)
        |  mode:shadow                      |--> score + log, never surface
        |  mode:active                      |--> score, alert if GEM > thresh
        +-----------------+-----------------+
                          | (unless bypassed)
                          v
                +------------------+
                |  2. JEV STUB     |   weighted rule-based scorer
                |  jev_stub.py     |   fabricated latency + cost
                |  call_jev_api()  |   // swap for real API when available
                +---------+--------+
                          | result dict
                          v
              +----------------------+       +---------------------+
              |  4. CLI              |-----> |  5. LOGGING         |
              |  cli.py              |       |  logbook.py         |
              |  print one line/each |       |  gem_scan_log.jsonl |
              |  + final summary     |       |  (append-only)      |
              +----------------------+       +---------------------+
```

## The "Grok Bot" boundary

In the framing of this project, **Jev** (TypeSafe) is the fast decision model
and **Grok Bot** is a downstream trading bot that would consume verdicts. The
router is the seam between them:

> "a new launch appeared"  →  **router**  →  "an action happens"

In this MVP the only "action" is a printed/logged alert line. There is **no**
trading integration, on purpose. The router is where you would later gate a
real bot — and shadow mode is how you'd validate the model's verdicts against a
human review of `gem_scan_log.jsonl` *before* ever letting `mode: active` touch
anything downstream.

## Why the Jev call is a stub

There is no public TypeSafe Jev decision-model API to call, so
`call_jev_api()` is a clearly labeled deterministic stand-in. Every place it
appears carries the marker:

```python
# swap this for a real Jev/TypeSafe API call when available.
```

Swapping in a real model means replacing that one function's body with an HTTP
call and mapping the response onto the same `{verdict, confidence, reason,
latency_ms, cost_usd}` shape. Nothing else in the pipeline needs to change.
