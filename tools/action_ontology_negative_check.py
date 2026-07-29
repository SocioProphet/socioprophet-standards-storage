#!/usr/bin/env python3
"""Negative-case checks: every invalid fixture must be REJECTED by a checker.

The fixture list used to be four hardcoded loads. Adding an invalid fixture to
examples/action-ontology/ therefore did nothing — the file sat in the directory
looking like coverage while no checker ever opened it, which is the failure this
suite exists to catch, one level up.

So the cases are still declared explicitly (each fixture needs the RIGHT
checker, and a glob cannot infer that), but the set is now ratcheted: every
*invalid*.json in the directory must appear in CASES, or this exits non-zero.
A fixture added without a checker is a build failure rather than dead weight.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import action_ontology_bundle_check as bundle_check
import action_ontology_pattern_check as pattern_check

ROOT = Path(__file__).resolve().parents[1] / "examples" / "action-ontology"


def _bundle(doc):
    return bundle_check.check_bundle(doc)


def _contract_net(doc):
    return pattern_check.check_contract_net(doc)


def _pubsub(doc):
    return pattern_check.check_pubsub(doc)


def _bridge(doc):
    errs = []
    errs.extend(pattern_check.check_contract_net(doc))
    errs.extend(pattern_check.check_pubsub(doc))
    errs.extend(pattern_check.check_contractnet_pubsub_bridge(doc))
    return errs


# fixture -> (loader, checker)
CASES = {
    "invalid-missing-state-bundle.json": (bundle_check.load, _bundle),
    "contract-net-invalid-missing-done-ref.json": (pattern_check.load, _contract_net),
    "pubsub-invalid-missing-ack.json": (pattern_check.load, _pubsub),
    "contractnet-pubsub-invalid-missing-publish-bridge.json": (pattern_check.load, _bridge),
    # rescued from followup/action-ontology-failure-matrix-v0-2
    "contract-net-invalid-missing-bid.json": (pattern_check.load, _contract_net),
    "pubsub-invalid-duplicate-ack.json": (pattern_check.load, _pubsub),
    "pubsub-invalid-duplicate-publish.json": (pattern_check.load, _pubsub),
    "contractnet-pubsub-invalid-wrong-task-bridge.json": (pattern_check.load, _bridge),
}


def must_fail(name, errs):
    if not errs:
        print(f"ERR: {name} unexpectedly passed")
        raise SystemExit(2)
    print(f"OK: {name} failed as expected")


def assert_every_invalid_fixture_is_covered():
    """A fixture nothing opens is not coverage. Fail loudly rather than skip."""
    on_disk = {p.name for p in ROOT.glob("*invalid*.json")}
    uncovered = sorted(on_disk - set(CASES))
    if uncovered:
        print("ERR: invalid fixtures present but exercised by no checker:")
        for name in uncovered:
            print(f"  - {name}")
        raise SystemExit(2)
    missing = sorted(set(CASES) - {p.name for p in ROOT.glob("*.json")})
    if missing:
        print("ERR: CASES names fixtures that do not exist:")
        for name in missing:
            print(f"  - {name}")
        raise SystemExit(2)
    print(f"OK: all {len(on_disk)} invalid fixtures are covered")


def main():
    assert_every_invalid_fixture_is_covered()
    for name, (load, check) in CASES.items():
        must_fail(name, check(load(ROOT / name)))
    print("OK: action ontology negative-case checks passed")


if __name__ == "__main__":
    main()
