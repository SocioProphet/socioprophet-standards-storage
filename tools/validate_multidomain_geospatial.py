#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_TOP = [
    "record_type",
    "record_id",
    "source",
    "observed_at",
    "geometry_ref",
    "provenance",
    "governance",
]

REQUIRED_SOURCE = ["source_id", "source_type", "license_ref"]
REQUIRED_GEOMETRY = ["crs", "encoding"]
REQUIRED_PROVENANCE = ["chain", "derived_from"]
REQUIRED_GOVERNANCE = ["privacy_tier", "safety_tier", "retention_tier", "redistribution"]

RECORD_TYPES = {
    "SpaceAssetRecord",
    "OrbitEphemerisRecord",
    "GroundStationContactEvent",
    "TelemetryObservation",
    "EarthObservationProductRecord",
    "VesselTrackObservation",
    "AirTrackObservation",
    "SensorObservationEnvelope",
    "MultiDomainFusionEvent",
    "SensitiveGeoPolicyRecord",
    "MapLayerManifest",
    "RuntimeBoundaryEvidenceRecord",
}


def fail(msg: str) -> None:
    print(f"ERR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def require_keys(obj: dict, keys: list[str], where: str) -> None:
    missing = [key for key in keys if key not in obj]
    if missing:
        fail(f"{where}: missing required keys: {', '.join(missing)}")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path}: expected top-level object")
    return data


def validate_fixture(path: Path) -> None:
    data = load_json(path)
    require_keys(data, REQUIRED_TOP, str(path))
    if data["record_type"] not in RECORD_TYPES:
        fail(f"{path}: unsupported record_type {data['record_type']!r}")
    if not isinstance(data.get("source"), dict):
        fail(f"{path}: source must be object")
    require_keys(data["source"], REQUIRED_SOURCE, f"{path}:source")
    if not isinstance(data.get("geometry_ref"), dict):
        fail(f"{path}: geometry_ref must be object")
    require_keys(data["geometry_ref"], REQUIRED_GEOMETRY, f"{path}:geometry_ref")
    if not isinstance(data.get("provenance"), dict):
        fail(f"{path}: provenance must be object")
    require_keys(data["provenance"], REQUIRED_PROVENANCE, f"{path}:provenance")
    if not isinstance(data["provenance"].get("chain"), list):
        fail(f"{path}: provenance.chain must be array")
    if not isinstance(data["provenance"].get("derived_from"), list):
        fail(f"{path}: provenance.derived_from must be array")
    if not isinstance(data.get("governance"), dict):
        fail(f"{path}: governance must be object")
    require_keys(data["governance"], REQUIRED_GOVERNANCE, f"{path}:governance")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    schema = root / "schemas/jsonschema/multidomain/multidomain_geospatial_record.v1.schema.json"
    if not schema.exists():
        fail(f"missing schema: {schema.relative_to(root)}")
    load_json(schema)

    fixture_dir = root / "fixtures/multidomain"
    fixtures = sorted(fixture_dir.glob("*.json")) if fixture_dir.exists() else []
    if not fixtures:
        fail("no multidomain fixtures found")
    for fixture in fixtures:
        validate_fixture(fixture)
    print(f"OK: validated {len(fixtures)} multidomain geospatial fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
