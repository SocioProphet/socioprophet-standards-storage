#!/usr/bin/env python3
import csv, json, sys
from pathlib import Path

def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def compile_bundles(summary_csv, detail_csv, monitors_csv, tests_csv, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = load_csv(summary_csv)
    detail = {r["row_id"]: r for r in load_csv(detail_csv)}
    monitors = load_csv(monitors_csv)
    tests = load_csv(tests_csv)

    policy_bundle = []
    for row in summary:
        det = detail.get(row["row_id"], {})
        policy_bundle.append({
            "row_id": row["row_id"],
            "phase": row["phase"],
            "connector": row["connector"],
            "authority": row["authority"],
            "enforcement_point": row["enforcement_point"],
            "approval_mode": row["approval_mode"],
            "policy_version": row["policy_version"],
            "ship_blocker": row.get("ship_blocker", "UNKNOWN"),
            "preconditions": det.get("preconditions", ""),
            "rollback_path": det.get("rollback_path", ""),
            "runbook_id": row.get("runbook_id", ""),
        })
    with open(out_dir / "compiled_policy_bundle.json", "w") as f:
        json.dump(policy_bundle, f, indent=2)

    with open(out_dir / "compiled_monitor_bundle.json", "w") as f:
        json.dump(monitors, f, indent=2)

    with open(out_dir / "compiled_test_bundle.json", "w") as f:
        json.dump(tests, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("usage: matrix_compiler_v3.py summary.csv detail.csv monitors.csv tests.csv out_dir", file=sys.stderr)
        sys.exit(2)
    compile_bundles(*sys.argv[1:])
