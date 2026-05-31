---
confluence_id: "753752"
title: "ADR-001 — Four-Layer Architecture"
---

# ADR-001 — Four-Layer Architecture

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifact | [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) |

## Context

Oraclous v0 grew organically: services were added where they fit at the moment they were needed. The result was a system where data flowed in too many directions, where state could live in any service, where a request could traverse three services to perform what should have been a single substrate operation, and where security boundaries were enforced at whichever layer noticed the request rather than at a designed enforcement plane. The v0 system worked, but it could not be reasoned about: any new feature required tracing through every service to confirm it would not break invariants nobody had written down.

For the v1 restart, the question is not whether to have layers — every non-trivial system has them implicitly — but whether to commit to a small number of explicit layers with declared dependencies and declared responsibilities. A four-layer model is the smallest commitment that captures the platform's actual concerns: persistent state, capability discovery, harness execution, and external API. Fewer layers would force two concerns to share a single layer (which is what produced v0's reasoning problems); more layers would create boundaries that exist only on paper because there is no genuine concern separating them.

The decision matters at the founding stage because every later decision — where state lives, what a capability is, how harnesses access governance, which service owns audit — depends on knowing which layer owns what. Postponing this decision means every other ADR has to re-litigate it.

## Decision

The platform is organised into exactly four layers, with strict downward-only dependencies:

1. **Substrate** — the only stateful layer. Owns persistence, ReBAC primitives, KMS integration, audit storage, the OHM document store, the asset store, and the per-organisation tenancy anchor. Every storage and security primitive lives here. No other layer holds durable state.
2. **Capability registry** — the catalogue of capabilities (built-in, organisation-private, federated). Depends only on the substrate. Resolves capability references, enforces capability-descriptor integrity, gates federated capability access through ReBAC.
3. **Harness runtime** — loads OHM documents, resolves their references, executes harnesses against the model and capability providers. Depends on the capability registry and the substrate. Owns execution-time governance enforcement (budgets, audit emission, tool-call validation).
4. **Application gateway** — the external API surface. Translates authenticated requests into harness executions or substrate operations. Depends on all three layers below.

The dependency direction is strict: substrate code does not import from any higher layer; capability registry imports only from substrate; harness runtime imports from capability registry and substrate; application gateway imports from all three. Upward imports are an architectural error caught at code review and (later) by import linters.

## Alternatives considered

### A. Three-layer model (substrate, runtime, gateway)

Collapse the capability registry into either substrate or runtime. Simpler at first glance but loses the boundary that makes capability resolution a distinct concern with its own security model (federation, descriptor integrity, registry trust). Capability concerns would bleed into either the substrate (making it less focused on storage) or the runtime (making it harder to reason about as a pure execution engine). Rejected.

### B. Five-layer model (substrate, capability registry, harness runtime, application gateway, edge)

Add an "edge" layer for CDN, rate-limiting, TLS termination. Real concerns, but they are operational and infrastructural, not architectural — they belong in 05. Operations and the devops-implementer's scope, not in the platform's logical layer model. Pulling them into the architecture would muddle the distinction between "what the platform _is_" and "how the platform _runs_". Rejected.

### C. Hexagonal / ports-and-adapters around a single core

Treat the entire platform as a single core with adapter rings. This works well for systems with one dominant concern; it fits Oraclous poorly because the platform has multiple co-equal concerns (storage _and_ capability resolution _and_ execution _and_ external API) that each deserve their own enforcement plane. Hexagonal would force ad-hoc cross-cutting between adapters. Rejected.

### D. No commitment; let layers emerge

The v0 approach. Documented here for honesty: it is a valid choice for a prototype, and it is the choice we are explicitly stepping back from for v1. Rejected on the basis of v0 evidence.

## Consequences

### Positive

* Every architectural question has an unambiguous home: "which layer owns this?" has a single answer.
* Security enforcement points are predictable: substrate enforces tenancy and ReBAC; harness runtime enforces governance policy; gateway enforces authentication. The [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) can name enforcement points concretely.
* Layer boundaries become testable: an import linter (planned for Phase 1) can mechanically enforce the downward-only rule.
* [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) has a stable frame for review: every PR is locatable in a layer; cross-layer changes get explicit attention.

### Negative

* The strict boundary will sometimes feel like overhead. Some changes will need to thread through three layers to deliver a single user-visible effect; this is the cost of having reasoning-friendly boundaries.
* The four-layer commitment locks out architectural patterns that would benefit from circular dependencies (e.g. a capability registry that queries the harness runtime for live invocation statistics). These will require deliberate workarounds (event-driven pub-sub from the runtime to the registry, never direct calls).
* Layer boundaries must be defended against sprint pressure. A "quick fix" that adds an upward import is a long-term liability; [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) and [code-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/622800) are responsible for blocking them.

## Implementation notes

* Each layer maps to a separate top-level package in the `oraclous-backend` repository (planned for Phase 1 scaffolding).
* Layer dependencies are declared in each package's `pyproject.toml` dependency list; upward dependencies are rejected at install time, not just at runtime.
* An import linter (e.g. `import-linter`) is planned for Phase 1 CI to mechanically enforce the rule.
* 04. Services Reference will be organised by layer; each service page declares its layer in its identity table.

## References

* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — the architectural narrative for this decision
* [ADR-009](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393423) — metering at substrate, which depends on substrate being the only stateful layer
* [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) — organisation tenancy, which is anchored in the substrate per this layer model
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — threats name layer-specific enforcement points

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. Decision content unchanged from prior draft. |
