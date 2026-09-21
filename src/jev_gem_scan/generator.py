"""
Mock data generator.

Fabricates fake "new token launch" events. Everything here is synthetic —
these tokens do not exist and no market data is fetched from anywhere.
"""

_TICKERS = ["ZAPX", "MOON", "DOGE2", "PEPE9", "GIGA", "FLOKI", "WOJAK", "TURBO",
            "SNEK", "BONK", "HODL", "REKT", "LAMBO", "CHAD", "NPC", "BASED",
            "PEPINU", "KIBAX", "NOVA", "GHOST7", "ATLAS9", "RUGBUSTER"]


def generate_launch(rng):
    """
    Fabricate one fake 'new token launch' event using the given PRNG
    (a `random.Random` instance, so runs are reproducible per --seed).

    Fields
    ------
    symbol               str    e.g. "$ZAPX882"
    liquidity_lock_days  int    0-400   (how long LP is locked)
    top10_holder_pct     float  0-100   (concentration in top 10 wallets)
    dev_wallet_pct       float  0-100   (share held by the deployer)
    contract_renounced   bool           (ownership renounced?)
    honeypot_flag        bool           (can't-sell trap detected?)
    social_age_days      int    0-200   (age of the project's socials)
    """
    return {
        "symbol": "$" + rng.choice(_TICKERS) + str(rng.randint(0, 999)),
        "liquidity_lock_days": rng.randint(0, 400),
        "top10_holder_pct": round(rng.uniform(0, 100), 1),
        "dev_wallet_pct": round(rng.uniform(0, 100), 1),
        "contract_renounced": rng.random() < 0.5,
        "honeypot_flag": rng.random() < 0.15,
        "social_age_days": rng.randint(0, 200),
    }
