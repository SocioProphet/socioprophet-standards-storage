# Descriptor and order examples v0.1

## Purpose

This note provides concrete examples for the initial AOKC contract pack so downstream implementations do not start from abstract schema names alone.

## Example: `GeneralDescriptor`

```json
{
  "apiVersion": "knowledge.socioprophet.org/v0.1",
  "kind": "GeneralDescriptor",
  "metadata": {
    "id": "asset:github:SocioProphet/agentplane/docs/system-space.md",
    "name": "system-space-strategy",
    "displayName": "System Space Strategy",
    "createdAt": "2026-04-05T00:00:00Z",
    "updatedAt": "2026-04-05T00:00:00Z",
    "version": "1.0.0",
    "labels": ["system-space", "execution", "evidence-forward"]
  },
  "spec": {
    "object": {
      "objectType": "DocumentAsset",
      "schemaRef": "schema:knowledge.asset.document/v0.1",
      "sourceSystem": "github",
      "sourceRef": {
        "repo": "SocioProphet/agentplane",
        "path": "docs/system-space.md",
        "ref": "main"
      },
      "contentHash": "sha256:example"
    },
    "relationships": {
      "domains": ["execution-control", "knowledge-commons"],
      "categories": ["strategy", "architecture-note"],
      "tasks": ["fleet-bootstrap", "run-replay-audit"],
      "owners": ["team:agentplane"],
      "contentSpaces": ["content-space:agentplane-system-space"],
      "repos": ["SocioProphet/agentplane"],
      "relatedObjects": ["bundle-schema-v0.1", "run-artifact-v0.1"]
    },
    "policies": {
      "visibility": "internal",
      "accessPolicyRef": "policy:knowledge/internal-read/v1",
      "promotionPolicyRef": "policy:knowledge/promotion/v1",
      "stewardReviewRequired": true,
      "agentActionsAllowed": ["retrieve", "bundle", "summarize", "propose-promotion"]
    },
    "provenance": {
      "hash": "sha256:example",
      "lineage": {
        "derivedFrom": [],
        "supersedes": []
      },
      "evidenceRefs": ["evidence:github-commit:example"],
      "stewards": ["team:agentplane"]
    },
    "presentations": {
      "para": {
        "projects": ["project:aokc-bootstrap"],
        "areas": ["area:agentplane"],
        "resources": ["resource:architecture"],
        "archives": []
      },
      "labels": ["strategy", "internal"]
    }
  }
}
```

## Example: `OrderDescriptor`

```json
{
  "apiVersion": "orders.socioprophet.org/v0.1",
  "kind": "OrderDescriptor",
  "metadata": {
    "id": "order:promotion:matrix-thread:incident-8421",
    "name": "promote-incident-thread-to-canonical-asset",
    "createdAt": "2026-04-05T00:00:00Z",
    "createdBy": "principal:matrix-user:alice",
    "labels": ["promotion", "matrix", "steward-review"]
  },
  "spec": {
    "orderType": "AssetPromotionOrder",
    "action": "promote_to_canonical_asset",
    "targets": [
      {
        "targetRef": "conversation:matrix:room123/thread456",
        "targetType": "ConversationAsset"
      }
    ],
    "inputs": {
      "requestedOutputType": "RunbookAsset",
      "contentSpace": "content-space:identity-auth",
      "destinationRepo": "SocioProphet/open-knowledge-commons"
    },
    "lifecycle": {
      "state": "requested",
      "allowedTransitions": [
        "classified",
        "validated",
        "needs-human-review",
        "approved",
        "published",
        "rejected",
        "archived"
      ]
    },
    "validation": {
      "requiredChecks": [
        "source-provenance-present",
        "policy-check-passed",
        "duplicate-check-complete",
        "human-review-complete"
      ],
      "humanGateRequired": true,
      "maxRunSeconds": 900
    },
    "policy": {
      "policyPackRef": "policy:knowledge/promotion/v1",
      "policyPackHash": "sha256:example",
      "errorPolicyRef": "policy:orders/retry-none-human-escalate/v1"
    },
    "outputs": {
      "expectedArtifacts": [
        "ValidationArtifact",
        "PromotionArtifact",
        "PublicationArtifact",
        "ReplayArtifact"
      ],
      "publishTargets": [
        "ck:canonical-store",
        "repo:SocioProphet/open-knowledge-commons",
        "matrix:review-room"
      ]
    }
  }
}
```

## Example: event progression

### `order.requested`
- order created for governed work
- references `orderId`, target refs, and optional `policyPackRef`

### `order.validated`
- validation checks completed
- references pass/fail state and evidence refs

### `asset.promoted`
- promotion completed
- links source descriptor, target descriptor, and order id

### `asset.used`
- retrieval or reuse completed in a real task or case
- links descriptor id to downstream outcome feedback

## Implementation readiness checklist

A downstream implementation is ready to claim support for the v0.1 contract pack when it can do all of the following:

1. validate a `GeneralDescriptor` against schema
2. validate an `OrderDescriptor` against schema
3. emit `order.requested` and `order.validated`
4. emit `asset.promoted` or `asset.used` when applicable
5. preserve stable `descriptorId` and `orderId` references across transport and execution layers
