#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    print("ERR: missing dependency PyYAML (install requirements-dev.txt)", file=sys.stderr)
    raise SystemExit(2) from exc

try:
    from fastavro import parse_schema, schemaless_reader, schemaless_writer  # type: ignore
except Exception as exc:  # pragma: no cover
    print("ERR: missing dependency fastavro (install requirements-dev.txt)", file=sys.stderr)
    raise SystemExit(2) from exc


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "standards/semantic-layer/heller-schema-context-id-registry-v0.1.md"
EVENT_AVRO = ROOT / "schemas/avro/heller/v1/heller_event_envelope.avsc"
STATE_AVRO = ROOT / "schemas/avro/heller/v1/heller_state_snapshot.avsc"
EVENT_JSON_SCHEMA = ROOT / "schemas/jsonschema/heller/v1/heller_event_envelope.schema.json"
STATE_JSON_SCHEMA = ROOT / "schemas/jsonschema/heller/v1/heller_state_snapshot.schema.json"
EVENT_CATALOG = ROOT / "events/heller/v0/heller-events.v0.1.yaml"
EVENT_SAMPLE = ROOT / "examples/heller/v1/sample_event_envelope_v1.json"
STATE_SAMPLE = ROOT / "examples/heller/v1/sample_state_snapshot_v1.json"

EXPECTED_IDS = {
    "HELLER_EVENT_AVRO_v1": "69de72bfc1ff283618ff01dc8ad0d64c7254076db286a7ea0154be57e9851c58",
    "HELLER_STATE_AVRO_v1": "038609da12e4c7b6ace729ab53b73eb20654e3f86cb4ffb88944e3da4663290d",
    "HELLER_CONTEXT_v1": "5f7bb0541e2e79bd3d38f3d561df91ffc5135611543fa0cc65bc41214f8c5052",
}

REQUIRED_FILES = [
    REGISTRY,
    EVENT_AVRO,
    STATE_AVRO,
    EVENT_JSON_SCHEMA,
    STATE_JSON_SCHEMA,
    EVENT_CATALOG,
    EVENT_SAMPLE,
    STATE_SAMPLE,
]


def fail(msg: str) -> None:
    print(f"ERR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}")


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        fail(f"{path} is not valid YAML: {exc}")


def assert_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        fail(f"missing Heller contract files: {', '.join(missing)}")


def assert_registry_ids() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    for label, expected_hex in EXPECTED_IDS.items():
        derived = hashlib.sha3_256(label.encode("utf-8")).hexdigest()
        if derived != expected_hex:
            fail(f"internal validator bug: derived ID mismatch for {label}")
        if f"`{label}`" not in text:
            fail(f"registry missing label {label}")
        if expected_hex not in text:
            fail(f"registry missing derived ID for {label}")


def assert_schema_shapes() -> None:
    event_avro = load_json(EVENT_AVRO)
    state_avro = load_json(STATE_AVRO)
    event_json_schema = load_json(EVENT_JSON_SCHEMA)
    state_json_schema = load_json(STATE_JSON_SCHEMA)

    if event_avro.get("name") != "HellerEventEnvelope":
        fail("event Avro schema name must be HellerEventEnvelope")
    if state_avro.get("name") != "HellerStateSnapshot":
        fail("state Avro schema name must be HellerStateSnapshot")
    if event_avro.get("namespace") != "socioprophet.heller.v1":
        fail("event Avro namespace must be socioprophet.heller.v1")
    if state_avro.get("namespace") != "socioprophet.heller.v1":
        fail("state Avro namespace must be socioprophet.heller.v1")

    for path, schema in (
        (EVENT_JSON_SCHEMA, event_json_schema),
        (STATE_JSON_SCHEMA, state_json_schema),
    ):
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"{path.relative_to(ROOT)} must declare JSON Schema 2020-12")
        if schema.get("type") != "object":
            fail(f"{path.relative_to(ROOT)} must describe a top-level object")
        if not schema.get("required"):
            fail(f"{path.relative_to(ROOT)} must declare required fields")


def assert_event_catalog() -> None:
    catalog = load_yaml(EVENT_CATALOG)
    if not isinstance(catalog, dict):
        fail("Heller event catalog must be a YAML mapping")
    envelope = catalog.get("event_envelope")
    events = catalog.get("events")
    if not isinstance(envelope, dict):
        fail("Heller event catalog missing event_envelope mapping")
    if not isinstance(events, list) or not events:
        fail("Heller event catalog must include at least one event")

    required = envelope.get("required")
    if not isinstance(required, list):
        fail("Heller event catalog envelope.required must be a list")
    if "event_id" not in required or "payload" not in required:
        fail("Heller event catalog envelope must require event_id and payload")
    for entry in events:
        if not isinstance(entry, dict):
            fail("Heller event catalog event entries must be mappings")
        if not str(entry.get("type", "")).startswith("heller."):
            fail("Heller event type must start with heller.")
        if entry.get("payload_schema") != "socioprophet.heller.v1.HellerEventEnvelope":
            fail("Heller event payload_schema must reference the event envelope")


def normalize_event_sample(record: dict[str, Any]) -> dict[str, Any]:
    record = dict(record)
    record.setdefault("recipients", [])
    return record


def avro_roundtrip(schema_path: Path, record_path: Path, normalize: bool = False) -> None:
    schema = parse_schema(load_json(schema_path))
    record = load_json(record_path)
    if normalize:
        record = normalize_event_sample(record)

    buf = io.BytesIO()
    try:
        schemaless_writer(buf, schema, record)
        buf.seek(0)
        decoded = schemaless_reader(buf, schema)
    except Exception as exc:
        fail(f"Avro round-trip failed for {record_path.relative_to(ROOT)}: {exc}")

    if decoded != record:
        fail(f"Avro round-trip changed record for {record_path.relative_to(ROOT)}")


def main() -> int:
    assert_required_files()
    assert_registry_ids()
    assert_schema_shapes()
    assert_event_catalog()
    avro_roundtrip(EVENT_AVRO, EVENT_SAMPLE, normalize=True)
    avro_roundtrip(STATE_AVRO, STATE_SAMPLE, normalize=False)
    print("OK: Heller contract registry, schemas, catalog, samples, and Avro round-trips validate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
