---
confluence_id: TBD
title: "R6 — Gateway hardening (release brief)"
---

# R6 — Gateway hardening (release brief)

| Release ID | R6 |
| --- | --- |
| Status | **RELEASED — §22-signed-off (Reza, 2026-06-10).** All 9 slices: 1–6 ✅ · Slice 7 ✅ (#209/#210/#211, webhook ingress — 3 services) · Slice 8 ✅ (#213, MCP server; MCP client/import deferred) · Slice 9 ✅ (#215, sole-ingress). Sign-off artifact: the full gateway smoke GW-1..GW-15 = 81 checks / 0 fails, live on the real stack from merged main. Successor: [R7-SEC — security hardening](r7-security-hardening-brief.md). |
| Owner | tech-lead (Reza Jahankohan) |
| Briefer | product-planner (architecture: solution-architect; threats: security-architect) |
| Dependencies | R3.5 (all six services real), R4 (harness), R5 (execution-engine) — all §22-signed-off |
| Governing decisions | **[ADR-019](../adr/adr-019-r6-gateway-datastore-and-integration-key-authz-floor.md)** (Accepted — gateway datastore + integration-key authz floor); **[ADR-015](../adr/adr-015-gateway-incremental-contract-and-versioning.md)** (Accepted 2026-06-08 — unblocked Slice 1) |

> R3.5 built the gateway as a real **reverse-proxy edge** (route table → proxy, edge-JWT + identity forwarding, CORS, health; §22-signed-off). The *richer* surface was deferred. **R6 hardens the gateway into the platform's sole, external contract surface.** Built **first** and **strictly sequential** (Reza's decision): one vertical slice at a time, each ending in a §22 gateway smoke against the real stack, signed off before the next opens.

## Goal

Make the application-gateway the single hardened external door: a versioned public OpenAPI + the (already-built) ORA-37 error contract; the first stateful authorization floor (integration keys → published agents, reused by widgets/MCP); gateway-owned chat persistence riding the R4 harness; the engine EVENT-fire path + webhook ingress; edge rate-limit / request-size / per-key CORS; and finally **sole-ingress** — closing upstream host ports so every external request transits `:8006`.

## The two decisions (confirmed — see ADR-019)

1. **The gateway gets its OWN dedicated, org-scoped, RLS-backed Postgres** (integration-key store, published-agent records, chat persistence) — reversing the R3.5 "stateless / no database" invariant for those surfaces. Gates Slices 3 / 4 / 6.
2. **R6 adds exactly one new authz primitive — the integration-key allow-list** (per-key → bound agent/capability, per-key CORS + rate-limit, org_id, TTL). Everything else stays `organisation_id`-scoped. **Cross-org / ReBAC sharing is explicitly deferred**; the published contract declares only enforced auth-modes.

## Scope

**In:** versioned public OpenAPI + ORA-37 confirmation; gateway Postgres + integration-key store; published-agent public surface + key CRUD; per-key CORS; chat persistence + thin chat surface (rides the R4 harness, non-streaming); engine EVENT-fire + webhook ingress; edge rate-limit + request-size; MCP server + client (with HITL + admin-approval); sole-ingress.

**Out (deferred / other releases):** cross-org / federation ReBAC and wiring `ReBACEngine` at the gateway (ADR-019); **all FE work** (chat/keys/widget/published-agents UI → R-Frontend); streaming/SSE chat (needs a streaming harness execute); the embeddable-widget *build-out* (reuses the key model, a later slice); members/invitations admin surface (org-scoping + a role bit — fold post-keys only if scope extends); closing substrate ports (Neo4j/Postgres/Redis — application-services-only unless security-architect decides otherwise).

## The 9 slices (strictly sequential)

| # | Slice | Source verdict | Est | Opens only after |
| --- | --- | --- | --- | --- |
| **1** | **Public OpenAPI** (`openapi/v1.yaml` as the declared contract, served before the catch-all) + **openapi-diff-gate** CI + confirm **ORA-37** on gateway-own *and proxied-upstream* errors | greenfield | M | **ADR-015 Accepted** |
| **2** | **Edge hardening pt.1** — Redis-backed rate-limit (429 + Retry-After) + request-body-size guard (caps *streamed* bytes, not the header) | reshape | M | S1 + limiter-posture ruling |
| **3** | **Gateway datastore + integration-key store/validator** (the stateful authz floor — established once, reused by 4/8) | reshape | L | **ADR-019** (done) |
| **4** | **Published-agent public surface** (`GET /v1/agents/{slug}`, `POST .../invoke`) + **integration-key CRUD** (publish/list/rotate/revoke) | reshape | L | S2, S3 (the key store + validator already shipped in S3) |
| **5** | **Edge hardening pt.2** — per-key / per-origin CORS scoping (stops the blanket middleware answering keyed paths) | reshape | M | S2, S4 |
| **6** | **Chat persistence + thin chat surface** (gateway's first customer-data write; executes via the R4 harness synthetic-agent pattern; **re-tenant to org**, not legacy user-scope) | reshape | L | ADR-019 (same gateway DB) |
| **7** | **Engine EVENT-fire path** *(the one cross-service prerequisite)* → **webhook ingress** (HMAC-verify raw-body-first, 404-never-403, dedup via engine idempotency) | reshape | L | R5 engine (done) + **cred-broker webhook-secret ns** + security T5 ruling |
| **8** | **MCP server + client** (org-scoped tools/list+call over Streamable-HTTP; import external MCP tools as OHM `kind=tool` via a `McpToolExecutor`) with **first-invocation HITL + admin-approval** | greenfield | L | S3/S4 + **MCP-substrate ADR** + cap-registry `McpToolExecutor` |
| **9** | **Sole-ingress** — close upstream host ports; gateway becomes the only door (smoke reshape **must land first**, all 7 upstreams `AUTH_MODE=gateway`) | greenfield | S | **all** prior + security sole-ingress ADR |

## Cross-service prerequisites (R6 is not gateway-only)

* **auth-service:** ~~an integration-key mint/scope/validate route~~ — **superseded (Slice-3 scoping):** ADR-019 puts the integration-key store + the mint/validate in the **gateway's own** Postgres, and auth-service has no integration-key store to reuse. The only surviving auth-service item is confirming an **org-admin role claim** in the member JWT for the admin-gated surfaces (members/invitations, MCP-client register) — not a key route, not on the Slice-4 critical path.
* **credential-broker:** an org-scoped **webhook-secret namespace** (HMAC secrets live there, ADR-008 — never in the stateless gateway).
* **capability-registry:** the **`McpToolExecutor` + external-MCP registry** (the import target for Slice 8 — without it imported descriptors raise `NoExecutorError`).
* **gateway infra (devops):** **Redis** wired in (`GATEWAY_REDIS_URL` + lifespan + compose) for Slices 2/5; the **openapi-diff-gate** CI job; the **sole-ingress compose overlay**.
* **Contracts (record once → `flows/interface-contracts.md` with a shared fixture, then migrate into `openapi/v1.yaml`):** webhook→schedule(org/principal) + engine EVENT-fire shape; the chat request/response shape the FE consumes; the integration-key publish/invoke shapes. ORA-54 (BE error envelope) closes here vs the ORA-53 fixture; ORA-55 (FE parse) stays R-Frontend.
* **security-architect rulings (before the dependent merges):** webhook replay/timestamp tolerance + per-source rate-limit (S7); rate-limiter fail-open posture + `X-Forwarded-For` trust boundary (S2); HITL/admin-approval seam for imported MCP tools (S8); sole-ingress dev-vs-prod port split + substrate-port decision (S9).

## Top risks

* **Org-scoping leak via the new auth paths (T1):** integration-key/webhook/chat mint identity *without* `verify_token()` — a bug = an external caller asserting an arbitrary org. Strip-then-assert anti-spoof on every new path; `org_id` real, never `''`; fail-closed on no org.
* **Chat tenancy reshape:** legacy chat is *user*-scoped; re-tenant to *org* + the ADR-012 scoped seam; cross-org isolation test is a gate.
* **Re-importing the MCP failure mode (S8):** the retired MCP substrate failed on untyped schemas / static auth / per-SSE pool teardown — those are **acceptance criteria** now (typed OHM schemas, per-request integration-key auth, process-scoped pool, pinned Streamable-HTTP transport behind the executor).
* **Malicious imported MCP tool (S8):** runs in the org's harness with its creds — first-invocation HITL + admin approval + descriptor validation + a provenance row per call are non-optional.
* **Webhook replay (S7):** HMAC proves authenticity not freshness — timestamp tolerance + verify-before-process + 404-never-403.
* **Stateless-gateway traps (S2/S7):** dedup lives in the engine, not the gateway; HMAC secrets in the broker; **rate-limit fails *open*** (a Redis outage must not throttle the sole ingress), while size + CORS fail *closed*.
* **Sole-ingress breaks if done early (S9):** every smoke curls localhost upstream ports — the smoke reshape (PR1) must precede the port close (PR2), and the `X-Internal-Key` gate becomes the only thing between "on the docker network" and "trusted principal."
* **Published-contract disclosure (S1):** the spec is a deliberate disclosure surface — it must expose only the public plane (never `/internal/*`), keep the error component `additionalProperties:false`, and claim no authz the substrate doesn't enforce.

## Definition of Done

Each slice meets the full **§22 8-gate per-service DoD** (structure-conformant — the gateway shell stays thin except the ADR-019-sanctioned chat/key Postgres; not-hollow; runs; real endpoints; a **smoke vs the real substrate**; **Reza sign-off**) before the next opens. **Release-level:** ADR-015 Accepted + ADR-019 honoured before any stateful slice; `openapi/v1.yaml` published + the diff-gate live + the canonical-contract home flipped from `flows/interface-contracts.md` (docs-writer) only after publish+gate; ORA-37 proven on gateway-own *and* proxied errors with zero forbidden-substring leakage; the integration-key allow-list is the only new authz primitive and the spec claims no authz the substrate can't enforce; cross-org ReBAC explicitly not pulled forward; **sole-ingress proven** (gateway smoke green *while* direct localhost upstream curls are refused, all 7 upstreams `AUTH_MODE=gateway`). Sequential: slices run 1→9, no parallel cuts; each ends by handing off to the named next owner (§4/§9.1).
