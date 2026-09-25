"""Performance analytics for historical Jev decisions.

This module is downstream research only. It never changes Jev verdicts.
Paper results are hypothetical and exclude fees/slippage unless explicitly modeled.
"""
import json, sqlite3, statistics

HORIZONS=(3600,21600,86400,604800)

def _db(path):
    db=sqlite3.connect(path); db.row_factory=sqlite3.Row; return db

def _safe_mean(xs): return sum(xs)/len(xs) if xs else None

def _median(xs): return statistics.median(xs) if xs else None

def performance_summary(path, verdict="GEM"):
    with _db(path) as db:
        out={"verdict":verdict,"horizons":{}}
        for h in HORIZONS:
            rows=db.execute("SELECT o.return_pct FROM outcomes o JOIN scans s ON s.id=o.scan_id WHERE s.verdict=? AND o.horizon_seconds=? AND o.return_pct IS NOT NULL",(verdict,h)).fetchall()
            vals=[float(r[0]) for r in rows]
            out["horizons"][str(h)]={"observations":len(vals),"win_rate_pct":round(100*sum(v>0 for v in vals)/len(vals),2) if vals else None,"avg_return_pct":round(_safe_mean(vals),2) if vals else None,"median_return_pct":round(_median(vals),2) if vals else None,"best_return_pct":round(max(vals),2) if vals else None,"worst_return_pct":round(min(vals),2) if vals else None}
        return out

def confidence_buckets(path,horizon=86400,verdict="GEM"):
    buckets=[(0.50,0.60),(0.60,0.70),(0.70,0.80),(0.80,0.90),(0.90,1.01)]; out=[]
    with _db(path) as db:
        for lo,hi in buckets:
            vals=[float(r[0]) for r in db.execute("SELECT o.return_pct FROM outcomes o JOIN scans s ON s.id=o.scan_id WHERE s.verdict=? AND s.confidence>=? AND s.confidence<? AND o.horizon_seconds=? AND o.return_pct IS NOT NULL",(verdict,lo,hi,horizon)).fetchall()]
            out.append({"bucket":"%.2f-%.2f"%(lo,min(1.0,hi)),"observations":len(vals),"win_rate_pct":round(100*sum(v>0 for v in vals)/len(vals),2) if vals else None,"avg_return_pct":round(_safe_mean(vals),2) if vals else None,"median_return_pct":round(_median(vals),2) if vals else None})
    return out

def paper_portfolio(path,starting_cash=10000.0,position_size=100.0,min_confidence=0.80,horizon=86400):
    """Simple non-overlapping accounting of fixed-size hypothetical GEM entries.

    Each eligible scan is treated as an independent fixed-dollar paper position and
    closed at the requested measured horizon. This is a research baseline, not an
    execution simulator; it does not model fees, slippage, pool price impact or fills.
    """
    with _db(path) as db:
        rows=db.execute("SELECT s.id,s.ts,s.symbol,s.confidence,o.return_pct,o.price_then,o.price_now FROM scans s JOIN outcomes o ON o.scan_id=s.id WHERE s.verdict='GEM' AND s.confidence>=? AND o.horizon_seconds=? AND o.return_pct IS NOT NULL ORDER BY s.ts",(min_confidence,horizon)).fetchall()
    cash=float(starting_cash); peak=cash; max_dd=0.0; wins=0; gross_profit=0.0; gross_loss=0.0; trades=[]
    for r in rows:
        stake=min(float(position_size),cash)
        if stake<=0: break
        pnl=stake*float(r["return_pct"])/100.0; cash+=pnl; peak=max(peak,cash); dd=(peak-cash)/peak*100 if peak else 0; max_dd=max(max_dd,dd)
        if pnl>0: wins+=1; gross_profit+=pnl
        elif pnl<0: gross_loss+=abs(pnl)
        trades.append({"scan_id":r["id"],"symbol":r["symbol"],"confidence":r["confidence"],"entry_price":r["price_then"],"exit_price":r["price_now"],"return_pct":round(float(r["return_pct"]),2),"stake":round(stake,2),"pnl":round(pnl,2),"equity":round(cash,2)})
    return {"starting_cash":round(starting_cash,2),"ending_equity":round(cash,2),"net_profit":round(cash-starting_cash,2),"return_pct":round((cash/starting_cash-1)*100,2) if starting_cash else None,"trades":len(trades),"wins":wins,"losses":len(trades)-wins,"win_rate_pct":round(100*wins/len(trades),2) if trades else None,"profit_factor":round(gross_profit/gross_loss,2) if gross_loss else (None if not gross_profit else "inf"),"max_drawdown_pct":round(max_dd,2),"position_size":position_size,"min_confidence":min_confidence,"horizon_seconds":horizon,"assumptions":"Fixed-dollar paper positions; measured horizon exits; excludes fees, slippage, price impact and fill risk.","recent_trades":trades[-100:][::-1]}
