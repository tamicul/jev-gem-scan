"""
Decision engine — the "Jev" stand-in.

THIS IS A STUB. There is no real TypeSafe Jev / decision-model API being
called here. `call_jev_api` is a deterministic weighted rule-based scorer over
the mock features, with fabricated latency/cost so the demo UX resembles a
real fast decision-model API call.

    // swap this for a real Jev/TypeSafe API call when available.
"""

GEM_CONFIDENCE_THRESHOLD = 0.85  # active mode only surfaces GEM above this


def call_jev_api(features, rng):
    """
    STUB decision model.

    Parameters
    ----------
    features : dict   one launch from generator.generate_launch
    rng      : random.Random   seeded stream for reproducible telemetry

    Returns
    -------
    dict with keys: verdict ("GEM"|"RUG"), confidence (0-1), reason (str),
                    latency_ms (int), cost_usd (float)

    // swap this for a real Jev/TypeSafe API call when available.
    """
    score = 0.0        # positive => GEM, negative => RUG
    reasons = []

    # ---- RUG signals ----
    if features["honeypot_flag"]:
        score -= 1.2
        reasons.append("honeypot=true")
    if features["dev_wallet_pct"] > 15:
        score -= 0.9
        reasons.append("dev_wallet=%.0f%%" % features["dev_wallet_pct"])
    if features["top10_holder_pct"] > 40:
        score -= 0.7
        reasons.append("top10=%.0f%%" % features["top10_holder_pct"])
    if features["liquidity_lock_days"] < 30:
        score -= 0.6
        reasons.append("lock=%dd" % features["liquidity_lock_days"])

    # ---- GEM signals ----
    if features["liquidity_lock_days"] >= 180:
        score += 0.8
        reasons.append("lock=%dd" % features["liquidity_lock_days"])
    if features["contract_renounced"]:
        score += 0.5
        reasons.append("renounced")
    if features["top10_holder_pct"] < 20:
        score += 0.5
        reasons.append("top10=%.0f%%" % features["top10_holder_pct"])
    if features["social_age_days"] > 90:
        score += 0.4
        reasons.append("social=%dd" % features["social_age_days"])

    verdict = "GEM" if score >= 0 else "RUG"
    # squash |score| into a 0.50-0.99 confidence band
    confidence = round(min(0.99, 0.5 + min(abs(score), 2.0) / 2.0 * 0.49), 2)
    reason = ", ".join(reasons) if reasons else "no strong signals"

    # fabricated telemetry (seeded -> reproducible)
    latency_ms = rng.randint(200, 900)
    cost_usd = round(rng.uniform(0.0002, 0.0006), 5)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
    }
