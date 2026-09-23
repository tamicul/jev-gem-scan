"""Live scanner service; Jev remains the GEM/RUG decision authority."""
import random, time
from .database import connect,recent_seen,save
from .providers.dexscreener import discover,enrich
from .providers.solana_rpc import enrich_solana
from .router import route_launch

def scan_once(config,limit=30,chain=None,db_path="data/gem_scan.db",dedupe_seconds=900):
    db=connect(db_path); rng=random.Random(); stats={"discovered":0,"scored":0,"gems":0,"rugs":0,"alerts":0,"errors":0}; rows=[]
    for c in discover(limit=limit,chain=chain):
        stats["discovered"]+=1
        try:
            if recent_seen(db,c["chain_id"],c["token_address"],dedupe_seconds): continue
            f=enrich(c)
            if not f: continue
            # Native enrichment supplies evidence to Jev; it never makes/vetoes the verdict.
            if f.get("chain_id")=="solana": f=enrich_solana(f)
            r,action=route_launch(f,config,rng)
            if action=="bypass": continue
            save(db,f,r,action); stats["scored"]+=1; stats["gems" if r["verdict"]=="GEM" else "rugs"]+=1
            if action=="alert": stats["alerts"]+=1
            rows.append((f,r,action))
        except Exception as exc:
            stats["errors"]+=1; rows.append((c,{"error":str(exc)},"error"))
    db.close(); return rows,stats

def run_forever(config,interval=30,**kwargs):
    while True:
        yield scan_once(config,**kwargs); time.sleep(max(5,interval))
