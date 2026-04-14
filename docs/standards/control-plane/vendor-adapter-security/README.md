# Vendor Adapter Security Package

This directory defines the control-plane security package for vendor adapters and local model gateways in the SocioProphet standards canon.

## Scope

The package governs services that:
- expose local or remote inference through an adapter or gateway;
- translate one provider or model interface into another API surface;
- expose tool-calling or function-calling execution paths;
- attach debug, health, introspection, or administrative routes to the inference plane.

The package is intentionally vendor-neutral. It captures our own control requirements and implementation doctrine by hardening against externally observed failure patterns. It is not a remediation guide or advertisement for any third-party project.

## Package Contents

- `standard.md` — normative policy standard for vendor adapters and local model gateways
- `hardening-spec.md` — implementation-oriented doctrine and control mapping
- `local-model-gateway-security-baseline.md` — concise baseline for operator and implementation teams
- `vendor-adapter-security-controls-checklist.yaml` — machine-checkable control manifest

## Control Intent

The primary goal is to prevent semantic trust collapse between:
- model output;
- tool intent;
- executable capability scope;
- administrative or debug exposure.

The package therefore centers on:
- non-loopback authentication requirements;
- explicit capability scope;
- strict tool-intent validation;
- planning versus execution separation;
- routing integrity for tools and adapters;
- debug and administrative surface isolation;
- transport hygiene and protocol honesty;
- documentation and runtime consistency.

## Runtime Consumers

Expected downstream consumers include:
- `agentplane`
- `sociosphere`
- `prophet-platform`
- any local model gateway or vendor-adapter service that exposes tool-calling or administrative control surfaces.
