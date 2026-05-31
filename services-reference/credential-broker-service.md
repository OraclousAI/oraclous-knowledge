---
confluence_id: "753812"
title: "credential-broker-service"
---

# credential-broker-service

**Layer:** 1 (Substrate) · **Port:** 8002 · **Status:** Production-grade (extension pending Phase 1)

## Purpose

`credential-broker-service` is the platform's secret keeper. It stores credentials (OAuth tokens, API keys, BYOM provider credentials, internal service tokens) under per-organisation encryption and resolves them on demand for authorised invocations. Credentials never leave the broker in plaintext.

## Responsibilities

* Encrypted credential storage (per-organisation encryption keys)
* OAuth token storage with refresh-flow management
* BYOM provider credentials (Anthropic, OpenAI-compatible, AWS Bedrock — ADR-007)
* Capability descriptors for external providers (Google Drive, Notion, PostgreSQL, MySQL, etc.)
* Per-invocation token resolution; tokens never cached outside the broker
* Delegated scope verification (Phase 1 extension)
* Internal credential brokerage for cross-workspace traversal (Phase 1 extension)

## Dependencies

* **Upstream:** Postgres (encrypted credential store), KMS (per-organisation encryption keys), `auth-service` (for principal-type verification)
* **Downstream consumers:** `harness-runtime-service`, `execution-engine-service`, every tool invocation path

## Security commitments

* Credentials stored encrypted at rest with per-organisation keys; cross-organisation decryption is structurally impossible
* Credentials never returned via API in plaintext; admins can verify existence and rotate, not retrieve
* In cloud mode: KMS separation ensures Oraclous-the-company cannot unilaterally decrypt (ADR-008)
* Outbound provider calls scoped to the requesting organisation; no code path can substitute another organisation's credentials

## Current state

Production-grade. Encrypted credential storage, OAuth refresh flows, and capability descriptors are all real and in use. The Phase 1 extension adds delegated identity scope verification and internal credential brokerage — both extensions, not replacements.

## Phase 1 deliverables

* Delegated identity tokens (member-to-agent scope delegation)
* Internal credential brokerage for cross-workspace traversal
* Multi-party authorisation for production credential rotation (cloud mode)

## Related

* ADR-007 — BYOM with Three Protocol Shapes
* ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty
* Section 6.5 — Threat 4 (identity confusion), Threat 10.3 (BYOM credential leakage), Threat 10.4 (operator-side attacks)
