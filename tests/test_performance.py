import os,tempfile,unittest
from jev_gem_scan.database import connect,save,save_outcome
from jev_gem_scan.performance import performance_summary,confidence_buckets,paper_portfolio
from jev_gem_scan.dashboard import _performance_page,_paper_page

class PerformanceTests(unittest.TestCase):
    def setUp(self):
        fd,self.path=tempfile.mkstemp(suffix='.db'); os.close(fd); db=connect(self.path)
        for symbol,conf,ret in [('WIN',.91,50),('LOSS',.85,-20),('LOW',.65,10)]:
            sid=save(db,{'chain_id':'solana','token_address':symbol,'symbol':symbol,'source':'test','price_usd':1.0},{'verdict':'GEM','confidence':conf,'reason':'test','evidence':[]},'shadow')
            save_outcome(db,sid,86400,1.0,{'price_usd':1+ret/100,'liquidity_usd':10000,'volume_h24':1000})
        db.close()
    def tearDown(self):
        for suffix in ('','-wal','-shm'):
            try:os.remove(self.path+suffix)
            except (FileNotFoundError,PermissionError):pass
    def test_summary_and_buckets(self):
        p=performance_summary(self.path); self.assertEqual(p['horizons']['86400']['observations'],3); self.assertAlmostEqual(p['horizons']['86400']['win_rate_pct'],66.67)
        b=confidence_buckets(self.path); self.assertEqual(sum(x['observations'] for x in b),3)
    def test_paper_portfolio(self):
        p=paper_portfolio(self.path,10000,100,.80,86400); self.assertEqual(p['trades'],2); self.assertAlmostEqual(p['net_profit'],30.0); self.assertEqual(p['wins'],1)
    def test_pages_render(self):
        self.assertIn('Performance Lab',_performance_page(self.path)); self.assertIn('Paper Portfolio',_paper_page(self.path,{}))

if __name__=='__main__':unittest.main()
