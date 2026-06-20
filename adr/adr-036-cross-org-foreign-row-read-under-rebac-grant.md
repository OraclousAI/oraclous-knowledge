# ADR-036 — Cross-Org Foreign-Row Read under a Fail-Closed ReBAC Read Grant

## Status

| | |
| --- | --- |
| Status | Proposed |
| Date | 2026-06-20 |
| Deciders | solution-architect (drafted), security-architect (adversarial review), Reza (directed: "ReBAC foreign-row read — a granted foreign graph returns the owner's rows", and chose "ADR + Contract first, then build") |
| Driving epic | E7-SEC ReBAC · issue [#446](https://github.com/OraclousAI/oraclous-backend/issues/446) (the gate, merged #459) |
| Builds on | [ADR-004](adr-004-federation-via-rebac-traversal.md) (federation via ReBAC) · [ADR-026](adr-026-federated-cross-graph-query.md) (federated query as aggregator) · [ADR-030](adr-030-realize-postgres-rls-backstop.md) (RLS backstop) · #446/#459 (ReBAC enforcement — the admission gate) |
| Amends | **ADR-026 Decision 1** (the "no new access" floor) |
| Extends | **ADR-004** — applies its "federation is a pattern of ReBAC relations" principle to graph foreign-ROW reads (a new ReBAC-grant pattern, not a contradiction) |
| Contract | [Contract G2 — owner-org on AccessDecision](../flows/contract-g2-owner-org-on-access-decision.md) |

## Context

ADR-026 built federated cross-graph query as a strict **aggregator over already-accessible graphs** — Decision 1: *"Federation grants NO new access."* That decision deliberately **deferred** cross-org sharing: its parenthetical says *"when ReBAC enforcement lands (R7-SEC+), federation inherits it,"* and Alternative 3 reserves *"cross-org/sharing semantics … to the R7-SEC+ ReBAC work."* This ADR is that R7-SEC+ work — it does not contradict ADR-026 so much as **realize the exception ADR-026 reserved**.

#446 (merged as #459) landed the **gate**: the federated retriever's `resolve_scope` now admits a foreign graph (one in another organisation) into the fan-out scope when the caller holds a fail-closed ReBAC `read` grant (`authorise_cross_org_traversal`). But the **row read still binds the caller's home org** — `RetrievalRepository` is constructed once per fan-out with `enforced_organisation_id()` (the caller's org) and shared across every branch — so an admitted foreign graph's Cypher filters `…organisation_id = <caller org>` while the graph's rows carry the **owner's** org, matching **zero rows**. The admitted graph appears in scope but returns empty. The deferred slice is: make a granted foreign graph return the **owner org's rows**, safely.

Where the rows live matters: KRS graph data is **Neo4j Community (no RLS)** — tenant isolation on this read path is *entirely* the bound `$organisation_id` Cypher parameter, with `graph_id` pinning the slice. ADR-030's Postgres RLS backstop is **not** on this path. So the change is not an RLS change; it is a change to which org value is bound, per graph, in Cypher.

## Decision

1. **A fail-closed, owner-issued ReBAC `read` grant authorises reading the granted graph's OWNER-org rows in federated retrieval — and ONLY that graph's rows, ONLY for the granted caller.** This **amends ADR-026 Decision 1**: federation may now grant new access, but *exclusively* through an explicit, owner-issued ReBAC grant — the controlled exception ADR-026 §Alt-3 reserved. The default behaviour (no grant) is unchanged: no new access.

2. **The owner org is recorded SERVER-SIDE at grant time, never from client input.** `grant_service.grant_read` runs `assert_owned` under the **owner's** bound org context; at that moment the owner org = `enforced_organisation_id()`. That value is persisted as a **non-key property** (`owner_organisation_id`) on the `HAS_ROLE` edge. The edge stays **keyed by the grantee org**, so the grantee-scoped Phase-B check is byte-for-byte unchanged; the owner org is read-back metadata only. A caller can never supply or influence it.

3. **The owner org travels back through the decision, per-graph.** The ReBAC resolver surfaces `hr.owner_organisation_id`; `AccessDecision` carries `owner_organisation_id` (populated only on an `allowed=True`); `authorise_cross_org_traversal` returns it on a successful allow (still raising `CrossOrganisationDenied` on any non-grant). KRS's `_admit_granted` sets it on the admitted `GraphInfo`, and the fan-out binds it **per-branch** — each admitted-granted branch gets its own repository bound to that graph's owner org, never the shared caller-org repo. See Contract G2 for the exact shape.

4. **Fail-closed everywhere.** A graph admitted by ReBAC but with **no** recorded owner org (e.g. a pre-ADR-036 grant) is **DROPPED** — not read under the caller's org, never `None` into Cypher; it returns empty exactly as today until re-granted. The **default** (no `graph_ids`) scope is *never* overridden (those `GraphInfo` carry `owner_organisation_id = None` → caller's org). Absent/ambiguous/store-error decisions deny, unchanged.

5. **No oracle, no widening.** `resolve_scope` still raises one `FederatedAccessError` for unknown AND ungranted ids (no existence/owner oracle). The per-branch owner-org binding is gated on `graph_id` AND the owner org together, so a granted gid can only ever read that one graph's owner-org rows — never a third org, never another graph.

## Alternatives considered

* **Keep deferring (status quo).** Rejected — Reza directed the read; the gate without the read is a half-feature (admitted graphs return empty).
* **Resolve the owner org in KRS from the request or a KRS-local lookup.** Rejected — owner-org-from-caller is a **tenant-spoofing primitive** (a caller reads any org by naming its graph + asserting its org). The owner org must come from the one moment the system holds both orgs under proof: grant time.
* **A blanket cross-org read for any admitted graph.** Rejected — must be per-graph + per-grant; the shared-repo design would bleed one owner org across all fan-out branches.
* **Carry the owner org on the grant edge KEY (re-key HAS_ROLE by owner org).** Rejected — would change the grantee-scoped Phase-B check; owner org is read-back metadata, not part of the authorisation key.

## Consequences

* **Schema:** the `HAS_ROLE` edge gains a non-key `owner_organisation_id` property; `AccessDecision`, the resolver, and `GraphInfo` each gain an optional `owner_organisation_id`. (Contract G2 records the shape once.)
* **Migration:** grants written before ADR-036 have no `owner_organisation_id` → admitted-but-dropped (empty, safe) until re-issued. No destructive migration; old grants simply don't yet confer row visibility.
* **Mandatory tests:** a deployed-stack **deny → grant → read** e2e through the gateway (org A grants org B; org B federated-searches graph A and now gets graph A's **rows**, not empty), plus cross-org isolation tests proving an ungranted caller still gets empty and no third org's rows ever surface.
* **RLS untouched:** this path is Neo4j (no RLS); the in-Cypher org predicate remains the wall, now bound to the owner org for the one granted branch.
* **Security:** the design was adversarially reviewed — caller-forges-admission, owner-org spoofing, third-org leak, default-scope widening, concurrent-branch bleed, stale-grant fall-open, cache poisoning, and existence oracle were each checked and defended (see Contract G2 §Security).

## See also

* [Contract G2](../flows/contract-g2-owner-org-on-access-decision.md) (the cross-service shape) · ADR-026 (amended — Decision 1) · ADR-004 (extended — ReBAC-federation principle) · ADR-030 (RLS — not on this path)
* #446/#459 (the admission gate this completes) · the rebac-foreign-row-read design workflow (2026-06-20)
