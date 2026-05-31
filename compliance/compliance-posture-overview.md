# Compliance Posture Overview

**Status:** Placeholder — formal compliance work begins as cloud-hosted launch approaches (Phase 6+)

## Target certifications

- **ISO 27001** — information security management system
- **SOC 2 Type II** — operational effectiveness of trust service criteria over an audit period of 6–12 months

## Compliance principles

1. **Architectural controls over policy controls** — wherever a guarantee can be enforced by code, it is
2. **Provenance is evidence** — the substrate's provenance spine _is_ the audit trail
3. **Same code, same guarantees** — cloud-hosted runs the same code path as self-hosted
4. **No special compliance code paths** — there is no "audit mode"; the platform always operates the way the certifications require

## Trust service criteria → architecture mapping

| Criterion | Architectural enforcement |
| --- | --- |
| Security | ReBAC at the substrate; per-organisation KMS keys; mTLS; secret broker separation |
| Availability | Horizontal scaling per service; durable execution engine; defined RPO/RTO |
| Confidentiality | `organization_id` scoping at every query; per-org encryption; operator separation |
| Processing Integrity | Content-hashed OHM artifacts; manifest version pinning; full provenance |
| Privacy | Customer data never used for training; data export and deletion via OHM portability |
