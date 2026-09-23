"""Local Jev-compatible decision engine; unknown live facts are neutral."""
import time
GEM_CONFIDENCE_THRESHOLD=0.85

def call_jev_api(f,rng):
    started=time.perf_counter(); score=0.0; reasons=[]; known=0
    hp=f.get("honeypot_flag"); dev=f.get("dev_wallet_pct"); top=f.get("top10_holder_pct"); lock=f.get("liquidity_lock_days"); ren=f.get("contract_renounced"); social=f.get("social_age_days")
    if hp is not None:
        known+=1
        if hp: score-=1.2; reasons.append("honeypot=true")
    if dev is not None:
        known+=1
        if dev>15: score-=0.9; reasons.append("dev_wallet=%.0f%%"%dev)
    if top is not None:
        known+=1
        if top>40: score-=0.7; reasons.append("top10=%.0f%%"%top)
        elif top<20: score+=0.5; reasons.append("top10=%.0f%%"%top)
    if lock is not None:
        known+=1
        if lock<30: score-=0.6; reasons.append("lock=%dd"%lock)
        elif lock>=180: score+=0.8; reasons.append("lock=%dd"%lock)
    if ren is not None:
        known+=1
        if ren: score+=0.5; reasons.append("renounced")
    if social is not None:
        known+=1
        if social>90: score+=0.4; reasons.append("social=%dd"%social)
    liq=f.get("liquidity_usd"); vol=f.get("volume_h1"); buys=f.get("buys_h1"); sells=f.get("sells_h1")
    if liq is not None:
        known+=1
        if liq>=100000: score+=0.25; reasons.append("liq=$%.0fk"%(liq/1000))
        elif liq<5000: score-=0.25; reasons.append("low_liq=$%.0f"%liq)
    if vol is not None:
        known+=1
        if vol>=50000: score+=0.20; reasons.append("vol1h=$%.0fk"%(vol/1000))
    if buys is not None and sells is not None:
        known+=1
        if buys>=20 and buys>sells*1.5: score+=0.20; reasons.append("buy_pressure=%d/%d"%(buys,sells))
        elif sells>=20 and sells>buys*2: score-=0.20; reasons.append("sell_pressure=%d/%d"%(buys,sells))
    verdict="GEM" if score>=0 else "RUG"; confidence=round(min(0.99,0.5+min(abs(score),2.0)/2.0*0.49),2)
    return {"verdict":verdict,"confidence":confidence,"reason":", ".join(reasons) if reasons else "no strong known signals","score":round(score,3),"known_signal_groups":known,"latency_ms":max(1,int((time.perf_counter()-started)*1000)),"cost_usd":0.0,"engine":"local-jev-compatible-v2"}
