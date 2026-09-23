"""Creator/deployer ownership intelligence for Solana SPL tokens.

This module only measures facts. It never classifies a token. It queries all
SPL token accounts owned by the probable deployer, filtered to the candidate
mint, then expresses that balance as a percentage of current supply.
"""
from .solana_rpc import _post


def enrich_creator_ownership(features):
    out = dict(features)
    if out.get("chain_id") != "solana":
        return out
    owner = out.get("probable_deployer")
    mint = out.get("token_address")
    supply = out.get("token_supply")
    if not owner or not mint or not supply:
        return out
    out.setdefault("creator_ownership_rpc_ok", False)
    try:
        result = _post("getTokenAccountsByOwner", [
            owner,
            {"mint": mint},
            {"encoding": "jsonParsed", "commitment": "confirmed"},
        ])
        values = (result or {}).get("value") or []
        total = 0.0
        accounts = 0
        for row in values:
            info = (((row.get("account") or {}).get("data") or {}).get("parsed") or {}).get("info") or {}
            amount = (info.get("tokenAmount") or {}).get("uiAmountString")
            try:
                total += float(amount or 0)
                accounts += 1
            except (TypeError, ValueError):
                pass
        pct = max(0.0, total / float(supply) * 100.0)
        out["deployer_token_balance"] = total
        out["deployer_token_accounts"] = accounts
        out["dev_wallet_pct"] = round(pct, 4)
        out["creator_ownership_rpc_ok"] = True
    except Exception as exc:
        out["creator_ownership_rpc_error"] = str(exc)[:300]
    return out
