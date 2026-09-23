import json, os, tempfile, unittest
from jev_gem_scan.database import connect, save, save_outcome
from jev_gem_scan.dashboard import summary, recent, detail

class DashboardTests(unittest.TestCase):
    def setUp(self):
        fd,self.path=tempfile.mkstemp(suffix=".db"); os.close(fd)
        db=connect(self.path)
        f={"chain_id":"solana","token_address":"mint1","symbol":"TEST","source":"test","price_usd":1.0,"liquidity_usd":100000,"dev_wallet_pct":2.0}
        r={"verdict":"GEM","confidence":0.91,"reason":"test evidence","score":1.2,"evidence":[{"signal":"dev_wallet_pct","value":2,"delta":0.25}]}
        self.scan_id=save(db,f,r,"alert"); save_outcome(db,self.scan_id,3600,1.0,{"price_usd":1.5,"liquidity_usd":120000,"volume_h24":500000}); db.close()
    def tearDown(self):
        for p in (self.path,self.path+"-wal",self.path+"-shm"):
            try: os.remove(p)
            except FileNotFoundError: pass
    def test_summary(self):
        s=summary(self.path); self.assertEqual(s["total"],1); self.assertEqual(s["gems"],1); self.assertEqual(s["alerts"],1)
    def test_recent_and_detail(self):
        self.assertEqual(recent(self.path)[0]["symbol"],"TEST")
        d=detail(self.path,self.scan_id); self.assertEqual(d["result"]["verdict"],"GEM"); self.assertAlmostEqual(d["outcomes"][0]["return_pct"],50.0)

if __name__=="__main__": unittest.main()
