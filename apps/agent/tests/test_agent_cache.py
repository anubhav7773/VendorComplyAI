# apps/agent/tests/test_agent_cache.py

import unittest
from decimal import Decimal
from src.local_cache import LocalCacheManager


class TestLocalCacheManager(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite database for deterministic isolation
        self.cache = LocalCacheManager(":memory:")

    def test_ledger_delta_filtering(self):
        sample_ledgers = [
            {"name": "Vendor A", "pan": "ABCDE1234F", "gstin": "27ABCDE1234F1Z5", "credit_days": 30},
            {"name": "Vendor B", "pan": "XYZAB9876C", "gstin": "27XYZAB9876C1Z1", "credit_days": 15}
        ]

        # First pass: All ledgers are new deltas
        deltas = self.cache.filter_and_stage_ledgers(sample_ledgers)
        self.assertEqual(len(deltas), 2)

        # Second pass: No modifications -> 0 deltas
        deltas_clean = self.cache.filter_and_stage_ledgers(sample_ledgers)
        self.assertEqual(len(deltas_clean), 0)

        # Third pass: Modify credit_days on Vendor A -> Exactly 1 delta
        sample_ledgers[0]["credit_days"] = 45
        deltas_modified = self.cache.filter_and_stage_ledgers(sample_ledgers)
        self.assertEqual(len(deltas_modified), 1)
        self.assertEqual(deltas_modified[0]["name"], "Vendor A")

    def test_voucher_delta_filtering(self):
        sample_vouchers = [
            {
                "voucher_number": "PUR/001",
                "invoice_reference": "INV-101",
                "bill_date": "2026-09-01",
                "party_name": "Vendor A",
                "amount": Decimal("50000.00"),
                "due_date": "2026-09-16"
            }
        ]

        deltas = self.cache.filter_and_stage_vouchers(sample_vouchers)
        self.assertEqual(len(deltas), 1)

        # Re-evaluating unmodified voucher yields 0 deltas
        deltas_clean = self.cache.filter_and_stage_vouchers(sample_vouchers)
        self.assertEqual(len(deltas_clean), 0)


if __name__ == "__main__":
    unittest.main()
