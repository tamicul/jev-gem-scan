"""Solana native enrichment using standard JSON-RPC only.

No API key is required by default. Set SOLANA_RPC_URL to use a private/high-rate
endpoint. Failures leave fields unknown; they never fabricate safety facts.
"""
import json, os, urllib.request

DEFAULT_RPC = "https://api.mainnet-beta.solana.com"


def _post(method, params, timeout=12):
    url = os.environ.get("SOLANA_RPC_URL", DEFAULT_RPC)
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type":"application/json","User-Agent":"jev-gem-scan/2"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        obj = json.loads(r.read().decode())
    if obj.get("error"):
        raise RuntimeError(obj["error"])
    return obj.get("result")


def enrich_solana(features):
    """Return a copy enriched with mint authority, supply and holder concentration."""
    out = dict(features)
    mint = out.get("token_address")
    if not mint or out.get("chain_id") != "solana":
        return out
    out.setdefault("solana_rpc_ok", False)
    try:
        info = _post("getAccountInfo", [mint, {"encoding":"jsonParsed","commitment":"confirmed"}])
        value = (info or {}).get("value") or {}
        parsed = ((value.get("data") or {}).get("parsed") or {}).get("info") or {}
        if parsed:
            out["mint_authority"] = parsed.get("mintAuthority")
            out["freeze_authority"] = parsed.get("freezeAuthority")
            out["contract_renounced"] = parsed.get("mintAuthority") is None
            out["decimals"] = parsed.get("decimals")
            supply_raw = parsed.get("supply")
            if supply_raw is not None and out.get("decimals") is not None:
                out["token_supply"] = int(supply_raw) / (10 ** int(out["decimals"]))
        largest = _post("getTokenLargestAccounts", [mint, {"commitment":"confirmed"}])
        accounts = (largest or {}).get("value") or []
        supply = out.get("token_supply")
        if supply and accounts:
            balances = []
            for a in accounts:
                try: balances.append(float(a.get("uiAmountString") or 0))
                except (TypeError, ValueError): pass
            out["top10_holder_pct"] = round(sum(balances[:10]) / supply * 100.0, 4)
            out["top20_holder_pct"] = round(sum(balances[:20]) / supply * 100.0, 4)
            out["largest_holder_pct"] = round((balances[0] / supply * 100.0), 4) if balances else None
            out["largest_accounts_observed"] = len(balances)
        out["solana_rpc_ok"] = True
    except Exception as exc:
        out["solana_rpc_error"] = str(exc)[:300]
    return out
