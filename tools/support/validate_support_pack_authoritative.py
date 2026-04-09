from __future__ import annotations
from pathlib import Path
import json, re, hashlib
from typing import Any
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

BASE = Path(__file__).resolve().parents[2]
BUILD = BASE / 'build'
ROOT_SCHEMA = BUILD / 'generated' / 'jsonschema_root' / 'support-fabric.root.schema.json'
WRAPPERS = BUILD / 'generated' / 'jsonschema_wrappers'
GRAPH_DIR = BUILD / 'generated' / 'jsonschema_graph'
FIXTURES = BASE / 'fixtures' / 'support' / 'v0'
REPORT = BUILD / 'validation-report.authoritative.json'

results: dict[str, Any] = {'schema_checks': [], 'fixture_checks': [], 'proto_compile': {}, 'summary': {}}

root_schema = json.loads(ROOT_SCHEMA.read_text())
Draft202012Validator.check_schema(root_schema)
root_registry = Registry().with_resource(root_schema['$id'], Resource.from_contents(root_schema))
results['schema_checks'].append({'schema': ROOT_SCHEMA.name, 'status': 'valid'})

schemas = {}
for path in sorted(WRAPPERS.glob('*.schema.json')):
    data = json.loads(path.read_text())
    Draft202012Validator.check_schema(data)
    schemas[path.stem.replace('.schema', '')] = data
    results['schema_checks'].append({'schema': path.name, 'status': 'valid'})
for path in sorted(GRAPH_DIR.glob('*.schema.json')):
    data = json.loads(path.read_text())
    Draft202012Validator.check_schema(data)
    schemas[path.stem.replace('.schema', '')] = data
    results['schema_checks'].append({'schema': f'graph/{path.name}', 'status': 'valid'})

bundle_map = {
    'case': 'Case',
    'session': 'CaseSession',
    'turns': 'Turn',
    'assets': 'Asset',
    'evidence_packet': 'EvidencePacket',
    'confidence': 'ConfidenceObject',
    'route_decision': 'RouteDecision',
    'assignment_decision': 'AssignmentDecision',
    'recommendation': 'Recommendation',
    'policy_decision': 'PolicyDecision',
    'cairns': 'Cairn',
    'graph_nodes': 'GraphNode',
    'graph_edges': 'GraphEdge',
    'graph_queries': 'GraphTraversalQuery',
}

for fpath in sorted(FIXTURES.glob('*.json')):
    bundle = json.loads(fpath.read_text())
    for key, schema_name in bundle_map.items():
        if key not in bundle:
            continue
        schema = schemas[schema_name]
        registry = root_registry.with_resource(schema['$id'], Resource.from_contents(schema))
        validator = Draft202012Validator(schema, registry=registry)
        objs = bundle[key] if isinstance(bundle[key], list) else [bundle[key]]
        for idx, obj in enumerate(objs):
            errs = [e.message for e in validator.iter_errors(obj)]
            results['fixture_checks'].append({
                'fixture': fpath.name,
                'key': key,
                'index': idx,
                'schema': schema_name,
                'status': 'valid' if not errs else 'invalid',
                'errors': errs,
            })

common = (BASE / 'support_common.proto').read_text() if (BASE / 'support_common.proto').exists() else ''
services = (BASE / 'support_services.proto').read_text() if (BASE / 'support_services.proto').exists() else ''
msg_names = set(re.findall(r'^message\s+(\w+)', common, flags=re.M)) | set(re.findall(r'^message\s+(\w+)', services, flags=re.M))
missing = []
for req, resp in re.findall(r'rpc\s+\w+\((\w+)\)\s+returns\s+\((\w+)\)', services):
    if req not in msg_names:
        missing.append(req)
    if resp not in msg_names:
        missing.append(resp)

desc = BUILD / 'generated' / 'support_contracts.desc'
results['proto_compile'] = {
    'compiler': 'structural_lint',
    'status': 'valid' if not missing else 'invalid',
    'missing_symbols': sorted(set(missing)),
    'descriptor_present': desc.exists(),
    'descriptor_sha256': hashlib.sha256(desc.read_bytes()).hexdigest() if desc.exists() else None,
}

results['summary'] = {
    'schemas_validated': len(results['schema_checks']),
    'fixture_objects_checked': len(results['fixture_checks']),
    'invalid_fixture_objects': sum(1 for x in results['fixture_checks'] if x['status'] != 'valid'),
    'proto_status': results['proto_compile'].get('status'),
}
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(results, indent=2), encoding='utf-8')
print(json.dumps(results['summary'], indent=2))
