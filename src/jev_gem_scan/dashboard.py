"""Dependency-free local web dashboard for Jev Gem Scan.

Read-only UI: it visualizes Jev decisions and evidence; it never changes or vetoes them.
"""
import argparse, html, json, sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def _db(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def _loads(v):
    try: return json.loads(v or "{}")
    except Exception: return {}


def summary(path):
    with _db(path) as db:
        total = db.execute("SELECT COUNT(*) n FROM scans").fetchone()["n"]
        rows = db.execute("SELECT verdict,COUNT(*) n FROM scans GROUP BY verdict").fetchall()
        counts = {r["verdict"]: r["n"] for r in rows}
        alerts = db.execute("SELECT COUNT(*) n FROM scans WHERE action='alert'").fetchone()["n"]
        return {"total": total, "gems": counts.get("GEM",0), "rugs": counts.get("RUG",0), "alerts": alerts}


def recent(path, limit=100, verdict=None):
    with _db(path) as db:
        sql = "SELECT id,ts,chain_id,token_address,symbol,verdict,confidence,reason,action,features_json,result_json FROM scans"
        args=[]
        if verdict in ("GEM","RUG"):
            sql += " WHERE verdict=?"; args.append(verdict)
        sql += " ORDER BY id DESC LIMIT ?"; args.append(max(1,min(int(limit),500)))
        return [dict(r) for r in db.execute(sql,args).fetchall()]


def detail(path, scan_id):
    with _db(path) as db:
        row=db.execute("SELECT * FROM scans WHERE id=?",(scan_id,)).fetchone()
        if not row: return None
        out=dict(row); out["features"]=_loads(out.pop("features_json")); out["result"]=_loads(out.pop("result_json"))
        out["outcomes"]=[dict(r) for r in db.execute("SELECT * FROM outcomes WHERE scan_id=? ORDER BY horizon_seconds",(scan_id,)).fetchall()]
        return out


def _page(path, verdict=None):
    s=summary(path); rows=recent(path,100,verdict)
    cards=f'<div class="cards"><b>Total {s["total"]}</b><b>GEM {s["gems"]}</b><b>RUG {s["rugs"]}</b><b>Alerts {s["alerts"]}</b></div>'
    trs=[]
    for r in rows:
        f=_loads(r["features_json"]); cls="gem" if r["verdict"]=="GEM" else "rug"
        trs.append("<tr><td>%s</td><td class='%s'>%s</td><td>%.2f</td><td>%s</td><td>%s</td><td>%s</td><td><a href='/scan?id=%s'>inspect</a></td></tr>" % (
            html.escape(r["symbol"] or "?"),cls,r["verdict"],r["confidence"] or 0,html.escape(r["action"] or ""),
            html.escape(str(f.get("liquidity_usd"))),html.escape(str(f.get("dev_wallet_pct"))),r["id"]))
    body=(cards+"<p><a href='/'>All</a> | <a href='/?verdict=GEM'>GEM</a> | <a href='/?verdict=RUG'>RUG</a> | <a href='/api/scans'>JSON API</a></p>"+
          "<table><tr><th>Token</th><th>Jev</th><th>Confidence</th><th>Action</th><th>Liquidity</th><th>Dev %</th><th></th></tr>%s</table>"%"".join(trs))
    return _html("Jev Gem Scan",body)


def _detail_page(path, scan_id):
    d=detail(path,scan_id)
    if not d: return _html("Not found","<h2>Scan not found</h2>")
    f,r=d["features"],d["result"]
    evidence="".join("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(html.escape(str(e.get("signal"))),html.escape(str(e.get("value"))),e.get("delta")) for e in r.get("evidence",[]))
    outcomes="".join("<tr><td>%sh</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(round(o["horizon_seconds"]/3600,1),o["return_pct"],o["price_now"],bool(o["pair_alive"])) for o in d["outcomes"])
    body="<p><a href='/'>← dashboard</a></p><h2>%s — <span class='%s'>%s</span> %.2f</h2><p>%s</p>"%(html.escape(d.get("symbol") or "?"),"gem" if d["verdict"]=="GEM" else "rug",d["verdict"],d["confidence"] or 0,html.escape(d.get("reason") or ""))
    body+="<h3>Observed snapshot</h3><pre>%s</pre>"%html.escape(json.dumps(f,indent=2,sort_keys=True))
    body+="<h3>Jev evidence ledger</h3><table><tr><th>Signal</th><th>Observed</th><th>Contribution</th></tr>%s</table>"%evidence
    body+="<h3>Measured outcomes</h3><table><tr><th>Horizon</th><th>Return %</th><th>Price</th><th>Pair alive</th></tr>%s</table>"%outcomes
    return _html("Scan %s"%scan_id,body)


def _html(title,body):
    return """<!doctype html><html><head><meta charset='utf-8'><meta http-equiv='refresh' content='20'><title>%s</title><style>body{font-family:system-ui;max-width:1200px;margin:30px auto;padding:0 16px;background:#101318;color:#e8edf2}a{color:#77bdfb}.cards{display:flex;gap:12px;flex-wrap:wrap}.cards b{background:#1b222c;padding:16px 24px;border-radius:10px}table{width:100%%;border-collapse:collapse;background:#171c23}th,td{padding:10px;border-bottom:1px solid #303844;text-align:left}.gem{color:#61d095;font-weight:700}.rug{color:#ff7272;font-weight:700}pre{white-space:pre-wrap;background:#171c23;padding:16px;border-radius:8px;overflow:auto}</style></head><body><h1>%s</h1>%s</body></html>"""%(html.escape(title),html.escape(title),body)


def serve(db_path="data/gem_scan.db",host="127.0.0.1",port=8787):
    class Handler(BaseHTTPRequestHandler):
        def _send(self,body,ctype="text/html; charset=utf-8",status=200):
            raw=body.encode(); self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
        def do_GET(self):
            u=urlparse(self.path); q=parse_qs(u.query)
            try:
                if u.path=="/": self._send(_page(db_path,(q.get("verdict") or [None])[0])); return
                if u.path=="/scan": self._send(_detail_page(db_path,int((q.get("id") or [0])[0]))); return
                if u.path=="/api/summary": self._send(json.dumps(summary(db_path)),"application/json"); return
                if u.path=="/api/scans":
                    data=recent(db_path,int((q.get("limit") or [100])[0]),(q.get("verdict") or [None])[0])
                    for x in data: x["features"]=_loads(x.pop("features_json")); x["result"]=_loads(x.pop("result_json"))
                    self._send(json.dumps(data),"application/json"); return
                self._send("not found","text/plain",404)
            except Exception as exc: self._send("dashboard error: %s"%html.escape(str(exc)),"text/plain",500)
        def log_message(self,fmt,*args): pass
    server=ThreadingHTTPServer((host,port),Handler)
    print("Jev dashboard: http://%s:%s"%(host,port)); server.serve_forever()


def main():
    p=argparse.ArgumentParser(); p.add_argument("--db",default="data/gem_scan.db"); p.add_argument("--host",default="127.0.0.1"); p.add_argument("--port",type=int,default=8787); a=p.parse_args(); serve(a.db,a.host,a.port)

if __name__=="__main__": main()
