---
confluence_id: TBD
title: "ADR-019 — R6 Gateway: a dedicated gateway datastore + the integration-key authorization floor"
---

# ADR-019 — R6 Gateway: dedicated datastore + integration-key authz floor

## Status

| Field | Value |
|---|---|
| Status | **Accepted** |
| Date | 2026-06-08 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Superseded by | None |
| Amends | [ADR-015](adr-015-gateway-incremental-contract-and-versioning.md) (the "stateless edge" note); [ADR-016](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md) §22 gateway DoD; the [gateway service-reference](../services-reference/application-gateway-service.md) ("holds no database") |
| Driving artifact | R6 release-brief scoping (2026-06-08): integration keys, published agents, and chat persistence all need per-key→resource and customer-data state that org-scoping cannot express |

## Context

R6 hardens the [application-gateway-service](../services-reference/application-gateway-service.md) from the R3.5 reverse-proxy edge into the platform's **sole external contract surface** (public OpenAPI, published agents, integration keys, embeddable widgets, MCP, chat, webhooks). Two facts collide:

1. **The gateway was §22-signed-off as a *thin, stateless, no-DB* edge** (ADR-016 / §21; the service-reference asserts "holds no database — by design, the gateway is stateless"). Its only state is the in-memory route table.
2. **Several R6 surfaces need durable state the edge cannot fake.** An **integration key** must encode "this key may call *exactly this one* agent / *this* capability allow-list, with *this* per-key CORS and rate-limit." That per-key→resource binding has **no org-scoped or stateless expression** — `organisation_id` scoping says "this key's org," not "this key's *one* agent." **Published-agent** records (slug → agent, visibility) and **chat persistence** (conversations / messages / tool-call audit) are likewise customer-data writes with no home today.

Two delegation alternatives were considered and rejected: (b) put the state in [knowledge-graph-service](../services-reference/knowledge-graph-service.md) (Neo4j, where the legacy `PublishedAgent` lived) — fragments ownership (tools/agents/chat are not graph concerns) and still forces a synchronous cross-service *validate* hop on every external request; (c) put integration keys in [auth-service](../services-reference/auth-service.md) as a new credential kind — reuses its bcrypt prefix-index, but published-agent metadata (slug, CORS, rate-limit, capability binding) is not an auth concern, so it still splits the model.

Separately, R6 forces an **authorization** question. As-built, the **gateway enforces `organisation_id` scoping only** — it has zero relationship authz. The substrate's `packages/rebac` ReBACEngine is real and fail-closed but enforces `HAS_ROLE`/`CAN_ACCESS` + agent delegation **only at Layer-1** (knowledge-graph); **cross-org / federation ReBAC (ADR-004) is designed-but-unbuilt.** R6's external surfaces (published agents, API keys, MCP) are the first that genuinely need *narrower-than-org* authz, so the floor must be decided explicitly — and the published contract must not claim authz the substrate does not enforce.

## Decision

**1. The application-gateway gets its OWN dedicated database.** A gateway-owned, **`organisation_id`-scoped, RLS-backed (ADR-012)** Postgres — separate from every lower service's store — holds the **integration-key store**, **published-agent records**, and **chat persistence**. This **reverses the R3.5 "gateway holds no database" invariant** for these three surfaces only; the proxy/auth/health paths stay stateless. A dedicated gateway store is the minimal coherent home (delegation fragments ownership and still costs a stateful hop). The §22 gateway DoD and the gateway service-reference are amended accordingly; repositories remain the only DB-access layer (§21).

**2. R6 adds exactly ONE new authorization primitive: the integration-key allow-list.** Each key is `{ hashed key (prefix + last4, constant-time compare), bound published-agent slug OR capability allow-list, per-key CORS origins, per-key rate-limit, organisation_id NOT NULL, status, optional TTL }`. **One mechanism** serves every surface that needs narrower-than-org authz: published agents, embeddable widgets, and MCP key-scoping (member/agent MCP modes reuse the existing Layer-1 org+role engine). **Everything else stays `organisation_id`-scoped** (+ an org-admin role claim already minted by auth-service for admin-gated surfaces — chat, members/invitations, MCP-client registration; webhook receivers are signature-verification, not authz).

**3. Cross-org / ReBAC sharing is explicitly DEFERRED — R6 must not pull it forward.** Out of scope for R6: cross-org / federation ReBAC (ADR-004 `has_federation_agreement`, `federated:*`); wiring `ReBACEngine` as the gateway's production authorizer; fine-grained per-member-per-resource sharing beyond Layer-1 `HAS_ROLE`. The published OpenAPI's per-operation **auth-mode declarations reflect only what is enforced** — edge-JWT, `organisation_id`-scoping, and the integration-key allow-list — never a ReBAC-selectivity the substrate cannot deliver (documenting that would be security theatre). The ReBAC-selectivity upgrade is filed as a follow-on for when gateway/cross-org enforcement is real.

## Consequences

**Positive**
* A clean, single per-key→resource authorization floor for every external ingress; a real home for published-agent metadata and chat persistence; the gateway can become the sole external door (R6 sole-ingress) without a stateful detour.
* The authz story is honest end-to-end: the contract declares only enforced modes.

**Cost / negative**
* **The gateway is no longer a pure stateless proxy** — a signed-off invariant is reversed (for three surfaces). ADR-015 / ADR-016 / the service-reference are amended; the gateway gains a Postgres (+ Redis for rate-limit/CORS) availability dependency on the sole ingress.
* **A new tenancy-leak surface (Threat T1).** The integration-key, webhook, and chat paths mint `X-Principal-*` / `X-Organisation-Id` **without `verify_token()`** — from the key's bound org, a webhook source→org resolution, or the edge JWT. The same **strip-then-assert anti-spoof** discipline as JWT mode must hold on every new path; `organisation_id` must be **real and never empty** (the legacy `org_id=''` placeholder is a tenancy hole — fix before ship); fail-closed when no org is bound. A cross-org isolation test is a release gate for each stateful slice.
* **Chat tenancy reshape:** legacy chat is `user_id`-scoped; the platform is `organisation_id`-scoped — a naive lift carries the wrong isolation axis. Re-tenant to `organisation_id` + the ADR-012 scoped seam; decide whether per-user privacy *within* an org is still required.

**Deferred (filed as follow-on)**
* Cross-org / federation ReBAC (ADR-004); `ReBACEngine` as the gateway authorizer; fine-grained sharing beyond Layer-1 roles.

## See also

* [R6 — Gateway hardening (release brief)](../releases/r6-gateway-hardening-brief.md) — the slices this decision gates (3/4/6 are blocked on it)
* [ADR-015](adr-015-gateway-incremental-contract-and-versioning.md) — gateway contract & versioning (amended); [ADR-016](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md) — §21/§22 (amended); [ADR-012](adr-012-async-worker-database-pooling.md) — RLS / pooled-session scoping; [ADR-018](adr-018-edge-authentication-trusted-gateway.md) — trusted-gateway identity; [ADR-004] — cross-org federation (deferred); [ADR-006] — org-scoping
