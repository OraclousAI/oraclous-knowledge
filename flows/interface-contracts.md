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
| Resolvable citation on any tool result | — ([oraclous-backend#735](https://github.com/OraclousAI/oraclous-backend/issues/735); FE [#194](https://github.com/OraclousAI/oraclous-frontend/issues/194)) | AGREED at **rev6** (2026-08-14, [#776](https://github.com/OraclousAI/oraclous-backend/issues/776) names the §CITE-QUAL declaration `result_kind`); the data path, the run's served set, and the answer-time gate have all shipped ([#742](https://github.com/OraclousAI/oraclous-backend/issues/742), [#743](https://github.com/OraclousAI/oraclous-backend/issues/743), [#782](https://github.com/OraclousAI/oraclous-backend/issues/782)); evidence [oraclous-backend#734](https://github.com/OraclousAI/oraclous-backend/issues/734) | See §CITE |
| The declared form of a deliverable | — ([oraclous-backend#870](https://github.com/OraclousAI/oraclous-backend/issues/870); implementing story [#730](https://github.com/OraclousAI/oraclous-backend/issues/730)) | AGREED (2026-09-04); neither repo has implemented it | See §DELIV |

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

## §CITE — Resolvable citation on any tool result (UC-D1 / UC-E1)

Owner: solution-architect. Status: **AGREED at rev5, shipped on the backend** — the minting path ([`#742`](https://github.com/OraclousAI/oraclous-backend/issues/742)), the run's served set ([`#743`](https://github.com/OraclousAI/oraclous-backend/issues/743)), and the answer-time gate with its correction loop ([`#782`](https://github.com/OraclousAI/oraclous-backend/issues/782)) are live at the run boundary and proven on the deployed stack against a live model. The frontend consumer is open. Driving evidence: the UC-D1 proof of concept, [`oraclous-backend#734`](https://github.com/OraclousAI/oraclous-backend/issues/734), filed against §5.3 capability 6. Tracking Contract: [`oraclous-backend#735`](https://github.com/OraclousAI/oraclous-backend/issues/735); frontend consumer: [`oraclous-frontend#194`](https://github.com/OraclousAI/oraclous-frontend/issues/194); follow-on knowledge-record Contract: [`oraclous-backend#741`](https://github.com/OraclousAI/oraclous-backend/issues/741).

> **rev2 (2026-08-09, Reza).** Three decisions, taken after rev1 was recorded and before any code was written.
>
> 1. **Scope is every tool result an agent may assert from, not only the knowledge base.** rev1 covered the ingest→storage→retrieval path. Live web research (`core/web-research`), MCP-imported tools, and connector reads now mint citations on the same shape. A citation is minted at the **tool-execution boundary**, which subsumes the ingest path rather than replacing it.
> 2. **A citation is produced by code, never by a model.** The platform mints it and hands it to the model. The model may only *reference* an id the platform issued. This was implicit in rev1 and is now a stated rule, because it is the property the whole design exists to guarantee.
> 3. **Precision is enforced when a tool is connected, not when an answer is written.** rev1 blocked an answer whose citation lacked a document id or a link. That punishes the user for a third-party tool's limitation at the worst possible moment. The check moves to connect time (§CITE-QUAL), where the admin can act on it by choosing a better tool. The answer-time gate keeps only the two anti-fabrication rules, which cost a third party nothing because the platform mints the id itself.
>
> **rev3 (2026-08-09, Reza).** Two simplifications on top of rev2, both narrowing v1.
>
> 4. **No locator in v1.** A citation points at a **document version**, not at a chunk, a line range or a page. Sub-document precision is a later release. This deletes the `locator` field and, with it, the rev2 debate about whether it belonged in the identity hash — there is nothing left to churn.
> 5. **A tool that cannot cite its sources is not permitted, rather than permitted-with-a-warning.** rev2 graded a `weak` tool and warned the admin. rev3 refuses it at connect time. **Stated reason:** reliable alternatives exist for every source class we care about, so tolerating a tool that cannot describe its own output buys nothing and costs the guarantee. See §CITE-QUAL for the two limits this rule needs to stay sane.
>
> Rev2 amended how UC-E1's `citation-checker` clause ("refuses to ship a sentence whose citation does not resolve") is read, under use-case §5.4 rule 4. **Stated reason:** an intermediate tool's limitation must degrade the citation's precision, never block the product. The strictness the clause asks for is preserved in full against fabrication, which is the threat it was written for. **rev3 narrows that amendment**: the tolerance now applies only to a *missing version*, because a tool with no document identity at all is refused before it can ever be used.
>
> **rev4 (2026-08-12, Reza).** Five decisions, all downstream of one sentence: **the model is not a source of truth.** We give it sources; it reasons over them on our behalf. rev1–rev3 never said this outright, and several questions that stayed open turned out to be that omission wearing different hats.
>
> 6. **A model does not cite itself in conversation.** An answer carries citations for external sources only; sentences the model reasoned out carry none, because it is evident the agent is speaking. **Stated reason:** a model citation is not evidence. Minting one for every uncited sentence adds volume to the record without adding truth, and teaches a reader to skim past citations rather than trust them.
> 7. **Content the agent itself wrote is marked as agent-generated.** A file an agent writes into a workspace carries `source_system: "agent"`, never `"upload"`. **Stated reason:** an agent can otherwise write a file, retrieve it, and cite it — passing every rule while showing the reader something that looks like external evidence and is the agent quoting itself. A human uploading a real document is a different act and keeps `"upload"`; the distinction is who authored the content, so it needs its own value.
> 8. **Rule 1 is deleted and replaced.** rev2's rule 1 ("an asserted fact carries no `citation_id`") is not implementable in platform code: separating an asserted fact from reasoning is a judgment call, and this Contract forbids a model-implemented gate. It is replaced by the narrower rule in §"What 'resolves' means". **Stated reason:** the first implementation approximated it as "the run served sources and the answer cited none", which fails an honest decline — a member that searches, reads what came back, and reports that it has no answer. That member is behaving correctly. Refusing to hallucinate is the product working, and a gate that punishes it is worse than no gate.
> 9. **A violation is returned to the model, not to the user.** A blocked answer is fed back to the member with a specific, actionable message naming what is wrong and what to do, and the member answers again. **Stated reason:** the member is the only party that can fix the defect, and it can only act on an error that says what to change. Retries are bounded by the run's existing iteration budget.
> 10. **A run returns citation records, not bare ids.** The set a run served is exposed as the citation objects themselves. **Stated reason:** a list of opaque ids forces the console into one lookup per source before it can draw a link — a second round trip over data the run already held, on the surface where latency is most visible.
>
> **rev5 (2026-08-12 / 2026-08-13, Reza).** Three decisions taken *while the gate was being built*. Each one closes a defect that only a live run on the deployed stack exposed.
>
> 11. **`source_tool_call_id` is not a rule 1 marker** ([`oraclous-backend#788`](https://github.com/OraclousAI/oraclous-backend/issues/788), ruled 2026-08-12). rev4's marker list was `source:`, `sources:`, `source_tool_call_id`; the third is removed. `source:` and `sources:` stay. **Stated reason:** [`#642`](https://github.com/OraclousAI/oraclous-backend/issues/642)'s `validate_grounding` already resolves every declared `source_tool_call_id` against an `ok` tool step in the member's own trace, failing closed on a missing, null, unresolvable, or errored id. Rule 1 watching the same token with a prose pattern laid a **guess over a working proof**, and the guess won — see "Two mechanisms, one token" below.
> 12. **Terminal precedence splits by rule, not by mechanism** ([`oraclous-backend#792`](https://github.com/OraclousAI/oraclous-backend/issues/792), ruled 2026-08-13). Neither the gate nor the data-absence degrade blanket-outranks the other; what wins follows what the blocking rule actually caught. Recorded in full under "What a violation does".
> 13. **A correction must name a remedy the member can perform.** When a run served nothing, rule 1's message no longer tells the member to cite an id it was never given. **Stated reason:** on the deployed stack a live member spent all 25 of its iterations being corrected toward an impossible instruction. That is the [`#692`](https://github.com/OraclousAI/oraclous-backend/issues/692)/[`#693`](https://github.com/OraclousAI/oraclous-backend/issues/693) failure again — an error a member can only retry blindly. The correction strings are Contract text, so both variants are recorded here.
>
> **rev6 (2026-08-14, Parham Davari).** Three decisions ([`oraclous-backend#776`](https://github.com/OraclousAI/oraclous-backend/issues/776)). rev3 introduced a declaration — "a tool declares whether it returns assertable content or only a status" — and then never gave it a home, a name, or a set of values. Two sentences in this document (§CITE-QUAL Limit 1, and the minting note that consumes it) were its entire specification. rev6 writes it down.
>
> 14. **The declaration is a per-capability field named `result_kind`, with three values: `status`, `single`, `collection`.** It is recorded in §CITE-QUAL and specified there. **Stated reason:** the declaration has three consumers, not one, and a boolean serves only the first. §CITE-QUAL needs status-versus-content so action tools are never graded. The minting table needs to know **how many** citations one tool result yields, which it never said — a search returning ten hits is one result and ten sources. The console's ingest picker needs "one addressable document I can fetch with a small form", which is `single` alone; under a boolean, `core/web-research.search` becomes pickable and the console's single-`content`/single-`source` read path breaks on the first result.
> 15. **`emits_source` is not adopted; a capability never declares that it reports its source.** [`#776`](https://github.com/OraclousAI/oraclous-backend/issues/776) proposed it as a second, separate field. **Stated reason:** for a first-party connector it is a tautology of `single`/`collection` — we write the code, so a read returning content without a `SourceRef` is a defect in that connector, and a flag would let the defect be recorded as if it were a design choice. For a third-party tool the author never writes our field, so whether the response carries source identity has to be *discovered*, and discovering it is the §CITE-QUAL grade. Two authored fields that can disagree are worse than one declaration plus one determined grade, and the second would be an unverified copy of the first.
> 16. **An absent `result_kind` means undeclared, and fails closed in both directions.** It is never read as `status`. **Stated reason:** a boolean default cannot fail closed for both consumers at once. Absent-means-false is correctly closed for the picker, but absent-means-`status` is **fail-open** for the gate: an ungraded content-returning tool would declare itself an action tool, skip grading entirely, and let a member read from it and assert uncited. That inverts §3.5 of the backend operating contract, so the field is required going forward and `null` is refused rather than defaulted.

### Why this crosses the repo boundary

The console renders the citation and the user clicks it, so the shape is consumed by both repos and may not be defined inside either (`oraclous-backend/CLAUDE.md` §12). It is also a **gate**, not decoration: UC-E1 makes the `citation-checker` a blocking role. A gate cannot run against free-form prose.

### The rule the whole Contract exists to enforce

**The platform mints every citation in code. A model can reference one; it can never author one.**

This is the finding that drove the Contract. In the PoC a real model, on a real question, emitted `(source: partner-agreement.md)` — a bare filename — alongside `source_tool_call_id=call_...`, an id the platform never issued. The answer was correct and the provenance was fiction, and nothing in the system could tell the two apart. Every mechanism below is downstream of closing that gap.

### What exists today, and why it cannot carry a citation

| Layer | Today | Why it fails |
| --- | --- | --- |
| Ingest | `IngestTextRequest = {content, filename, source_type, recipe_id, valid_from, valid_to, event_time}` | No field for source identity. The GitHub connector returns `{path, content}` and discards the repo, the blob `sha`, and the `html_url` the GitHub API already gave it. |
| Storage | The node carries `ingestion_source = "README.md"` and `created_by = "multi_tenant_pipeline"` | One untyped string in free-form `properties`. It does not resolve, and it names no system, no revision, and no person. |
| Retrieval | `NodeResultModel = {id, type, properties}` | No typed citation field anywhere in the retriever or the gateway. |
| Answer | The model wrote `(source: partner-agreement.md)` plus an invented `source_tool_call_id=call_...` | Model prose. The platform never issued that id. Nothing typed, nothing clickable, nothing a gate can check. |

### The typed record

```jsonc
// Citation — the resolvable source identity of one knowledge record.
{
  "citation_id": "cit_9f2a4c81…",          // platform-computed, deterministic; the ONLY handle an answer may cite
  "source_system": "github",                // a REGISTERED connector slug; "upload" for a direct file upload
  "source_id": "OraclousAI/oraclous-backend:README.md",  // identity WITHIN that system, stable across revisions
  "revision": "e3b0c44298fc1c14…",         // the version read; never null outbound
  "revision_kind": "blob_sha",              // commit | blob_sha | version_id | etag | edited_at | block | content_hash
  "url": "https://github.com/OraclousAI/oraclous-backend/blob/e3b0c44/README.md",  // absolute and openable
  "title": "README.md",                     // display label ONLY — never identity
  "author": { "display_name": "Parham Davari", "source_handle": "parhamdavari" },  // the SOURCE's author; null if the system exposes none
  "retrieved_at": "2026-08-08T09:14:22Z",   // as-of: when this revision was read from the source
  "permission_ref": null                     // the source's own permission handle; CARRIED now, UNENFORCED until capability 27
}
```

`author.email` is optional and omitted unless the source exposes it.

**A citation resolves to a document version, not to a place inside it (rev3).** There is no `locator` in v1 — no chunk index, no line range, no page, no heading anchor. Sub-document precision is a later release, and adding it later is additive: a new optional field, no change to identity.

**`revision` is never null, on any path.** This is a global rule, not an ingest-only one, and it holds even for a `document`-grade source that exposes no version of its own. The platform always holds the content at the moment it mints, so it can always fall back to the SHA-256 of that content with `revision_kind: "content_hash"`. **`revision_kind` is what tells the two apart** — a source-native version (`commit`, `blob_sha`, `version_id`, `etag`, `edited_at`, `block`) versus our own fallback. The JSON Schema therefore makes `revision` **required and non-nullable**, which keeps both the identity hash and the supersession rule total: a page that changes between two reads yields a new hash, so a new `citation_id`, so a correctly superseding record. The cost is accepted openly — a trivial change to a web page, such as a rotating footer, counts as a new revision.

**`citation_id` is the whole security mechanism.** It is deterministic, and it is keyed on exactly the three fields that identify a document version:

```
citation_id = "cit_" + sha256(source_system ‖ 0x00 ‖ source_id ‖ 0x00 ‖ revision)[:32]
```

Determinism buys three things at once: re-reading the same revision yields the same id (an idempotent refresh); a **new revision yields a different id**, which is what makes supersession computable without a supersession table; and an id the model invents is not in the run's served set, so it fails the gate.

Because identity is document-level, **re-chunking a document never changes its `citation_id`** — a citation already stored in a published answer or an evidence ledger keeps resolving. When sub-document precision arrives it must stay outside this hash for the same reason.

**`source_system` is a registered slug, not a frozen enum.** UC-E1 acceptance 6 requires a sixth, unplanned source type to be connectable without re-modelling existing records. A closed enum would break that. The constraint is that the value must name a **registered connector**, plus two reserved values: `upload` for a file a person uploaded directly, and `agent` for content a harness member wrote itself (rev4).

**Why `permission_ref` is in the shape now but enforced later.** Per-user permission mirroring (capability 27) is out of the first slice, but the source's permission handle is only obtainable *at read time from the connector*. Omitting the field would force a full re-ingest of every record when capability 27 lands. The field is cheap now and expensive to backfill.

### Where it lives in the retrieval envelope

One typed sibling field, following the `FederatedNodeResultModel` precedent (`source_graph_id` is a sibling, not a `properties` key):

```jsonc
// NodeResultModel and FederatedNodeResultModel each gain ONE field
{ "id": "...", "type": "Chunk", "properties": { … }, "citation": Citation | null }
```

`citation: null` means the record has no source identity — ingested before this Contract, or ingested without a `source`. It is **never a partly-filled object**: a half-citation is indistinguishable from a real one at a glance, and the gate must be able to say "this record cannot be cited" without inspecting five fields.

**One citation per node, on lexical nodes only.** A `Chunk`/`Document` node has exactly one source, so `citation` is singular. A derived or extracted entity node carries `citation: null` in v1, and an answer must cite the lexical hit rather than the entity. Multi-provenance ("one claim, two provenances" — the UC-E1 deduplicator) belongs to the follow-on knowledge-record Contract, not here.

### Where it lives in the run's response (rev4)

A retrieval hit carries its citation on the envelope. A **run** additionally reports the set of citations it served, as the records themselves:

```jsonc
// the run's response gains one field
"citations": [
  {
    "citation_id": "cit_9f2a4c81…",
    "source_system": "github",
    "title": "partner-agreement.md",
    "url": "https://github.com/OraclousAI/…/blob/e3b0c44/partner-agreement.md"
  }
]
```

**Records, not ids.** A list of opaque ids would force the console into one lookup per source before it can render a link, over data the run already held. This follows the shape the wider industry settled on: a citation is structured data returned beside the answer and computed by the platform, never a marker the model writes into prose. Whatever marker a member writes (`[1]`, or any wrapper chosen later) is a display concern that maps onto these records; the records are the source of truth.

**Which fields are required here is a shape question for the implementing Contract issue** ([`oraclous-backend#785`](https://github.com/OraclousAI/oraclous-backend/issues/785)), together with whether the record is resolved by the loop or at read time. The four shown above are the minimum a console needs to render a link, and `url` may be null — an `upload` or `agent` citation has nothing to open.

### Where a citation is minted (rev4, cardinality settled in rev6)

A citation is minted **once, in platform code, at the tool-execution boundary** — the point where a tool result comes back into the runtime. There are four paths into that boundary, and they share one minting function:

| Path | Example | What the tool supplies |
| --- | --- | --- |
| **Connector read → ingest → retrieval** | a GitHub file lands in a workspace and is later searched | full source identity; the citation is stamped at ingest and returned on the retrieval hit |
| **Connector read used directly in a run** | an agent reads a Drive file mid-run and asserts from it | full source identity, minted on the tool result; never stored |
| **Live web / MCP tool** | `core/web-research` search, or an imported MCP tool | whatever the tool's response carries; see §CITE-QUAL |
| **Agent-written content (rev4)** | a member writes a summary into its workspace and a later member retrieves it | no external source at all — `source_system: "agent"`, `source_id` the ingest job id, `revision` the content hash, `url: null` |

The third row is why rev2 widened the scope. An agent citing a web page it just read is the same guarantee problem as an agent citing an ingested file, and rev1 covered only the second.

**The fourth row is the only one with no external source, and it exists to be legible rather than resolvable.** Its `url` is null by construction: there is nothing outside the platform to open. Its value is that a reader can tell at a glance that a cited passage was written by an agent rather than read from the world — which the previous behaviour, minting it as `"upload"`, actively concealed.

**One minting function, shared by all four rows.** It lives in `packages/citation/` and takes a `SourceRef`; it is not an ingest helper that the other paths borrow. Rows two and three have no stored record to stamp, so a minting function shaped around ingest would have to be rewritten for them.

**Rows two and three depend on one declaration that rev3 introduced for a different reason.** §CITE-QUAL requires each capability to declare whether it returns *assertable content* or only a *status*, so that action tools are never graded. That declaration is **`result_kind`**, named and specified in §CITE-QUAL (rev6). The same declaration answers "which tool results must be minted for". It is authored once and consumed twice, and the minting work for rows two and three therefore sequences after it.

**`result_kind` also settles how many citations one tool result yields (rev6).** A `single` capability returns one document, so its result mints one citation. A `collection` capability returns many content items, each with its own identity, so its result mints **one citation per item** — a web search returning ten hits is one tool result and ten sources, and each hit carries its own `source_system`, `source_id` and `revision`. A `status` capability mints nothing. This was open until rev6: the table above named the paths but never the cardinality.

**The model is never in this path.** It receives citations as a reserved result key it cannot write, exactly as it receives `data_absent` (#580). Its only power is to reference an id.

### How a citation is carried through ingest

`IngestTextRequest`, `BatchIngestItem`, and `InternalIngestRequest` each gain one optional field:

```jsonc
"source": {                      // SourceRef — the inbound half
  "source_system": "github",
  "source_id": "OraclousAI/oraclous-backend:README.md",
  "revision": "e3b0c44298fc1c14…",   // optional inbound
  "revision_kind": "blob_sha",        // optional inbound
  "url": "https://github.com/…/blob/e3b0c44/README.md",
  "title": "README.md",
  "author": { "display_name": "…", "source_handle": "…" },
  "permission_ref": null
}
```

The platform computes `citation_id` and `retrieved_at` server-side. When `revision` is absent inbound, the platform sets it to the SHA-256 of the ingested content with `revision_kind: "content_hash"` — so `revision` is **never null outbound**, and a source with no version concept still supersedes correctly on content change.

**One consequence of dropping the locator.** Every chunk of one ingested document now shares a single `citation_id`, because they share a document version. That is correct for v1: a citation answers "which document, at which version", and the reader opens it. It is also why sub-document precision, when it arrives, is an additional field and never a change to identity.

**Who fills it: the connector, and only the connector.** The connector is the one party holding the source-native identity — the GitHub API response the platform already receives carries `sha` and `html_url`, and today the connector throws both away. The ingest caller passes `source` through **unmodified** and never synthesizes one.

**The `upload` path, corrected (rev2).** rev1 said an absent `source` yields an `upload` citation whose `url` is "the platform's own document URL". **That URL does not exist.** Verified during briefing: `GET /api/v1/graphs/{id}/documents` and `GET .../jobs/{job_id}` return ingest-job metadata only, and `GET .../documents/{job_id}` is not a route. So an uploaded file is currently the one source the platform itself cannot resolve, which is the same defect this Contract exists to fix — and the one case where we have no third party to blame.

Until that route exists, an `upload` citation carries `source_id` = the ingest job id, `revision` = the content hash, and `url: null`. Serving an uploaded document back is tracked as its own work item; it is small, and it should not stay open long.

**`citation` is server-stamped and unforgeable.** A caller- or LLM-supplied `citation` (or any `source_*` key) inside `properties` is **stripped**, exactly as `organisation_id` and `ingestion_source` are stripped today (`knowledge-graph-service/multi_tenant.py`, threat T1). `ingestion_source` is retained for backward compatibility and becomes derived from `citation.title`.

**In the agent loop.** The knowledge-retriever connector returns each hit with its `citation`, and the run records the set of `citation_id`s it served. This is a **reserved result key** the platform sets and the model cannot — the same mechanism as `data_absent` (#580).

### What "resolves" means, mechanically (rev4, markers narrowed in rev5)

Two rules, both blocking, both evaluated **in platform code** at the end of a run. Neither depends on anything a third-party tool chooses to send, because the platform mints the id itself.

| # | Rule | Kills |
| --- | --- | --- |
| 1 | An answer **names a source in prose** while carrying no `citation_id` for it. The markers are **`source:` and `sources:`**, and nothing else (rev5). | `(source: partner-agreement.md)` — a fact pointing at a source the platform never issued. |
| 2 | A cited `citation_id` is **not in the set the platform served** to that run. | Every hallucinated source: an id the model invented, or an id served to some other run. |

Otherwise it PASSES.

**The two rules are not the same kind of check, and the difference must not be blurred.**

**Rule 2 verifies.** It tests membership of a set the platform minted, recorded, and served. The model never sees the derivation, so it cannot forge its way into that set. This is the guarantee the Contract exists to give.

**Rule 1 does not verify anything.** `source:` / `sources:` is a prose heuristic: it guesses that a member is attributing a fact, and it cannot check any claim against anything. It is **a nudge inside a feedback loop, not a guarantee**, and it is defensible only on that footing — a blocked draft costs the member one iteration rather than costing the user an answer. Limit 2 below states the consequence directly: if the feedback loop is ever removed, this check stops being acceptable. Anyone reading rule 1 as a second guarantee has misread it.

**Two mechanisms, one token (rev5).** `source_tool_call_id` was a rule 1 marker under rev4 and is not one now, because a real verifier already owns it. [`#642`](https://github.com/OraclousAI/oraclous-backend/issues/642)'s `validate_grounding` resolves every declared `source_tool_call_id` against an `ok` tool step in the member's own trace and fails closed on a missing, null, unresolvable, or errored id. The division has to be stated plainly, because it is the thing a future reader will get wrong:

> **#642 answers "did this call really happen". §CITE answers "was this source really served". Two mechanisms, two questions, one token — and only one of them can verify it.**

The cost of getting this wrong was not theoretical. The platform *orders* every tool-declaring member to emit that token (`GROUNDING_DIRECTIVE`), so on the deployed stack a live member was corrected four times and killed at `citation_unresolved` for obeying its own instructions, while #642 was satisfied throughout. Harness execution `15674e6f-73c1-4467-b6fa-a33177924330` is the record. A gate should be code that checks platform state, never a pattern that reads prose over a token something else already proves.

**What this Contract guarantees, and where the guarantee stops.** §CITE guarantees **provenance**: the cited source exists, and it was really served to this run. It does **not** check **fidelity** — whether the cited source actually supports the sentence beside it. A model can put a served `cit_` id next to a wholly invented claim and pass both rules. That gap is deliberately outside this Contract, and it is the open question on [`oraclous-backend#789`](https://github.com/OraclousAI/oraclous-backend/issues/789).

**An answer that cites nothing at all is not a violation.** The model is not a source of truth, so anything it says without a citation is its own reasoning, and reasoning needs no source. This covers the case the gate must never punish: a member that retrieves, reads what came back, and honestly reports that it has no answer. That is the product working. *Why* a member found nothing is a separate concern with a hundred causes — retrieval quality, an empty workspace, a poor query — and it is a retrieval problem, not a citation problem. This gate does not pretend to diagnose it.

**Rule 1 replaces rev2's rule 1, which is deleted.** The old rule ("an asserted fact carries no `citation_id`") cannot be evaluated in code — separating an asserted fact from reasoning is a judgment call, and a gate implemented as a model instruction is a gate that can be talked out of. The replacement checks the one thing that is both mechanical and diagnostic: the member pointed at a source, so a citation was available to it, and it wrote prose instead.

**Where the checker runs: in the platform, not as a model.** UC-E1 draws `citation-checker` as a team member, and a harness member may still review citation *quality* as an ordinary reviewer. The **guarantee**, however, is code at the run boundary.

### What a violation does (rev4)

**A blocked answer goes back to the member, not to the user.** The member receives a specific message naming the defect and the remedy, and produces another answer. Only a member that cannot satisfy the rules within the run's iteration budget fails the run.

| Rule | Case | What the member is told |
| --- | --- | --- |
| 1 | the run served at least one citation | Your answer names a source in text but carries no citation. Cite the `citation_id` you were given for that source, or remove the claim. |
| 1 | **the run served nothing** (rev5) | Your answer names a source in text but carries no citation. No citations were served to this run, so there is no `citation_id` for you to cite — remove the source attribution from your answer and state the claim on your own account, or drop the claim. |
| 2 | — | You cited an id that was never served to this run. Cite only ids from the results you were given. |

**Stated reason:** the member is the only party that can fix the defect, and an error it cannot act on is one it can only retry blindly — the failure [`oraclous-backend#692`](https://github.com/OraclousAI/oraclous-backend/issues/692) recorded, where a member was told "409" and simply repeated the failing call.

**Why rule 1 has two messages (rev5).** The verdict is the same in both cases — pointing at a source the platform never issued is the defect whatever the run served, and a run that served nothing is exactly the run where a prose source is most likely to be invented. What differs is the **remedy**. rev4's single message names a remedy that does not exist on an empty served set, and a live member burned its entire iteration budget discovering that. A correction the member cannot perform is the #692 defect again, reached from a different direction.

**Terminal precedence (rev5, [`oraclous-backend#792`](https://github.com/OraclousAI/oraclous-backend/issues/792)).** One line, for the case where the budget is spent, the last draft was blocked by this gate, *and* the run's retrieval reported data-absence ([`#580`](https://github.com/OraclousAI/oraclous-backend/issues/580)):

> **Terminal precedence:** a rule 2 violation outranks every degrade; a rule 1-only block on a data-absent run degrades as `empty_retrieval` (ADR-021).

Three branches follow from it. A block **including a rule 2 violation** ends `ESCALATED` / `citation_unresolved`, whatever the retrieval reported — a forged citation is WRONG data, which is this Contract's core threat, and shipping it as a flagged PARTIAL is the outcome the Contract rejected. A **rule 1-only** block on a data-absent run ends `PARTIAL` / `empty_retrieval`: a `Sources:` line on a nothing-served run is the accepted Limit 2 misfire landing on MISSING data, and Limit 2 priced that misfire at one iteration, never at a hard failure of the honest decline rev4 exists to protect. A **rule 1-only** block on a run whose retrieval *did* return data is unchanged — `ESCALATED` / `citation_unresolved`, because the member had sources to cite and spent the budget not citing them.

**Both obvious answers are wrong, which is why the clause splits by rule.** "The gate always wins" hard-fails the protected member over a single word: the same data-absent decline flips outcome on whether it wrote `Sources:`. "Empty retrieval always wins" is worse — a member that kept forging ids until the cap would ship its forged-id answer to the user as PARTIAL output. Each of those positions is right about one rule and wrong about the other.

**Two limits the implementing brief must set.**

**Limit 1 — retries are finite.** A member that cannot satisfy the gate must not loop. The run's existing iteration budget is the bound, and what a run that exhausts it reports is the terminal-precedence clause above.

**Limit 2 — rule 1's detection will misfire, and that is tolerable only because of the feedback loop.** "I edited `partner-agreement.md` for you" names a file and asserts no fact; a naive pattern blocks it. Under rev4 that costs the member one iteration rather than costing the user an answer, which is what makes a prose-shaped check acceptable here where a hard block would not be. **If the feedback loop is ever removed, this check stops being acceptable and must be re-derived.** The detection is narrowed as far as it can be, and the markers are named in the Contract (`source:`, `sources:` — rev5) rather than left to a regex written at implementation time. **Changing that list is the Contract's business, never the implementer's.**

**What rev1 had as rules 3 and 4 is not gone — it moved.** Requiring a document id, a version, and a link is right, but enforcing it mid-answer punishes the user for a tool limitation at the moment nothing can be done about it. It is enforced at §CITE-QUAL instead, when a tool is connected and an admin can still choose a different one. Under rev3 a tool with no document identity is refused there outright, so by the time an answer is written the only thing that can still be missing is the **version** — and a missing version degrades the citation rather than failing the answer. The console shows exactly what is known and what is not.

**Deliberately NOT in the check: fetching the `url` to confirm the document still exists.** That is freshness and deletion propagation (§5.3 capability 8, UC-E1 acceptance 3), a separate mechanism on its own cadence. Folding it in would make an in-loop gate network-bound and rate-limited, and would conflate "well-formed and really served" with "unchanged at the source". Both are needed; they are not the same gate.

Checked against the recorded PoC output, the `(source: partner-agreement.md)` half of that run fails at rule 1 — a filename in prose, pointing at a source the platform never issued. Its invented `source_tool_call_id=call_...` is caught by [`#642`](https://github.com/OraclousAI/oraclous-backend/issues/642) rather than here (rev5), which is where it was always better caught: #642 can tell whether the call actually ran, and §CITE cannot. That was the state before any of this shipped. Since [`oraclous-backend#742`](https://github.com/OraclousAI/oraclous-backend/issues/742) a retrieval hit carries a real citation; since [`#743`](https://github.com/OraclousAI/oraclous-backend/issues/743) a run records what it served; and since [`#782`](https://github.com/OraclousAI/oraclous-backend/issues/782) the gate itself runs at the run boundary, so a member writing that same prose is corrected and re-answers.

### §CITE-QUAL — a tool that cannot cite its sources is refused at connect time (rev3, declaration named and moved to the capability in rev6)

Our own connectors always carry document identity, because we write them: GitHub gives a repo, a path and a commit; Drive gives a file id and a revision; a REST or SQL read gives an addressable record. **The uncertainty is confined to tools we did not write** — an imported MCP server returns whatever shape its author chose. One Notion MCP returns a page id, a URL and an edit timestamp. Another returns a title and a wall of text.

That is a **procurement problem, not an answer-time problem**. The admin connecting the tool is the person who can fix it, and connect time is the moment they can still pick something else.

Each **content-returning** tool is graded at connect or import time:

| Grade | Meaning | Consequence |
| --- | --- | --- |
| `exact` | document identity, a version, and an openable link | permitted |
| `document` | document identity and a link, no version | permitted; "as of" falls back to read time |
| `weak` | the connection is known, the document is not | **refused** — the tool cannot be connected, and the admin is told why |

**A `weak` tool is refused, not warned (rev3).** Reliable alternatives exist for every source class in the portfolio, so tolerating a tool that cannot describe its own output buys nothing and costs the guarantee. A warning that an admin can click past is a guarantee with a hole in it.

This rule needs two limits, or it refuses things it was never aimed at.

**Limit 1 — it applies only to capabilities that return assertable content.** Most of the catalogue returns a *status*, not content: open a pull request, send a message, write a file, deliver a report. Those have no source to cite and are never graded. A capability declares which kind it is, in `result_kind` below; only the content-returning kinds are gated. Getting this wrong would refuse half the registry, so it is a first-class part of the rule rather than a footnote. **rev1–rev5 said "a tool declares"; rev6 corrects that to the capability.** One tool exposes a `read_file` that cites next to a `list_files` that does not, so a tool-level declaration is wrong the moment the same field is consumed by anything other than the gate. For an MCP import the two are the same object — one imported tool becomes one operation — which is why the tool-level wording survived this long.

**Limit 2 — first-party sources must pass our own gate before it is switched on.** An uploaded file currently grades `weak`, because no route serves an uploaded document back (see the `upload` note above). Under rev3 that would refuse our own upload path, which is absurd. Serving an uploaded document back is therefore a **prerequisite** for enabling the refusal, not a follow-up to it.

#### `result_kind` — the declaration itself (rev6)

Each entry of a capability descriptor's `spec.capabilities[]` carries one more field. It is **declared by the connector, never inferred by a caller** — the same rule this Contract applies to the `SourceRef`.

```jsonc
// spec.capabilities[i]
{
  "name": "read_file",
  "description": "Read a file's content",
  "parameters": {"repo": "str", "path": "str"},
  "result_kind": "single"        // "status" | "single" | "collection"; absent = undeclared
}
```

| Value | The capability returns | Graded here | Minted for (§CITE rows 2–3) | Offered as a knowledge source |
| --- | --- | --- | --- | --- |
| `status` | an outcome, not content — open a pull request, send a message, write a file, deliver a report | no | no | no |
| `single` | the content of **one** identified document | yes | yes, one citation | **yes** |
| `collection` | **many** content items, each with its own identity — `core/web-research.search` | yes | yes, one citation per item | no |
| absent / `null` | undeclared | **refused** | no | no |

**Why the value is `single` and not `document`.** `document` is already a `citation_grade` value in the table above, meaning "document identity and a link, no version". Two different things under one word in one section is a reading hazard, and the grade is agreed text from rev3, so the newer field gives way.

**Absent is undeclared, and it is never read as `status` (decision 16).** `null` is refused by this gate *and* hidden from the ingest picker. Reading it as `status` is fail-open: an ungraded content-returning tool would skip the gate entirely.

**What a wrong declaration can and cannot do.** First-party declarations are trusted by construction; third-party ones are not, which is why this section grades rather than asks. The two failure directions are not symmetric, and only one of them is dangerous. **Over-claiming** — `single` on a capability that returns no source — cannot manufacture provenance: minting takes a `SourceRef` the connector actually returned, so no `SourceRef` means no citation, no served id, and rule 2 blocks any assertion from it. The cost is one wasted call and an honest refusal. **Under-claiming** — `status` on a capability that returns content — skips grading *and* skips minting, so a member reads content and asserts from it uncited. That is the fail-open case, and it is the reason the field is required rather than defaulted.

Two points stay with the implementing brief, because they are mechanism and not shape. **How the grade is determined** — reading a declared output schema is cheap but many MCP servers declare nothing useful, while a probe call is reliable but needs a credential and may cost money; a hybrid is likely right and should be argued rather than assumed. **Where the grade is stored** — the tool instance in the capability registry is the obvious home, and it should be confirmed against the existing configure flow rather than given a new table by reflex. `result_kind` is the declaration and lives on the **descriptor**; the grade is determined and lives on the **instance**. They are two fields on two objects with two authors, and neither replaces the other.

**Where `result_kind` itself is specified is an open gap, and it is not this page's to close.** The descriptor's own `spec.capabilities[]` operation list is specified nowhere: OHM v1.0 §3.3 specifies the *harness manifest's* capability references (`ref`, `binding`, `config`), a different object, and [`Kind: tool`](../architecture/platform-architecture-v1.1/section-4-manifest-format-specification.md) gives a tool a single `spec.input_schema`/`spec.output_schema` pair with no operation list at all, which shipped multi-operation descriptors already contradict. Recording the field here is therefore provisional on that shape being written down properly. **This is not an OHM version note** — §3.3 describes something else — and it is tracked separately rather than resolved inside a citation contract.

**Migrating the existing catalogue, and the console consumer.** First-party descriptors are backfilled in the same change that adds the field. MCP-imported rows stay `null` and heal on re-import. The console's ingest picker filters on a `read_<noun>` operation-name test today ([`oraclous-frontend#202`](https://github.com/OraclousAI/oraclous-frontend/pull/202), merged); that test is **deleted with no fallback**, because a fallback would keep the guess alive permanently and there is nothing left for it to catch once the backfill lands. The backend ships the field, the backfill and the gateway surface first, so the picker never empties. Every currently-imported MCP tool leaves the picker on the day the console switches, and nothing that worked stops working, because no MCP read mints a citation today. The console's existing post-read refusal stays: it is the enforcement, and `result_kind` is the affordance that stops the wasted call from being offered.

### Author is in; label and confidence are not

**`author` is in this Contract.** It is a property of the source record, it arrives on the same connector call that yields the content, and it is unrecoverable later. UC-D1 acceptance 3 ("a decision made six months ago is retrievable with its rationale and **its author**") depends on it. `created_by = "multi_tenant_pipeline"` is the pipeline, not a person, and is not a substitute.

**`label` (DIRECT / INFERRED / ABSENCE / ASSUMPTION), `confidence`, and `supersedes` are NOT.** They are properties of a claim the platform *derived*, not of a source document; an ingested chunk is DIRECT by construction, so the label carries no information until a claim record exists separately from a source chunk. That object is the Claim Registry and the UC-E2 evidence ledger. Freezing the shape before the object exists would be guessing.

This Contract is therefore the **source half** of the use-case glossary's knowledge record (§1.7): the claim, the source, the label, the confidence, the as-of date, the supersession pointer. It delivers the source, the as-of date (`retrieved_at`), and the supersession *mechanism* (a revision-derived `citation_id`). The claim, the label, and the confidence are the follow-on Contract, which consumes `Citation` unchanged as its `source` field.

## §DELIV — The declared form of a deliverable (#730 / #870)

Owner: solution-architect. Status: **AGREED (2026-09-04, Parham Davari)** — shape ruled, neither repo has implemented it. Tracking Contract: [`oraclous-backend#870`](https://github.com/OraclousAI/oraclous-backend/issues/870); implementing story: [`oraclous-backend#730`](https://github.com/OraclousAI/oraclous-backend/issues/730). Adjacent and deliberately separate: [`oraclous-backend#855`](https://github.com/OraclousAI/oraclous-backend/issues/855) (`requires_valid_json`, [`#853`](https://github.com/OraclousAI/oraclous-backend/issues/853)).

### Why this crosses the repo boundary

The console renders a chooser at team-definition time and shows the declared form on a finished run, so both repos consume the shape and neither may define it (`oraclous-backend/CLAUDE.md` §12). `OHMTaskInput` is the precedent: it became a Contract for the same reason, and is read by the same screen at the same moment.

### What exists today

`OHMManifest` carries `members`, `orchestration`, `task_board`, `budget` and `task_input`. Nothing expresses what the team is meant to **produce**. Two nearby member fields are not this one: `outputs_schema` names the required keys of an already-parsed hand-off payload, which is the shape of data passing between members; `requires_valid_json` says one member's output must parse. Neither says what form the user receives.

No renderer exists anywhere in the capability layer — no PDF writer, no docx writer, no HTML artefact builder. That is what the ruling defers, and it is why the reserved values must be refused at definition time rather than accepted and quietly ignored.

### The shape

Two fields, not one.

| Field | Lives on | Says |
| --- | --- | --- |
| `deliverable_format` | `OHMManifest` | the form of what the **user** receives |
| `deliverable_format` | `OHMMember` | the form of what **that member** hands on |

Both are optional. Accepted values: `markdown`, `text` (supported now); `pdf`, `docx`, `html` (declared, refused).

### Decision 1 — both levels, because they answer different questions

A member declares the form of what it hands on; the team declares the form of what the user receives. **Stated reason:** a team produces one deliverable for a person, and a member produces an intermediate for another member. Collapsing them into one field makes "the deliverable" mean whichever member happened to run last, which is a property of the graph rather than a choice anybody made.

### Decision 2 — the team's form is stated, never inferred from its members

The last member to finish does **not** decide, and neither does a named final member. **Stated reason:** inference makes the deliverable's form change when the team is edited for unrelated reasons. Add a proof-reader after the writer and the user silently starts receiving plain text instead of markdown, with no format setting touched and nothing in the diff that looks like a format change. An explicit field on the team costs one more value at definition time and removes that entire class of surprise.

### Decision 3 — reserved values are declared, and refused at definition time

`pdf`, `docx` and `html` are members of the accepted value set from day one, marked unavailable, and **refused when the team is defined** — never accepted and discovered at the end of a paid run.

The refusal must distinguish *not built yet* from *unrecognised*. A message reading "not a valid value" sends the user hunting for a misspelling that is not there; "not supported yet" tells them the truth, which is that the renderer does not exist. **Stated reason:** the cheaper option — leaving the reserved names out of the set entirely, so they fail as unknown values — saves one list of names and pays for it by lying to the user about why. The console renders the unavailable values visibly rather than hiding them, so the chooser doubles as the roadmap.

Failing at run's end was considered and rejected outright: it spends a full run and its model cost before refusing, and the work is unusable when it arrives.

### Decision 4 — absence is back-compatible, and stays that way

The field is optional. A team without it produces whatever the model typed, exactly as today. **Stated reason:** every stored team omits it, so any other reading breaks them all. Absence is specifically **not** read as `markdown`: that would silently change what a saved team produces, which nobody asked for and nobody would see happen.

### Decision 5 — the boundary with `requires_valid_json` is stated, not merged

`requires_valid_json` ([`#853`](https://github.com/OraclousAI/oraclous-backend/issues/853)) says a member's output must **parse**, so the next member can read it. `deliverable_format` says what **form** the text takes. Two settings, two audiences: one serves the next member, the other serves the person.

**Stated reason:** [`#855`](https://github.com/OraclousAI/oraclous-backend/issues/855) raises "this member writes YAML" and "this member writes CSV" as a future requirement, and without a stated line the two would ship within one release as two fields both answering "what form is this text in" and disagreeing. If #855 later wants a typed format for a member's output, that is the member-level field above; it is not the team's deliverable, and it does not replace the parse requirement.

### For the implementing brief

The value set, which values are selectable now, and how an unavailable one is presented are all settled above — those were the three things the console needed. Two points stay with the brief because they are mechanism rather than shape: whether the member-level field is enforced or advisory before a renderer exists, and where the refusal is raised so a manifest arriving through the importer fails the same way as one built in the console.

