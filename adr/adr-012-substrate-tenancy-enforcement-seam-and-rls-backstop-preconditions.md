# ADR-012 — Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 29 May 2026 |
| Proposed by | solution-architect (with security-architect co-sign) |
| Approved by | tech-lead (Reza Jahankohan) |
| Refines | ADR-006 |
| Refined by | ADR-013 (refines §1's ReBAC slice) |
| Driving artifact | ORA-20 Tests Review |

## Decision

This ADR refines ADR-006 with three concrete commitments:

### 1. A single substrate tenancy-enforcement seam

All tenant-scoped substrate access goes through one module, `oraclous_substrate.access`. The module exposes:

- `enforced_organisation_id()` — raises when no context is bound (fail-closed)
- `org_scoped_cypher(query, *, alias=...)` — injects org filter as bound `$organisation_id` parameter
- `bind_organisation_guc(cursor)` — binds Postgres RLS GUC from context
- `authorise_cross_org_traversal(...)` + `CrossOrganisationDenied` — the ReBAC federation gate
- `scoped_pg_connection(dsn)`, `scoped_write_node(...)`, `scoped_traverse(...)`, `scoped_fulltext_search(...)`, `scoped_cache_get/set(...)`

### 2. RLS backstop precondition A — the application DB role

The production substrate Postgres connection MUST authenticate as a role that is `NOSUPERUSER` and `NOBYPASSRLS`.

### 3. RLS backstop precondition B — org-GUC lifetime

The organisation GUC (`app.current_organisation_id`) MUST be bound transaction-locally (`SET LOCAL`), or the connection MUST be reset before it returns to any pool.
