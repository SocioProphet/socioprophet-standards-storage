# Applying this overlay

This overlay is intended to be copied into the public `socioprophet-standards-storage` repository.

Suggested application order:
1. Copy ADR and standards documents.
2. Copy schema and conformance files.
3. Add positive and negative fixtures for each schema family.
4. Run the repository validation workflow.
5. Open follow-on PRs in implementation repos for channel adapters, routing policy, telephony ingress, and operator-room integration.

Follow-on implementation lanes likely include:
- Matrix homeserver and internal operator surfaces
- channel adapters / bridges for SMS-RCS, Telegram, Signal, and other ingress paths
- telephony/PSTN/SIP ingress controller
- profile-resolution and routing services
