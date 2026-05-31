---
source_page_id: 196831
title: "SOC 2 Programme"
---

# SOC 2 Programme

The SOC 2 Type II audit programme for cloud-hosted Oraclous. This page describes the trust service criteria in scope, evidence collection, and audit cadence.

## Status

Placeholder — formal programme work begins Phase 6+

## Scope

The SOC 2 report covers the **cloud-hosted Oraclous platform** as a service offering. The system description identifies the services, infrastructure, software, people, procedures, and data that comprise the cloud-hosted platform.

## Trust Service Criteria (TSC) in scope

* **Security** — common criteria; always in scope; covers logical access, change management, risk management, monitoring, communications
* **Availability** — included given customer expectations for cloud-hosted uptime
* **Confidentiality** — included given the platform processes customer-confidential information (credentials, knowledge graphs, harness manifests)
* **Processing Integrity** — included given the platform's mission-critical execution-fidelity guarantees (content-hashed manifests, deterministic capability resolution, full provenance)
* **Privacy** — included given the platform processes personal data on behalf of customers under their privacy obligations

## What this page will cover

* **System description** — the canonical SOC 2 system description (services, boundaries, components)
* **Control matrix** — mapping of each TSC criterion to one or more controls, with evidence sources
* **Complementary user entity controls** — what customers must do for the overall control objectives to be met
* **Subservice organisations** — third-party providers carved in or carved out of the audit (carve-in vs. carve-out approach to be decided)
* **Audit period** — the typical Type II observation period (6–12 months)
* **Auditor selection** — criteria, current auditor, engagement cadence
* **Findings and remediation** — process for handling findings during and after the audit
* **Customer access to the report** — NDA-gated distribution, refresh cadence

## Type I vs Type II

* **Type I** — point-in-time attestation of control design; precedes Type II by typically 6 months
* **Type II** — attestation of operational effectiveness over an observation period; the target end-state

The first audit will be Type I as a stepping stone; Type II follows after the initial observation period.

## Common controls with ISO 27001

Many controls satisfy both ISO 27001 Annex A and SOC 2 TSC requirements. The control framework is **unified** — we maintain one set of controls with mappings to both frameworks. This avoids:

* Duplicated documentation
* Conflicting control statements
* Double evidence collection

The mapping table (ISO Annex A control → SOC 2 TSC criterion) is maintained as part of the compliance evidence base.

## What auditors will look for

Auditors test design and (for Type II) operational effectiveness. Common evidence:

* Policy documents with approval signatures and review dates
* Access reviews (quarterly user-access certifications)
* Change management records (PR reviews, deploy approvals)
* Incident records and post-mortems
* Vulnerability management evidence (scan results, remediation timelines)
* Backup and restore test records
* Provenance queries demonstrating data-handling commitments

## Related references

* **Compliance Posture Overview** — high-level posture
* **ISO 27001 Programme** — overlapping certification framework
* **Section 6.5** — Security threats (drives security controls)
* **Incident Response** — incident handling under SOC 2
* **Deployment — Cloud-hosted** — operational stance audited under SOC 2
