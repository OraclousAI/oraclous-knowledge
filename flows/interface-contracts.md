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
| Resolvable citation on any tool result | — ([oraclous-backend#735](https://github.com/OraclousAI/oraclous-backend/issues/735); FE [#194](https://github.com/OraclousAI/oraclous-frontend/issues/194)) | AGREED at **rev3** (2026-08-09), unimplemented — blocks the UC-D1 first slice; evidence [oraclous-backend#734](https://github.com/OraclousAI/oraclous-backend/issues/734) | See §CITE |

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

Owner: solution-architect. Status: **AGREED, unimplemented** — no side has built it. Driving evidence: the UC-D1 proof of concept, [`oraclous-backend#734`](https://github.com/OraclousAI/oraclous-backend/issues/734), filed against §5.3 capability 6. Tracking Contract: [`oraclous-backend#735`](https://github.com/OraclousAI/oraclous-backend/issues/735); frontend consumer: [`oraclous-frontend#194`](https://github.com/OraclousAI/oraclous-frontend/issues/194); follow-on knowledge-record Contract: [`oraclous-backend#741`](https://github.com/OraclousAI/oraclous-backend/issues/741).

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

**`source_system` is a registered slug, not a frozen enum.** UC-E1 acceptance 6 requires a sixth, unplanned source type to be connectable without re-modelling existing records. A closed enum would break that. The constraint is that the value must name a **registered connector**, plus the reserved value `upload`.

**Why `permission_ref` is in the shape now but enforced later.** Per-user permission mirroring (capability 27) is out of the first slice, but the source's permission handle is only obtainable *at read time from the connector*. Omitting the field would force a full re-ingest of every record when capability 27 lands. The field is cheap now and expensive to backfill.

### Where it lives in the retrieval envelope

One typed sibling field, following the `FederatedNodeResultModel` precedent (`source_graph_id` is a sibling, not a `properties` key):

```jsonc
// NodeResultModel and FederatedNodeResultModel each gain ONE field
{ "id": "...", "type": "Chunk", "properties": { … }, "citation": Citation | null }
```

`citation: null` means the record has no source identity — ingested before this Contract, or ingested without a `source`. It is **never a partly-filled object**: a half-citation is indistinguishable from a real one at a glance, and the gate must be able to say "this record cannot be cited" without inspecting five fields.

**One citation per node, on lexical nodes only.** A `Chunk`/`Document` node has exactly one source, so `citation` is singular. A derived or extracted entity node carries `citation: null` in v1, and an answer must cite the lexical hit rather than the entity. Multi-provenance ("one claim, two provenances" — the UC-E1 deduplicator) belongs to the follow-on knowledge-record Contract, not here.

### Where a citation is minted (rev2)

A citation is minted **once, in platform code, at the tool-execution boundary** — the point where a tool result comes back into the runtime. There are three paths into that boundary, and they share one minting function:

| Path | Example | What the tool supplies |
| --- | --- | --- |
| **Connector read → ingest → retrieval** | a GitHub file lands in a workspace and is later searched | full source identity; the citation is stamped at ingest and returned on the retrieval hit |
| **Connector read used directly in a run** | an agent reads a Drive file mid-run and asserts from it | full source identity, minted on the tool result; never stored |
| **Live web / MCP tool** | `core/web-research` search, or an imported MCP tool | whatever the tool's response carries; see §CITE-QUAL |

The last row is why rev2 widened the scope. An agent citing a web page it just read is the same guarantee problem as an agent citing an ingested file, and rev1 covered only the second.

**One minting function, shared by all three rows.** It lives in `packages/citation/` and takes a `SourceRef`; it is not an ingest helper that the other paths borrow. Rows two and three have no stored record to stamp, so a minting function shaped around ingest would have to be rewritten for them.

**Rows two and three depend on one declaration that rev3 introduced for a different reason.** §CITE-QUAL requires each tool to declare whether it returns *assertable content* or only a *status*, so that action tools are never graded. The same declaration answers "which tool results must be minted for". It is authored once and consumed twice, and the minting work for rows two and three therefore sequences after it.

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

### What "resolves" means, mechanically (rev2)

Two rules, both blocking, both evaluated **in platform code** at the end of a run. Neither depends on anything a third-party tool chooses to send, because the platform mints the id itself.

| # | Rule | Kills |
| --- | --- | --- |
| 1 | An asserted fact carries no `citation_id`. | `(source: partner-agreement.md)` — prose is not a citation. |
| 2 | A cited `citation_id` is not in the set the platform served to that run. | The invented `source_tool_call_id=call_...`, and every hallucinated source. |

Otherwise it PASSES.

**Where the checker runs: in the platform, not as a model.** UC-E1 draws `citation-checker` as a team member, and a harness member may still review citation *quality* as an ordinary reviewer. The **guarantee**, however, is code at the run boundary. A gate implemented as a model instruction is a gate that can be talked out of, which is precisely the failure this Contract addresses.

**What rev1 had as rules 3 and 4 is not gone — it moved.** Requiring a document id, a version, and a link is right, but enforcing it mid-answer punishes the user for a tool limitation at the moment nothing can be done about it. It is enforced at §CITE-QUAL instead, when a tool is connected and an admin can still choose a different one. Under rev3 a tool with no document identity is refused there outright, so by the time an answer is written the only thing that can still be missing is the **version** — and a missing version degrades the citation rather than failing the answer. The console shows exactly what is known and what is not.

**Deliberately NOT in the check: fetching the `url` to confirm the document still exists.** That is freshness and deletion propagation (§5.3 capability 8, UC-E1 acceptance 3), a separate mechanism on its own cadence. Folding it in would make an in-loop gate network-bound and rate-limited, and would conflate "well-formed and really served" with "unchanged at the source". Both are needed; they are not the same gate.

Checked against the recorded PoC output, every citation the platform produces today fails at rule 1.

### §CITE-QUAL — a tool that cannot cite its sources is refused at connect time (rev3)

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

**Limit 1 — it applies only to tools that return assertable content.** Most of the catalogue returns a *status*, not content: open a pull request, send a message, write a file, deliver a report. Those have no source to cite and are never graded. A tool declares which kind it is; only the content-returning kind is gated. Getting this wrong would refuse half the registry, so it is a first-class part of the rule rather than a footnote.

**Limit 2 — first-party sources must pass our own gate before it is switched on.** An uploaded file currently grades `weak`, because no route serves an uploaded document back (see the `upload` note above). Under rev3 that would refuse our own upload path, which is absurd. Serving an uploaded document back is therefore a **prerequisite** for enabling the refusal, not a follow-up to it.

Two points stay with the implementing brief, because they are mechanism and not shape. **How the grade is determined** — reading a declared output schema is cheap but many MCP servers declare nothing useful, while a probe call is reliable but needs a credential and may cost money; a hybrid is likely right and should be argued rather than assumed. **Where the grade is stored** — the tool instance in the capability registry is the obvious home, and it should be confirmed against the existing configure flow rather than given a new table by reflex.

### Author is in; label and confidence are not

**`author` is in this Contract.** It is a property of the source record, it arrives on the same connector call that yields the content, and it is unrecoverable later. UC-D1 acceptance 3 ("a decision made six months ago is retrievable with its rationale and **its author**") depends on it. `created_by = "multi_tenant_pipeline"` is the pipeline, not a person, and is not a substitute.

**`label` (DIRECT / INFERRED / ABSENCE / ASSUMPTION), `confidence`, and `supersedes` are NOT.** They are properties of a claim the platform *derived*, not of a source document; an ingested chunk is DIRECT by construction, so the label carries no information until a claim record exists separately from a source chunk. That object is the Claim Registry and the UC-E2 evidence ledger. Freezing the shape before the object exists would be guessing.

This Contract is therefore the **source half** of the use-case glossary's knowledge record (§1.7): the claim, the source, the label, the confidence, the as-of date, the supersession pointer. It delivers the source, the as-of date (`retrieved_at`), and the supersession *mechanism* (a revision-derived `citation_id`). The claim, the label, and the confidence are the follow-on Contract, which consumes `Citation` unchanged as its `source` field.
