---
title: "Contract G2 — owner-org on the ReBAC AccessDecision (cross-org foreign-row read)"
owner: solution-architect
status: accepted
consumes: federated retrieval (KRS) — a granted foreign graph returns the OWNER org's rows
backend-issue: oraclous-backend (to be filed — implements ADR-036)
governs: ADR-036
---

# Contract G2 — owner-org on the ReBAC AccessDecision

**Goal.** Let a federated read of a *granted* foreign graph bind the **owner** organisation's id as the
in-Cypher `$organisation_id` for that one branch — so the granted graph returns the owner's rows, not
empty. The owner org is a single value that must travel, under proof, across three boundaries:
**KGS (grant time) → `packages/rebac` + `packages/substrate` (the AccessDecision) → KRS (the fan-out)**.
Because the shape crosses services/repos, it is recorded **once** here (CLAUDE.md §12.4), not defined
locally in KRS. Governed by [ADR-036](../adr/adr-036-cross-org-foreign-row-read-under-rebac-grant.md).

## The invariant (why this is safe)

`owner_organisation_id` is **never** client input. It is captured **server-side at grant time**, the one
moment the system holds both orgs under proof — `grant_service.grant_read` calls `assert_owned` under the
**owner's** bound org context, so `enforced_organisation_id()` there *is* the owner org. It is written as
**read-back metadata** on the grant edge (not part of the authorisation key) and only ever surfaces on an
`allowed=True` decision the caller genuinely holds. A caller cannot supply, poison, or probe it.

## The shape (producer → carrier → consumer)

### 1. KGS — `grant_service.grant_read` (producer)
After `assert_owned` succeeds (owner's bound context), capture `owner_organisation_id = enforced_organisation_id()`
— server-derived under owner proof, **never** from a request body — and pass it to `engine.grant_role`. Accept
no caller-supplied owner org.

### 2. `packages/rebac` — `ReBACEngine.grant_role` + the `HAS_ROLE` edge
`grant_role` gains an `owner_organisation_id: str` param. In `_GRANT_ROLE_QUERY` the MERGE **key stays
`{graph_id, organisation_id}`** (the **grantee** org) — UNCHANGED, so the grantee-scoped Phase-B check is
untouched — and `hr.owner_organisation_id = $owner_organisation_id` is added to **both** `ON CREATE SET` and
`ON MATCH SET`. The read-back query (`_PHASE_B_PERM_QUERY` or a sibling) returns `hr.owner_organisation_id`.

### 3. `packages/rebac` — `ReBACEngineResolver` (adapter) + `packages/substrate` — `AccessDecision`
- `AccessDecision` (substrate `rebac.py`) gains `owner_organisation_id: str | None = None` — **fail-closed
  default None**, populated ONLY when `allowed is True`.
- `ReBACEngineResolver.resolve` surfaces `hr.owner_organisation_id` from the engine read-back onto the
  decision. Unknown relation / non-graph resource / non-user subject still return `None` (fail-closed) and
  carry no owner org.

### 4. `packages/substrate` — `authorise_cross_org_traversal` (carrier)
Returns the `owner_organisation_id` (or the full `AccessDecision`) on a successful **allow**, instead of
`None`. On any non-grant it still raises `CrossOrganisationDenied`. Subject + org for the decision stay
sourced from the **bound context** (caller/grantee), never an argument.

### 5. KRS — `GraphInfo` + `_admit_granted` + the fan-out (consumer)
- `GraphInfo` (graph_registry_client) gains `owner_organisation_id: str | None = None` (frozen dataclass,
  defaulted — both existing construction sites keep compiling; home-org graphs from `accessible_graphs`
  leave it `None`).
- `_admit_granted` sets it from the value `authorise_cross_org_traversal` returns:
  `GraphInfo(id=gid, name="(shared graph)", owner_organisation_id=<resolved>)`. **If a graph is admitted
  (ReBAC allowed) but the owner org is `None`/unresolved → DROP it** (do not admit) — never read it under the
  caller's org, never pass `None` to Cypher.
- The fan-out binds **per-branch**: replace the single shared `_repo()` with a per-graph repository bound to
  `graph.owner_organisation_id or enforced_organisation_id()`. Home/default branches → caller's org
  (unchanged); admitted-granted branches → the owner org, for that `graph_id` only.

## Security (security-architect lens — all defended in the design review)

| Attack | Defence |
| --- | --- |
| Caller reads an ungranted graph | `_admit_granted` only admits after `authorise_cross_org_traversal` allows, resolving the **grantee-org-scoped** `HAS_ROLE` edge; fail-closed on absent/ambiguous/error. |
| Caller poisons the owner org to read a third org | owner org is **never** caller input — written server-side at grant time under `assert_owned`, read back only via the grantee-scoped decision. |
| Leak a third org's rows | the bound branch pins `organisation_id = owner_org` **AND** `graph_id = <granted gid>`; the owner org recorded is the org that actually owned the graph when it granted. |
| Widen the default (no `graph_ids`) scope | default branch graphs carry `owner_organisation_id = None` → every default branch binds the caller's org. Only explicitly-admitted granted gids get an override. |
| Concurrent fan-out branches bleed org | per-branch repository (not the shared one); each branch binds its own org. |
| Stale grant (no owner org) falls open | admitted-but-no-owner-org → **dropped**; returns empty (today's safe behaviour), never caller-org or `None`-to-Cypher. |
| Stale permission cache serves wrong owner org | cache the `(allowed, owner_organisation_id)` pair under the same org-namespaced key, or skip cache for the read-back. |
| Existence/owner oracle | one `FederatedAccessError` for unknown AND ungranted ids; owner org only returned on a genuine allow. |

## Done

A deployed-stack **deny → grant → read** e2e through the gateway: org A owns + ingests a graph; org B
federated-searches it → empty/denied; org A grants org B a read; org B federated-searches it → returns
**graph A's rows** (org A's data), labeled `source_graph_id`. Plus cross-org isolation tests: an ungranted
caller still gets empty; no third org's rows ever surface; the default-all scope is never widened.

## Implementation breakdown (one coherent feature — bundle into ≤1–2 PRs, never one-per-commit)

1. **`packages/rebac` + `packages/substrate`:** `grant_role` owner-org param + `HAS_ROLE` read-back property;
   `AccessDecision.owner_organisation_id`; resolver surfaces it; `authorise_cross_org_traversal` returns it.
2. **KGS:** `grant_read` captures + passes the server-derived owner org.
3. **KRS:** `GraphInfo.owner_organisation_id`; `_admit_granted` sets-or-drops; per-branch repo binding.
4. **e2e:** the deny→grant→read gateway proof + isolation tests (extends `test_rebac_cross_org_grant_gateway_e2e.py`).
