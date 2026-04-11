#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_bundle(doc):
    errs = []
    for top in ["agents", "actionTypes", "states", "actions", "traces"]:
        if top not in doc or not isinstance(doc[top], list):
            errs.append(f"missing list: {top}")
    if errs:
        return errs

    state_ids = {x.get("id") for x in doc["states"]}
    action_ids = {x.get("id") for x in doc["actions"]}

    for s in doc["states"]:
        if not s.get("affordances"):
            errs.append(f"state {s.get('id')} missing affordances")

    for a in doc["actions"]:
        for req in ["id", "performedBy", "actionType", "fromState", "toState", "timestamp"]:
            if req not in a:
                errs.append(f"action missing {req}: {a}")
        if a.get("fromState") not in state_ids:
            errs.append(f"action {a.get('id')} fromState not found: {a.get('fromState')}")
        if a.get("toState") not in state_ids:
            errs.append(f"action {a.get('id')} toState not found: {a.get('toState')}")

    for t in doc["traces"]:
        for req in ["id", "pattern", "traceKind", "medium", "timestamp"]:
            if req not in t:
                errs.append(f"trace missing {req}: {t}")
        if "refAction" in t and t["refAction"] not in action_ids:
            errs.append(f"trace {t.get('id')} refAction not found: {t['refAction']}")

    return errs


def main():
    root = Path(__file__).resolve().parents[1] / "examples" / "action-ontology"
    failures = []
    for p in sorted(root.glob("*.json")):
        errs = check_bundle(load(p))
        if errs:
            failures.append((p.name, errs))
    if failures:
        for name, errs in failures:
            print(f"ERR: {name}")
            for e in errs:
                print(f"  - {e}")
        sys.exit(2)
    print("OK: action ontology bootstrap bundles passed lightweight checks")


if __name__ == "__main__":
    main()
