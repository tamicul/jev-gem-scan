"""Local Jev-compatible decision engine.

Jev remains the sole GEM/RUG authority. Provider observations are evidence only.
Unknown facts stay neutral and are never converted to safe defaults.
"""
import time
GEM_CONFIDENCE_THRESHOLD = 0.85


def _add(reasons, evidence, label, value, delta):
    evidence.append({"signal": label, "value": value, "delta": round(delta, 3)})
    if delta:
        reasons.append("%s=%s" % (label, value))
    return delta


def call_jev_api(f, rng):
    started = time.perf_counter()
    score = 0.0
    reasons, evidence = [], []
    known = 0

    # Original protocol signals.
    hp = f.get("honeypot_flag")
    dev = f.get("dev_wallet_pct")
    top = f.get("top10_holder_pct")
    lock = f.get("liquidity_lock_days")
    ren = f.get("contract_renounced")
    social = f.get("social_age_days")

    if hp is not None:
        known += 1
        score += _add(reasons, evidence, "honeypot", bool(hp), -1.2 if hp else 0.15)
    if dev is not None:
        known += 1
        d = -0.9 if dev > 15 else (0.25 if dev <= 5 else 0.0)
        score += _add(reasons, evidence, "dev_wallet_pct", round(dev, 2), d)
    if top is not None:
        known += 1
        d = -0.7 if top > 40 else (0.5 if top < 20 else 0.0)
        score += _add(reasons, evidence, "top10_holder_pct", round(top, 2), d)
    if lock is not None:
        known += 1
        d = -0.6 if lock < 30 else (0.8 if lock >= 180 else 0.0)
        score += _add(reasons, evidence, "liquidity_lock_days", lock, d)
    if ren is not None:
        known += 1
        score += _add(reasons, evidence, "mint_authority_revoked", bool(ren), 0.5 if ren else -0.2)
    if social is not None:
        known += 1
        score += _add(reasons, evidence, "social_age_days", social, 0.4 if social > 90 else 0.0)

    # Live market / pool evidence.
    liq = f.get("liquidity_usd")
    vol = f.get("volume_h1")
    buys, sells = f.get("buys_h1"), f.get("sells_h1")
    liq_ratio = f.get("liquidity_to_valuation_ratio")
    turnover = f.get("volume_to_liquidity_h1")
    pair_age = f.get("pair_age_minutes")
    p1 = f.get("price_change_h1")

    if liq is not None:
        known += 1
        d = 0.25 if liq >= 100000 else (-0.35 if liq < 5000 else 0.0)
        score += _add(reasons, evidence, "liquidity_usd", round(liq, 2), d)
    if vol is not None:
        known += 1
        score += _add(reasons, evidence, "volume_h1", round(vol, 2), 0.20 if vol >= 50000 else 0.0)
    if buys is not None and sells is not None:
        known += 1
        d = 0.20 if buys >= 20 and buys > sells * 1.5 else (-0.25 if sells >= 20 and sells > buys * 2 else 0.0)
        score += _add(reasons, evidence, "buy_sell_h1", "%s/%s" % (buys, sells), d)
    if liq_ratio is not None:
        known += 1
        d = -0.30 if liq_ratio < 0.01 else (0.20 if liq_ratio >= 0.08 else 0.0)
        score += _add(reasons, evidence, "liquidity_valuation_ratio", round(liq_ratio, 4), d)
    if turnover is not None:
        known += 1
        d = 0.15 if 0.25 <= turnover <= 5 else (-0.15 if turnover > 20 else 0.0)
        score += _add(reasons, evidence, "turnover_h1", round(turnover, 3), d)
    if pair_age is not None:
        known += 1
        # Very new is informative, not automatically bad. Mature observed liquidity gets modest credit.
        d = 0.10 if pair_age >= 1440 else 0.0
        score += _add(reasons, evidence, "pair_age_min", round(pair_age, 1), d)
    if p1 is not None:
        known += 1
        d = -0.20 if p1 <= -40 else (0.10 if 5 <= p1 <= 80 else 0.0)
        score += _add(reasons, evidence, "price_change_h1", round(p1, 2), d)

    # Solana-native security/holder evidence. These are observations, never vetoes.
    freeze = f.get("freeze_authority")
    largest = f.get("largest_holder_pct")
    if freeze is not None:
        known += 1
        score += _add(reasons, evidence, "freeze_authority_active", bool(freeze), -0.35 if freeze else 0.15)
    if largest is not None:
        known += 1
        d = -0.45 if largest > 30 else (0.15 if largest < 10 else 0.0)
        score += _add(reasons, evidence, "largest_holder_pct", round(largest, 2), d)

    verdict = "GEM" if score >= 0 else "RUG"
    confidence = round(min(0.99, 0.5 + min(abs(score), 2.5) / 2.5 * 0.49), 2)
    positive = round(sum(max(0, e["delta"]) for e in evidence), 3)
    negative = round(sum(min(0, e["delta"]) for e in evidence), 3)
    return {
        "verdict": verdict,
        "confidence": confidence,
        "reason": ", ".join(reasons) if reasons else "no strong known signals",
        "score": round(score, 3),
        "positive_evidence": positive,
        "negative_evidence": negative,
        "known_signal_groups": known,
        "evidence": evidence,
        "latency_ms": max(1, int((time.perf_counter() - started) * 1000)),
        "cost_usd": 0.0,
        "engine": "local-jev-compatible-v3"
    }
