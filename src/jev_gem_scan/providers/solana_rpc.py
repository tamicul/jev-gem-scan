"""Solana native enrichment using standard JSON-RPC only.

No API key is required by default. Set SOLANA_RPC_URL to use a private/high-rate
endpoint. Failures leave fields unknown; they never fabricate safety facts.
"""
import datetime as dt
import json, os, time, urllib.request

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


def _account_key(entry):
    return entry.get("pubkey") if isinstance(entry, dict) else entry


def _creation_evidence(mint):
    """Best-effort mint history/deployer evidence; returns only observed facts.

    getSignaturesForAddress is reverse chronological. We page toward the oldest
    available signature, then inspect that transaction. Public RPC history can
    be incomplete, so history_complete is explicitly recorded.
    """
    before=None; oldest=None; pages=0; max_pages=max(1,int(os.environ.get("SOLANA_HISTORY_PAGES","3")))
    while pages < max_pages:
        cfg={"limit":1000,"commitment":"confirmed"}
        if before: cfg["before"]=before
        batch=_post("getSignaturesForAddress",[mint,cfg]) or []
        if not batch: break
        pages += 1; oldest=batch[-1]
        if len(batch) < 1000: break
        before=oldest.get("signature")
    if not oldest: return {"mint_history_observed":False}
    out={"mint_history_observed":True,"mint_history_pages":pages,"mint_oldest_signature":oldest.get("signature"),"mint_oldest_slot":oldest.get("slot"),"mint_created_at":oldest.get("blockTime"),"mint_history_complete":len(batch)<1000}
    if oldest.get("blockTime"):
        out["token_age_seconds"]=max(0,int(time.time()-oldest["blockTime"]))
        out["token_age_days"]=round(out["token_age_seconds"]/86400.0,3)
        out["mint_created_at_iso"]=dt.datetime.fromtimestamp(oldest["blockTime"],dt.timezone.utc).isoformat()
    sig=oldest.get("signature")
    if sig:
        tx=_post("getTransaction",[sig,{"encoding":"jsonParsed","commitment":"confirmed","maxSupportedTransactionVersion":0}])
        msg=(((tx or {}).get("transaction") or {}).get("message") or {})
        keys=msg.get("accountKeys") or []
        signers=[_account_key(k) for k in keys if isinstance(k,dict) and k.get("signer")]
        if signers:
            out["creation_signers"]=signers
            out["probable_deployer"]=signers[0]
    return out


def enrich_solana(features):
    """Return a copy enriched with authorities, supply, holders and mint history."""
    out = dict(features); mint = out.get("token_address")
    if not mint or out.get("chain_id") != "solana": return out
    out.setdefault("solana_rpc_ok", False)
    errors=[]
    try:
        info = _post("getAccountInfo", [mint, {"encoding":"jsonParsed","commitment":"confirmed"}])
        value = (info or {}).get("value") or {}; parsed = ((value.get("data") or {}).get("parsed") or {}).get("info") or {}
        if parsed:
            out["mint_authority"] = parsed.get("mintAuthority"); out["freeze_authority"] = parsed.get("freezeAuthority")
            out["contract_renounced"] = parsed.get("mintAuthority") is None; out["freeze_disabled"] = parsed.get("freezeAuthority") is None
            out["decimals"] = parsed.get("decimals"); supply_raw = parsed.get("supply")
            if supply_raw is not None and out.get("decimals") is not None: out["token_supply"] = int(supply_raw)/(10**int(out["decimals"]))
    except Exception as exc: errors.append("account:"+str(exc)[:180])
    try:
        largest = _post("getTokenLargestAccounts", [mint, {"commitment":"confirmed"}]); accounts = (largest or {}).get("value") or []; supply=out.get("token_supply")
        if supply and accounts:
            balances=[]
            for a in accounts:
                try: balances.append(float(a.get("uiAmountString") or 0))
                except (TypeError,ValueError): pass
            out["top10_holder_pct"]=round(sum(balances[:10])/supply*100,4); out["top20_holder_pct"]=round(sum(balances[:20])/supply*100,4)
            out["largest_holder_pct"]=round(balances[0]/supply*100,4) if balances else None; out["largest_accounts_observed"]=len(balances)
    except Exception as exc: errors.append("holders:"+str(exc)[:180])
    try: out.update(_creation_evidence(mint))
    except Exception as exc: errors.append("history:"+str(exc)[:180])
    out["solana_rpc_ok"] = not errors
    if errors: out["solana_rpc_error"]=" | ".join(errors)[:500]
    return out
