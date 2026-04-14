#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import action_ontology_bundle_check as bundle_check
import action_ontology_pattern_check as pattern_check

ROOT = Path(__file__).resolve().parents[1] / "examples" / "action-ontology"


def must_fail(name, errs):
    if not errs:
        print(f"ERR: {name} unexpectedly passed")
        raise SystemExit(2)
    print(f"OK: {name} failed as expected")


def main():
    doc = bundle_check.load(ROOT / "invalid-missing-state-bundle.json")
    must_fail("invalid-missing-state-bundle.json", bundle_check.check_bundle(doc))

    doc = pattern_check.load(ROOT / "contract-net-invalid-missing-done-ref.json")
    must_fail("contract-net-invalid-missing-done-ref.json", pattern_check.check_contract_net(doc))

    doc = pattern_check.load(ROOT / "pubsub-invalid-missing-ack.json")
    must_fail("pubsub-invalid-missing-ack.json", pattern_check.check_pubsub(doc))

    doc = pattern_check.load(ROOT / "contractnet-pubsub-invalid-missing-publish-bridge.json")
    errs = []
    errs.extend(pattern_check.check_contract_net(doc))
    errs.extend(pattern_check.check_pubsub(doc))
    errs.extend(pattern_check.check_contractnet_pubsub_bridge(doc))
    must_fail("contractnet-pubsub-invalid-missing-publish-bridge.json", errs)

    print("OK: action ontology negative-case checks passed")


if __name__ == "__main__":
    main()
