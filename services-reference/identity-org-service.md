---
title: "identity-org-service"
---

# identity-org-service — NOT BUILT (superseded)

**Status:** **Tombstone.** This service was *planned* by [ADR-017](../adr/adr-017-identity-org-service-split.md) but **never built as a separate service.** R3.5 consolidated the entire identity lifecycle — human users, email/password, OAuth (Google/GitHub/Notion), organisations, members, roles, invitations, **plus** agents and service accounts — into the single **[auth-service](auth-service.md)** (port 8005).

## What actually happened

ADR-017 planned to split identity into two services: a machine-only `auth-service` and a new human-facing `identity-org-service`. During the R3.5 build that split was reconsidered: the whole identity lifecycle is tightly coupled (an invitation creates a membership for a user in an org with a role), so it was kept in **one** deployable rather than scattered across a network boundary.

**ADR-017's core fix was still delivered:** organisation/member/role/invitation **left the knowledge-graph-service** — they no longer live in a domain service, which was the actual boundary fault the audit found. They now live in `auth-service`, the identity/tenancy authority. Only the two-service decomposition was dropped.

## Where everything lives now

Everything this page used to describe is in **[auth-service](auth-service.md)** — see that page for the real, R3.5-complete identity service (users, OAuth, orgs, members, invitations, agents, service accounts; port 8005; all eight §22 gates passed).

## Related

* [auth-service](auth-service.md) — the single as-built identity authority (where this scope landed)
* [ADR-017](../adr/adr-017-identity-org-service-split.md) — the superseded split decision (carries the as-built status note)
