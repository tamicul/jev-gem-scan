"""DexScreener live discovery and pair enrichment."""
import time
from .http import get_json
BASE = "https://api.dexscreener.com"

def _f(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def discover(limit=30, chain=None):
    profiles = get_json(BASE + "/token-profiles/latest/v1")
    out, seen = [], set()
    for p in profiles if isinstance(profiles, list) else []:
        cid, addr = p.get("chainId"), p.get("tokenAddress")
        if not addr or (chain and cid != chain) or (cid, addr) in seen: continue
        seen.add((cid, addr)); out.append({"chain_id": cid, "token_address": addr})
        if len(out) >= limit: break
    return out

def enrich(c):
    cid, addr = c["chain_id"], c["token_address"]
    data = get_json(BASE + "/token-pairs/v1/%s/%s" % (cid, addr))
    pairs = data if isinstance(data, list) else []
    if not pairs: return None
    pair = max(pairs, key=lambda x: _f((x.get("liquidity") or {}).get("usd")) or 0.0)
    base, tx, vol, pc, liq = pair.get("baseToken") or {}, pair.get("txns") or {}, pair.get("volume") or {}, pair.get("priceChange") or {}, pair.get("liquidity") or {}
    h1, created = tx.get("h1") or {}, pair.get("pairCreatedAt")
    age = max(0.0, (time.time()*1000-float(created))/60000.0) if created else None
    return {"symbol":base.get("symbol") or addr[:8],"name":base.get("name"),"chain_id":cid,"token_address":addr,
      "pair_address":pair.get("pairAddress"),"dex_id":pair.get("dexId"),"url":pair.get("url"),"price_usd":_f(pair.get("priceUsd")),
      "liquidity_usd":_f(liq.get("usd")),"fdv":_f(pair.get("fdv")),"market_cap":_f(pair.get("marketCap")),
      "volume_h1":_f(vol.get("h1")),"volume_h24":_f(vol.get("h24")),"price_change_h1":_f(pc.get("h1")),"price_change_h24":_f(pc.get("h24")),
      "buys_h1":int(h1.get("buys") or 0),"sells_h1":int(h1.get("sells") or 0),"pair_age_minutes":age,
      "liquidity_lock_days":None,"top10_holder_pct":None,"dev_wallet_pct":None,"contract_renounced":None,"honeypot_flag":None,"social_age_days":None,"source":"dexscreener"}
