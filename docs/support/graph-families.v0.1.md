# Graph Families v0.1

## Purpose
The support cognition fabric uses three graph families from day one. This prevents retrieval, routing, and reuse from collapsing into flat chunk matching.

## 1. Case Graph
### Core nodes
- Case
- CaseSession
- Turn
- Cairn
- Recommendation
- RouteDecision
- AssignmentDecision
- Outcome

### Core edges
- `CASE_HAS_SESSION`
- `SESSION_HAS_TURN`
- `CASE_EMITS_CAIRN`
- `CASE_HAS_ROUTE_DECISION`
- `CASE_HAS_ASSIGNMENT_DECISION`
- `CASE_HAS_RECOMMENDATION`
- `CASE_RESOLVES_TO_OUTCOME`
- `TURN_UPDATES_CASE_STATE`

### Why it matters
This graph supports online re-scoring for route and assignment, replay, escalation analysis, and operator audit.

## 2. Asset Graph
### Core nodes
- Asset
- AssetChunk
- EvidencePacket
- PolicyDecision
- BenchmarkRun
- EvalSuite
- EvalCase

### Core edges
- `ASSET_HAS_CHUNK`
- `EVIDENCE_USES_ASSET`
- `CASE_USED_ASSET`
- `ASSET_GOVERNED_BY_POLICY`
- `ASSET_TESTED_IN_SUITE`
- `ASSET_PROMOTED_FROM_CASE`
- `ASSET_DEPRECATED_BY_POLICY`

### Why it matters
This graph enables structured evidence retrieval, asset reuse measurement, promotion control, and deprecation hygiene.

## 3. Product / Entity Graph
### Core nodes
- Product
- Version
- Service
- Component
- Entitlement
- Team
- Queue
- CustomerOrg

### Core edges
- `PRODUCT_HAS_VERSION`
- `SERVICE_OWNS_COMPONENT`
- `TEAM_OWNS_QUEUE`
- `QUEUE_HANDLES_CATEGORY`
- `CUSTOMER_HAS_ENTITLEMENT`
- `CASE_IMPACTS_COMPONENT`
- `KNOWN_ISSUE_AFFECTS_VERSION`

### Why it matters
This graph improves route accuracy, assignment scoring, and support reuse by preserving operational structure that flat text retrieval loses.

## Cross-Graph Rules
- no cross-tenant joins without explicit delegated policy
- every EvidencePacket span must resolve to an AssetChunk
- every RouteDecision and AssignmentDecision should preserve ranked alternatives
- every promoted Asset should maintain provenance links back to the originating Case and Cairn chain
