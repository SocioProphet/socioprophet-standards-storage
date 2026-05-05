#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import validate_heller_contracts  # noqa: E402


class HellerContractValidationTest(unittest.TestCase):
    def test_heller_contract_bundle_validates(self) -> None:
        self.assertEqual(validate_heller_contracts.main(), 0)


if __name__ == "__main__":
    unittest.main()
