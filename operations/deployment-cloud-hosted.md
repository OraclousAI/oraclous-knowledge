---
confluence_id: "589868"
title: "Deployment — Cloud-hosted"
---

# Deployment — Cloud-hosted

Operational stance for the Oraclous-the-company cloud-hosted deployment. This page describes how Oraclous-the-company operates the platform on behalf of cloud-hosted customers, with equivalent data-sovereignty guarantees backed by formal compliance.

## Status

Placeholder — substantive content lands in Phase 6

Cloud-hosted deployment runs the same platform code as self-hosted (ADR-008). The architectural code path does not branch on deployment mode. What differs is who operates the platform and the compliance posture maintained around it.

## Operational posture

Oraclous-the-company operates cloud-hosted on the following principles:

* **Per-organisation isolation through** `organization_id` — every row in Postgres and every node in Neo4j is scoped to an organisation; the application enforces this at every query (ADR-006)
* **Per-organisation encryption keys** — credentials, sensitive artifacts, and provenance are encrypted with per-organisation KMS keys held with operator separation; Oraclous-the-company staff cannot decrypt customer data
* **Audited access** — any operational access to customer-affecting infrastructure is logged and reviewable
* **No data egress without explicit customer action** — model providers receive only the data the customer's harnesses send them, and only under the customer's BYOM configuration

## What this page will cover

* **Service-level commitments** — availability targets, response-time targets, support windows
* **Compliance posture** — ISO 27001 certification, SOC 2 Type II report, audit log access for customers
* **Infrastructure** — cloud provider, regions, multi-region availability, data residency options
* **Onboarding** — how a new organisation is provisioned, key generation, initial seeding, first user invite
* **Upgrade cadence** — automatic platform upgrades, maintenance windows, customer notification, rollback windows
* **Customer-facing operational artifacts** — status page, incident notifications, planned maintenance announcements
* **Data export and offboarding** — the OHM portability story applied operationally; customer-initiated full export; deletion timelines
* **Operator separation** — which Oraclous-the-company roles can access what, and what they cannot access (customer data)
* **Subprocessor list** — third-party services involved in operating cloud-hosted

## Boundary with the Compliance section

This page describes the operational stance. The formal control framework, audit evidence, and certification scopes live under 06. Compliance.

## Related references

* **Deployment Topology** — shared service architecture
* **06. Compliance** — formal compliance posture
* **ADR-006** — Organisation as outermost tenancy unit
* **ADR-008** — Cloud-hosted mode with equivalent data sovereignty
* **Section 6.5** — Security threats and mitigations (covers operator-trust threat class)
