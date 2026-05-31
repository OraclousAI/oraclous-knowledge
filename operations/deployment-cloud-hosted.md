# Deployment — Cloud-hosted

Operational stance for the Oraclous-the-company cloud-hosted deployment.

**Status:** Placeholder — substantive content lands in Phase 6

Cloud-hosted deployment runs the same platform code as self-hosted (ADR-008). What differs is who operates the platform and the compliance posture maintained around it.

## Operational principles

- **Per-organisation isolation through** `organization_id`
- **Per-organisation encryption keys** — customer data encrypted; Oraclous staff cannot decrypt
- **No data egress without explicit customer action**
