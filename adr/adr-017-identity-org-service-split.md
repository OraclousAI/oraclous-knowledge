---
confluence_id: TBD
title: "ADR-017 — Identity/Org Service Split"
---

# ADR-017 — Identity/Org Service Split

## Status

| Field | Value |
|---|---|
| Status | **Superseded by as-built (R3.5)** — original decision Accepted 2026-06-04 |
| Date | 2026-06-04 (superseded 2026-06-05) |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Superseded by | As-built R3.5 — see [auth-service](../services-reference/auth-service.md) |
| Driving artifact | ORAA-4 operating contract (rev15) — R3.5 graph-first per-service order, service #3; R3.5 auth-hollowness finding |

> **As-built outcome (2026-06-05).** This ADR's two-service split was **not executed**. In the R3.5 build the whole identity lifecycle — human users, email/password, OAuth, organisations, members, roles, invitations, **and** the machine principals (agents, service accounts) — was consolidated into the **single** [auth-service](../services-reference/auth-service.md), not a new `identity-org-service`. The reasoning is the ADR's own "Alternative C" applied one level up: users/orgs/members/roles/invitations form one tightly-coupled lifecycle, so they stay in one deployable rather than split across a network boundary. **The ADR's core fix held** — org/member/role/invitation **left the knowledge-graph-service** (the boundary fault the audit found is fixed); only the *separate-service* decomposition was dropped. There is no `identity-org-service`. A future split remains available if a concern genuinely diverges (an R6+ call). The Decision section below is retained as the historical record of the original choice.

## Context

The R3.5 hollowness audit found that the legacy build had **buried identity and organisation management inside the graph service**. Users, members, roles, and invitations were modelled and persisted as part of the knowledge-graph service's responsibilities, and the R2/R3 auth surface that should have owned them instead **dropped human/email/OAuth/org management entirely** — it shipped hollow. Identity ended up in the wrong place (the graph service) *and* underbuilt where it belonged (auth).

This is two faults at once. First, a **boundary fault**: organisation, member, role, and invitation are tenancy and identity concerns, not graph concerns. [ADR-006](adr-006-organisation-as-outermost-tenancy-unit.md) makes the organisation the platform's *outermost tenancy unit* — every storage operation, audit event, and ReBAC relation is anchored on `organisation_id`. A concept that anchors the entire substrate cannot be a subsidiary table of one domain service; the graph service is a *tenant* of the organisation boundary, not its owner. Burying org management in the graph service inverts that: it makes the tenancy anchor depend on a domain service that should depend on it.

Second, a **completeness fault**: the user-facing identity surface a real product needs — human accounts, email/password, OAuth sign-in (Google, GitHub, Notion), and the org/member/role/invitation lifecycle — simply did not exist as a coherent, runnable service. R3.5 rebuilds every service real and end-to-end ([ADR-016](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md)), and identity is service #3 in the graph-first order (after knowledge-graph-service and knowledge-retriever-service, before credential-broker-service). Rebuilding it real means first deciding **where it lives**.

## Decision

Identity and organisation management is **extracted out of the graph service into a dedicated identity/org service**, created new in R3.5 as service #3 in the per-service rebuild order.

### What the identity/org service owns

- **Users** — human accounts as first-class entities.
- **Authentication** — email/password, and OAuth sign-in via **Google, GitHub, and Notion**.
- **Organisations** — the tenancy-anchor entities of [ADR-006](adr-006-organisation-as-outermost-tenancy-unit.md). The organisation record and its lifecycle live here.
- **Members, roles, invitations** — the org-membership lifecycle: who belongs to an org, in what role, and the invitation flow that adds them.

### What moves, and from where

`orgs`, `members`, `roles`, and `invitations` **leave the graph service** (where the legacy build wrongly buried them) and become the identity/org service's domain. The knowledge-graph-service and knowledge-retriever-service no longer model or persist organisation membership; they *consume* organisation identity (the `organisation_id` tenancy anchor) the same way every other service does.

### How it is built

The service is built to the canonical service-internal architecture and the eight-gate Definition of Done of [ADR-016](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md): the `services/identity/src/oraclous_identity_service/` package shape, the three non-negotiable rules, the §21 lint gates, and the §22 per-service DoD (it is not done until it runs against real substrate and Reza signs off). Finer-grained access *within* an organisation continues to be expressed as ReBAC relations per [ADR-004](adr-004-federation-via-rebac-traversal.md) and [ADR-006](adr-006-organisation-as-outermost-tenancy-unit.md) — this ADR moves the *ownership of org/member/role/invitation records*, it does not change the tenancy model or the ReBAC traversal model.

## Alternatives considered

### A. Leave org/member/role/invitation in the graph service and just fill the gaps

The path of least change: keep the legacy placement and merely build out the missing auth surface around it. Rejected because it cements the boundary fault. The organisation is the *outermost tenancy unit* (ADR-006); making it a subsidiary of the graph domain forces every other service that needs organisation identity to reach *through* the graph service for it, and inverts the dependency direction (the tenancy anchor would depend on a domain service). It also leaves the graph service carrying a concern it has no reason to own.

### B. Fold identity into the credential-broker-service

Identity and credentials are adjacent, so co-locating them is tempting. Rejected: they are distinct concerns with distinct lifecycles. The credential broker manages *secrets a principal holds* (BYOM keys, connector credentials); the identity service manages *who the principal is and which org they belong to*. Conflating them produces a service with two unrelated reasons to change and a blast radius spanning both authentication and secret-handling. They are sequenced as separate R3.5 services (identity is #3, credential-broker is #4) precisely to keep them apart.

### C. A standalone auth service plus a separate org service (two services)

Split identity even finer: authentication in one service, organisation/membership in another. Rejected for R3.5 as premature decomposition. Users, orgs, members, roles, and invitations form one tightly-coupled lifecycle (an invitation creates a membership for a user in an org with a role); splitting it across two services would scatter that lifecycle across a network boundary for no current benefit and would violate the §23 "one service = one deliverable" discipline. One identity/org service owns the whole lifecycle; a future split remains available if a concern genuinely diverges.

## Consequences

### Positive

- **The tenancy anchor lives where ADR-006 says it should** — organisation is owned by a service whose job is identity and tenancy, not buried in a domain service. The dependency direction is restored: graph and retriever services *consume* `organisation_id`, they do not *own* the org record.
- **The graph service shrinks to its actual concern.** Removing org/member/role/invitation from it makes the knowledge-graph-service a smaller, more legible service focused on ingestion ([ADR-022](../adr/)).
- **A real, runnable identity surface exists** — human accounts, email/password, OAuth (Google/GitHub/Notion), and the full member/role/invitation lifecycle — closing the auth-hollowness gap the audit found.
- **Clear service boundaries for downstream R3.5 services.** The credential-broker (service #4) and capability-registry (service #5) consume a single, well-defined identity/org service rather than reaching into the graph service for membership data.

### Negative

- **A cross-service dependency replaces an in-process one.** Where the graph service once read membership from its own tables, services now consume organisation/membership identity across a service boundary. This is the correct boundary, but it is a network hop with the usual availability and latency implications; the identity/org service becomes a service others depend on.
- **A migration moves org/member/role/invitation data out of the graph service.** Until the gateway exists, services are reached directly by host IP:port (legacy parity), so the move and the cut-over must be sequenced carefully against the graph service's rebuild.
- **One more service to operate.** The identity/org service is a new deployable with its own substrate, lifecycle, and the eight-gate DoD to satisfy before service #4 (credential-broker) opens.
- **OAuth provider integrations (Google/GitHub/Notion) add external dependencies** to a security-critical path; each provider is a surface the security review must cover.

## See also

- [ADR-006 — Organisation as Outermost Tenancy Unit](adr-006-organisation-as-outermost-tenancy-unit.md) — why organisation ownership belongs in an identity/tenancy service, not a domain service
- [ADR-004 — Federation via ReBAC Traversal](adr-004-federation-via-rebac-traversal.md) — the model for finer-grained intra-org access this ADR leaves unchanged
- [ADR-016 — Canonical Service-Internal Architecture and Hardened Definition of Done](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md) — the §21 shape and §22 eight-gate DoD this service is built to
- [ADR-022 — Concern-Driven Agent Ingestion (recipe/primitive/unified-graph)](../adr/) — the ingestion spec for the knowledge-graph-service this ADR slims down
- [Release Process](../engineering/release-process.md) — the R3.5 graph-first per-service order placing identity/org as service #3
- ORAA-4 operating contract (rev15) — the canonical source; when this ADR and ORAA-4 diverge, ORAA-4 wins

## Revision history

| Date | Change |
|---|---|
| 2026-06-04 | Initial publication. Records the R3.5 extraction of users/auth/orgs/members/roles/invitations out of the graph service into a dedicated identity/org service (graph-first order, service #3). |
