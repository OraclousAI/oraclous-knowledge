---
confluence_id: "622923"
title: "R4 — Phase 4: Harness runtime extraction"
---

# R4 — Phase 4: Harness runtime extraction

> **SUPERSEDED by [R3.5 — Make every service real](r3.5-make-every-service-real.md) (2026-06-04).** This phase is discarded as a standalone release; any still-needed surface folds into the R3.5 per-service sequence. R2/R3 shipped hollow and are being rebuilt real, per service, before any post-gateway work resumes. Content below is retained for reference only.

| Release ID | R4 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 17-20 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0, R0.5, R1 (agent identity), R2 (capability registry), R3 (knowledge retriever exists) |
| --- | --- |

## Goal

Lift the `AgentExecutor` and the production-grade agent runtime that today lives buried inside `knowledge-graph-builder` into its own service: `harness-runtime-service`. Generalise the executor past single-graph use so that it can host the default compiler, consciousness agents, customer harnesses, and every other harness the platform runs in subsequent releases. This is the central nervous system of the new platform — until it exists in target shape, harnesses cannot be defined or run.

## Scope

### In scope

* `harness-runtime-service` deployed as its own service with its own deployment unit, scaling profile, and observability surface
* The `AgentExecutor`, agent toolkit, LLM client factory, LLM config service, and provenance collector all migrated from `knowledge-graph-builder` to the new runtime service
* Agent CRUD APIs moved: the `:Agent` nodes themselves remain in the graph substrate, but the service that creates, reads, updates, and deletes them lives with the runtime
* The runtime calls into the Capability Registry (R2) for capability resolution instead of the agent toolkit's in-memory schema registry
* The runtime calls into the Knowledge Retriever (R3) for graph reads instead of direct Neo4j queries from the toolkit
* Multi-actor coordination primitives at v1 scope: agent-to-agent hand-off via task board state (HITL and round-tables come in R5)
* Per-invocation ReBAC recheck wired in: every capability invocation calls the Substrate's access decision API before dispatching, never trusts a cached decision (closes the runtime side of T2-M1)
* The chat engine's synthetic-agent pattern moves with the runtime; chat APIs continue working through the new service backing them
* Provenance writes are routed through a single layer — the runtime now owns in-flight provenance collection; persistence flows to the Substrate as before

### Out of scope

* Execution engine extraction (R5) — durable jobs, schedules, checkpoints stay where they are until R5
* HITL primitive (R5)
* Round-table primitive (R5)
* Cross-workspace federation traversal in the runtime (R5)
* Application gateway extraction (R6) — chat endpoints continue to live with their pre-R4 routing
* Compiler harness (R7) — the runtime must exist first so the compiler has somewhere to run

## Deliverables

- [ ] **harness-runtime-service deployed** — verified by the new service running with its own deployment unit, port allocation, and observability; green CI; the AgentExecutor in `knowledge-graph-builder` is gone (or a deprecation shim only)
- [ ] **Agent runtime modules migrated** — verified by the AgentExecutor, agent toolkit, LLM client factory, LLM config service, and provenance collector all living in `harness-runtime-service`; their tests moved with them; their behaviour preserved
- [ ] **Agent CRUD moved to runtime** — verified by the agent lifecycle service (create, read, update, delete) living in the runtime; `:Agent` nodes still persist in the graph substrate; existing customer-facing agent management APIs preserve their contracts
- [ ] **Capability resolution routes through R2 registry** — verified by every capability lookup in the runtime calling the Capability Registry service; the agent toolkit's in-memory schema registry is gone; no duplicate descriptor storage
- [ ] **Graph reads route through R3 retriever** — verified by every read of substrate data from the runtime going through the knowledge-retriever-service; no direct Neo4j queries from the toolkit; the runtime cannot mutate the graph directly
- [ ] **Agent-to-agent handoff working** — verified by an integration test that runs a two-agent harness where agent A hands off to agent B via task board state; provenance captures both turns; the orchestration agent picks B correctly from the harness manifest's prose
- [ ] **Per-invocation ReBAC recheck wired** — verified by every capability dispatch from the runtime calling the Substrate's access decision API; an integration test that revokes an agent's scope mid-execution proves the next dispatch fails fast
- [ ] **Chat continues working** — verified by chat regression tests passing; chat APIs backed by the new runtime via the synthetic-agent pattern; no breaking changes for current customer integrations
- [ ] **Single provenance write path** — verified by all provenance entries from runtime operations flowing through the runtime's collector and persisting to the Substrate; static analysis confirms no direct provenance writes to the database from anywhere else

## Architecture references

* [Section 8 — Phase 4](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) — the phase narrative this release operationalises
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Layer 3 (Harness Runtime + Execution Engine) ownership, exposed APIs, the two operational modes
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — Flow 2 (Execute) is the flow this runtime implements
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — the harness manifest format the runtime loads
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — policy envelope enforcement is a runtime concern

## ADRs implemented

* [ADR-003](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884737) — Platform-as-Code, Actors-as-Harnesses (the runtime is the platform-code half; harnesses run on top)
* [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772) — Workflow Concept Retirement; Harness as Replacement (the runtime is what makes the harness model executable in production)

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T2 — Privilege escalation | T2-M1 (per-invocation ReBAC recheck at the runtime side, completing the wiring from R1) | Full T2-M1 + T2-M2 + T2-M3 coverage at this point |
| T3 — Prompt injection / capability misuse | T3-M1 (runtime enforces that an agent's declared capability allocation cannot be expanded by prompt content; the orchestration prose is interpreted but routing happens only to actors and capabilities in the manifest), T3-M2 enforcement (content-hash mismatch causes the runtime to reject a capability) | Full T3 baseline; the indirect prompt injection sanitization extensions land in R8 |
| T7 — Audit-log gap | T7-M1 (single provenance write path; every capability dispatch produces a provenance record; nothing in the runtime can bypass it) | Full T7 baseline; cross-workspace traversal audit reports land in R8 |

## Governance impact

R4 makes the policy envelope enforceable at runtime. Before this release, policy sets exist in the Governance Taxonomy and bind to `owner_organization` from R0.5, but no runtime enforces them because no general-purpose runtime exists. After R4, every capability invocation passes through the runtime's policy envelope — budget caps consume from the manifest's declared limits, output redaction patterns run on every dispatched result, scope limits gate every cross-workspace read. The Governance Taxonomy becomes operational here.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| The lift introduces latency on chat that previously executed in-process inside `knowledge-graph-builder` | High | Cross-service calls localised to same cluster. Latency budget defined and tested. If chat regresses past the budget, in-memory caching of recently-resolved capability descriptors and agent identities is added on the runtime side. | backend-implementer + devops-implementer |
| An agent toolkit code path is missed during the migration | High | Static analysis identifies all toolkit consumers. Each is migrated individually with a deprecation shim left in the old location until R4 closes; the shim logs every call so missed paths surface in observability. | backend-implementer + code-reviewer |
| Per-invocation ReBAC rechecks add unacceptable latency to high-frequency tool dispatch | Medium | The Substrate's access decision API is designed for high frequency. Short-lived decision caches (seconds) at the runtime are acceptable per T2-M2; the substrate's revocation event stream invalidates cached decisions on revocation. | security-architect |
| Provenance write path becomes a bottleneck under high concurrency | Medium | Provenance writes are async-batched with a backpressure-safe queue; if the persistence pipeline fails, the operation still completes but the provenance entry is logged for replay (same pattern as R0.5 metering). | backend-implementer |
| The chat regression risks customer-visible breakage | Medium | Regression test suite for chat APIs is the release gate. Canary deployment to a fraction of traffic before full rollout. Rollback path documented. | qa-engineer + devops-implementer |
| The orchestration agent's prose-interpretation behaviour differs subtly from the pre-R4 AgentExecutor | Medium | Behavioural regression tests cover the orchestration prose patterns from existing customer harnesses; any deviation triggers a review with solution-architect before R4 closes. | test-author + solution-architect |

## Dependencies

**Upstream:** R0 (architecture), R0.5 (organisation scoping), R1 (agent identity, delegated tokens), R2 (capability registry for resolution), R3 (knowledge retriever for substrate reads).

**Downstream:** R5 (execution engine sits underneath the runtime for durable execution; HITL, round-tables, schedules, federation traversal land in R5 because they require the runtime to exist first). R6 (application gateway calls the runtime for harness execution). R7 (compiler harness is the first production harness running on this runtime).

## Sprint references

Jira epics to be created during Group E. Each deliverable above maps to one or more epics.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R4 as the harness runtime extraction release; matches Section 8 Phase 4 |
