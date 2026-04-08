from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / 'schemas' / 'governance' / 'cso-partnerships'
EXAMPLE_DIR = ROOT / 'examples' / 'governance' / 'cso-partnerships'
DOCS_DIR = ROOT / 'docs' / 'standards' / 'governance'

NEGATIVE_CASES = [
    (
        SCHEMA_DIR / 'partner-profile.schema.json',
        EXAMPLE_DIR / 'invalid-partner-profile-missing-legal-name.json',
        'partner profile missing legal_name',
    ),
    (
        SCHEMA_DIR / 'incident-record.schema.json',
        EXAMPLE_DIR / 'invalid-incident-record-bad-status.json',
        'incident record invalid status',
    ),
    (
        SCHEMA_DIR / 'evidence-pack.schema.yaml',
        EXAMPLE_DIR / 'invalid-evidence-pack-missing-capacity.yaml',
        'evidence pack missing capacity assessment',
    ),
]

MD_FILES = sorted(DOCS_DIR.rglob('*.md'))


def load_structured(path: Path) -> Any:
    text = path.read_text(encoding='utf-8')
    if path.suffix in {'.yaml', '.yml'}:
        return yaml.safe_load(text)
    return json.loads(text)


def expect_failure(schema_path: Path, example_path: Path, label: str) -> list[str]:
    schema = load_structured(schema_path)
    data = load_structured(example_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    if errors:
        return [f'PASS negative validation: {label} ({len(errors)} error(s))']
    return [f'FAIL negative validation unexpectedly passed: {label}']


def markdown_hygiene(path: Path) -> list[str]:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    first_nonempty = next((line for line in lines if line.strip()), '')
    issues: list[str] = []
    if not first_nonempty.startswith('#'):
        issues.append('first non-empty line is not a heading')
    if '\t' in text:
        issues.append('contains tab characters')
    if 'TODO' in text:
        issues.append('contains TODO marker')
    if len(text.strip()) < 40:
        issues.append('appears too small to be meaningful')
    if issues:
        return [f"FAIL markdown hygiene: {path.as_posix()} :: {'; '.join(issues)}"]
    return [f'PASS markdown hygiene: {path.as_posix()}']


def main() -> int:
    lines: list[str] = []
    ok = True

    for schema_path, example_path, label in NEGATIVE_CASES:
        if not schema_path.exists() or not example_path.exists():
            lines.append(f'FAIL missing negative case asset: {label}')
            ok = False
            continue
        result_lines = expect_failure(schema_path, example_path, label)
        lines.extend(result_lines)
        ok &= all(line.startswith('PASS') for line in result_lines)

    for md_path in MD_FILES:
        result_lines = markdown_hygiene(md_path)
        lines.extend(result_lines)
        ok &= all(line.startswith('PASS') for line in result_lines)

    print('\n'.join(lines))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
