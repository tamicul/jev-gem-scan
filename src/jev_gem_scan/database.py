"""SQLite persistence for immutable scan snapshots and measurable outcomes."""
import json, os, sqlite3, time

def connect(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True); db=sqlite3.connect(path); db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, chain_id TEXT, token_address TEXT, symbol TEXT, source TEXT, verdict TEXT, confidence REAL, reason TEXT, action TEXT, features_json TEXT NOT NULL, result_json TEXT NOT NULL)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_scans_token ON scans(chain_id,token_address,ts)")
    db.execute("CREATE TABLE IF NOT EXISTS outcomes (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER NOT NULL, observed_ts REAL NOT NULL, horizon_seconds INTEGER NOT NULL, price_then REAL, price_now REAL, return_pct REAL, liquidity_now REAL, volume_h24_now REAL, pair_alive INTEGER, observation_json TEXT NOT NULL, UNIQUE(scan_id,horizon_seconds), FOREIGN KEY(scan_id) REFERENCES scans(id))")
    db.execute("CREATE INDEX IF NOT EXISTS idx_outcomes_scan ON outcomes(scan_id,horizon_seconds)"); db.commit(); return db

def save(db,f,r,action):
    cur=db.execute("INSERT INTO scans(ts,chain_id,token_address,symbol,source,verdict,confidence,reason,action,features_json,result_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(time.time(),f.get("chain_id"),f.get("token_address"),f.get("symbol"),f.get("source"),r.get("verdict"),r.get("confidence"),r.get("reason"),action,json.dumps(f,sort_keys=True),json.dumps(r,sort_keys=True))); db.commit(); return cur.lastrowid

def recent_seen(db,chain,address,seconds):
    row=db.execute("SELECT MAX(ts) FROM scans WHERE chain_id=? AND token_address=?",(chain,address)).fetchone(); return bool(row and row[0] and time.time()-row[0] < seconds)

def due_scans(db,horizon_seconds,limit=100):
    cutoff=time.time()-horizon_seconds
    return db.execute("SELECT s.id,s.ts,s.chain_id,s.token_address,s.features_json FROM scans s LEFT JOIN outcomes o ON o.scan_id=s.id AND o.horizon_seconds=? WHERE s.ts<=? AND o.id IS NULL ORDER BY s.ts LIMIT ?",(horizon_seconds,cutoff,limit)).fetchall()

def save_outcome(db,scan_id,horizon_seconds,price_then,observation):
    p=observation.get("price_usd") if observation else None; ret=((p/price_then)-1)*100 if p is not None and price_then not in (None,0) else None
    db.execute("INSERT OR IGNORE INTO outcomes(scan_id,observed_ts,horizon_seconds,price_then,price_now,return_pct,liquidity_now,volume_h24_now,pair_alive,observation_json) VALUES(?,?,?,?,?,?,?,?,?,?)",(scan_id,time.time(),horizon_seconds,price_then,p,ret,observation.get("liquidity_usd") if observation else None,observation.get("volume_h24") if observation else None,1 if observation else 0,json.dumps(observation or {},sort_keys=True))); db.commit()
