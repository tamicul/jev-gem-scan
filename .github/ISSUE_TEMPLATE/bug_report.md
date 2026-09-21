---
name: Bug report
about: Something in the demo behaves incorrectly
title: "[bug] "
labels: bug
---

**What happened**
A clear, concise description of the bug.

**Reproduce**
Exact command, including `--seed` (runs are deterministic):

```
PYTHONPATH=src python3 -m jev_gem_scan --launches 12 --seed 1 --mode shadow
```

**Expected**
What you expected instead.

**Environment**
- OS:
- Python version (`python3 --version`):
- Commit / release:

**Note**
This project is an educational demo — it makes no network calls and places no
trades. Please do not file issues asking for real trading, wallet, or exchange
integration; that is explicitly out of scope.
