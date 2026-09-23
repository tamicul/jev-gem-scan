"""All-in-one Jev scanner service.

Runs scanning, outcome measurement and the read-only dashboard together.
No component here changes a Jev verdict.
"""
import argparse, threading, time
from .dashboard import serve
from .outcomes import collect
from .router import load_config
from .scanner import scan_once


def _scanner_loop(cfg, db_path, chain, limit, interval, dedupe):
    while True:
        try:
            rows, stats = scan_once(cfg, limit=limit, chain=chain, db_path=db_path, dedupe_seconds=dedupe)
            print("[scanner] " + " ".join("%s=%s" % x for x in stats.items()))
            for f, r, action in rows:
                if action != "error" and (action == "alert" or r.get("verdict") == "GEM"):
                    print("[signal] %s %s %.2f action=%s" % (f.get("symbol") or "?", r.get("verdict"), r.get("confidence",0), action))
        except Exception as exc:
            print("[scanner:error] %s" % exc)
        time.sleep(max(5, interval))


def _outcome_loop(db_path, interval):
    while True:
        try:
            stats=collect(db_path=db_path)
            if any(stats.values()): print("[outcomes] " + " ".join("%s=%s" % x for x in stats.items()))
        except Exception as exc:
            print("[outcomes:error] %s" % exc)
        time.sleep(max(60, interval))


def run(db_path="data/gem_scan.db", chain="solana", scan_interval=30, outcome_interval=300,
        limit=30, dedupe_seconds=900, host="127.0.0.1", port=8787, mode=None, config_path=None):
    cfg=load_config(config_path)
    if mode: cfg["mode"]=mode
    threading.Thread(target=_scanner_loop,args=(cfg,db_path,chain,limit,scan_interval,dedupe_seconds),daemon=True).start()
    threading.Thread(target=_outcome_loop,args=(db_path,outcome_interval),daemon=True).start()
    print("Jev service started | chain=%s mode=%s db=%s"%(chain,cfg.get("mode"),db_path))
    serve(db_path,host,port)


def main():
    p=argparse.ArgumentParser(description="Run scanner + outcome tracker + dashboard")
    p.add_argument("--db",default="data/gem_scan.db"); p.add_argument("--chain",default="solana")
    p.add_argument("--scan-interval",type=int,default=30); p.add_argument("--outcome-interval",type=int,default=300)
    p.add_argument("--limit",type=int,default=30); p.add_argument("--dedupe-seconds",type=int,default=900)
    p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8787)
    p.add_argument("--mode",choices=["shadow","active"]); p.add_argument("--config")
    a=p.parse_args(); run(a.db,a.chain,a.scan_interval,a.outcome_interval,a.limit,a.dedupe_seconds,a.host,a.port,a.mode,a.config)

if __name__=="__main__": main()
