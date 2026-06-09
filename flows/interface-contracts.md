---
confluence_id: "1277953"
title: "Interface Contracts"
---

# Interface Contracts

This page is the single canonical home for every API shape that crosses the repo boundary, until R6 when the gateway OpenAPI spec takes over. Record once, link many.

## How to use this page

Each contract below corresponds to a `Contract` issue in Jira. The Jira issue tracks the _agreement process_; this page records the _agreed shape_. When a Contract is marked Done, its shape must be frozen here and a shared fixture must encode it.

## Index

| Contract | Jira | Status | Canonical shape |
| --- | --- | --- | --- |
| Auth token claims | — ⚠ (see note) | Done | See §1 |
| OHM manifest envelope | — ⚠ (see note) | Done | See §2 |
| Gateway error envelope | [ORA-56](https://oraclous.atlassian.net/browse/ORA-56) | AGREED & enforced (fixture [ORA-53](https://oraclous.atlassian.net/browse/ORA-53) Done); implementing stories **deferred** — BE ([ORA-54](https://oraclous.atlassian.net/browse/ORA-54)) → R6, FE ([ORA-55](https://oraclous.atlassian.net/browse/ORA-55)) → R-Frontend | See §3 |
| Webhook ingress → engine + broker (R6 S7) | — (sole-worker; #209/#210/#211) | Done & live (GW-13 + engine smoke) | See §S7 |
| Org-role claim + `X-Principal-Org-Role` (R7-SEC S2) | — (sole-worker; #217) | Done & live (GW-17) | See §S2-ROLE |

> ⚠ **Index integrity (31 May 2026, solution-architect).** Of the three rows, only the Gateway error envelope has a real `Contract`-type Jira issue: [**ORA-56**](https://oraclous.atlassian.net/browse/ORA-56), backfilled 31 May 2026. The keys previously shown for the other two rows were **wrong** — "ORA-12" is the R0.5 0d substrate-test-harness story and "ORA-19" is the deferred B1 isolation story; neither the Auth-token-claims nor the OHM-manifest-envelope shape has a Contract issue yet (the same applies to the `(ORA-12)`/`(ORA-19)` keys in the §1/§2 headers below). Backfilling those two is **pending** — the 31 May coordinator decision limited this pass to the gateway envelope. Until then, treat §1/§2 as shape-of-record without a tracking Contract.

## §1 — Auth token claims (ORA-12 ⚠ — wrong key; see Index note)

Frozen. See ADR-004.

```
{ "sub": "usr_...", "org": "org_...", "roles": [...], "exp": 1234567890 }
```

## §2 — OHM manifest envelope (ORA-19 ⚠ — wrong key; see Index note)

Frozen. See OHM Spec page.

## §3 — Gateway error envelope ([ORA-56](https://oraclous.atlassian.net/browse/ORA-56))

Owner: security-architect (dominant risk: sensitive-data leakage in error bodies). The gateway produces this envelope for **every** 4xx/5xx response; the frontend api-client consumes it.

> **Status (31 May 2026): agreed and enforced, implementation deferred.** The shape is frozen and the shared-fixture enforcement ([ORA-53](https://oraclous.atlassian.net/browse/ORA-53)) has **landed (Done)**. Both implementing stories are **deferred to their host services**, which do not exist yet: [ORA-54](https://oraclous.atlassian.net/browse/ORA-54) (gateway emits the envelope) → **R6** (the application gateway is the R6 Application Gateway extraction), and [ORA-55](https://oraclous.atlassian.net/browse/ORA-55) (api-client parses it) → **R-Frontend** (after the FE foundation / clone-and-refactor lands). Contract [ORA-56](https://oraclous.atlassian.net/browse/ORA-56) stays **open** as the tracker and closes when both land and pass against ORA-53. This is the contract-first pattern working as intended — the agreement and its enforcement are done ahead of either implementation; it is not stalled work.

### Threat model (STRIDE-lite)

* **Info-disclosure (dominant):** error bodies leaking stack traces, internal hostnames/IPs, service names, SQL, library versions, tokens, or PII.
* **Elevation / existence-disclosure:** 403-vs-404 differential confirming a hidden resource exists; user-not-found vs wrong-password differential on auth.
* **Tampering/spoofing:** free-text error type rendered by the FE becomes a phishing surface — mitigated by a closed machine-readable taxonomy; the FE switches on `code`, never on `message`.
* **Repudiation:** incidents must be traceable — expose one opaque `requestId` that maps server-side to the full trace.
* **DoS/amplification:** never reflect request content back in the error body.

### Envelope shape

```
{
  "error": {
    "code": "VALIDATION_FAILED",        // closed taxonomy; the FE's only branch key
    "message": "One or more fields are invalid.",  // curated, generic; never an exception message
    "requestId": "req_01J9Z...",         // opaque correlation handle; the ONLY trace exposed
    "retryable": false,                  // server-authoritative: may a retry succeed?
    "details": [                          // ONLY for VALIDATION_FAILED
      { "field": "email", "issue": "INVALID_FORMAT" }  // closed sub-vocabulary; never the raw value
    ]
  }
}
```

JSON Schema constraints: single top-level `error` object; `additionalProperties: false` at every level (so no `stack`/`cause`/`exception`/`trace` field can ever exist); `code` constrained to the enum below; `retryable` required boolean; `details` present only for `VALIDATION_FAILED`.

**retryable** is server-authoritative and decoupled from `code` so the FE never hardcodes which codes are retryable — it reads the boolean. Guidance: `true` for `RATE_LIMITED`/`SERVICE_UNAVAILABLE`/`GATEWAY_TIMEOUT`; `false` for all 4xx; `INTERNAL_ERROR` defaults `false` but the server MAY set `true` when it knows the fault is transient. The FE still honours request idempotency and any `Retry-After` header — `retryable` signals server-side transience, not a license to replay non-idempotent calls.

### Error-code taxonomy (closed set) + HTTP + retryable

| code | HTTP | retryable | When |
| --- | --- | --- | --- |
| VALIDATION_FAILED | 400 | false | schema validation failed; `details[]` set |
| MALFORMED_REQUEST | 400 | false | unparseable body / bad content-type |
| UNAUTHENTICATED | 401 | false | missing/invalid/expired credentials (generic — no user-vs-password differential) |
| UNAUTHORIZED | 403 | false | authenticated, ReBAC denies, and caller may already know the resource exists |
| NOT_FOUND | 404 | false | resource absent, or hidden from a caller without read permission (existence-hiding) |
| METHOD_NOT_ALLOWED | 405 | false | method not permitted on resource |
| CONFLICT | 409 | false | state/version conflict |
| PAYLOAD_TOO_LARGE | 413 | false | body exceeds limit |
| UNSUPPORTED_MEDIA_TYPE | 415 | false | content-type not supported |
| RATE_LIMITED | 429 | true | throttle; retry hint via `Retry-After` header, not body |
| INTERNAL_ERROR | 500 | false\* | unexpected fault; message always generic (\*server may set true when transient) |
| SERVICE_UNAVAILABLE | 503 | true | dependency down / draining |
| GATEWAY_TIMEOUT | 504 | true | upstream timeout |

**Existence-hiding rule:** prefer `404` over `403` when the caller has no read permission, so the error does not confirm existence; use `403` only when the caller can already enumerate the resource.

### Sensitive-data rules — must NEVER appear in an error body

1. Stack traces, exception class names, file paths, line numbers.
2. Internal hostnames, IPs, ports, service/container names, topology.
3. SQL, ORM errors, DB constraint names.
4. Tokens, secrets, API keys, session ids, `Authorization` contents.
5. Framework/library names + versions (fingerprinting).
6. PII or the raw offending value reflected back (reflected-XSS / PII echo) — `details[].issue` describes the problem, not the value.
7. Auth differential messaging (user-not-found vs wrong-password).
8. Raw upstream error bodies — the gateway translates, never passes through.

### Enforcement (Contract not Done until this exists)

A shared fixture (pre-R6): a JSON Schema encoding the envelope with `additionalProperties: false` + the `code` enum, plus sample fixtures and a forbidden-substring negative test. The backend asserts every error response validates and `code` is in the enum; the frontend api-client parses against the same fixture. Built by devops-implementer. This is the fixture story [ORA-53](https://oraclous.atlassian.net/browse/ORA-53) (**Done**), which blocks both the BE ([ORA-54](https://oraclous.atlassian.net/browse/ORA-54)) and FE ([ORA-55](https://oraclous.atlassian.net/browse/ORA-55)) implementing stories.

## §S7 — Webhook ingress: gateway → engine + gateway → broker (R6 Slice 7)

Two internal, `X-Internal-Key`-gated cross-service shapes the gateway webhook ingress depends on. Built + live (gateway `GW-13` + the engine event-fire smoke); recorded here as the canonical home (sole-worker mode — no separate Contract issue; the implementing PRs are #209 cred-broker, #210 engine, #211 gateway).

### (a) Gateway → execution-engine — fire a verified webhook event

`POST /v1/engine/events` (the engine; gated by `X-Internal-Key` + the gateway-asserted `X-Principal-Id`/`X-Principal-Type`/`X-Organisation-Id`, the **same** trust gate as `/v1/engine/jobs` — the engine does **not** re-verify the signature, the gateway already did).

```jsonc
// request body
{ "manifest_ref": "<bound_capability_ref>",   // XOR "manifest" (inline OHM) — exactly one
  "input": "<goal built from the event payload>",
  "idempotency_key": "<provider delivery id | sha256(raw_body)>",  // ≤255 chars; dedupe key
  "event_type": "webhook", "source": "<subscription id>" }         // audit only
// response 202
{ "accepted": true, "deduped": false, "job_id": "<uuid>" }          // deduped:true + job_id:null on a redelivery
```
Invariants: `organisation_id`/`user_id` are **never** in the body (ORG001) — both come from the gateway-asserted principal headers (ADR-006/ADR-018). Idempotent on the engine's existing `(org, idempotency_key)` UNIQUE → a redelivered event is a no-op, still `202`. The engine reuses the R5 durable spine unchanged (no new table).

### (b) Gateway → credential-broker — the webhook signing secret

`POST /internal/webhook-secrets` (mint) + `POST /internal/webhook-secrets/resolve` (decrypt) on the broker, under the existing `verify_internal_key` gate. The secret is AES-256-GCM at rest (ADR-008); the gateway stores only the returned id (`broker_secret_ref`), never the plaintext.

```jsonc
// mint  -> 200            // resolve -> 200 (cross-org/missing -> 404, mask)
{ "organisation_id": "<uuid>", "secret": "<whsec_…>" }      // mint in
{ "secret_id": "<uuid>" }                                   // mint out
{ "organisation_id": "<uuid>", "secret_id": "<uuid>" }      // resolve in
{ "secret": "<whsec_…>" }                                   // resolve out (the gateway recomputes the HMAC, then discards)
```
Enforcement: live cross-service smokes (the gateway `GW-13` mints + resolves against the running broker; the cred-broker smoke step 9 covers mint/resolve/cross-org-404/no-key-401). A redundant shared fixture is unnecessary while both sides live in one repo + are smoke-pinned; revisit if either side moves.

## §S2-ROLE — Org-role claim + the `X-Principal-Org-Role` trust header (R7-SEC S2)

The org-roles floor (admin vs member on the management plane) crosses two boundaries: **auth-service → the JWT** and **the gateway → upstreams** (ADR-018). Recorded once here; built + live (`GW-17`); sole-worker mode (no separate Contract issue; implementing PR #217).

### (a) The `org_role` access-token claim (auth-service → the gateway/any verifier)

The user **access** JWT (and only the access token) carries the member's role in the **token's** organisation:

```jsonc
// access-token claims (in addition to the existing sub / principal_type / organisation_id / type / iat / exp / jti)
{ "org_role": "owner" | "admin" | "member" }   // the member's role in `organisation_id`; OMITTED when unknown
```
Invariants: the role is **per-`(user, org)`** — an admin-in-A / member-in-B user gets `member` in a B-scoped token. **Omitted** (not `null`) when the issuer can't resolve a membership role, and on agent/service-account tokens — a verifier reads a missing claim as **None**, which never satisfies an admin gate (fail-closed). Canonical rank lives in `packages/governance` (`org_role_at_least`, owner≥admin≥member, fail-closed); every service checks admin-vs-member the same way.

### (b) The `X-Principal-Org-Role` forwarded trust header (gateway → upstreams)

On an authenticated request the gateway **strips** any client-supplied `X-Principal-Org-Role` and **injects** the verified `principal.org_role` (present only when the principal carries one), exactly like the other `X-Principal-*` headers (ADR-018, §1). An upstream MAY role-gate on it; today **only the gateway enforces** (its `require_admin` gates the destructive management ops — key mint/rotate/revoke, agent publish, webhook-subscription create/delete), so no upstream is half-wired to trust it. The header is also on the gateway's response **denylist** (never reflected to the client).

Enforcement: the gateway `GW-17` smoke (member → mint/publish/webhook-create = 403; admin → 201; member reads = 200) + unit tests (`require_admin` allows admin/owner, denies member/None/unknown; the forward strip-then-inject; the auth-service claim present/omitted).
