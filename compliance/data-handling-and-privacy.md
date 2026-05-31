---
confluence_id: "294916"
title: "Data Handling and Privacy"
---

# Data Handling and Privacy

How the platform handles customer data, what guarantees are made, and how data sovereignty is preserved. This page covers the platform's data-handling commitments under both deployment modes, with extra detail for cloud-hosted obligations.

## Status

Placeholder — formal content lands alongside compliance work in Phase 6+

## Foundational principles

The platform's data-handling posture is set by Architecture v1.1's founding principles (per Section 1) and reinforced by ADR-008:

1. **Customer data never leaves customer-isolated infrastructure** — applies in both modes
2. **Same code, same guarantees** — cloud-hosted runs the same enforcement code as self-hosted; what differs is who operates the deployment
3. **Per-organisation isolation** — `organization_id` is the outermost tenancy unit (ADR-006); all data is scoped to it
4. **No training on customer data** — Oraclous-the-company does not use customer data to train any model
5. **Customer-initiated egress only** — model providers receive only the data the customer's harnesses send them, under the customer's BYOM configuration

## Data classification

The platform handles several classes of customer data:

| Class | Examples | Encryption | Provenance tracked |
| --- | --- | --- | --- |
| Credentials | API keys, OAuth tokens, model provider keys | Per-org KMS; never logged | Yes (access events) |
| Knowledge artifacts | Knowledge graph nodes/edges, ingested documents | At rest with per-org keys | Yes (every read/write) |
| OHM manifests | Harness, agent, skill, tool, capability definitions | At rest with per-org keys | Yes (compile, commit, execute) |
| Task content | Task board entries, HITL responses | At rest with per-org keys | Yes |
| Provenance | The audit trail itself | At rest; immutable; long retention | (it is the trail) |
| Metering | Per-org usage counters | At rest | Yes |
| Operational telemetry | Logs, traces, metrics | At rest; bounded retention; PII redacted | No (not customer-domain) |

## What this page will cover

* **Data residency** — supported regions (cloud-hosted), how customers select region, data movement between regions
* **Encryption in detail** — at rest (KMS configuration), in transit (mTLS), in use (where applicable)
* **Retention policies** — defaults per data class, customer-configurable overrides, hard limits
* **Deletion** — when, how, and how long after a customer request before data is gone (including backups)
* **Customer data export** — how a customer extracts all their data (OHM artifacts + knowledge graphs + provenance)
* **Subprocessor list** — which third-party services touch customer data and what they do
* **DPA template** — the Data Processing Agreement for cloud-hosted customers
* **Cross-border data transfer** — Standard Contractual Clauses, region-pinning options
* **Personal data handling** — when customer data contains personal data; GDPR / CCPA obligations
* **Telemetry policy** — what we send to ourselves from customer deployments; opt-out where applicable
* **Customer privacy obligations** — what customers must do to keep their use of the platform compliant (e.g. inform their end users)

## Cloud-hosted specifics

In cloud-hosted mode, Oraclous-the-company is the data processor under most privacy regimes. The customer is the data controller. The relationship is governed by:

* A signed DPA
* Documented subprocessor list with notification of changes
* Defined incident notification timelines
* Customer-initiated audit rights (within reason and under NDA)

## Self-hosted specifics

In self-hosted mode, the customer is both controller and processor. The platform provides:

* Per-organisation isolation enforced by code
* Encryption primitives the customer configures
* Provenance for the customer's own audit purposes
* Export and deletion APIs

The customer maintains their own DPA framework with their end users.

## Related references

* **ADR-006** — Organisation as outermost tenancy unit (the isolation primitive)
* **ADR-008** — Equivalent data sovereignty in both modes
* **Section 1** — Founding principles (open source, no vendor lock-in, data ownership, data-sovereign deployment)
* **Section 6.5** — Security threats (covers data-handling threat families)
* **Section 7** — Portability story (OHM as the export format)
* **Deployment — Cloud-hosted** — operational stance for processor obligations
