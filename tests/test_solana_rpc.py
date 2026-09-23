import unittest
from unittest.mock import patch
from jev_gem_scan.providers import solana_rpc

class SolanaRpcTests(unittest.TestCase):
 def test_non_solana_unchanged(self):
  f={"chain_id":"base","token_address":"x"}; self.assertEqual(solana_rpc.enrich_solana(f),f)
 @patch("jev_gem_scan.providers.solana_rpc._post")
 def test_native_features(self,p):
  p.side_effect=[
   {"value":{"data":{"parsed":{"info":{"mintAuthority":None,"freezeAuthority":None,"decimals":2,"supply":"10000"}}}}},
   {"value":[{"uiAmountString":"20"},{"uiAmountString":"10"}]}
  ]
  r=solana_rpc.enrich_solana({"chain_id":"solana","token_address":"mint"})
  self.assertTrue(r["contract_renounced"]); self.assertEqual(r["token_supply"],100.0)
  self.assertEqual(r["top10_holder_pct"],30.0); self.assertTrue(r["solana_rpc_ok"])
 @patch("jev_gem_scan.providers.solana_rpc._post",side_effect=RuntimeError("rate limit"))
 def test_rpc_failure_is_unknown_not_fabricated(self,p):
  r=solana_rpc.enrich_solana({"chain_id":"solana","token_address":"mint"})
  self.assertFalse(r["solana_rpc_ok"]); self.assertNotIn("contract_renounced",r)

if __name__=="__main__": unittest.main()
