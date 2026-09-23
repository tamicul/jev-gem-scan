# Jev Gem Scan v2 — production scanner branch

This branch turns the original offline MVP into a live scanner **without changing the protocol authority**:

`discovery -> feature snapshot -> Jev decision -> router policy -> persistence/output`

Jev remains the component that decides `GEM` or `RUG`. The router only decides what to do with that verdict (`shadow`, `alert`, `suppress`, `bypass`). Unknown facts are stored as unknown; the live provider never invents contract-security data.

## Quick start

Python 3.10+; no third-party packages are required.

```bash
python -m jev_gem_scan --source sim --launches 20 --mode shadow
python -m jev_gem_scan --source live --chain solana --limit 30 --mode shadow
python -m jev_gem_scan --source live --chain solana --watch --interval 30 --mode active
```

Run from the repository with `PYTHONPATH=src` if the package is not installed:

```bash
PYTHONPATH=src python -m jev_gem_scan --source live --chain solana --limit 20
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m jev_gem_scan --source live --chain solana --limit 20
```

## What is live now

The live provider uses DexScreener public endpoints for latest token-profile discovery and pair enrichment. It captures chain/token/pair identity, price, liquidity, FDV/market cap when available, 1h/24h volume, 1h/24h price change, recent buys/sells, DEX and pair age.

Every scored live observation is written to `data/gem_scan.db` (SQLite/WAL) as an immutable feature snapshot plus the exact Jev result and router action. Duplicate rescans are suppressed for 15 minutes by default; this affects collection only, never Jev's verdict.

## Known-vs-unknown rule

DexScreener does not authoritatively provide every original security feature (honeypot status, LP lock duration, top-holder %, developer %, renouncement, social age). Those fields are `None` until a dedicated chain/security provider supplies them. The decision engine ignores unknown facts rather than treating missing data as safe or dangerous.

The original simulator still supplies all original fields, so it remains a reproducible protocol regression mode.

## Decision protocol

The local Jev-compatible engine preserves the original weighted signals and adds live market observations as additional evidence. It returns verdict, confidence, reason, raw score, known-signal count, measured local latency, zero API cost, and engine identifier. There is no downstream veto model.

In `shadow`, every decision is recorded but not alerted. In `active`, the existing router behavior remains: only a GEM above `gem_confidence_threshold` becomes an alert. Everything else is still scored and recorded.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Safety / scope

This scanner performs discovery, classification, monitoring and research logging. It does not hold keys, connect a wallet, sign transactions, or place trades. Scanner outputs are signals, not guarantees of token safety or future returns.

## Next provider expansion

The provider boundary is intentionally modular (`src/jev_gem_scan/providers/`). Chain-native security/holder providers can fill currently unknown fields without inserting another decision gate between Jev and the router.
