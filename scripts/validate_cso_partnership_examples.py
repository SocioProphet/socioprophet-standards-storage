from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / 'schemas' / 'governance' / 'cso-partnerships'
EXAMPLE_DIR = ROOT / 'examples' / 'governance' / 'cso-partnerships'
DOCS_DIR = ROOT / 'docs' / 'standards' / 'governance' / 'cso-partnerships'

CASES = [
    (
        SCHEMA_DIR / 'partner-profile.schema.json',
        EXAMPLE_DIR / 'example-partner-profile.json',
        'partner profile',
    ),
    (
        SCHEMA_DIR / 'incident-record.schema.json',
        EXAMPLE_DIR / 'example-incident-record.json',
        'incident record',
    ),
    (
        SCHEMA_DIR / 'evidence-pack.schema.yaml',
        EXAMPLE_DIR / 'example-evidence-pack.yaml',
        'evidence pack',
    ),
]

REQUIRED_DOCS = [
    DOCS_DIR / 'README.md',
    DOCS_DIR / 'framework.md',
    DOCS_DIR / 'field-sheet.md',
    DOCS_DIR / 'templates' / 'partner-intake.md',
    DOCS_DIR / 'templates' / 'instrument-decision-worksheet.md',
    DOCS_DIR / 'templates' / 'incident-escalation-form.md',
    DOCS_DIR / 'templates' / 'evidence-pack-checklist.md',
    DOCS_DIR / 'templates' / 'capacity-assessment-sheet.md',
]


def load_structured(path: Path) -> Any:
    text = path.read_text(encoding='utf-8')
    if path.suffix in {'.yaml', '.yml'}:
        return yaml.safe_load(text)
    return json.loads(text)


def validate_case(schema_path: Path, example_path: Path, label: str) -> list[str]:
    schema = load_structured(schema_path)
    data = load_structured(example_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if not errors:
        return [f'PASS schema validation: {label}']
    lines = [f'FAIL schema validation: {label}']
    for err in errors:
        where = '.'.join(str(x) for x in err.path) or '<root>'
        lines.append(f'  - {where}: {err.message}')
    return lines


def check_required_docs() -> list[str]:
    lines: list[str] = []
    for path in REQUIRED_DOCS:
        if not path.exists():
            lines.append(f'FAIL missing required doc: {path.as_posix()}')
            continue
        size = path.stat().st_size
        if size < 40:
            lines.append(f'FAIL suspiciously small doc: {path.as_posix()} ({size} bytes)')
        else:
            lines.append(f'PASS required doc present: {path.as_posix()}')
    return lines


def main() -> int:
    lines: list[str] = []
    ok = True

    for schema_path, example_path, label in CASES:
        if not schema_path.exists():
            lines.append(f'FAIL missing schema: {schema_path.as_posix()}')
            ok = False
            continue
        if not example_path.exists():
            lines.append(f'FAIL missing example: {example_path.as_posix()}')
            ok = False
            continue
        result_lines = validate_case(schema_path, example_path, label)
        lines.extend(result_lines)
        ok &= all(line.startswith('PASS') for line in result_lines)

    doc_lines = check_required_docs()
    lines.extend(doc_lines)
    ok &= all(line.startswith('PASS') for line in doc_lines)

    print('\n'.join(lines))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
