---
confluence_id: "753812"
title: "credential-broker-service"
---

# credential-broker-service

**Layer:** 1 (Substrate) · **Port:** 8002 · **Status:** R3.5 step 4 — rebuilt to a real **AES-256-GCM** encrypted credential store with **runtime OAuth token resolution**, built after the identity-org service is signed off and before the capability registry needs it.

## Honest current reality

The broker did not get the genuine R3.5 treatment until step 4. What R3.5 commits to here is concrete and unhedged: an **AES-256-GCM** encrypted credential store with per-organisation keys, and **runtime OAuth token resolution** — handing a freshly-valid provider token to an authorised tool invocation, refreshing it transparently when expired. It is rebuilt as **step 4** of the per-service order: after [identity-org-service](identity-org-service.md) (whose org boundary scopes the encryption) and before [capability-registry-service](capability-registry-service.md) (whose connector tool calls need the tokens).

## Purpose (R3.5 target)

`credential-broker-service` is the platform's **secret keeper**. It stores credentials — OAuth tokens, API keys, BYOM provider credentials, internal service tokens — under per-organisation AES-256-GCM encryption, and resolves them on demand for authorised invocations. Credentials never leave the broker in plaintext.

## Responsibilities (R3.5 target)

* **Encrypted credential storage** with **AES-256-GCM**, per-organisation keys
* **Runtime OAuth token resolution:** resolve a provider token for an authorised tool call, refreshing transparently on expiry (the refresh-flow runtime, distinct from the *login* OAuth in [identity-org-service](identity-org-service.md))
* BYOM provider credentials (Anthropic, OpenAI-compatible, AWS Bedrock — ADR-007)
* Capability descriptors for external providers (Google Drive, Notion, PostgreSQL, MySQL, etc.)
* Per-invocation resolution; tokens never cached outside the broker
* Delegated-scope verification for member→agent delegated calls
* Internal credential brokerage for cross-workspace traversal

## Login OAuth vs runtime OAuth

These are two different jobs and they live in two different services:

* **Login OAuth** (proving *who a human is*) — [identity-org-service](identity-org-service.md): Google / GitHub / Notion sign-in.
* **Runtime OAuth** (handing a *tool* a valid token) — **here**: store the provider token, refresh it, resolve it per invocation.

## Dependencies

* **Upstream:** Postgres (encrypted credential store), KMS (per-organisation encryption keys), [identity-org-service](identity-org-service.md) + [auth-service](auth-service.md) (principal-type verification for human and machine callers)
* **Downstream consumers:** [capability-registry-service](capability-registry-service.md) and every tool invocation path; reached **directly by host IP:port** until [application-gateway-service](application-gateway-service.md) exists

## Security commitments

* Credentials encrypted at rest with **AES-256-GCM**, per-organisation keys; cross-organisation decryption is structurally impossible
* Credentials never returned via API in plaintext; admins verify existence and rotate, not retrieve
* Cloud mode: KMS separation so Oraclous-the-company cannot unilaterally decrypt (ADR-008)
* Outbound provider calls scoped to the requesting organisation; no code path can substitute another org's credentials

## Architecture conformance (ORAA-4 §21)

Layered shape: package root `services/credential-broker-service/src/oraclous_credential_broker_service/` with `routes/` (parse → one service call → HTTP map), all encryption/resolution/refresh logic in `services/`, the only Postgres/KMS access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`. No logic in handlers; no non-`BaseModel` classes or DB drivers in `routes/`.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: store → resolve → refresh an OAuth token, AES-256-GCM round-trip vs real Postgres/KMS via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh`, run as the docker-required `r3_5_gate` job); Reza personally tests and signs off. Per §23: one service, ≤6 coarse vertical slices.

## Related

* ADR-007 — BYOM with Three Protocol Shapes
* ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty
* [identity-org-service](identity-org-service.md) — login OAuth (distinct from this service's runtime OAuth)
* [capability-registry-service](capability-registry-service.md) — primary consumer (connector tool calls)
* Section 6.5 — Threat 4 (identity confusion), Threat 10.3 (BYOM credential leakage), Threat 10.4 (operator-side attacks)
