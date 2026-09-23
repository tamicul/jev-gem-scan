"""Solana deployer-wallet observations using standard JSON-RPC.

These are evidence fields only. They never make or veto a Jev verdict.
Public RPC history may be incomplete, so completeness is always recorded.
"""
import time
from .solana_rpc import _post


def _signatures(address, limit=100):
    return _post("getSignaturesForAddress", [address, {"commitment":"confirmed","limit":max(1,min(int(limit),1000))}]) or []


def enrich_deployer(features, limit=100):
    out=dict(features); wallet=out.get("probable_deployer")
    if out.get("chain_id")!="solana" or not wallet: return out
    try:
        rows=_signatures(wallet,limit)
        now=time.time(); valid=[r for r in rows if not r.get("err")]
        times=[r.get("blockTime") for r in valid if r.get("blockTime")]
        out["deployer_tx_observed"]=len(rows)
        out["deployer_success_tx_observed"]=len(valid)
        out["deployer_failed_tx_observed"]=len(rows)-len(valid)
        out["deployer_history_window_hours"]=round((max(times)-min(times))/3600.0,3) if len(times)>1 else None
        out["deployer_last_activity_age_minutes"]=round((now-max(times))/60.0,3) if times else None
        out["deployer_history_page_full"]=len(rows)>=limit
        out["deployer_rpc_ok"]=True
    except Exception as exc:
        out["deployer_rpc_ok"]=False; out["deployer_rpc_error"]=str(exc)[:300]
    return out
