#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
SCHEMAS = ROOT / "schemas"
CANONICAL_TAGS = {"#local_agent", "#fog_mesh", "#synthetic_data", "#secure_updates"}

FILES = {
    "decisions": ROOT / "registry" / "decisions.yaml",
    "krs": ROOT / "registry" / "krs.yaml",
    "nfrs": ROOT / "registry" / "nfrs.yaml",
    "owners": ROOT / "registry" / "owners.yaml",
    "control_plane_gates": ROOT / "registry" / "control_plane_gates.yaml",
}
SCHEMA_FILES = {
    "decisions": SCHEMAS / "decisions.schema.json",
    "krs": SCHEMAS / "krs.schema.json",
    "nfrs": SCHEMAS / "nfrs.schema.json",
    "owners": SCHEMAS / "owners.schema.json",
    "control_plane_gates": SCHEMAS / "control_plane_gates.schema.json",
}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text())


def load_json(path: Path):
    return json.loads(path.read_text())


def validate_against_schema(name: str, payload: dict, schema: dict) -> list[str]:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    msgs = []
    for e in errors:
        loc = "/".join(str(p) for p in e.path) or "<root>"
        msgs.append(f"{name}: schema error at {loc}: {e.message}")
    return msgs


def main() -> int:
    errors: list[str] = []
    payloads = {name: load_yaml(path) for name, path in FILES.items()}
    schemas = {name: load_json(path) for name, path in SCHEMA_FILES.items()}

    for name in FILES:
        errors.extend(validate_against_schema(name, payloads[name], schemas[name]))

    spec_ids = {payloads[name]["spec_id"] for name in payloads}
    versions = {payloads[name]["version"] for name in payloads}
    if len(spec_ids) != 1:
        errors.append(f"cross-file: spec_id mismatch: {sorted(spec_ids)}")
    if len(versions) != 1:
        errors.append(f"cross-file: version mismatch: {sorted(versions)}")

    for key in ("decisions", "krs", "nfrs"):
        seen = set()
        for item in payloads[key][key]:
            item_id = item["id"]
            if item_id in seen:
                errors.append(f"{key}: duplicate id {item_id}")
            seen.add(item_id)

    gate_ids = set()
    for gate in payloads["control_plane_gates"]["gates"]:
        gate_id = gate["id"]
        if gate_id in gate_ids:
            errors.append(f"control_plane_gates: duplicate id {gate_id}")
        gate_ids.add(gate_id)

    owner_roles = set()
    for item in payloads["owners"]["owners"]:
        owner_roles.add(item["primary_owner"])
        owner_roles.update(item["secondary_owners"])
    owner_roles.add("all_domain_owners")

    for dec in payloads["decisions"]["decisions"]:
        if dec["owner"] not in owner_roles:
            errors.append(f"decisions: unknown owner role {dec['owner']} in {dec['id']}")
    for kr in payloads["krs"]["krs"]:
        if kr["owner"] not in owner_roles:
            errors.append(f"krs: unknown owner role {kr['owner']} in {kr['id']}")
        if kr["tag"] is not None and kr["tag"] not in CANONICAL_TAGS:
            errors.append(f"krs: non-canonical tag {kr['tag']} in {kr['id']}")

    kr_ids = {kr["id"] for kr in payloads["krs"]["krs"]}
    nfr_ids = {nfr["id"] for nfr in payloads["nfrs"]["nfrs"]}
    for nfr in payloads["nfrs"]["nfrs"]:
        for kr_id in nfr["linked_krs"]:
            if kr_id not in kr_ids:
                errors.append(f"nfrs: unknown linked KR {kr_id} in {nfr['id']}")

    for gate in payloads["control_plane_gates"]["gates"]:
        for target in gate["enforces"]:
            if target.startswith("KR-") and target not in kr_ids:
                errors.append(f"control_plane_gates: unknown enforced KR {target} in {gate['id']}")
            if target.startswith("NFR-") and target not in nfr_ids:
                errors.append(f"control_plane_gates: unknown enforced NFR {target} in {gate['id']}")

    domains = set()
    for owner in payloads["owners"]["owners"]:
        domain = owner["domain"]
        if domain in domains:
            errors.append(f"owners: duplicate domain {domain}")
        domains.add(domain)

    tags_present = {kr["tag"] for kr in payloads["krs"]["krs"] if kr["tag"] is not None}
    missing = CANONICAL_TAGS - tags_present
    if missing:
        errors.append(f"krs: missing canonical tag coverage for {sorted(missing)}")

    if errors:
        print("VALIDATION: FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("VALIDATION: PASSED")
    print(f"spec_id={next(iter(spec_ids))}")
    print(f"version={next(iter(versions))}")
    print(f"decision_count={len(payloads['decisions']['decisions'])}")
    print(f"kr_count={len(payloads['krs']['krs'])}")
    print(f"nfr_count={len(payloads['nfrs']['nfrs'])}")
    print(f"gate_count={len(payloads['control_plane_gates']['gates'])}")
    print(f"owner_domain_count={len(payloads['owners']['owners'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
