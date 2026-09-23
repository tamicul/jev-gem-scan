"""Measure what happened after a Jev decision; never changes that decision."""
import json
from .database import connect,due_scans,save_outcome
from .providers.dexscreener import enrich

DEFAULT_HORIZONS=(3600,21600,86400,604800)

def collect(db_path="data/gem_scan.db",horizons=DEFAULT_HORIZONS,limit=100):
    db=connect(db_path); stats={"observed":0,"missing":0,"errors":0}
    for horizon in horizons:
        for scan_id,ts,chain,address,raw in due_scans(db,horizon,limit):
            try:
                original=json.loads(raw); obs=enrich({"chain_id":chain,"token_address":address})
                save_outcome(db,scan_id,horizon,original.get("price_usd"),obs)
                stats["observed" if obs else "missing"]+=1
            except Exception:
                stats["errors"]+=1
    db.close(); return stats
