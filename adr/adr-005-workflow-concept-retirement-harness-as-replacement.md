---
confluence_id: "753772"
title: "ADR-005 — Workflow Concept Retirement; Harness as Replacement"
---

# ADR-005 — Workflow Concept Retirement; Harness as Replacement

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR; supersedes v0's two-concept model in implementation, not as a formal ADR) |
| Superseded by | None |
| Driving artifact | [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380) |

## Context

The v0 system carried two parallel first-class concepts: _agents_ (leaf-level actors that took an input, called a model, possibly invoked tools, and returned output) and _workflows_ (orchestrations of agents, with explicit edges, conditional branches, and shared state). The split followed a familiar pattern from process-orchestration tools (Temporal, Airflow), but it created persistent costs.

The split forced two governance evaluations on every composed execution: the workflow's policy bindings and the agent's policy bindings, with no canonical answer to which wins when they disagree. It forced two audit streams that observers had to correlate to reconstruct an execution. It forced two budget surfaces that frequently disagreed on what counted (does the workflow's `max_tokens` include or exclude the agent's invocations?). It forced two failure-mode catalogues (workflow-level errors and agent-level errors, frequently overlapping).

The split also failed at composition. A workflow that called other workflows was supported only awkwardly, with the outer workflow's identity sometimes dominating governance and sometimes not, depending on which service held the call. Composing across organisations was effectively impossible because cross-org workflows had no clean governance story.

The deeper observation is that the workflow-vs-agent distinction is a distinction in the orchestration layer, not in the platform model. From the platform's point of view, both are the same kind of thing: a binding of capabilities, models, prompts, governance, and runtime metadata that can be executed and audited as a unit. The orchestration concern (run X, then Y based on output of X) lives _inside_ the harness as a capability composition, not _above_ the harness as a separate concept.

## Decision

The platform has one first-class actor concept: the **harness**. The v0 "workflow" concept is retired. Behaviour that the v0 model called a workflow is expressed in v1 as a harness whose entrypoint capability orchestrates other capabilities — including, when needed, other harnesses referenced through the federated or organisation-private registries.

Concretely:

* Every executable thing on the platform is a harness, described by an OHM document.
* Composition is expressed by a harness referencing other capabilities (including capabilities that themselves wrap other harnesses), not by a separate workflow concept.
* Governance, audit, and budget apply at the harness level. A composed execution has one governance evaluation, one audit stream, one budget surface — the harness's. Composed harnesses that invoke other harnesses do so through the capability registry, which preserves the substrate's authoritative view of each harness's identity and policy bindings.
* There is no workflow service, workflow database, or workflow type in the substrate. Any v0 code or data carrying the workflow concept is migrated to the harness model during Phase 1 (or retired if no longer relevant).

## Alternatives considered

### A. Keep both concepts; clarify their interaction

The conservative path. Define which governance, audit, and budget surface wins when both apply; document the rules; train the agent team to apply them. Considered seriously because retirement is destructive. Rejected because the cost of supporting two concepts is structural and recurring (every new feature has to be defined for both); the cost of retirement is bounded and one-time.

### B. Retire agents instead of workflows

Keep workflow as the first-class concept; treat individual model calls as steps inside a workflow. This is closer to the Temporal/Airflow model. Rejected because the unit of governance and identity on Oraclous is the actor, not the orchestration. Treating every leaf-level capability invocation as a sub-workflow would force governance and audit at a granularity that does not match the platform's actual needs.

### C. Workflows as a capability subtype

Keep workflows as an internal subtype of capability, distinct from leaf capabilities. Considered because it preserves the workflow vocabulary while reducing it to a special case. Rejected because the distinction has no architectural consequence — from the platform's point of view, a "workflow capability" and a "leaf capability" are governed, audited, and budgeted identically. The subtype would be vocabulary without behaviour, which is exactly the kind of distinction this ADR is retiring.

### D. Externalise orchestration (delegate to Temporal, Airflow, etc.)

Have the platform provide harnesses; let customers wire them together with their own orchestration tools. Real option for some use cases. Rejected as the platform's _only_ story because it pushes the governance question outside the platform's reach — the platform cannot enforce policy across orchestrations it does not see. Externalisation is fine as an option (a harness can be invoked from outside) but is not a replacement for first-class composition inside the platform.

## Consequences

### Positive

* One actor concept means one governance evaluation, one audit stream, one budget surface, one failure-mode catalogue. The cognitive load on every other agent and document drops.
* The OHM specification ([OHM v1.0](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501)) describes a single document type. No parallel workflow-manifest spec.
* Composition is uniform and federated-friendly: a harness can reference capabilities from its own org, from the core registry, or from federated orgs, with the same load-time semantics for each.
* Migration from v0 has a clear target. There is no ambiguity about whether a v0 workflow becomes a harness or stays a workflow — everything becomes a harness.

### Negative

* Some patterns that were natural in the v0 workflow model become slightly indirect in the harness model. A long-running, branchy orchestration is now a harness whose entrypoint capability is an orchestrator capability that calls other capabilities; the orchestration logic lives in the capability, not in a workflow-graph editor.
* Customers familiar with workflow-graph tooling will not find it on Oraclous v1. The platform's position is that the value of the workflow-graph tooling is largely in the orchestration capabilities, not in the workflow concept itself; if a customer needs graph-style authoring, they can build a UI that emits OHM documents wrapping an orchestrator capability.
* The migration of v0 data (workflows in v0's storage) requires explicit work. Phase 1 includes a migration tool that converts v0 workflows into harnesses; some v0 workflows will not migrate cleanly and will need rework or retirement.

## Implementation notes

* The substrate has no workflow table, type, or service. Any v0 schema migration removes them.
* Composition is implemented as a capability composition: an orchestrator capability invokes other capabilities; the harness binds the orchestrator as its entrypoint.
* Orchestrator capabilities are themselves capabilities like any other — published to a registry, versioned, ReBAC-gated. The platform ships a small set of baseline orchestrator capabilities in `core` (sequential, parallel, conditional).
* Phase 1 v0 migration tool converts v0 workflows into OHM documents whose entrypoint is a generated orchestrator capability matching the v0 workflow shape. Customers can then refactor toward simpler or alternative orchestrators.

## References

* [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380)
* [ADR-003](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884737) — platform-as-code, actors-as-harnesses (the framing this ADR specialises)
* [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) — OHM as the single descriptor format
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501)
* [Section 8 — Consolidation and Migration Plan](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) — v0 migration sequencing

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Initial publication in uniform ADR template. |
