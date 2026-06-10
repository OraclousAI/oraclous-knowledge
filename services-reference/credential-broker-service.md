---
confluence_id: "753812"
title: "credential-broker-service"
---

# credential-broker-service

**Layer:** 1 (Substrate) · **Port:** 8002 · **Status:** **Real — R3.5-complete, §22-signed-off.** Service #4: a real **AES-256-GCM** encrypted credential store with **runtime OAuth token resolution**, delegated-token issuance, and a credential-resolution seam (`/internal/runtime-token`, `/internal/resolve-credential`) consumed by the capability registry.

## What it is now

R3.5 rebuilt the broker real, end-to-end. Concrete and unhedged: an **AES-256-GCM** encrypted credential store — since **R7-SEC S5 ([ADR-020](../adr/adr-020-per-org-envelope-encryption-kms-held-kek.md)) a per-org envelope**: a KEK-wrapped data key (DEK) per `organisation_id` behind a `KmsProvider` seam, the org bound as AEAD associated data; `organisation_id` query-scoping (ADR-006) is the defense-in-depth tenancy anchor on top (no longer the only isolation), and **runtime OAuth token resolution** — handing a freshly-valid provider token to an authorised tool invocation, refreshing it transparently on expiry. `routes/` (`credential_routes`, `internal_routes`) → `services/` (`credential_service`, `credential_broker_service`, `delegation_service`, `refresh_client`) → repositories; `domain/` holds `providers`, `scopes`, `errors`. The smoke proves store → resolve → decrypt with **ciphertext (not plaintext) at rest in the DB**, plus delegated-token issue/validate. It serves [auth-service](auth-service.md) for principal verification and is consumed by [capability-registry-service](capability-registry-service.md).

## Purpose

`credential-broker-service` is the platform's **secret keeper**. It stores credentials — OAuth tokens, API keys, BYOM provider credentials, internal service tokens — under AES-256-GCM encryption (a **per-org DEK** behind a KMS seam since R7-SEC S5; `organisation_id` query-scoping on top), and resolves them on demand for authorised invocations. Credentials never leave the broker in plaintext.

## Responsibilities

* **Encrypted credential storage** with **AES-256-GCM** under a **per-org DEK** behind a KMS seam (R7-SEC S5, ADR-020 — `LocalKmsProvider` env-KEK default → `AwsKmsProvider` at the cloud cutover); `organisation_id` query-scoping (ADR-006) on top. The legacy single `ENCRYPTION_KEY` is now only the **v1-decrypt fallback** during the staged online migration
* **Runtime OAuth token resolution:** resolve a provider token for an authorised tool call, refreshing transparently on expiry (the refresh-flow runtime, distinct from the *login* OAuth in [auth-service](auth-service.md))
* BYOM provider credentials are stored as generic `api_key`/`raw` secrets in the same encrypted store and resolved via `/internal/resolve-credential`; the broker is provider-agnostic — no Anthropic/OpenAI/Bedrock-specific protocol logic lives here (the three-protocol-shape handling per ADR-007 lives in the consuming runtime/registry)
* Provider descriptors for external providers (Google — Drive/Docs/Sheets, Notion — pages/databases, GitHub — repos/issues/PRs) — `domain/providers.py`
* Per-invocation resolution; tokens never cached outside the broker
* Delegated-scope verification + delegated-token issuance for member→agent delegated calls
* Internal credential brokerage for cross-workspace traversal

## Login OAuth vs runtime OAuth

These are two different jobs and they live in two different services:

* **Login OAuth** (proving *who a human is*) — [auth-service](auth-service.md): Google / GitHub / Notion sign-in.
* **Runtime OAuth** (handing a *tool* a valid token) — **here**: store the provider token, refresh it, resolve it per invocation.

## Dependencies

* **Upstream:** Postgres (encrypted credential store + the `org_data_keys` DEK wraps), [auth-service](auth-service.md) (principal-type verification). Per-organisation key custody (the ADR-008 cloud-mode posture) is **now built — R7-SEC S5 / ADR-020**: a per-org DEK behind a `KmsProvider` seam (`local` env-KEK default — the local KEK is HKDF-derived from `ENCRYPTION_KEY`; `aws` selects a CMK in AWS KMS at the cloud cutover). The single `ENCRYPTION_KEY` remains the **v1-decrypt fallback** until the backfill (`tasks/backfill_envelope`) retires it (a later signed-off op). **Operational caveat:** the KEK must be stable — changing it (or the local-KEK derivation) after DEKs exist makes the wrapped DEKs un-unwrappable; rotation requires re-wrapping (deferred).
* **Downstream consumers:** [capability-registry-service](capability-registry-service.md) and every tool invocation path; reached **directly by host IP:port** until [application-gateway-service](application-gateway-service.md) fronts it

## Security commitments

* Credentials encrypted at rest with **AES-256-GCM** under a **per-org DEK** (R7-SEC S5 / ADR-020 — a KEK-wrapped data key per `organisation_id`, the org bound as AEAD AAD so a ciphertext is cryptographically pinned to its org); behind a `KmsProvider` seam. `organisation_id` query-scoping (ADR-006) is the defense-in-depth tenancy anchor on every read/write on top. The single `ENCRYPTION_KEY` remains the v1-decrypt fallback during the staged migration
* Credentials never returned via API in plaintext; admins verify existence and rotate, not retrieve
* Cloud mode: KMS separation so Oraclous-the-company cannot unilaterally decrypt (ADR-008) — a later, cloud-mode commitment, not in this build
* Outbound provider calls scoped to the requesting organisation; no code path can substitute another org's credentials

## Architecture conformance (ORAA-4 §21)

Layered shape: package root `services/credential-broker-service/src/oraclous_credential_broker_service/` with `routes/` (parse → one service call → HTTP map), all encryption/resolution/refresh logic in `services/`, the only Postgres/KMS access in `repositories/(+models.py)`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`. No logic in handlers; no non-`BaseModel` classes or DB drivers in `routes/`.

## Definition of Done (ORAA-4 §22) — MET

All 8 gates passed: structurally conformant; not hollow (`check_no_stubs` zero findings, `claimed_done: true`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: store → resolve → refresh, AES-256-GCM round-trip vs real Postgres via testcontainers, ciphertext-at-rest asserted, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh`, `r3_5_gate` job); Reza signed off.

## Related

* ADR-007 — BYOM with Three Protocol Shapes
* ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty (the KMS posture, later)
* [auth-service](auth-service.md) — login OAuth (distinct from this service's runtime OAuth)
* [capability-registry-service](capability-registry-service.md) — primary consumer (connector tool calls)
* Section 6.5 — Threat 4 (identity confusion), Threat 10.3 (BYOM credential leakage), Threat 10.4 (operator-side attacks)
