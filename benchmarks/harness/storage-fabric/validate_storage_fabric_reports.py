#!/usr/bin/env python3
"""Minimal storage-fabric report validator.

This intentionally performs lightweight structural validation so the scaffold can run
without extra dependencies. Full JSON Schema validation can be added once the harness
is promoted beyond scaffold status.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPORT_REQUIREMENTS = {
    "storage": {"generatedAt", "suiteVersion", "results", "summaryByRole"},
    "service": {"generatedAt", "packageVersion", "executionMode", "engineStatus", "results"},
    "history": {"generatedAt", "packageVersion", "baselineVersion", "summary"},
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate(report_type: str, path: Path) -> list[str]:
    data = load_json(path)
    required = REPORT_REQUIREMENTS[report_type]
    missing = sorted(required - set(data))
    errors: list[str] = []
    if missing:
        errors.append(f"{path}: missing required keys: {', '.join(missing)}")
    if report_type == "service":
        statuses = {str(item.get("status", "")) for item in data.get("results", []) if isinstance(item, dict)}
        invalid = sorted(status for status in statuses if status and status not in {"PASS", "FAIL", "SKIP"})
        if invalid:
            errors.append(f"{path}: invalid service result statuses: {', '.join(invalid)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report_type", choices=sorted(REPORT_REQUIREMENTS))
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    errors = validate(args.report_type, args.report)
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"ok: {args.report_type} report {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
