from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / 'docs' / 'standards' / 'governance' / 'cso-partnerships' / 'templates'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Scaffold a governed CSO partnership pack.')
    parser.add_argument('--output', required=True)
    parser.add_argument('--name', default='Generated Governed CSO Pack')
    parser.add_argument('--force', action='store_true')
    return parser.parse_args()


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def write_json(path: Path, payload: dict) -> None:
    write_text(path, json.dumps(payload, indent=2) + '\n')


def main() -> int:
    args = parse_args()
    output = Path(args.output).expanduser().resolve()
    if output.exists():
        if not args.force:
            raise SystemExit(f'Output already exists: {output} (use --force to replace it)')
        shutil.rmtree(output)

    (output / 'records').mkdir(parents=True, exist_ok=True)
    (output / 'local').mkdir(parents=True, exist_ok=True)
    (output / 'templates').mkdir(parents=True, exist_ok=True)

    for src in sorted(TEMPLATE_DIR.glob('*.md')):
        shutil.copy2(src, output / 'templates' / src.name)

    partner_profile = {
        'legal_name': args.name,
        'aliases': [],
        'registration_status': 'draft',
        'jurisdiction': 'TBD',
        'year_founded': 'TBD',
        'contacts': [{'name': 'Primary contact', 'email': 'contact@example.org', 'phone': '+00 0000 0000'}],
        'mission': 'Describe the mission and intended public-interest role of the partner.',
        'constituency': 'Describe the primary constituency or stakeholder group.',
        'operating_geographies': ['TBD'],
        'safeguarding_status': 'developing',
        'data_classes_handled': ['TBD'],
        'civic_space_risks': ['TBD']
    }
    incident_record = {
        'incident_id': 'INC-STARTER-001',
        'date_reported': '2026-04-07',
        'incident_type': 'starter_case',
        'programme': args.name,
        'partner': args.name,
        'immediate_risk_to_people': 'Replace with real intake details if an incident occurs.',
        'data_involved': False,
        'safeguarding_involved': False,
        'civic_space_risk': False,
        'fraud_risk': False,
        'escalation_owner': 'Governance Lead',
        'status': 'open'
    }
    evidence_pack = "partner_profile: records/partner-profile.json\ninstrument_decision: templates/instrument-decision-worksheet.md\ncapacity_assessment: templates/capacity-assessment-sheet.md\nsafeguarding_record: local/safeguarding-record.md\ndata_schedule: local/data-schedule.md\napprovals:\n  - local/approvals.md\nreporting_calendar: local/reporting-calendar.md\ncloseout_note: local/closeout-note.md\n"
    readme = f"# {args.name}\n\nThis directory was scaffolded from the governed CSO partnership pack.\n\n## Next steps\n1. Fill records/partner-profile.json with real partner information.\n2. Complete the copied templates under templates/.\n3. Update records/evidence-pack.yaml so every reference reflects the live engagement.\n4. Record any real incident in records/incident-record.json or create a new incident file.\n5. Keep local evidence in local/ until it is archived elsewhere.\n"

    write_json(output / 'records' / 'partner-profile.json', partner_profile)
    write_json(output / 'records' / 'incident-record.json', incident_record)
    write_text(output / 'records' / 'evidence-pack.yaml', evidence_pack)
    write_text(output / 'README.md', readme)
    write_text(output / 'local' / 'safeguarding-record.md', '# Safeguarding record\n\nDocument safeguarding controls and escalation notes here.\n')
    write_text(output / 'local' / 'data-schedule.md', '# Data schedule\n\nDescribe data categories, handling rules, retention, and deletion here.\n')
    write_text(output / 'local' / 'approvals.md', '# Approvals\n\nRecord approval references, dates, and decision owners here.\n')
    write_text(output / 'local' / 'reporting-calendar.md', '# Reporting calendar\n\nRecord cadence, due dates, and accountable roles here.\n')
    write_text(output / 'local' / 'closeout-note.md', '# Closeout note\n\nCapture closure conditions, lessons, and final disposition here.\n')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
