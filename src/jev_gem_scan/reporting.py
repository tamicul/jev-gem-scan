"""Human-readable monitoring output for scanner decisions."""

def decision_view(features, result, action):
    """Return a serializable dashboard-style record without changing the decision."""
    return {
        "token": {
            "symbol": features.get("symbol"),
            "name": features.get("name"),
            "chain": features.get("chain_id"),
            "address": features.get("token_address"),
            "pair": features.get("pair_address"),
            "dex": features.get("dex_id"),
        },
        "decision": {
            "verdict": result.get("verdict"),
            "confidence": result.get("confidence"),
            "score": result.get("score"),
            "action": action,
            "reason": result.get("reason"),
            "known_signal_groups": result.get("known_signal_groups"),
        },
        "market": {
            "price_usd": features.get("price_usd"),
            "liquidity_usd": features.get("liquidity_usd"),
            "market_cap": features.get("market_cap"),
            "fdv": features.get("fdv"),
            "volume_h1": features.get("volume_h1"),
            "volume_h24": features.get("volume_h24"),
            "buys_h1": features.get("buys_h1"),
            "sells_h1": features.get("sells_h1"),
            "price_change_h1": features.get("price_change_h1"),
            "pair_age_minutes": features.get("pair_age_minutes"),
        },
        "security": {
            "mint_authority": features.get("mint_authority"),
            "freeze_authority": features.get("freeze_authority"),
            "mint_authority_revoked": features.get("contract_renounced"),
            "dev_wallet_pct": features.get("dev_wallet_pct"),
            "largest_holder_pct": features.get("largest_holder_pct"),
            "top10_holder_pct": features.get("top10_holder_pct"),
            "honeypot_flag": features.get("honeypot_flag"),
            "liquidity_lock_days": features.get("liquidity_lock_days"),
        },
        "evidence": result.get("evidence") or [],
    }


def format_decision(features, result, action):
    view = decision_view(features, result, action)
    t, d, m, s = view["token"], view["decision"], view["market"], view["security"]
    lines = [
        "%s | %s | confidence %.2f | score %s | %s" % (
            t.get("symbol") or "?", d.get("verdict") or "?", d.get("confidence") or 0,
            d.get("score"), d.get("action")),
        "market: price=%s liq=%s mcap=%s vol1h=%s buys/sells=%s/%s age_min=%s" % (
            m.get("price_usd"), m.get("liquidity_usd"), m.get("market_cap"), m.get("volume_h1"),
            m.get("buys_h1"), m.get("sells_h1"), m.get("pair_age_minutes")),
        "security: dev%%=%s top10%%=%s largest%%=%s mint_revoked=%s freeze=%s" % (
            s.get("dev_wallet_pct"), s.get("top10_holder_pct"), s.get("largest_holder_pct"),
            s.get("mint_authority_revoked"), bool(s.get("freeze_authority")) if s.get("freeze_authority") is not None else None),
        "reason: %s" % (d.get("reason") or "")
    ]
    return "\n".join(lines)
