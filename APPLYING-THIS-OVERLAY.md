# Applying this overlay

This overlay is intended to be copied into the root of the public `socioprophet-standards-storage` repository.

Suggested application order:
1. Copy ADR and standards documents.
2. Copy schema and example fixtures.
3. Replace `tools/validate.py`, `requirements-dev.txt`, `Makefile`, and `.github/workflows/validate.yml`.
4. Run `python3 -m pip install -r requirements-dev.txt`.
5. Run `make validate`.
6. Open PRs for follow-on work in the dependent repos (`identity-is-prime-reference`, `human-digital-twin`, `mcp-a2a-zero-trust`, `TriTRPC`, `agentplane`).
