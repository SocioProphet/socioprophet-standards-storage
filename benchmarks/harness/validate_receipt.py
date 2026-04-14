#!/usr/bin/env python3
"""Minimal receipt validator for the MAIPJ receipt slice.

Usage:
  python benchmarks/harness/validate_receipt.py <receipt.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_TOP = {
    "receipt_id",
    "trace_id",
    "task",
    "context",
    "placement",
    "model_runtime",
    "energy_j",
    "outcome",
    "evidence",
    "replay",
}


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python benchmarks/harness/validate_receipt.py <receipt.json>")
    data = json.loads(Path(sys.argv[1]).read_text())
    missing = sorted(REQUIRED_TOP - set(data.keys()))
    if missing:
        raise SystemExit(f"missing top-level keys: {missing}")
    energy = data.get("energy_j", {})
    required_energy = ["inference", "data_move", "network", "storage", "control", "idle", "total"]
    missing_energy = [k for k in required_energy if k not in energy]
    if missing_energy:
        raise SystemExit(f"missing energy keys: {missing_energy}")
    print("[receipt-validate] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
