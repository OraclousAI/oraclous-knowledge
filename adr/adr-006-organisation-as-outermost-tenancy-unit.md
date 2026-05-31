---
confluence_id: "393403"
title: "ADR-006 — Organisation as Outermost Tenancy Unit"
---

# ADR-006 — Organisation as Outermost Tenancy Unit

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Refined by | [ADR-012 — Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) |
| Driving artifact | [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900) |

## Context

Every multi-tenant platform has to pick a tenancy unit, and every choice has consequences that propagate everywhere. The unit determines which fields are required on every storage row, which boundaries the security model enforces, which billing surface aggregates costs, which audit scope is meaningful, and which entity owns ReBAC relations. Picking it late, or picking it implicitly, means the platform ends up enforcing different units in different layers — which is exactly what makes multi-tenant security bugs hard to avoid.

The plausible candidates are user, team, project, and organisation. User-as-tenancy works for personal-productivity tools but breaks down whenever multiple users share access to anything. Team-as-tenancy fits internal collaboration but does not match how enterprises actually buy software (they buy at the organisation level, not the team level). Project-as-tenancy is appealing for resource grouping but does not match how access decisions actually flow (a principal's access usually crosses projects within an organisation).

Organisation-as-tenancy is the largest reasonable unit. It matches how customers procure the platform, how data sovereignty obligations attach, how billing reconciles, how regulatory accountability is assigned, and how cross-tenant boundaries are best policed (a single boundary per organisation, not N boundaries per team or project). Within an organisation, finer-grained access is expressed through ReBAC relations — teams, projects, roles — without making any of those the platform's tenancy unit.

## Decision

The **organisation** is the outermost tenancy unit on Oraclous. Every storage operation, audit event, ReBAC relation, BYOM credential, OHM document, capability publication, and metering record is anchored on an `organisation_id`.

Concretely:

* Every substrate table that holds tenant-scoped data has an `organisation_id` column. There is no "global" tenant-scoped data.
* Every read parameterises by `organisation_id`, sourced from the authenticated principal context (never from request body). Defense-in-depth row-level security backs this in the storage layer.
* Every write carries `organisation_id`. Writes that lack it fail at the substrate boundary, not at the storage layer.
* Cross-organisation traversal goes through the ReBAC layer exclusively. No code path bypasses ReBAC by holding a direct database reference across organisations (see [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083)).
* Finer-grained units (teams, projects, roles) exist _within_ an organisation as ReBAC relations on objects, not as tenancy units. The platform does not partition data on team or project.

## Alternatives considered

### A. User as tenancy unit

Smallest possible unit. Forces every shared resource into ad-hoc sharing mechanisms; makes enterprise billing impractical (every user is a separate billing entity); makes data-sovereignty claims awkward (data belongs to a user, not the contracting party). Rejected.

### B. Team as tenancy unit

A common pattern in collaboration tools. Considered seriously. Rejected because teams within an organisation routinely share resources, and policing cross-team boundaries with full security enforcement (per-team encryption, per-team audit) is heavier than the value justifies. Teams are better expressed as ReBAC relations within an organisation.

### C. Project as tenancy unit

Matches resource-grouping mental models. Rejected because projects within an organisation routinely share principals, capabilities, and budgets — the cross-project boundary is permeable in ways the organisation boundary is not. Treating projects as a tenancy unit would force expensive cross-project enforcement for boundaries customers do not actually want.

### D. Organisation as outer tenancy with team-as-inner tenancy (two-level)

Anchor on organisation outermost; require team_id additionally on team-scoped data. Considered seriously because it expresses both the platform-level boundary and the customer-level boundary. Rejected because the two-level model requires every storage operation to track two IDs and risks confusion about which boundary the substrate enforces (the answer should be unambiguous: the outer one, always). Teams are better expressed as ReBAC relations than as a tenancy column.

## Consequences

### Positive

* Tenancy enforcement has one concrete invariant: every storage operation carries `organisation_id`. [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195)'s credential-and-isolation review skill has a single thing to check.
* [Threat T1 (data exfiltration)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) has a concrete mitigation surface: every read is `organisation_id`-parameterised, every write carries `organisation_id`, ReBAC mediates cross-organisation traversal.
* Billing reconciles cleanly at the organisation level. A customer's invoice is the sum of organisation activity, without team-level or project-level reconciliation costs.
* Data sovereignty obligations attach to organisations, matching how legal agreements are signed.
* Cloud-hosted operator separation ([ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792)) is enforceable at one boundary, not many.

### Negative

* Every storage call signature carries `organisation_id`. The verbosity is real and unavoidable; type-system and dependency-injection patterns reduce but do not eliminate it.
* Finer-grained units (team, project, role) are not free either; they live in ReBAC and require deliberate modelling. Customers expecting team-level data isolation as a built-in get a different model: their team isolation is policy-defined (ReBAC), not data-partition-defined.
* Cross-organisation features (federation, marketplace listings) require explicit work to be exposed, because the default boundary is strict. [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) handles federation; future ADRs will handle marketplace patterns as they are needed.

## Implementation notes

* Substrate schema convention: every tenant-scoped table has `organisation_id UUID NOT NULL` as part of (or alongside) the primary key. Row-level security policies parameterise on `organisation_id` as defense-in-depth.
* Repository layer convention: every read accepts an explicit organisation context object; reads that defaulted from a global session are forbidden at code-review.
* Audit events carry `organisation_id` as a top-level field, not buried in payload.
* BYOM credentials are scoped to `organisation_id`; cross-organisation credential reuse is not permitted (matches [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920)).
* Phase 1 includes a substrate-level test marker `organization_isolation` that exercises every storage path against a "principal in org A cannot read rows in org B" assertion.
* The concrete enforcement seam (`oraclous_substrate.access`) and the two preconditions that make the row-level-security backstop real in production — the `NOSUPERUSER/NOBYPASSRLS` application role and the transaction-local org-GUC lifetime — are specified in [ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396), which refines this ADR.

## References

* [Section 6 — Governance Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720900)
* [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) — substrate as the only stateful layer; tenancy anchor lives here
* [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) — cross-organisation traversal via ReBAC
* [ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) — refines this ADR: the substrate enforcement seam (`oraclous_substrate.access`) and the RLS backstop preconditions (application-role attributes; org-GUC lifetime)
* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — cloud-hosted operator separation, enforced at the organisation boundary
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — T1, T2 mitigations all anchor on organisation tenancy
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — policy sets reference `owner_organization` as a pseudo-subject

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
| 29 May 2026 | Refined by [ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) (substrate tenancy-enforcement seam and RLS backstop preconditions). No change to this ADR's decision; "Refined by" status row, an implementation note, and cross-references added. |
