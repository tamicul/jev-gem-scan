"""SQLite persistence for immutable scan snapshots."""
import json, os, sqlite3, time

def connect(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    db=sqlite3.connect(path); db.execute("PRAGMA journal_mode=WAL")
    db.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, chain_id TEXT, token_address TEXT, symbol TEXT, source TEXT, verdict TEXT, confidence REAL, reason TEXT, action TEXT, features_json TEXT NOT NULL, result_json TEXT NOT NULL)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_scans_token ON scans(chain_id,token_address,ts)"); db.commit(); return db

def save(db,f,r,action):
    db.execute("INSERT INTO scans(ts,chain_id,token_address,symbol,source,verdict,confidence,reason,action,features_json,result_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
      (time.time(),f.get("chain_id"),f.get("token_address"),f.get("symbol"),f.get("source"),r.get("verdict"),r.get("confidence"),r.get("reason"),action,json.dumps(f,sort_keys=True),json.dumps(r,sort_keys=True))); db.commit()

def recent_seen(db,chain,address,seconds):
    row=db.execute("SELECT MAX(ts) FROM scans WHERE chain_id=? AND token_address=?",(chain,address)).fetchone()
    return bool(row and row[0] and time.time()-row[0] < seconds)
