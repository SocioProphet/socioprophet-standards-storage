#!/usr/bin/env python3
"""Validate the vendor-adapter security checklist against package invariants.

This validator intentionally uses the Python standard library only. It checks the
minimum structural invariants needed to keep the checklist mechanically useful
without adding a repository dependency.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - dependency fallback path
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "docs" / "standards" / "control-plane" / "vendor-adapter-security"
CHECKLIST = PACKAGE / "vendor-adapter-security-controls-checklist.yaml"
SCHEMA = PACKAGE / "vendor-adapter-security-controls.schema.json"
MATRIX = PACKAGE / "verification-matrix.md"
EXPECTED_CONTROLS = {f"VAS-{idx:03d}" for idx in range(1, 13)}
EXPECTED_GATES = {f"AG-{idx:03d}" for idx in range(1, 8)}


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required for checklist validation")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} did not parse to a mapping")
    return data


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} did not parse to a JSON object")
    return data


def main() -> int:
    errors: list[str] = []

    for path in (CHECKLIST, SCHEMA, MATRIX):
        if not path.exists():
            errors.append(f"missing required artifact: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    checklist = _load_yaml(CHECKLIST)
    schema = _load_json(SCHEMA)
    matrix_text = MATRIX.read_text(encoding="utf-8")

    if checklist.get("artifact_type") != "security_control_checklist":
        errors.append("artifact_type must be security_control_checklist")

    controls = checklist.get("controls")
    if not isinstance(controls, list):
        errors.append("controls must be a list")
        controls = []

    control_ids = {item.get("id") for item in controls if isinstance(item, dict)}
    missing_controls = EXPECTED_CONTROLS - control_ids
    extra_controls = control_ids - EXPECTED_CONTROLS
    if missing_controls:
        errors.append(f"missing controls: {sorted(missing_controls)}")
    if extra_controls:
        errors.append(f"unexpected controls: {sorted(extra_controls)}")

    for item in controls:
        if not isinstance(item, dict):
            errors.append("control entry must be a mapping")
            continue
        cid = item.get("id")
        for field in ("title", "category", "priority", "normative_statement", "rationale", "check"):
            if field not in item:
                errors.append(f"{cid} missing field {field}")
        check = item.get("check")
        if isinstance(check, dict):
            for field in ("type", "logic", "evidence"):
                if field not in check:
                    errors.append(f"{cid} check missing field {field}")
        else:
            errors.append(f"{cid} check must be a mapping")
        if cid and cid not in matrix_text:
            errors.append(f"{cid} not referenced in verification matrix")

    gates = checklist.get("acceptance_gates")
    if not isinstance(gates, list):
        errors.append("acceptance_gates must be a list")
        gates = []
    gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
    missing_gates = EXPECTED_GATES - gate_ids
    extra_gates = gate_ids - EXPECTED_GATES
    if missing_gates:
        errors.append(f"missing acceptance gates: {sorted(missing_gates)}")
    if extra_gates:
        errors.append(f"unexpected acceptance gates: {sorted(extra_gates)}")

    for gate in gates:
        if not isinstance(gate, dict):
            errors.append("acceptance gate entry must be a mapping")
            continue
        gid = gate.get("id")
        maps_to = gate.get("maps_to")
        if not isinstance(maps_to, list) or not maps_to:
            errors.append(f"{gid} must map to at least one control")
            continue
        for cid in maps_to:
            if cid not in EXPECTED_CONTROLS:
                errors.append(f"{gid} maps to unknown control {cid}")
        if gid and gid not in matrix_text:
            errors.append(f"{gid} not referenced in verification matrix")

    required_schema_title = "VendorAdapterSecurityControlsChecklist"
    if schema.get("title") != required_schema_title:
        errors.append(f"schema title must be {required_schema_title}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("vendor adapter security controls validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
