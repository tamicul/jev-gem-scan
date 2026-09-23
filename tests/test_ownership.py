import unittest
from unittest.mock import patch
from jev_gem_scan.providers.ownership import enrich_creator_ownership

class OwnershipTests(unittest.TestCase):
    @patch("jev_gem_scan.providers.ownership._post")
    def test_deployer_percentage_is_measured(self, post):
        post.return_value={"value":[{"account":{"data":{"parsed":{"info":{"tokenAmount":{"uiAmountString":"125"}}}}}}]}
        f={"chain_id":"solana","token_address":"MINT","probable_deployer":"OWNER","token_supply":1000}
        r=enrich_creator_ownership(f)
        self.assertEqual(r["dev_wallet_pct"],12.5)
        self.assertEqual(r["deployer_token_balance"],125.0)
        self.assertTrue(r["creator_ownership_rpc_ok"])

    @patch("jev_gem_scan.providers.ownership._post", side_effect=RuntimeError("rate limited"))
    def test_rpc_failure_does_not_invent_percentage(self, post):
        f={"chain_id":"solana","token_address":"MINT","probable_deployer":"OWNER","token_supply":1000,"dev_wallet_pct":None}
        r=enrich_creator_ownership(f)
        self.assertIsNone(r["dev_wallet_pct"])
        self.assertFalse(r["creator_ownership_rpc_ok"])

if __name__=="__main__": unittest.main()
