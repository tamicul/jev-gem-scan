import random,unittest
from jev_gem_scan.generator import generate_launch
from jev_gem_scan.jev_stub import call_jev_api
from jev_gem_scan.router import route_launch
class ProtocolTests(unittest.TestCase):
 def test_simulator_reproducible(self):
  a,b=random.Random(7),random.Random(7); self.assertEqual(generate_launch(a),generate_launch(b))
 def test_unknown_facts_neutral(self):
  f={"honeypot_flag":None,"dev_wallet_pct":None,"top10_holder_pct":None,"liquidity_lock_days":None,"contract_renounced":None,"social_age_days":None,"liquidity_usd":None,"volume_h1":None,"buys_h1":0,"sells_h1":0}
  r=call_jev_api(f,random.Random(1)); self.assertEqual(r["verdict"],"GEM"); self.assertEqual(r["confidence"],.5)
 def test_router_preserves_jev_verdict(self):
  f={"honeypot_flag":True,"dev_wallet_pct":50,"top10_holder_pct":70,"liquidity_lock_days":0,"contract_renounced":False,"social_age_days":0}
  d=call_jev_api(f,random.Random(1)); r,a=route_launch(f,{"enabled":True,"bypass_jev":False,"mode":"shadow"},random.Random(1)); self.assertEqual(d["verdict"],r["verdict"]); self.assertEqual(a,"shadow")
if __name__=="__main__": unittest.main()
