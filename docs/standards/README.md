# Standards Index

This directory contains normative standards for the SocioProphet platform. Requirements use **MUST/SHOULD/MAY** language to define portable, vendor-neutral expectations.

## Current standards
- `000-platform-standards.md` — versioning, compatibility, and publishing rules.
- `005-design-philosophy.md` — platform design axioms and how they translate to standards.
- `006-ecosystem-repos-docs-milestones.md` — ecosystem repository roles and automation milestones.
- `010-storage-contexts.md` — canonical storage contexts and boundaries.
- `020-data-formats.md` — contract formats (Avro, Arrow/Parquet, JSON-LD).
- `030-service-interfaces-tritrpc.md` — RPC and eventing interface expectations.
- `040-observability-otel.md` — OpenTelemetry observability requirements.
- `041-runtime-control-plane-telemetry.md` — bootstrap, runtime policy, connector routing, client memory, telemetry, recovery, and redaction requirements.
- `050-security-oidc-policy.md` — identity, authorization, and policy (OIDC/mTLS baseline).
- `060-storage-decision-guidance.md` — when to add optional storage tiers.
- `070-graph-rdf-hypergraph.md` — RDF, property graph, and hypergraph (AtomSpace) standards.
- `080-knowledge-context.md` — knowledge context pointer to sibling standards repo.
- `143-operation-plane-artifact-storage-sync-and-redaction-v0-1.md` — Operation Plane artifact storage, local-first sync states, and diagnostic redaction requirements.

## FIPS / NIST Compliance Standards
- `090-fips-nist-compliance.md` — FIPS 140-2/140-3 cryptographic requirements and approved algorithms.
- `091-nist-800-53-control-mappings.md` — NIST 800-53 Rev. 5 control-to-implementation mappings (28 controls).
- `092-zero-trust-nist-800-207.md` — zero-trust architecture requirements (NIST SP 800-207).
- `093-forensic-audit-nist-800-88.md` — forensic-ready audit trail requirements (NIST SP 800-88/800-92).
- `094-data-layer-fips-compliance.md` — FIPS compliance for 6 data stores (PostgreSQL, MongoDB, Elasticsearch, Redis, MinIO, RocksDB).
- `095-orchestration-fips-compliance.md` — FIPS compliance for Kubernetes federation, Vault, and service mesh.
- `096-conversational-mesh-canonical-plane.md` — canonical sovereign conversation plane, trust tiers, fragility tiers, and internal/external room separation.
- `097-channel-ranking-and-routing.md` — default channel ranking, reply routing, and escalation posture for the conversational mesh.
- `098-profile-resolution-and-channel-upgrade.md` — canonical profile resolution, merge/split policy, and channel-upgrade rules.
- `099-telephony-ingress-and-handoff.md` — telephony ingress, call-state handling, and human handoff policy.
- `120-lawful-learning-calibration.md` — calibrated lawful learning conformance draft.

## Authoring guidance
When adding a new standard:
1. Start with a brief rationale.
2. Use unambiguous MUST/SHOULD/MAY statements.
3. Include versioning impact and migration notes.
4. Add a "Related Standards" section with cross-references.
5. Add an "Implementation Evidence" section linking to implementation files.
