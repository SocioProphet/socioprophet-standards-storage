# 140. Action Ontology Transport and Consumer Surfaces (v0.1)

## Purpose

This note explains how the Action Ontology bootstrap package relates to transport and runtime consumers.

## Authority chain

- semantic ontology source: `SocioProphet/ontogenesis`
- bootstrap standards pack: `SocioProphet/socioprophet-standards-storage`
- deterministic wire contract: `SocioProphet/TriTRPC`
- runtime consumer / execution control plane: `SocioProphet/agentplane`

## Transport stance

The Action Ontology package does not define a new wire protocol.

Instead, it defines an object and pattern surface that MAY be carried over existing transport contracts such as TriTRPC or event-bus topics.

## Consumer stance

A runtime consumer such as `agentplane` SHOULD treat this package as:

- semantic guidance for action/state/trace concepts
- a source of portable bundle/example shapes
- a coordination pattern vocabulary for protocol validation

A runtime consumer SHOULD NOT treat this package as a replacement for runtime execution artifacts, placement decisions, run artifacts, replay artifacts, or executor-control semantics.

## Summary

The Action Ontology package supplies semantic and bootstrap coordination contracts. Transport and runtime execution remain external concerns owned by the appropriate repositories.