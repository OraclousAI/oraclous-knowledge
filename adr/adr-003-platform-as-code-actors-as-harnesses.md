---
confluence_id: "884737"
title: "ADR-003 — Platform-as-Code, Actors-as-Harnesses"
---

# ADR-003 — Platform-as-Code, Actors-as-Harnesses

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifact | [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380) |

## Context

A recurring confusion in the agentic-AI space is whether an "agent" is a piece of code, a configuration of a model, a long-running process, or a collection of tools wrapped around a prompt. Different platforms answer this differently, and the answer determines what is shipped, deployed, audited, and updated. In v0 the platform tracked agents and workflows as separate first-class concepts, which created a duplication: a workflow that called an agent ran two governance evaluations, two audit streams, two budget surfaces.

The deeper question is what the unit of platform behaviour is. If the unit is code (a deployed binary or service), then changes require deploys, governance must be enforced inside service code, and the substrate is just a database. If the unit is a descriptor (a configuration of capabilities and prompts), then changes are configuration updates, governance is enforced by the platform around the descriptor, and the substrate becomes the source of truth.

The platform-as-code choice means committing to descriptor-led behaviour: harnesses are the actors, and the platform interprets them. This shapes everything from deployment (we deploy the runtime, not individual harnesses) to governance (the platform enforces policy _around_ the harness, not inside it) to portability (an OHM moves between deployments without code changes).

## Decision

The platform is "platform-as-code" in the sense that the _platform itself_ (the substrate, capability registry, harness runtime, application gateway) is code that is deployed and versioned through normal engineering practice. The _actors_ on the platform — the things that perform agentic behaviour — are not code. They are harnesses, described by OHM documents, interpreted by the harness runtime.

Concretely:

* The platform is a small number of long-lived services (per the four-layer model in [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752)).
* Actors are harnesses: OHM documents that bind capabilities, models, prompts, governance, and runtime metadata.
* The platform never embeds harness-specific logic. If a harness needs special behaviour, that behaviour is expressed by selecting capabilities and binding them, not by extending the platform.
* The single concept "harness" replaces v0's parallel concepts of "agent" and "workflow" (see [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772)).

## Alternatives considered

### A. Agents as deployed code (per-agent service)

Each agent is a deployed service: its own container, its own process, its own deploy lifecycle. Common in early agentic platforms. Rejected because governance, budget, and audit would have to be re-implemented inside every agent, and portability would mean container portability rather than descriptor portability — a much higher bar.

### B. Agents and workflows as two first-class concepts (v0 model)

Keep the v0 distinction: agents are leaf-level actors, workflows compose them. Rejected explicitly in [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772); the duplication has measurable cost and no compensating clarity. A composition of harnesses is itself expressible as a harness (one that uses other harnesses as capabilities).

### C. Agents as ephemeral function calls (no first-class persistence)

Treat agentic behaviour as transient function calls against the model, with no platform-level identity. Works for chatbot prototypes; rejected for Oraclous because the platform's value is precisely in durable, governable, auditable harnesses with identity that persists across invocations.

### D. Hybrid (some actors as code, some as descriptors)

Permit both shapes side by side. Rejected because the cost of supporting two shapes — two governance surfaces, two audit surfaces, two portability stories — is exactly the cost the single-shape commitment is meant to eliminate. If hybrid becomes necessary later, a future ADR can revisit; v1 commits to single-shape.

## Consequences

### Positive

* The platform has a small, stable runtime surface. Operations expertise consolidates around the four-layer services, not around N agent containers.
* Harness changes do not require deploys. A new harness or a revision is a configuration update that the substrate accepts atomically.
* Portability is real: an OHM that loads on this deployment loads on any Oraclous deployment with compatible capability registries and BYOM availability.
* Governance is enforced by the platform around the harness — the harness cannot opt out, bypass, or re-implement governance in its own code.
* The agent team can converge on a single mental model: "build a harness" never requires the question "should this be code or a descriptor?"

### Negative

* Some behaviour that would be a few lines of code becomes a capability authored separately. The "I'll just write a quick Python function" path is closed; the path is "write a capability, publish to the registry, reference it in the harness". This is heavier for one-offs.
* The capability registry must offer enough breadth that most harness needs are met by composition. Phase 1 includes a baseline set of core capabilities; future phases will expand it.
* Debugging a misbehaving harness means debugging a descriptor and a runtime, not stepping through a single piece of code. Observability infrastructure (traces, structured logs, audit) must do more work than in a code-actor world.

## Implementation notes

* The harness runtime is the platform-side interpreter; it is the one piece of code that "runs harnesses".
* Custom behaviour is expressed by publishing a capability to `org:<org-id>` rather than embedding code in a harness. Phase 1 ships the capability-publish flow.
* OHM's reference semantics (resolve-at-load-time, atomic, fail-closed) preserve the platform's control over the actor's bindings; the harness cannot reference something the platform has not authorised.
* Compositions (one harness using other harnesses as capabilities) are explicitly supported via the federated capability registry path, gated by ReBAC per [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083).

## References

* [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380)
* [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) — the four-layer model the platform code occupies
* [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) — OHM as the descriptor format for actors
* [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772) — workflow retirement; harness as replacement
* [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) — federation via ReBAC, enabling cross-organisation harness composition

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
