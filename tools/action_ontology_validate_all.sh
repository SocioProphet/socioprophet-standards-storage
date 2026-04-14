#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 "$ROOT/tools/action_ontology_bundle_check.py"
python3 "$ROOT/tools/action_ontology_pattern_check.py"
python3 "$ROOT/tools/action_ontology_negative_check.py"

echo "OK: Action Ontology bootstrap validation suite passed"
