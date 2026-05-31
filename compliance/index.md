---
source_page_id: 163984
title: "06. Compliance"
---

# 06. Compliance

The compliance posture for cloud-hosted deployment of Oraclous. This section captures the formal control framework, the certifications we hold or pursue, and the customer-facing trust surface.

Self-hosted customers operate their own compliance posture; the platform exposes the substrate primitives (audit logs, isolation guarantees, encryption) they need to satisfy their auditors. See ADR-008 for the architectural commitment that drives both modes' guarantees from the same code.

## What's here

* [Compliance Posture Overview](https://oraclous.atlassian.net/wiki/spaces/OP/pages/196811) — high-level posture, target certifications, TSC-to-architecture mapping
* [ISO 27001 Programme](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557119) — the ISMS structure, Annex A scope, control owners, document set
* [SOC 2 Programme](https://oraclous.atlassian.net/wiki/spaces/OP/pages/196831) — Type I/II audit programme, TSC scope, evidence approach
* [Data Handling and Privacy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294916) — data classification, residency, retention, deletion, DPA
* [Audit Evidence and Records](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884800) — where evidence lives, retention, auditor access
* [Customer Trust Resources](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983061) — the customer-facing trust surface; what we publish, what's NDA-gated

## Status

Substantive compliance work begins as the cloud-hosted launch approaches (Phase 6+). The pages here are structured placeholders that fix the shape of each artifact before content lands. The architectural commitments (ADR-008, ADR-006, Section 6.5) are already locked and drive the framework.

## Posture summary

* **Target certifications**: ISO 27001 and SOC 2 Type II
* **In-scope deployment**: cloud-hosted only (self-hosted customers maintain their own posture)
* **Foundational principle**: architectural controls preferred over policy controls; provenance is evidence
* **Same-code guarantee**: self-hosted and cloud-hosted run the same enforcement code; cloud-hosted compliance evidence is indicative of self-hosted behaviour

## Operating model

* One unified control framework satisfies both ISO and SOC requirements; we do not maintain two separate control sets
* Every control has a named owner accountable for its design and effectiveness
* Evidence is generated as a side effect of operation (PR approvals, provenance, on-call records) — not as a separate compliance activity
* The risk register is the authoritative source for risk treatment; the certifications attest to the operating posture, not the absence of risk

## Related references

* **ADR-008** — Cloud-hosted mode with equivalent data sovereignty
* **ADR-006** — Organisation as outermost tenancy unit
* **Section 6.5** — Security threats and mitigations
* **Section 1** — Founding principles
* **Deployment — Cloud-hosted** (under 05. Operations) — the operational counterpart to this compliance posture
