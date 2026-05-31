---
source_page_id: 196811
title: "Compliance Posture Overview"
---

# Compliance Posture Overview

The high-level compliance posture for the Oraclous platform, applicable in cloud-hosted mode. This page summarises what we commit to, the certifications we hold (or are pursuing), and how compliance maps to the architecture.

## Status

Placeholder — formal compliance work begins as cloud-hosted launch approaches (Phase 6+)

## Compliance scope

Compliance applies to **cloud-hosted** deployment, where Oraclous-the-company is the operator. Self-hosted customers operate their own compliance posture; the platform exposes the substrate primitives (audit logs, isolation guarantees, encryption) they need to satisfy their own auditors. See ADR-008.

## Target certifications

The cloud-hosted launch targets two formal certifications (per ADR-008):

* **ISO 27001** — information security management system; covers risk management, access control, cryptography, supplier relationships, incident management, business continuity
* **SOC 2 Type II** — operational effectiveness of trust service criteria (Security, Availability, Confidentiality, Processing Integrity, Privacy) over an audit period of typically 6–12 months

Both certifications are pursued in parallel. The control framework is shared; the evidence collection is shared; only the audit form differs.

## Compliance principles

1. **Architectural controls over policy controls** — wherever a guarantee can be enforced by code or database constraint, it is. Policy-only controls (e.g. "operators shouldn't access customer data") are paired with technical enforcement (per-organisation KMS keys with operator separation).
2. **Provenance is evidence** — the substrate's provenance spine _is_ the audit trail. Auditors querying "show me every cross-organisation access in Q3" get a substrate query, not a log scrape.
3. **Same code, same guarantees** — self-hosted and cloud-hosted run the same code path. Compliance evidence collected in cloud-hosted is directly indicative of behaviour in self-hosted (where the customer is the operator).
4. **No special compliance code paths** — there is no "audit mode" or "compliance mode"; the platform always operates the way the certifications require.

## Trust service criteria → architecture mapping

| Criterion | Architectural enforcement |
| --- | --- |
| Security | ReBAC at the substrate; per-organisation KMS keys; mTLS between services; secret broker separation; audited operator access |
| Availability | Horizontal scaling per service; durable execution engine; defined RPO/RTO (see Deployment Topology) |
| Confidentiality | `organization_id` scoping enforced at every query; per-org encryption; operator separation; provenance-tracked access |
| Processing Integrity | Content-hashed OHM artifacts; manifest version pinning; deterministic capability resolution; full provenance per execution |
| Privacy | Customer data never used for training; data export and deletion via OHM portability; subprocessor list maintained |

## What this page will cover (when formalised)

* Current certification status with audit dates
* Scope statements for each certification
* Subprocessor list (cloud-hosted)
* Customer access to audit reports (NDA-gated where required)
* Annual recertification cadence
* How customers raise compliance questions
* Mapping table of controls to architecture
* Risk register summary (full risk register lives elsewhere with restricted access)

## Related references

* **ADR-008** — Cloud-hosted mode with equivalent data sovereignty (the architectural commitment driving compliance scope)
* **ADR-006** — Organisation as outermost tenancy unit (the isolation primitive)
* **Section 6.5** — Security threats and mitigations (drives the security controls)
* **Deployment — Cloud-hosted** — operational stance that compliance formalises
* **Incident Response** — incident handling under compliance obligations
