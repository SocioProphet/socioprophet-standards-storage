# Build / Validation Lane

## Purpose
This pack now includes a deterministic code generation and validation lane so the standards bundle can be reproduced and checked before broader repo landing.

## Commands
```bash
cd support_cognition_fabric_v0_1 && ./tools/bootstrap_codegen_env.sh && make all
```

## Outputs
- `build/support-fabric.combined.v0.1.yaml`
- `build/generated/jsonschema/*.schema.json`
- `build/generated/support_contracts.desc` when protobuf compilation is available
- `build/generated/proto_python/*_pb2.py` when protobuf compilation is available
- `build/manifest.json`
- `build/validation-report.json`

## Validation Scope
- JSON Schema structure
- Fixture conformance for golden and adversarial bundles
- Protobuf compilation using `grpc_tools.protoc` with structural fallback only if compiler import fails
