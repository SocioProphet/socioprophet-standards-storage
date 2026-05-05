#!/usr/bin/env python3
"""Dependency-free semantic retrieval reference harness.

The harness demonstrates the standards pattern: compact retrieval finds
candidates; structural verification decides whether a family mapping is credible.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from typing import Any, Iterable, Mapping

COMPAT = {
    "string": {"string", "unknown"},
    "integer": {"integer", "number", "unknown"},
    "number": {"integer", "number", "unknown"},
    "boolean": {"boolean", "unknown"},
    "date": {"date", "timestamp", "string", "unknown"},
    "timestamp": {"timestamp", "date", "string", "unknown"},
    "binary": {"binary", "unknown"},
    "json": {"json", "string", "unknown"},
    "unknown": {"string", "integer", "number", "boolean", "date", "timestamp", "binary", "json", "unknown"},
}


def now_z() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def tokens(value: str) -> list[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(value)).lower()
    return [part for part in re.split(r"[^a-z0-9]+", value) if part]


def token_set(values: Iterable[Any]) -> set[str]:
    out: set[str] = set()
    for value in values:
        out.update(tokens(str(value)))
    return out


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    lset, rset = set(left), set(right)
    if not lset and not rset:
        return 1.0
    if not lset or not rset:
        return 0.0
    return len(lset & rset) / len(lset | rset)


def digest(values: Iterable[str]) -> str:
    material = "\n".join(sorted(set(values))).encode("utf-8")
    return hashlib.blake2b(material, digest_size=16).hexdigest()


def profile_views(profile: Mapping[str, Any]) -> dict[str, set[str]]:
    lexical = profile.get("lexicalView", {})
    value = profile.get("valueProfileView", {})
    structural = profile.get("structuralView", {})
    usage = profile.get("usageLineageView", {})
    cols = list(lexical.get("columnNames", []))
    value_cols = list(value.get("columns", []))
    key_cols = [c for key in structural.get("candidateKeys", []) for c in key]
    lineage = list(usage.get("upstreamArtifactRefs", [])) + list(usage.get("downstreamArtifactRefs", [])) + list(usage.get("joinNeighborhoods", []))
    return {
        "lexical": token_set([lexical.get("artifactName", ""), *cols, *lexical.get("normalizedTokens", [])]),
        "valueProfile": token_set([*cols, *[c.get("primitiveType", "unknown") for c in value_cols]]),
        "structural": token_set([structural.get("rowGrainHypothesis") or "", *key_cols]),
        "usageLineage": token_set(lineage),
    }


def family_views(family: Mapping[str, Any]) -> dict[str, set[str]]:
    slots = list(family.get("slots", []))
    aliases = [a for s in slots for a in s.get("aliases", [])]
    slot_names = [s.get("slotName", "") for s in slots]
    types = [t for s in slots for t in s.get("acceptedPrimitiveTypes", [])]
    keys = [c for k in family.get("keyExpectations", []) for c in k.get("columns", [])]
    return {
        "lexical": token_set([family.get("familyName", ""), *slot_names, *aliases]),
        "valueProfile": token_set([*slot_names, *types]),
        "structural": token_set([family.get("grainExpectation") or "", *keys]),
        "usageLineage": token_set(family.get("commonJoinNeighborhoods", [])),
    }


def compact_hashes(obj: Mapping[str, Any], kind: str) -> dict[str, str]:
    views = profile_views(obj) if kind == "profile" else family_views(obj)
    return {name: digest(values) for name, values in views.items()}


def compatible(source_type: str, accepted: list[str]) -> bool:
    allowed: set[str] = set()
    for target in accepted:
        allowed |= COMPAT.get(target, {target})
    return source_type in allowed


def slot_score(column: Mapping[str, Any], slot: Mapping[str, Any]) -> tuple[float, list[str], list[str]]:
    col_tokens = token_set([column.get("name", ""), column.get("semanticTypeHint") or ""])
    slot_tokens = token_set([slot.get("slotName", ""), slot.get("semanticType") or "", *slot.get("aliases", [])])
    lex = jaccard(col_tokens, slot_tokens)
    type_ok = compatible(str(column.get("primitiveType", "unknown")), list(slot.get("acceptedPrimitiveTypes", ["unknown"])))
    unit = slot.get("unit")
    unit_ok = unit is None or column.get("unit") == unit
    null_max = slot.get("expectedNullRatioMax")
    null_ok = not isinstance(null_max, (int, float)) or float(column.get("nullRatio", 1.0)) <= float(null_max)
    unique_min = slot.get("expectedUniquenessRatioMin")
    unique_ok = not isinstance(unique_min, (int, float)) or float(column.get("uniquenessRatio", 0.0)) >= float(unique_min)
    score = (0.40 * lex) + (0.30 if type_ok else 0.0) + (0.10 if unit_ok else 0.0) + (0.10 if null_ok else 0.0) + (0.10 if unique_ok else 0.0)
    pos = []
    neg = []
    if lex >= 0.30:
        pos.append("lexical_or_alias_overlap")
    else:
        neg.append("weak_lexical_slot_overlap")
    if type_ok:
        pos.append("primitive_type_compatible")
    else:
        neg.append("primitive_type_incompatible")
    if unit_ok:
        pos.append("unit_compatible")
    else:
        neg.append("unit_mismatch")
    if null_ok:
        pos.append("null_ratio_within_expectation")
    else:
        neg.append("null_ratio_exceeds_expectation")
    if unique_ok:
        pos.append("uniqueness_ratio_within_expectation")
    else:
        neg.append("uniqueness_ratio_below_expectation")
    return round(score, 6), sorted(set(pos)), sorted(set(neg))


def align(profile: Mapping[str, Any], family: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    cols = list(profile.get("valueProfileView", {}).get("columns", []))
    slots = list(family.get("slots", []))
    candidates = []
    for c in cols:
        for s in slots:
            score, pos, neg = slot_score(c, s)
            candidates.append((score, c.get("name", ""), s.get("slotName", ""), pos, neg))
    candidates.sort(reverse=True, key=lambda row: row[0])
    used_cols, used_slots = set(), set()
    mappings, pos_all, neg_all = [], [], []
    for score, col, slot, pos, neg in candidates:
        if score < 0.45 or col in used_cols or slot in used_slots:
            continue
        used_cols.add(col)
        used_slots.add(slot)
        mappings.append({"sourceField": col, "targetSlot": slot, "confidence": score, "reasonCodes": pos})
        pos_all.extend(pos)
        neg_all.extend(neg)
    required = {s.get("slotName") for s in slots if s.get("required")}
    for missing in sorted(required - used_slots):
        neg_all.append(f"missing_required_slot:{missing}")
    return mappings, sorted(set(pos_all)), sorted(set(neg_all))


def verify(profile: Mapping[str, Any], family: Mapping[str, Any], decided_at: str | None = None) -> dict[str, Any]:
    mappings, pos, neg = align(profile, family)
    pv, fv = profile_views(profile), family_views(family)
    scores = {name: jaccard(pv[name], fv[name]) for name in pv}
    required = {s.get("slotName") for s in family.get("slots", []) if s.get("required")}
    mapped = {m["targetSlot"] for m in mappings}
    coverage = len(required & mapped) / len(required) if required else 1.0
    hard = [] if coverage >= 1.0 else ["required_slot_coverage_incomplete"]
    confidence = max(0.0, min(1.0, (0.20 * scores["lexical"] + 0.20 * scores["valueProfile"] + 0.25 * scores["structural"] + 0.10 * scores["usageLineage"] + 0.25 * coverage) - 0.15 * len(hard)))
    state = "accepted" if confidence >= 0.82 and not hard else "proposed" if confidence >= 0.55 else "rejected"
    source = profile.get("artifactRef", profile.get("profileId", "unknown"))
    target = family.get("familyId", family.get("familyName", "unknown"))
    material = {"source": source, "target": target, "mappings": mappings, "confidence": round(confidence, 6), "hard": hard}
    decision_id = "mapdec-" + hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()[:16]
    return {
        "decisionId": decision_id,
        "sourceArtifactRef": source,
        "targetRef": target,
        "targetKind": "family",
        "decisionState": state,
        "confidenceScore": round(confidence, 6),
        "fieldMappings": mappings,
        "reasonCodes": sorted(set(pos + [f"{k}_score:{v:.3f}" for k, v in scores.items()] + [f"required_slot_coverage:{coverage:.3f}"])),
        "negativeReasonCodes": sorted(set(neg)),
        "hardIncompatibilities": hard,
        "verifierVersion": "semantic-retrieval-reference-v1",
        "profileExtractionVersion": str(profile.get("profileVersion", "unknown")),
        "reviewerRef": None,
        "automationRef": "semantic_retrieval_reference.py",
        "decidedAt": decided_at or now_z(),
        "supersedesDecisionRef": None,
        "evidenceRefs": [],
    }


def candidate(profile: Mapping[str, Any], family: Mapping[str, Any], at: str | None = None) -> dict[str, Any]:
    ph, fh = compact_hashes(profile, "profile"), compact_hashes(family, "family")
    distances = {k: (int(ph[k], 16) ^ int(fh[k], 16)).bit_count() for k in ph}
    sim = {k: round(max(0.0, 1.0 - d / 128.0), 6) for k, d in distances.items()}
    source = profile.get("artifactRef", profile.get("profileId", "unknown"))
    target = family.get("familyId", family.get("familyName", "unknown"))
    material = {"source": source, "target": target, "scores": sim}
    return {
        "candidateId": "cand-" + hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()[:16],
        "queryArtifactRef": source,
        "targetRef": target,
        "targetKind": "family",
        "retrievalVersion": "semantic-retrieval-reference-v1",
        "retrievedAt": at or now_z(),
        "rank": 1,
        "scores": {
            "overall": round(sum(sim.values()) / len(sim), 6),
            "lexical": sim["lexical"],
            "valueProfile": sim["valueProfile"],
            "structural": sim["structural"],
            "usageLineage": sim["usageLineage"],
            "hammingDistance": int(round(sum(distances.values()) / len(distances))),
        },
        "reasonCodes": [f"{k}_hamming:{v}" for k, v in sorted(distances.items())],
        "retrievalEvidenceRefs": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    hp = sub.add_parser("hash-profile")
    hp.add_argument("--profile", required=True)
    vf = sub.add_parser("verify-family")
    vf.add_argument("--profile", required=True)
    vf.add_argument("--family", required=True)
    vf.add_argument("--candidate", action="store_true")
    vf.add_argument("--decided-at", default=None)
    args = parser.parse_args()
    if args.cmd == "hash-profile":
        print(json.dumps(compact_hashes(load(args.profile), "profile"), indent=2, sort_keys=True))
    elif args.cmd == "verify-family":
        p, f = load(args.profile), load(args.family)
        print(json.dumps(candidate(p, f, args.decided_at) if args.candidate else verify(p, f, args.decided_at), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
