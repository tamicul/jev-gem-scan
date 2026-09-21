# Modes & the kill switch

Config lives in `config.yaml` (copy it from `config.example.yaml`). The router
reads four keys:

| key                        | type  | effect                                              |
|----------------------------|-------|-----------------------------------------------------|
| `enabled`                  | bool  | `false` = kill switch, no Jev call at all           |
| `bypass_jev`               | bool  | `true` = kill switch, leaves `enabled` untouched    |
| `mode`                     | str   | `shadow` or `active`                                |
| `gem_confidence_threshold` | float | active mode: GEM must strictly exceed this to alert |

`--mode shadow|active` on the CLI overrides `mode` for a single run.

## `bypass` — the kill switch

`enabled: false` **or** `bypass_jev: true` short-circuits everything: each
launch is passed straight through with **no Jev call**, printed as
`[bypass] $SYM -> (kill switch: no Jev call)`, and **nothing is logged**. Use
this to instantly stop the model from being consulted at all.

## `shadow` — the default, and the safety net

Score every launch, **log every launch**, but **never surface an alert**.
Shadow mode records what *would* have happened so a human can read
`gem_scan_log.jsonl` and decide whether the verdicts are trustworthy. **This is
the whole point of the tool.** Ship in shadow; stay in shadow until the log
convinces you.

```
[shadow] $GIGA582 -> GEM (0.92, lock=391d, top10=6%, social=97d) 414ms $0.00024
```

## `active` — surface only high-confidence GEMs

Score every launch, log every launch, but only **surface an alert** for `GEM`
verdicts whose confidence is strictly above `gem_confidence_threshold`
(default `0.85`). Everything else is scored and logged but printed as
`(suppressed)`.

```
[ALERT]  $GIGA582 -> GEM (0.92, ...)          <- cleared the gate
[active] (suppressed) $PEPE9923 -> GEM (0.72, ...)   <- logged, not surfaced
```

Even in active mode, an "alert" is just a printed line. **No order, transfer,
or trade is ever placed by this project.**
