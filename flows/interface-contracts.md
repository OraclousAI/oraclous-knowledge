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
| Enriched graph schema (KGS recipe enrichment, #269) | — (epic #269; #270/#271/#274/#275, perf #272) | Live (KGS smoke) | See §GRAPH |
| BYOM spend estimate (`GET /v1/harnesses/spend`) | — | Live | See §SPEND |
| Workspace↔harness binding (G2) | — ([oraclous-backend#340](https://github.com/OraclousAI/oraclous-backend/issues/340); FE [#127](https://github.com/OraclousAI/oraclous-frontend/issues/127)) | AGREED ([ADR-029](../adr/adr-029-workspace-harness-binding.md)); BE impl open, FE #127 consumes | See §G2 |
| Team-run task input | — ([oraclous-backend#674](https://github.com/OraclousAI/oraclous-backend/issues/674)) | AGREED (2026-07-30); BE half in #674, FE Run-dialog field open | See §TASK |

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

## §GRAPH — Enriched graph schema (KGS recipe enrichment, #269)

The shape of the graph the `knowledge-graph-service` writes once a recipe uses the #269 enrichment rule shapes (`transform`, `from_each`+`edge_to_each`, `extractions`, `similarities`, `resolution`). Recorded here because the **knowledge-retriever** and the **frontend** read these labels/edges/properties. Domain labels and edge types are recipe-supplied (validated safe-identifiers), not platform-fixed; the set below is what the canonical enriched evidence recipe writes (`build_evidence_recipe`). Authoritative narrative + the rule-shape table: [knowledge-graph-service reference](../services-reference/knowledge-graph-service.md#recipe-rule-shapes-format-02--enriched-by-epic-269). Epic #269; slice PRs #270 (transform + list fan-out), #271 (free-text extraction), #274 (similarity), #275 (resolution), perf #272.

### Node labels

| Label | Origin |
| --- | --- |
| `Publisher` | Host-keyed from a source URL via `transform: host` — one node per domain (every article URL on `eurail.com` collapses to one `Publisher`). |
| `Tag` | Fanned from a list-valued field (`from_each`); MERGE-shared across records. |
| `Person`, `Organization`, `Product`, `Place` | Mined from a prose field by the LLM extractor under the recipe's inline ontology (`extractions[].ontology`). |

(alongside the recipe's structured baseline labels — for the evidence recipe: `Evidence`, `ClaimSource`, `Conflict`.)

### Edge types

| Edge | Pattern | Notes |
| --- | --- | --- |
| `PUBLISHED_BY` | `ClaimSource-[:PUBLISHED_BY]->Publisher` | Same-record identity. |
| `HAS_DIMENSION` | `Evidence-[:HAS_DIMENSION]->Tag` | One per fanned-out list element (`edge_to_each`). |
| `MENTIONS` | `Evidence-[:MENTIONS]->`entity | The extraction `link` edge from the record's primary node to each mined entity. |
| `OPERATES`, `LOCATED_IN` | `Organization-[:OPERATES]->Product`, `Organization-[:LOCATED_IN]->Place` | Relationship types declared in the inline extraction ontology, between mined entities. |
| `SIMILAR_TO` | `Evidence-[:SIMILAR_TO {score}]->Evidence` | Content-similarity (embed → cosine kNN); carries `score`. One edge per unordered pair. |
| `SAME_AS_CANDIDATE` | entity-`[:SAME_AS_CANDIDATE {score}]->`entity | Resolution review band — two canonical nodes that are close but **not** auto-merged; carries `score`. A flag for review, **not** an identity assertion. |

### Entity properties (on a resolved entity)

* `name` — the **canonical key** the node is keyed by (e.g. `eurail`).
* `canonical_name` — a chosen **display form** (e.g. `Eurail B.V.`).
* `aliases` — the set of original **surface forms** seen across records (the alias audit trail).

### Edge `score`

A rounded cosine similarity float, present on **`SIMILAR_TO`** and **`SAME_AS_CANDIDATE`** edges. On `SIMILAR_TO` it is the content-similarity of the two records; on `SAME_AS_CANDIDATE` it is the name-embedding similarity of the two canonical entities (in the `[candidate_threshold, merge_threshold)` band, default 0.85–0.92).

## §SPEND — BYOM spend estimate (`GET /v1/harnesses/spend`)

A read-only, org-scoped **estimate** of the caller organisation's own provider (BYOM) LLM spend, served by the `harness-runtime-service` and reachable through the gateway. The **frontend** consumes it (a spend/usage view). It is **not** platform billing or a charge Oraclous levies: per [ADR-009](../adr/adr-009-metering-at-substrate-billing-as-separable.md) the substrate meters **raw tokens**; pricing is a separable, read-time concern. Raw per-model token sums are priced at read time from a **static rate table**; a model absent from the table reports its tokens only (`estimated_usd: null`, `priced: false`) and is named in `unpriced_models`. `total_estimated_usd` sums only the priced rows.

Request: `GET /v1/harnesses/spend?since=<ISO8601>` — `since` is **optional**; it bounds the window to executions at or after it (omit for all-time). Org-scoped from the authenticated principal (`organisation_id` is never inbound).

```jsonc
// 200 — SpendResponse
{
  "since": "2026-06-01T00:00:00Z" | null,   // echoes the query param; null for all-time
  "currency": "USD",                          // always USD today
  "by_model": [
    { "model": "openai/gpt-4o" | null,        // the provider model id (null when unattributed)
      "input_tokens": 12000,
      "output_tokens": 3400,
      "executions": 7,                         // harness executions that used this model
      "estimated_usd": 0.085 | null,           // null when the model is not in the rate table
      "priced": true }                         // false → tokens-only (unpriced)
  ],
  "total_estimated_usd": 0.085,                // sum of estimated_usd over PRICED rows only
  "total_input_tokens": 12000,
  "total_output_tokens": 3400,
  "unpriced_models": ["some/unlisted-model"]   // recorded tokens but absent from the rate table
}
```

Mirrors the `harness-runtime-service` `SpendResponse`/`ModelSpendOut` schema and the gateway OpenAPI `SpendResponse`/`ModelSpendOut` components (`openapi/v1.yaml`). The operation is `x-stability: provisional`.

## §G2 — Workspace↔harness binding ([ADR-029](../adr/adr-029-workspace-harness-binding.md))

The relation tying an OHM agent (a `kind:harness` capability) to a workspace (a knowledge graph). Per ADR-029 it is a **many-to-many curation edge owned by the capability registry** — a `harness_graph_binding` join row, **not** an OHM manifest field and **not** a graph-substrate association. It is a **curation/visibility** association only — **not** an authorization grant and **not** an execution route (the agent's data access is unchanged; binding never grants new access).

> **rev2 (2026-06-17, post pre-build audit):** endpoints moved off `/api/v1/graphs/{id}/agents` (which the static-prefix gateway routes to knowledge-graph-service, not the registry) to a new **`/api/v1/agent-bindings`** registry prefix (one new route-table entry → `CAPABILITY_REGISTRY_URL`). Org-scoping is **visibility-based, verified both sides**: harness via the registry's caller-org-OR-`PLATFORM_ORG` lookup (so shared/platform agents are bindable); graph via a KGS membership call (`GET /internal/v1/graphs`, ADR-018 forward-and-trust) — an object not visible to the caller → **404** (no `409`). Cascade is **asymmetric**: harness-delete hard-cascades (in-service FK); graph-delete is **tolerate-and-lazily-ignore** (no cross-service cascade exists; dangling rows are skipped on read, safe because the edge is curation-only).

The **frontend** (`oraclous-frontend#127`) consumes these gateway endpoints; the binding data lives in and is served by the **capability registry**. FE labels them "workspace"/"agent"; the routes use the real objects.

```jsonc
// GET /api/v1/agent-bindings?graph_id={id} — agents bound to a workspace (live graphs only)
// 200
[ { "harness_id": "cap_...", "name": "Triage agent", "kind": "harness", "summary": "…" } ]

// GET /api/v1/agent-bindings?harness_id={id} — workspaces a harness serves (agent detail; live graphs only)
// 200
[ { "graph_id": "g_...", "name": "Acme support KB" } ]

// POST /api/v1/agent-bindings   body: { "harness_id": "cap_...", "graph_id": "g_..." }
//   201 created · 200 if already bound (idempotent); body: { "created": bool }
//   404 either object absent/not visible to caller's org
//   503 if the graph service is unreachable (attach verifies graph membership; fail-closed, retryable)

// DELETE /api/v1/agent-bindings?harness_id={id}&graph_id={id}
//   204 · 404 if not bound
```

Decisions pinned at acceptance: a shared `PLATFORM_ORG` agent **can** bind to a tenant workspace; members get the **read** view; attach/detach require org write access. **As shipped (`oraclous-backend#350`):** POST returns a small `{ "created": bool }` body alongside the 201/200 status (so the FE reads created-vs-already-bound without inspecting status); the graph-membership check is a network call to KGS, so an unreachable graph service is a fail-closed **503** (retryable), not a guess; a `GET ?graph_id=` for a graph not visible to the caller returns `[]` (the leak-free list mask). **Enforcement (live):** the gateway exposes the four endpoints (the `/api/v1/agent-bindings` route-table entry), backed by the `harness_graph_binding` migration in the capability registry (harness FK `ON DELETE CASCADE` + `UNIQUE(harness_capability_id, graph_id)` + `created_by`), the KGS membership check on attach, and graphs-resolved-on-read filtering; mirrored in the gateway OpenAPI (`openapi/v1.yaml`). Tracked: `oraclous-backend#340` (merged) + FE `#127`.

## §TASK — Team-run task input ([oraclous-backend#674](https://github.com/OraclousAI/oraclous-backend/issues/674))

The per-run task a user hands a **standing** compiled team ("review THIS pull request") — distinct from the compile-time "Inputs · Constraints · Success criteria" fields, which fold into the planner's brief and bake into the manifest. Evidence for the gap: UC-D7 run `9ddf00f3` — with no way to pass a target, the Fetcher **chose its own** public PR, its receipts passed the grounding grade, and the team confidently reviewed the wrong thing. The grounding gate proves a tool ran; only a delivered task proves it ran **on what the user meant**.

**OHM (declaration, additive v1.1 team block).** A team manifest MAY declare:

```jsonc
// OHMManifest.task_input (kind == "team"; absent → no run-time task, today's behaviour)
{ "required": true,                      // fail-closed: refuse to run without a task
  "description": "The pull-request URL to review",   // the Run dialog's label/help text
  "key": "task" }                        // the TeamRunCreate.inputs key it rides in (default "task")
```

**API (gateway → engine, existing endpoint).** The task rides the **existing** `TeamRunCreate.inputs` object as a string under the declared key (default `"task"`) — no new top-level field, same reserved-key pattern as `_refresh_seed` (#602):

```jsonc
// POST /v1/engine/team-runs
{ "manifest": { ... , "task_input": { "required": true, "description": "…" } },
  "sub_harnesses": { ... },
  "inputs": { "task": "https://github.com/acme/repo/pull/1" } }
```

**Engine (delivery).** `render_member_input` includes the task **verbatim** in **every** member's rendered input, as a `Task:` block between the objective and the inbound hand-offs. No member has to guess the target; fan-out/refresh consumption of `inputs` is unchanged.

**Fail-closed.** `task_input.required` + a missing/empty/non-string task → **422 at create** naming the missing input (the run is never enqueued, no tokens). A team with no `task_input` block accepts and ignores a stray `inputs.task` (back-compat).

**Frontend.** The console Run dialog renders a task field when the manifest declares `task_input` (blocking when `required`), labeled from `description`; naming keeps "Task for this run" visually distinct from the compile-time New-team "Inputs" so users don't bake a one-shot target into a standing team.

Out of scope (separate contracts): the PR-open **event trigger** (UC-D7's real invocation mode) and typed/multi-field run inputs — `task_input` is deliberately a single string until a use case demands structure.
