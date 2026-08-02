#!/usr/bin/env python3
"""Guard: there is exactly ONE canonical ProofArtifact schema, and every other
proof-artifact schema in the repo references it (never re-declares the enum).

Remediation R2 / standards-storage#97. Before R2, four divergent proof-artifact
schemas existed, three of them copy-pasting the `epistemicLevel` enum verbatim.
This check FAILS if an unversioned / independent proof-artifact schema reappears
that neither IS the canonical nor $refs it — stopping the fork from ever growing
back.

Rules (scanned over schemas/** only; this script lives in tools/ and is therefore
SELF-EXCLUDING — it can never flag itself):
  1. Exactly one schema file may carry the canonical $id. That is the canonical.
  2. Every other file that looks like a proof-artifact schema (filename matches
     proof*artifact / proof_artifact, or its JSON title mentions ProofArtifact)
     MUST reference the canonical $id via $ref (directly or inside an allOf).
     A schema that does neither is a resurrected fork and fails the build.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CANONICAL_ID = "https://schemas.socioprophet.ai/proof-artifact/v1.json"
CANONICAL_REL = "schemas/proof-artifact/proof-artifact.schema.v1.json"

# Filenames that look like a proof-artifact schema.
NAME_RE = re.compile(r"proof[-_]?artifact", re.IGNORECASE)


def fail(msg: str) -> "None":
    print(f"ERR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def _iter_refs(node: object):
    """Yield every ``$ref`` string value anywhere in a parsed schema.

    Recurses through dicts and lists so that ``allOf[].$ref``, nested
    ``$defs``, and property-level refs are all found. Only real ``$ref``
    *values* are yielded — a canonical URL sitting in a ``description``,
    ``$comment``, ``title``, or example is NOT a ``$ref`` and is ignored.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                yield value
            else:
                yield from _iter_refs(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_refs(item)


def _refs_canonical(doc: object) -> bool:
    """True iff the schema has a real ``$ref`` resolving to the canonical.

    Matches the canonical root ``$id`` exactly or a JSON-pointer into it
    (``<canonical>#/...``). Substring presence anywhere else in the text is
    deliberately NOT accepted.
    """
    for ref in _iter_refs(doc):
        if ref == CANONICAL_ID or ref.startswith(CANONICAL_ID + "#"):
            return True
    return False


def _looks_like_proof_artifact(path: Path, doc: object) -> bool:
    if NAME_RE.search(path.name):
        return True
    if isinstance(doc, dict):
        title = str(doc.get("title", ""))
        if "proofartifact" in title.replace(" ", "").lower():
            return True
    return False


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    schemas_dir = root / "schemas"
    if not schemas_dir.is_dir():
        print("OK: no schemas/ directory — nothing to check")
        return 0

    canonicals: list[Path] = []
    forks_ok: list[Path] = []
    violations: list[str] = []

    for path in sorted(schemas_dir.rglob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
            doc = json.loads(text)
        except (OSError, json.JSONDecodeError) as exc:
            # Only care about parse failures for proof-artifact-named files.
            if NAME_RE.search(path.name):
                fail(f"{path.relative_to(root)}: not valid JSON ({exc})")
            continue

        this_id = doc.get("$id") if isinstance(doc, dict) else None
        if this_id == CANONICAL_ID:
            canonicals.append(path)
            continue

        if not _looks_like_proof_artifact(path, doc):
            continue

        # A proof-artifact schema that is NOT the canonical must reference it
        # with a REAL $ref (parsed), not merely mention the URL in prose.
        if _refs_canonical(doc):
            forks_ok.append(path)
        else:
            violations.append(
                f"{path.relative_to(root)}: independent proof-artifact schema that "
                f"neither is the canonical nor has a $ref resolving to it "
                f"({CANONICAL_ID}). Mentioning the URL in a description/comment is "
                f"not enough. Converge it via allOf:[{{$ref: canonical}}, ...]."
            )

    if len(canonicals) == 0:
        fail(
            f"no canonical proof-artifact schema found (expected $id {CANONICAL_ID} "
            f"at {CANONICAL_REL})"
        )
    if len(canonicals) > 1:
        listing = ", ".join(str(p.relative_to(root)) for p in canonicals)
        fail(f"multiple schemas claim the canonical $id {CANONICAL_ID}: {listing}")

    canonical_path = canonicals[0]
    if canonical_path.relative_to(root).as_posix() != CANONICAL_REL:
        fail(
            f"canonical $id lives at {canonical_path.relative_to(root)} but must be "
            f"{CANONICAL_REL}"
        )

    if violations:
        for v in violations:
            print(f"ERR: {v}", file=sys.stderr)
        fail(f"{len(violations)} resurrected/unconverged proof-artifact schema(s)")

    print(
        "OK: proof-artifact singleton guard passed "
        f"(1 canonical: {canonical_path.relative_to(root)}; "
        f"{len(forks_ok)} converged consumer schema(s) $ref it)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
