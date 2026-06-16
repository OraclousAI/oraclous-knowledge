---
confluence_id: "2490396"
title: "ADR-012 — Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions"
---

# ADR-012 — Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 29 May 2026 |
| Proposed by | solution-architect (with security-architect co-sign) |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Refines | [ADR-006 — Organisation as Outermost Tenancy Unit](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) |
| Superseded by | None |
| Refined by | [ADR-013 — Fail-Closed Authority Placement at the Substrate ReBAC Seam](https://oraclous.atlassian.net/wiki/spaces/OP/pages/3702787) (refines §1's ReBAC slice, 31 May 2026) |
| Driving artifact | [ORA-20](https://oraclous.atlassian.net/browse/ORA-20) Tests Review ratification (the R0.5 organisation-boundary release gate) |

> **⚠ Implementation status (as-built, 2026-06-17 — grade-A audit WP-5).** The §1 enforcement seam exists (`oraclous_substrate.access` — the `scoped_*` ops + `bind_organisation_guc`/`scoped_pg_connection`), but the **§2 RLS backstop is NOT realized in any deployed schema**: no migration calls `oraclous_substrate.schema.postgres.apply(...)` / `ENABLE`/`FORCE ROW LEVEL SECURITY` / `CREATE POLICY` (verified — grep across all service migrations is empty), and the tenant-data services (e.g. capability-registry) run app-level `WHERE organisation_id = …` filtering only. **The sanctioned, live tenancy control today is therefore app-layer org-scoping** (correct everywhere observed); RLS is a **future defense-in-depth backstop, not a shipped one.** The Context line below stating ORA-16 "shipped … the `FORCE`d RLS policy" did not bear out as-built. Realizing the RLS backstop (migrations per tenant-data table + a `NOSUPERUSER NOBYPASSRLS` runtime role + routing request-path DB access through `scoped_pg_connection`) is tracked as an epic: **`oraclous-backend#353`**. This note corrects the over-claim without retracting the design — §1–§3 below remain the target shape.

## Context

[ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) commits the platform to organisation-scoped reads sourced from the authenticated principal context, organisation-stamped writes, and row-level security (RLS) as a defense-in-depth backstop. It leaves two things unstated that turn out to be load-bearing for the commitment actually holding in production:

1. The concrete **enforcement seam** — the single substrate surface every storage path goes through to acquire its organisation scope and fail closed when none is bound. Without a named seam, each store (Postgres, Neo4j, Redis) grows its own ad-hoc scoping and the "every path" invariant becomes unverifiable.
2. The **preconditions under which the RLS backstop is real rather than theatre.** Postgres RLS is silently bypassed by superuser and `BYPASSRLS` roles, and (without `FORCE ROW LEVEL SECURITY`) by the table owner. An RLS policy that the production connection bypasses is a no-op, and ADR-006's "defense-in-depth" commitment is then false in production with no test able to see it.

These surfaced during the Tests Review of [ORA-20](https://oraclous.atlassian.net/browse/ORA-20), the substrate-level organisation-boundary release gate, which reverse-specified the enforcement seam and exposed the RLS preconditions. The gate verifies behaviour at the data layer against real Neo4j/Postgres/Redis; [ORA-17](https://oraclous.atlassian.net/browse/ORA-17) (A2) implements the seam; [ORA-16](https://oraclous.atlassian.net/browse/ORA-16) (A1, merged) shipped the schema, the `FORCE`d RLS policy, and the org-scoped cache keys.

## Decision

This ADR refines ADR-006 with three concrete commitments. It does not supersede it; ADR-006 remains the tenancy-unit decision.

### 1. A single substrate tenancy-enforcement seam

All tenant-scoped substrate access goes through one module, `oraclous_substrate.access`, alongside the existing Layer-1 seams (`rebac`, `provenance`) and the A1 schema surface (`schema/`, `cache_keys`). The module exposes two complementary tiers — the consumer-facing scoped operations are composed over the lower-level enforcement primitives; internal file layout is the implementer's choice.

**Enforcement primitives** (the reshapes of A2's named legacy sources — `_inject_graph_id_filter`, `get_db()`, `FederationService`):

* `enforced_organisation_id()` — the single context-sourced chokepoint; raises when no context is bound.
* `org_scoped_cypher(query, *, alias=...)` — injects the org filter as a bound `$organisation_id` parameter (never interpolated), idempotent when already scoped.
* `bind_organisation_guc(cursor)` — binds A1's Postgres RLS GUC (`app.current_organisation_id`) from the context via `set_config` (bound parameter, never interpolated).
* `authorise_cross_org_traversal(...)` + `CrossOrganisationDenied` — the ReBAC federation gate; fail-closed on ambiguous/absent/error (ADR-004).

**Scoped store operations** (what the gate and consumers call, composed over the primitives):

* `scoped_pg_connection(dsn)` — context manager yielding a connection whose org-GUC is bound from the authenticated context.
* `scoped_write_node(driver, *, label, properties)` — stamps `organisation_id` from context; never honours a caller-supplied one (the Neo4j write boundary — Neo4j has no RLS WITH-CHECK backstop, so this primitive is the sole write control and must be proven by test).
* `scoped_traverse(driver, *, label, marker)` — org-scoped Cypher; cross-organisation traversal mediated by the ReBAC client and fail-closed ([ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083)).
* `scoped_fulltext_search(driver, *, index_name, query)` — hits confined to the bound organisation.
* `scoped_cache_get / scoped_cache_set(redis, *, graph_id, query_text, retriever_type[, value])` — over the A1 organisation-then-graph cache keys.

Every function reads the bound organisation context via `oraclous_governance.propagation` and raises `MissingOrganisationContextError` when none is bound (fail-closed; ADR-006, Threat Catalogue T1-M1). No storage path bypasses this seam, and no parallel module re-implements org-scoping. The retriever layer (A3 / [ORA-18](https://oraclous.atlassian.net/browse/ORA-18)) _consumes_ `scoped_traverse` / `scoped_fulltext_search` — it does not fork them. (Scoped for the neo4j-graphrag-based A3 wrappers by §1b below.)

The **ReBAC slice** of this seam — `oraclous_substrate.rebac.AccessDecisionClient` and the resolvers wired into it — is governed in finer detail by [ADR-013](https://oraclous.atlassian.net/wiki/spaces/OP/pages/3702787), which places fail-closed authority at the seam (not the resolver) so the resolver returns `bool | None` (or raises) and the seam translates ambiguity/error into deny + reason. This refinement does not alter §1; it pins where, inside §1, fail-closed translation happens for the ReBAC slice.

### 1a. Scope boundary — identity resolution is not substrate access

This seam governs _tenant-scoped knowledge-substrate_ access only — the Neo4j/Postgres/Redis tenant tables under ORA-16's `FORCE ROW LEVEL SECURITY` regime, reached via the `scoped_*` operations above. It does **not** govern pre-authentication identity resolution in `auth-service`. Validating an agent (or service-account, or user) credential resolves it by its unique high-entropy prefix in order to _discover_ the principal and its organisation; the operation is therefore the _producer_ of organisation context, not a consumer of it. Routing credential validation through `enforced_organisation_id()` would be circular — no context is bound until validation establishes it. The `auth-service` identity store is a distinct enforcement domain: its credential row carries `organisation_id` (ADR-006 / ORG002) and its _administrative_ paths (list/get/revoke under an already-authenticated principal) are org-scoped within `auth-service`, but the validate-by-prefix path is a legitimate pre-auth global lookup that MUST resolve to exactly one principal and MUST NOT become a cross-organisation enumeration surface. Every _downstream_ substrate access performed by the resolved principal binds its organisation into context and goes through this seam as normal. (Clarified from the [ORA-30](https://oraclous.atlassian.net/browse/ORA-30) escalation, 29 May 2026.)

### 1b. Consumption by neo4j-graphrag-based components (A3 / ORA-18)

The `scoped_*` operations in §1 are the substrate's own data-layer operations and the [ORA-20](https://oraclous.atlassian.net/browse/ORA-20) gate's call sites. They are **not** the execution surface of the A3 multi-tenant retriever/writer wrappers, which adapt third-party `neo4j-graphrag` objects whose Cypher the platform does not author — vector / vector-cypher / hybrid retrieval and bulk graph ingestion (`Neo4jWriter.run(graph)`) have no `scoped_*` equivalent (`scoped_traverse` is name-marker traversal, `scoped_fulltext_search` is fulltext, `scoped_write_node` is a single-node write). For these components, _consuming the seam_ means applying its org-scoping **discipline** — org id from the bound/authenticated organisation context only and never the request body; unconditional overwrite of any caller/LLM-supplied org id; parameterised predicates never interpolated; fail-closed on absent context; defense-in-depth (per-tenant index naming + filter injection + Cypher predicate + post-filter on read; unconditional property stamp on write) — **and proving organisation isolation by test against real Neo4j** (the ORA-18 `organization_isolation` suite, same-`graph_id` cross-bait). The org-scope **predicate spelling and canonical property name MUST have a single source of truth in** `oraclous_substrate.access` — a context-free helper that both the seam's own `org_scoped_cypher` / `scoped_write_node` and the A3 wrappers compose; independently re-deriving the predicate is the parallel re-implementation §1 and Alternative A forbid. Accordingly, §1's "A3 _consumes_ `scoped_traverse` / `scoped_fulltext_search`" and "`scoped_write_node` … the sole write control" statements are scoped to the **substrate's own** node read/write operations, not to the neo4j-graphrag ingestion/retrieval path; A3 consumes the seam's discipline and (per the single-source-of-truth requirement) its predicate helper. The follow-up that introduces that shared helper and binds the wrappers' context to the authenticated principal is tracked in [ORA-52](https://oraclous.atlassian.net/browse/ORA-52). (From the ORA-18 Code Review architecture sign-off, 31 May 2026; solution-architect with security-architect co-sign; tech-lead directed.)

### 1c. Cross-domain backfills — each store written by its owning domain

A migration that must touch **both** the `auth-service` identity store (`agents`, `agent_credentials`) **and** the substrate knowledge store (Neo4j ReBAC subject nodes) is a _cross-domain_ operation. §1a established these as distinct enforcement domains; this section governs migrations that span them. (From the [ORA-36](https://oraclous.atlassian.net/browse/ORA-36) Tests-Review escalation, 31 May 2026; solution-architect with security-architect co-sign; tech-lead accepted.)

**Rule — decompose; each store is written by its owning domain:**

* **auth-service half** (principal + credential rows) — hosted in `auth-service`, with rows produced through **auth-service-owned helpers** so the bcrypt/prefix/active-prefix-uniqueness convention (§1a) keeps a single home. A migration MAY raw-`INSERT` on the caller's connection to preserve caller-controlled transactions (the `org_backfill` convention), but the row _values_ — hash, prefix, inertness — MUST come from those helpers, never a re-implemented convention.
* **substrate half** (Neo4j ReBAC subject-node stamp) — performed by a **context-free, explicit-**`organisation_id` node-writer (a migration has no bound context). It lives in the **migrations namespace** (alongside `org_backfill`) and _composes_ the canonical `organisation_id`/label spelling single-sourced in `oraclous_substrate.access` (§1b); it is **not** exposed as a public writer on the request-path `access` seam beside `scoped_write_node`. A caller-chooses-org writer on a request path would be a T1 cross-org-write primitive — structurally barred, and proven by a test that the request-path seam admits no caller-supplied-org write.
* **orchestrator** — hosted on the _consuming_ side of the dependency edge (for agent-identity, `auth-service`), which may depend on the substrate package and call _down_ into its node-writer. The reverse — substrate depending on a service — is forbidden: substrate is the shared foundation and depends on nothing internal.

**Forbidden.** The substrate package MUST NOT host a migration that writes `auth-service`'s identity tables — neither by importing `oraclous_auth_service` (inverts the foundational dependency) nor by raw-SQL'ing the credential convention (a second credential-writing surface outside its §1a home; security-bearing for T2). _Avoiding the import is not avoiding the violation._

**Inert backfill credentials (T2).** A backfilled credential row exists so no principal lacks one, but it MUST authenticate against nothing — `validate_credential` returns `None` for every input (including the empty string and the bare credential prefix). Construct it as a bcrypt hash of a freshly-generated random secret that is **discarded** (never returned, never stored), _and_ a status that excludes it from `active_credentials_by_prefix` (defense in depth; leaves the active-prefix slot free for the first real credential an admin later issues). The backfill creates **no** `DELEGATED_TO` **edge and grants no role** — the principal exists with zero exercisable authority until an admin acts. Tests pin the behaviour, not a sentinel-hash spelling.

**Residual risk.** Org-less legacy agents default to `SEED_ORGANISATION_ID`; acceptable only if SEED is the platform/system organisation (never a customer tenant) and the assignment is auditable (T7). Verified at the implementation PR.

### 2. RLS backstop precondition A — the application DB role

The production substrate Postgres connection MUST authenticate as a role that is `NOSUPERUSER` and `NOBYPASSRLS`. A superuser or `BYPASSRLS` role silently bypasses RLS, voiding Threat Catalogue T1-M3 and ADR-006's defense-in-depth commitment. Because A1 applies `FORCE ROW LEVEL SECURITY` (so RLS binds even the table owner), the application role does _not_ additionally need to be a non-owner — but the `NOSUPERUSER/NOBYPASSRLS` attributes are mandatory. [ORA-17](https://oraclous.atlassian.net/browse/ORA-17) (A2) owns defining this role because it owns the connection.

### 3. RLS backstop precondition B — org-GUC lifetime

The organisation GUC (`app.current_organisation_id`) MUST be bound transaction-locally (`SET LOCAL` inside a transaction the seam owns), or the connection MUST be reset (`RESET` / `DISCARD`) before it returns to any pool. A bare session-level `SET` on a pooled connection is forbidden: a stale GUC would leak across organisations on connection reuse and silently defeat the fail-closed guarantee. A2/ORA-17 must carry an explicit pooled-connection-reuse test — a gate that uses a fresh connection per assertion cannot catch this failure mode.

## Consequences

### Positive

* T1-M1 (context-sourced scope) and T1-M3 (RLS backstop) become structurally enforced and verifiable through one named seam, not aspirational prose spread across stores.
* security-architect's credential-and-isolation review gains two concrete, checkable line items (role attributes; GUC lifetime) instead of "verify isolation."
* The cross-organisation traversal path has exactly one enforcement point (the seam → ReBAC client), consistent with ADR-004.

### Negative

* The seam is mandatory plumbing: every new store-touching path must route through `oraclous_substrate.access`, which is more ceremony than a direct driver call. This is the intended cost of a single verifiable boundary.
* The transaction-local GUC requirement constrains the connection-management strategy (pooling must reset or scope per transaction), removing the option of a cheap session-level `SET`.
* Neo4j has no RLS-equivalent backstop, so its write enforcement rests entirely on `scoped_write_node`; this raises the test bar (the write control must be proven, not assumed) — see the 29 May revision note.

## Alternatives considered

### A. Per-store ad-hoc scoping (no named seam)

Let each store apply organisation scope at its own call sites. Rejected: the ADR-006 "every path" invariant becomes unverifiable, and the org-context-vs-request-body discipline drifts per store.

### B. Rely on RLS alone (no application-layer seam)

Trust Postgres RLS as the sole enforcement. Rejected: RLS covers only Postgres (not Neo4j or Redis), and depends entirely on the role/GUC preconditions below — it is a backstop, not the primary control. ADR-006 already designates RLS as defense-in-depth.

### C. Session-level GUC on pooled connections

Set `app.current_organisation_id` once per checkout with a session `SET`. Rejected: a connection returned to the pool with a stale GUC leaks the previous organisation's scope to the next caller — a cross-organisation read that fail-closed cannot catch because the GUC is present (just wrong).

### D. Two modules — primitives and operations split (e.g. `query_scoping` + `access`)

Let A2's enforcement primitives live in one module and the scoped store operations in another. Rejected: two modules for the same concern reproduce the "two surfaces to audit" failure that the single-seam decision exists to prevent. Both tiers live in `oraclous_substrate.access`; the primitives are an internal layer, not a second public seam. (This reconciled the ORA-17 A2 test surface onto the gate's seam — see the 29 May revision note.)

## Implementation notes

* A1 ([ORA-16](https://oraclous.atlassian.net/browse/ORA-16), merged) already satisfies its half: `ENABLE` + `FORCE ROW LEVEL SECURITY` on every tenant table, policy `USING (organisation_id = current_setting('app.current_organisation_id', true)::uuid)`, and organisation-then-graph cache keys.
* A2 ([ORA-17](https://oraclous.atlassian.net/browse/ORA-17)) builds `oraclous_substrate.access` to the seam above and owns the production application DB role and the GUC lifetime.
* The ORA-20 gate stands up a `NOSUPERUSER/NOBYPASSRLS`, non-owner application role as the faithful test-time stand-in for the production role.
* Identity-store access in `auth-service` (agent/SA/user credential validation) is deliberately outside this seam — see §1a. The real Postgres-backed agent credential store ([ORA-30](https://oraclous.atlassian.net/browse/ORA-30) follow-up) is built to the auth-service's own DB conventions, not the `scoped_*` seam.
* The A3 neo4j-graphrag retriever/writer wrappers ([ORA-18](https://oraclous.atlassian.net/browse/ORA-18)) consume the seam's discipline per §1b; convergence onto the shared predicate helper + authenticated-context binding is tracked in [ORA-52](https://oraclous.atlassian.net/browse/ORA-52).
* A cross-domain backfill (auth-service identity store + substrate Neo4j) is decomposed per §1c: the auth-service half is hosted in `auth-service` through its own credential helpers; the substrate half is a migration-only, context-free explicit-org node-writer in the migrations namespace that composes §1b's canonical spelling; the orchestrator lives on the consuming side (auth-service → substrate, never the reverse). The agent-identity backfill ([ORA-36](https://oraclous.atlassian.net/browse/ORA-36)) is the first instance.

## References

* [ADR-013 — Fail-Closed Authority Placement at the Substrate ReBAC Seam](https://oraclous.atlassian.net/wiki/spaces/OP/pages/3702787) (refines §1's ReBAC slice — `AccessDecisionClient` fail-closed authority placement)
* [ADR-006 — Organisation as Outermost Tenancy Unit](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) (refined by this ADR)
* [ADR-004 — Federation via ReBAC Traversal](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083)
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T1 (data exfiltration), mitigations T1-M1, T1-M2, T1-M3
* [ORA-20](https://oraclous.atlassian.net/browse/ORA-20) — substrate organisation-boundary release gate (the driving artifact)
* [ORA-17](https://oraclous.atlassian.net/browse/ORA-17) (A2, implements the seam), [ORA-16](https://oraclous.atlassian.net/browse/ORA-16) (A1, RLS + schema, merged), [ORA-18](https://oraclous.atlassian.net/browse/ORA-18) (A3, consumes the seam), [ORA-52](https://oraclous.atlassian.net/browse/ORA-52) (A3 seam-consumption convergence follow-up)
* [ORA-36](https://oraclous.atlassian.net/browse/ORA-36) — agent-identity backfill (first §1c cross-domain backfill)

## Revision history

| Date | Change |
| --- | --- |
| 29 May 2026 | Initial draft (Proposed) from the ORA-20 Tests Review ratification. |
| 29 May 2026 | Accepted by tech-lead (Reza Jahankohan). Status → Accepted; downstream propagation (ADR-006 cross-ref, Architecture Revision History, agent skill pages, backend [CLAUDE.md](http://CLAUDE.md)) actioned. |
| 29 May 2026 | §Decision-1 amended to record the full reconciled seam surface — the enforcement primitives (`enforced_organisation_id`, `org_scoped_cypher`, `bind_organisation_guc`, `authorise_cross_org_traversal`/`CrossOrganisationDenied`) alongside the scoped store operations they compose into — plus alternative D. Reconciles the ORA-17 (A2) test surface, which had diverged onto a parallel `query_scoping` module, onto the one canonical seam. From the ORA-17 Tests Review. |
| 29 May 2026 | Scope boundary clarified (new §1a + implementation note): the seam governs tenant-scoped knowledge-substrate access only and does **not** govern pre-authentication identity/credential resolution in `auth-service`, which is the _producer_ of the organisation context the seam consumes. Credential validation by prefix is a legitimate pre-auth global lookup, outside the seam. From the [ORA-30](https://oraclous.atlassian.net/browse/ORA-30) escalation; tech-lead approved. |
| 31 May 2026 | [ADR-013](https://oraclous.atlassian.net/wiki/spaces/OP/pages/3702787) accepted (tech-lead, 31 May 2026): refines §1's ReBAC slice by placing fail-closed authority at the substrate seam (`AccessDecisionClient`) rather than the resolver. Resolver returns `bool | None` and may raise; seam translates ambiguity/error into deny + reason. No change to ADR-012's §1, §1a, §2, or §3 commitments — ADR-013 specifies where, inside §1, fail-closed translation happens for the ReBAC slice. References + status table updated with the back-reference. |
| 31 May 2026 | **§1b added — Consumption by neo4j-graphrag-based components (A3 / ORA-18).** The `scoped_*` operations are the substrate's own data-layer operations / the ORA-20 gate's call sites, not the execution surface of the A3 neo4j-graphrag retriever/writer wrappers (vector/hybrid retrieval + bulk graph ingestion have no `scoped_*` equivalent). A3 consumes the seam's org-scoping **discipline** plus a single-source-of-truth predicate helper, and proves isolation by test against real Neo4j; §1's "A3 consumes `scoped_traverse`/`scoped_fulltext_search`" and "`scoped_write_node` is the sole write control" wording is scoped to the substrate's own node read/write. Convergence onto the shared helper + authenticated-context binding tracked in [ORA-52](https://oraclous.atlassian.net/browse/ORA-52). From the [ORA-18](https://oraclous.atlassian.net/browse/ORA-18) Code Review architecture sign-off; solution-architect with security-architect co-sign; tech-lead directed. |
| 31 May 2026 | **§1c added — Cross-domain backfills: each store written by its owning domain.** A migration spanning the `auth-service` identity store and the substrate Neo4j store is decomposed so each store is written by its owner; the substrate provides a migration-only, context-free explicit-org node-writer (composing §1b's canonical spelling, **not** exposed on the request-path seam); the substrate package must not host writes to `auth-service` identity tables; inert backfill credentials + no delegation close T2. From the [ORA-36](https://oraclous.atlassian.net/browse/ORA-36) Tests-Review escalation; solution-architect with security-architect co-sign; accepted by tech-lead (Reza Jahankohan). |
