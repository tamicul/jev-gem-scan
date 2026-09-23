"""Pool/liquidity intelligence derived from live market observations.

This module enriches evidence only. It never returns a GEM/RUG verdict and
never blocks a Jev decision. Unknown data remains None.
"""
import math


def _f(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def enrich_pool(features):
    out = dict(features)
    liq = _f(out.get("liquidity_usd"))
    mc = _f(out.get("market_cap"))
    fdv = _f(out.get("fdv"))
    v1 = _f(out.get("volume_h1"))
    v24 = _f(out.get("volume_h24"))
    buys = int(out.get("buys_h1") or 0)
    sells = int(out.get("sells_h1") or 0)
    age = _f(out.get("pair_age_minutes"))

    denom = mc if mc and mc > 0 else (fdv if fdv and fdv > 0 else None)
    out["liquidity_to_valuation_pct"] = round(liq / denom * 100.0, 4) if liq is not None and denom else None
    out["volume_h1_to_liquidity"] = round(v1 / liq, 4) if v1 is not None and liq and liq > 0 else None
    out["volume_h24_to_liquidity"] = round(v24 / liq, 4) if v24 is not None and liq and liq > 0 else None
    out["buy_sell_ratio_h1"] = round(buys / sells, 4) if sells > 0 else (None if buys == 0 else float("inf"))
    out["transactions_h1"] = buys + sells
    out["buy_share_h1"] = round(buys / (buys + sells), 4) if buys + sells else None
    out["pair_age_hours"] = round(age / 60.0, 4) if age is not None else None

    # Observational flags are deliberately non-authoritative and do not imply safety.
    out["liquidity_observed"] = liq is not None
    out["liquidity_depth_band"] = (
        "unknown" if liq is None else
        "very_low" if liq < 10000 else
        "low" if liq < 50000 else
        "moderate" if liq < 250000 else
        "deep"
    )
    return out
