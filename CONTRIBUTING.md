# Contributing

Thanks for taking a look. Jev Gem Scan is a small **educational demo**, and
contributions should keep it that way: readable end-to-end, standard library
only, deterministic, and — above all — incapable of touching real money.

## Ground rules

1. **No real trading, ever.** No order execution, transfers, swaps, wallets,
   private keys, or exchange/on-chain integration. PRs that add any of these
   will be closed. The only "action" this project takes is printing/logging a
   line.
2. **No network calls and no new dependencies.** Keep it to the Python 3.8+
   standard library. `requirements.txt` stays empty of packages.
3. **Keep the Jev call a labeled stub.** `call_jev_api()` must stay a mocked
   stand-in and keep its `# swap this for a real Jev/TypeSafe API call when
   available.` marker.
4. **Stay deterministic.** Anything random must flow through the seeded
   `random.Random(seed)` stream so `--seed` keeps runs reproducible.

## Dev setup

```bash
git clone <your-fork>
cd jev
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1 --mode shadow
```

There are no build steps. To regenerate the example transcripts:

```bash
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1 --mode shadow --no-log > examples/shadow_run.txt
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1 --mode active --no-log > examples/active_run.txt
```

## Style

- Match the surrounding code: small modules, docstrings, plain functions.
- One logical change per PR; describe what a reviewer should run to see it.

## Reporting issues

Use the templates in `.github/ISSUE_TEMPLATE/`. Include the exact command and
`--seed`, since runs are reproducible.
