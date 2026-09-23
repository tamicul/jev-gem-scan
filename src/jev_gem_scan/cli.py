"""CLI for simulation and live scanning."""
import argparse,time
from random import Random
from .generator import generate_launch
from .router import route_launch,load_config
from .logbook import log_scan,LOG_PATH
from .scanner import scan_once,run_forever
from . import __version__

def build_parser():
    ap=argparse.ArgumentParser(prog="jev_gem_scan",description="Jev Gem Scan: simulation and live scanner")
    ap.add_argument("--source",choices=["sim","live"],default="sim"); ap.add_argument("--launches",type=int,default=20); ap.add_argument("--seed",type=int,default=1)
    ap.add_argument("--mode",choices=["shadow","active"]); ap.add_argument("--config"); ap.add_argument("--sleep",type=float,default=.15); ap.add_argument("--no-log",action="store_true")
    ap.add_argument("--chain"); ap.add_argument("--limit",type=int,default=30); ap.add_argument("--db",default="data/gem_scan.db"); ap.add_argument("--dedupe-seconds",type=int,default=900)
    ap.add_argument("--watch",action="store_true"); ap.add_argument("--interval",type=int,default=30); ap.add_argument("--version",action="version",version="jev_gem_scan "+__version__); return ap

def _print_live(rows,stats):
    for f,r,a in rows:
        if a=="error": print("[ERROR] %s"%r.get("error")); continue
        print("[%s] %s/%s %s -> %s %.2f | %s | liq=%s vol1h=%s"%(a.upper(),f.get("chain_id"),f.get("symbol"),f.get("token_address"),r["verdict"],r["confidence"],r["reason"],f.get("liquidity_usd"),f.get("volume_h1")))
    print("-- live summary -- "+" ".join("%s=%s"%x for x in stats.items()))

def run_live(args,cfg):
    kw=dict(limit=args.limit,chain=args.chain,db_path=args.db,dedupe_seconds=args.dedupe_seconds)
    if args.watch:
        try:
            for rows,stats in run_forever(cfg,interval=args.interval,**kw): _print_live(rows,stats)
        except KeyboardInterrupt: print("\nstopped")
    else: _print_live(*scan_once(cfg,**kw))

def run_sim(args,cfg):
    rng=Random(args.seed); mode=cfg.get("mode","shadow"); gems=rugs=alerts=scored=0
    for _ in range(args.launches):
        f=generate_launch(rng); r,a=route_launch(f,cfg,rng)
        if a=="bypass": print("[bypass] %s"%f["symbol"]); continue
        if not args.no_log: log_scan(f,r,mode)
        scored+=1; gems+=r["verdict"]=="GEM"; rugs+=r["verdict"]=="RUG"; alerts+=a=="alert"
        print("[%s] %s -> %s (%.2f, %s)"%(a,f["symbol"],r["verdict"],r["confidence"],r["reason"])); time.sleep(args.sleep)
    print("-- summary -- scanned=%d GEM=%d RUG=%d alerts=%d"%(scored,gems,rugs,alerts))
    if scored and not args.no_log: print("log appended -> %s"%LOG_PATH)

def main(argv=None):
    args=build_parser().parse_args(argv); cfg=load_config(args.config)
    if args.mode: cfg["mode"]=args.mode
    print("== Jev Gem Scan v%s | source=%s mode=%s =="%(__version__,args.source,cfg.get("mode")))
    (run_live if args.source=="live" else run_sim)(args,cfg)

if __name__=="__main__": main()
