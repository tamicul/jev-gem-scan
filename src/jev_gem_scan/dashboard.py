"""Local dashboard: scanner, measured outcomes and paper research lab."""
import argparse, html, json, sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from .performance import performance_summary, confidence_buckets, paper_portfolio

def _db(path):
    db=sqlite3.connect(path); db.row_factory=sqlite3.Row; return db

def _loads(v):
    try:return json.loads(v or "{}")
    except Exception:return {}

def _fmt(v,d=2): return "—" if v is None else (str(v) if isinstance(v,str) else ("{:.{}f}".format(v,d)))

def summary(path):
    with _db(path) as db:
        total=db.execute("SELECT COUNT(*) n FROM scans").fetchone()["n"]
        counts={r["verdict"]:r["n"] for r in db.execute("SELECT verdict,COUNT(*) n FROM scans GROUP BY verdict")}
        alerts=db.execute("SELECT COUNT(*) n FROM scans WHERE action='alert'").fetchone()["n"]
        return {"total":total,"gems":counts.get("GEM",0),"rugs":counts.get("RUG",0),"alerts":alerts}

def recent(path,limit=100,verdict=None):
    with _db(path) as db:
        sql="SELECT id,ts,chain_id,token_address,symbol,verdict,confidence,reason,action,features_json,result_json FROM scans"; args=[]
        if verdict in ("GEM","RUG"): sql+=" WHERE verdict=?"; args.append(verdict)
        sql+=" ORDER BY id DESC LIMIT ?"; args.append(max(1,min(int(limit),500)))
        return [dict(r) for r in db.execute(sql,args)]

def detail(path,scan_id):
    with _db(path) as db:
        row=db.execute("SELECT * FROM scans WHERE id=?",(scan_id,)).fetchone()
        if not row:return None
        out=dict(row); out["features"]=_loads(out.pop("features_json")); out["result"]=_loads(out.pop("result_json")); out["outcomes"]=[dict(r) for r in db.execute("SELECT * FROM outcomes WHERE scan_id=? ORDER BY horizon_seconds",(scan_id,))]; return out

def _nav(): return "<nav><a href='/'>Scanner</a><a href='/performance'>Performance Lab</a><a href='/paper'>Paper Portfolio</a><a href='/api/scans'>JSON API</a></nav>"

def _page(path,verdict=None):
    s=summary(path); rows=recent(path,100,verdict)
    cards='<div class="cards"><b>Total {total}</b><b>GEM {gems}</b><b>RUG {rugs}</b><b>Alerts {alerts}</b></div>'.format(**s); trs=[]
    for r in rows:
        f=_loads(r["features_json"]); cls="gem" if r["verdict"]=="GEM" else "rug"
        trs.append("<tr><td>{}</td><td class='{}'>{}</td><td>{:.2f}</td><td>{}</td><td>{}</td><td>{}</td><td><a href='/scan?id={}'>inspect</a></td></tr>".format(html.escape(r["symbol"] or "?"),cls,r["verdict"],r["confidence"] or 0,html.escape(r["action"] or ""),html.escape(str(f.get("liquidity_usd"))),html.escape(str(f.get("dev_wallet_pct"))),r["id"]))
    filters="<p><a href='/'>All</a> | <a href='/?verdict=GEM'>GEM</a> | <a href='/?verdict=RUG'>RUG</a></p>"
    table="<table><tr><th>Token</th><th>Jev</th><th>Confidence</th><th>Action</th><th>Liquidity</th><th>Dev %</th><th></th></tr>{}</table>".format("".join(trs))
    return _html("Jev Gem Scan",_nav()+cards+filters+table)

def _performance_page(path):
    p=performance_summary(path); h=p["horizons"]
    cards=[]
    labels=(("3600","1h"),("21600","6h"),("86400","24h"),("604800","7d"))
    for key,label in labels:
        x=h[key]; cards.append("<div class='metric'><strong>{}</strong><span>{} measured</span><em>{}% wins</em><span>median {}%</span><span>avg {}%</span></div>".format(label,x["observations"],_fmt(x["win_rate_pct"]),_fmt(x["median_return_pct"]),_fmt(x["avg_return_pct"])))
    buckets=confidence_buckets(path); rows="".join("<tr><td>{}</td><td>{}</td><td>{}%</td><td>{}%</td><td>{}%</td></tr>".format(b["bucket"],b["observations"],_fmt(b["win_rate_pct"]),_fmt(b["median_return_pct"]),_fmt(b["avg_return_pct"])) for b in buckets)
    body=_nav()+"<p class='note'>Measured forward returns from the price captured when Jev made each GEM decision. These are observations, not forecasts.</p><div class='metricgrid'>{}</div>".format("".join(cards))+"<h2>24h return by Jev confidence</h2><table><tr><th>Confidence</th><th>Measured</th><th>Win rate</th><th>Median return</th><th>Average return</th></tr>{}</table>".format(rows)
    return _html("Jev Performance Lab",body)

def _paper_page(path,q):
    try: start=float((q.get("capital") or [10000])[0]); size=float((q.get("size") or [100])[0]); conf=float((q.get("confidence") or [.80])[0]); horizon=int((q.get("horizon") or [86400])[0])
    except Exception: start,size,conf,horizon=10000,100,.80,86400
    p=paper_portfolio(path,start,size,conf,horizon)
    cards="<div class='cards'><b>Start ${}</b><b>Equity ${}</b><b>P/L ${}</b><b>Return {}%</b><b>Win rate {}%</b><b>Max DD {}%</b></div>".format(_fmt(p["starting_cash"]),_fmt(p["ending_equity"]),_fmt(p["net_profit"]),_fmt(p["return_pct"]),_fmt(p["win_rate_pct"]),_fmt(p["max_drawdown_pct"]))
    form="""<form><label>Capital $ <input name='capital' value='{capital}'></label><label>Position $ <input name='size' value='{size}'></label><label>Min confidence <input name='confidence' value='{conf}'></label><label>Exit <select name='horizon'>{opts}</select></label><button>Recalculate</button></form>""".format(capital=start,size=size,conf=conf,opts="".join("<option value='{}' {}>{}</option>".format(v,"selected" if horizon==v else "",lab) for v,lab in ((3600,"1h"),(21600,"6h"),(86400,"24h"),(604800,"7d"))))
    rows="".join("<tr><td>{}</td><td>{:.2f}</td><td>${}</td><td>{}%</td><td class='{}'>${}</td><td>${}</td></tr>".format(html.escape(t["symbol"] or "?"),t["confidence"] or 0,_fmt(t["stake"]),_fmt(t["return_pct"]),"gem" if t["pnl"]>=0 else "rug",_fmt(t["pnl"]),_fmt(t["equity"])) for t in p["recent_trades"])
    body=_nav()+"<p class='note'>Research simulation only. Fixed-dollar entries at Jev's recorded price and exit at the selected measured horizon. Fees, slippage, pool impact and fill risk are NOT included.</p>"+form+cards+"<p>Trades: {} | Wins: {} | Losses: {} | Profit factor: {}</p>".format(p["trades"],p["wins"],p["losses"],p["profit_factor"])+"<table><tr><th>Token</th><th>Confidence</th><th>Paper stake</th><th>Return</th><th>P/L</th><th>Equity</th></tr>{}</table>".format(rows)
    return _html("Paper Portfolio",body)

def _detail_page(path,scan_id):
    d=detail(path,scan_id)
    if not d:return _html("Not found","<h2>Scan not found</h2>")
    f,r=d["features"],d["result"]; evidence="".join("<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(html.escape(str(e.get("signal"))),html.escape(str(e.get("value"))),e.get("delta")) for e in r.get("evidence",[])); outcomes="".join("<tr><td>{}h</td><td>{}%</td><td>{}</td><td>{}</td></tr>".format(round(o["horizon_seconds"]/3600,1),_fmt(o["return_pct"]),o["price_now"],bool(o["pair_alive"])) for o in d["outcomes"]); cls="gem" if d["verdict"]=="GEM" else "rug"
    body=_nav()+"<h2>{} — <span class='{}'>{}</span> {:.2f}</h2><p>{}</p>".format(html.escape(d.get("symbol") or "?"),cls,d["verdict"],d["confidence"] or 0,html.escape(d.get("reason") or ""))+"<h3>Measured outcomes</h3><table><tr><th>Horizon</th><th>Return</th><th>Price</th><th>Pair alive</th></tr>{}</table>".format(outcomes)+"<h3>Jev evidence ledger</h3><table><tr><th>Signal</th><th>Observed</th><th>Contribution</th></tr>{}</table>".format(evidence)+"<h3>Observed snapshot</h3><pre>{}</pre>".format(html.escape(json.dumps(f,indent=2,sort_keys=True)))
    return _html("Scan {}".format(scan_id),body)

def _html(title,body):
    template="""<!doctype html><html><head><meta charset='utf-8'><meta http-equiv='refresh' content='30'><title>{title}</title><style>body{{font-family:system-ui;max-width:1250px;margin:28px auto;padding:0 18px;background:#0d1117;color:#e6edf3}}a{{color:#58a6ff}}nav{{display:flex;gap:18px;margin:0 0 24px}}.cards,.metricgrid{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}.cards b,.metric{{background:#161b22;padding:16px 20px;border:1px solid #30363d;border-radius:9px}}.metric{{display:flex;flex-direction:column;min-width:160px;gap:5px}}.metric strong{{font-size:20px}}.metric em{{font-size:18px;color:#61d095;font-style:normal}}table{{width:100%;border-collapse:collapse;background:#161b22}}th,td{{padding:10px;border-bottom:1px solid #30363d;text-align:left}}.gem{{color:#61d095;font-weight:700}}.rug{{color:#ff7b72;font-weight:700}}pre{{white-space:pre-wrap;background:#161b22;padding:16px;border-radius:8px}}.note{{padding:12px;background:#161b22;border-left:3px solid #58a6ff}}form{{display:flex;gap:12px;flex-wrap:wrap;align-items:end;margin:18px 0}}input,select,button{{background:#161b22;color:#e6edf3;border:1px solid #30363d;padding:8px;border-radius:6px}}label{{display:flex;flex-direction:column;gap:4px}}</style></head><body><h1>{title}</h1>{body}</body></html>"""; return template.format(title=html.escape(title),body=body)

def serve(db_path="data/gem_scan.db",host="127.0.0.1",port=8787):
    class Handler(BaseHTTPRequestHandler):
        def _send(self,body,ctype="text/html; charset=utf-8",status=200): raw=body.encode(); self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            u=urlparse(self.path); q=parse_qs(u.query)
            try:
                if u.path=="/":return self._send(_page(db_path,(q.get("verdict") or [None])[0]))
                if u.path=="/performance":return self._send(_performance_page(db_path))
                if u.path=="/paper":return self._send(_paper_page(db_path,q))
                if u.path=="/scan":return self._send(_detail_page(db_path,int((q.get("id") or [0])[0])))
                if u.path=="/api/summary":return self._send(json.dumps(summary(db_path)),"application/json")
                if u.path=="/api/performance":return self._send(json.dumps(performance_summary(db_path)),"application/json")
                if u.path=="/api/paper":return self._send(json.dumps(paper_portfolio(db_path)),"application/json")
                if u.path=="/api/scans":
                    data=recent(db_path,int((q.get("limit") or [100])[0]),(q.get("verdict") or [None])[0]); [x.update(features=_loads(x.pop("features_json")),result=_loads(x.pop("result_json"))) for x in data]; return self._send(json.dumps(data),"application/json")
                return self._send("not found","text/plain",404)
            except Exception as exc:return self._send("dashboard error: {}".format(html.escape(str(exc))),"text/plain",500)
        def log_message(self,fmt,*args):pass
    print("Jev dashboard: http://{}:{}".format(host,port)); ThreadingHTTPServer((host,port),Handler).serve_forever()

def main():
    p=argparse.ArgumentParser(); p.add_argument("--db",default="data/gem_scan.db"); p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8787); a=p.parse_args(); serve(a.db,a.host,a.port)
if __name__=="__main__":main()
