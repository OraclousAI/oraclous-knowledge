---
source_page_id: 557119
title: "ISO 27001 Programme"
---

# ISO 27001 Programme

The Information Security Management System (ISMS) for cloud-hosted Oraclous. This page describes how the ISO 27001 programme is structured, what's in scope, and how evidence is collected.

## Status

Placeholder — formal programme work begins Phase 6+

## Scope

The ISMS scope is the **cloud-hosted Oraclous platform and the supporting Oraclous-the-company operations that touch it**. Out of scope: self-hosted customer deployments (those are the customer's ISMS), marketing/sales infrastructure that does not touch customer data.

## What this page will cover

* **Statement of Applicability (SoA)** — which Annex A controls apply, which are excluded, and why
* **ISMS structure** — roles (CISO, ISMS owner, control owners), governance cadence, management review
* **Risk assessment methodology** — how we identify, score, and treat risks
* **Risk treatment plan** — current top risks and their treatment status (link to risk register)
* **Internal audit programme** — cadence, scope rotation, finding tracking
* **Certification cycle** — Stage 1 audit date, Stage 2 audit date, surveillance audits, recertification
* **Control evidence** — pointers to where evidence lives (each control has a designated evidence source)

## Annex A control families (target coverage)

The 93 controls in ISO/IEC 27001:2022 Annex A are organised into four themes:

* **Organisational controls (37)** — policies, roles, supplier management, threat intelligence, ICT readiness
* **People controls (8)** — screening, terms of employment, awareness, disciplinary process, remote working
* **Physical controls (14)** — perimeters, secure areas, equipment, cabling, maintenance, disposal
* **Technological controls (34)** — endpoint protection, access control, cryptography, secure development, logging, capacity, malware protection, vulnerability management, configuration, backups, network security

Many technological controls map directly to architecture elements documented elsewhere (Section 6.5, ADR-006, ADR-008). The ISMS documentation describes the policy framework; the architecture documentation describes the implementation.

## Control owners

Every Annex A control in scope has a named owner. Owners are responsible for:

* Maintaining the control's design (the policy, procedure, or technical configuration)
* Ensuring evidence of operation is collected
* Reporting on control health at management review
* Owning corrective actions on findings

The control owner matrix is maintained as part of the ISMS documentation.

## Documents maintained under this programme

* Information Security Policy
* Acceptable Use Policy
* Access Control Policy
* Cryptography Policy
* Supplier Relationship Policy
* Information Security Incident Management Policy
* Business Continuity Policy
* Secure Development Policy
* Data Classification and Handling Policy
* Risk Management Methodology

Each is owned, reviewed annually, and approved at the appropriate level.

## Related references

* **Compliance Posture Overview** — high-level posture this programme implements
* **SOC 2 Programme** — overlapping but distinct certification framework
* **Section 6.5** — Security threats (drives the risk register)
* **Incident Response** — incident management process aligned with ISMS requirements
* **ADR-008** — architectural commitment to cloud-hosted compliance posture
