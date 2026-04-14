#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _index_actions(doc):
    return {a.get("id"): a for a in doc.get("actions", []) if a.get("id")}


def check_contract_net(doc):
    errs = []
    actions = doc.get("actions", [])
    traces = doc.get("traces", [])
    action_by_id = _index_actions(doc)

    cfps = [t for t in traces if t.get("pattern") == "ContractNet" and t.get("traceKind") == "cfp" and t.get("taskId")]
    if not cfps:
        return ["ContractNet: missing cfp trace with taskId"]

    task_id = cfps[0]["taskId"]
    bids = [t for t in traces if t.get("pattern") == "ContractNet" and t.get("traceKind") == "bid" and t.get("taskId") == task_id]
    if not bids:
        errs.append(f"ContractNet: missing bid trace for taskId={task_id}")

    awards = [a for a in actions if a.get("actionType") == "award"]
    if not awards:
        errs.append("ContractNet: missing award action")

    execs = [a for a in actions if a.get("actionType") == "executeTask"]
    if not execs:
        errs.append("ContractNet: missing executeTask action")
    exec_ids = {a.get("id") for a in execs if a.get("id")}

    dones = [t for t in traces if t.get("pattern") == "ContractNet" and t.get("traceKind") == "done" and t.get("taskId") == task_id]
    if not dones:
        errs.append(f"ContractNet: missing done trace for taskId={task_id}")
    elif not any(t.get("refAction") in exec_ids for t in dones):
        errs.append(f"ContractNet: done trace must reference executeTask action via refAction in {sorted(exec_ids)}")

    for d in dones:
        ref = d.get("refAction")
        if ref and ref not in action_by_id:
            errs.append(f"ContractNet: done trace refAction not found: {ref}")

    return errs


def check_pubsub(doc):
    errs = []
    actions = doc.get("actions", [])
    traces = doc.get("traces", [])
    action_by_id = _index_actions(doc)

    pubs = [t for t in traces if t.get("pattern") == "PubSub" and t.get("traceKind") == "publish" and t.get("topicId") and t.get("messageId")]
    if not pubs:
        return ["PubSub: missing publish trace with topicId and messageId"]

    for p in pubs:
        topic = p.get("topicId")
        msgid = p.get("messageId")
        consumes = [a for a in actions if a.get("actionType") == "consume"]
        if not consumes:
            errs.append(f"PubSub: missing consume action for topicId={topic}, messageId={msgid}")
            continue
        consume_ids = {a.get("id") for a in consumes if a.get("id")}
        acks = [t for t in traces if t.get("pattern") == "PubSub" and t.get("traceKind") == "ack" and t.get("topicId") == topic and t.get("messageId") == msgid]
        if not acks:
            errs.append(f"PubSub: missing ack trace for topicId={topic}, messageId={msgid}")
            continue
        if not any(t.get("refAction") in consume_ids for t in acks):
            errs.append(f"PubSub: ack trace must reference consume action via refAction in {sorted(consume_ids)} for topicId={topic}, messageId={msgid}")
        for a in acks:
            ref = a.get("refAction")
            if ref and ref not in action_by_id:
                errs.append(f"PubSub: ack trace refAction not found: {ref}")

    return errs


def check_contractnet_pubsub_bridge(doc):
    errs = []
    traces = doc.get("traces", [])
    cfps = [t for t in traces if t.get("pattern") == "ContractNet" and t.get("traceKind") == "cfp" and t.get("taskId")]
    if not cfps:
        return ["Bridge: missing ContractNet cfp trace with taskId"]
    for cfp in cfps:
        task_id = cfp.get("taskId")
        matching_publishes = [
            t for t in traces
            if t.get("pattern") == "PubSub" and t.get("traceKind") == "publish" and t.get("taskId") == task_id
        ]
        if not matching_publishes:
            errs.append(f"Bridge: missing PubSub publish trace for taskId={task_id}")
    return errs


def main():
    root = Path(__file__).resolve().parents[1] / "examples" / "action-ontology"
    failures = []

    contract_path = root / "contract-net-bundle.json"
    if contract_path.exists():
        errs = check_contract_net(load(contract_path))
        if errs:
            failures.append((contract_path.name, errs))

    pubsub_path = root / "pubsub-bundle.json"
    if pubsub_path.exists():
        errs = check_pubsub(load(pubsub_path))
        if errs:
            failures.append((pubsub_path.name, errs))

    bridge_path = root / "contractnet-pubsub-bridge-bundle.json"
    if bridge_path.exists():
        doc = load(bridge_path)
        errs = []
        errs.extend(check_contract_net(doc))
        errs.extend(check_pubsub(doc))
        errs.extend(check_contractnet_pubsub_bridge(doc))
        if errs:
            failures.append((bridge_path.name, errs))

    if failures:
        for name, errs in failures:
            print(f"ERR: {name}")
            for e in errs:
                print(f"  - {e}")
        sys.exit(2)

    print("OK: action ontology bootstrap pattern checks passed")


if __name__ == "__main__":
    main()
