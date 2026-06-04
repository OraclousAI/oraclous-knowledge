---
confluence_id: "557322"
title: "R3 — Phase 3: Knowledge graph decomposition"
---

# R3 — Phase 3: Knowledge graph decomposition

> **Shipped HOLLOW — re-done under [R3.5](r3.5-make-every-service-real.md).** What merged for R3 was scaffolding, not real graph services: stub endpoints (`raise NotImplementedError`), a `GraphNodeService` **stub class defined inside a route file**, and no real ingestion or retrieval against the substrate. R3.5 rebuilds these real, end-to-end, in order — `knowledge-graph-service` (ingest, step 1) then `knowledge-retriever-service` (read, step 2) — each meeting ORAA-4 §22 (8 gates + Reza sign-off) before the next starts. The decomposition intent below stands; the implementation is redone.

| Release ID | R3 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 11-16 (the longest single release; six weeks reflecting the largest service decomposition) |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0, R0.5 (organisation scoping must exist before splitting the service), R2 (registry exists so retrievers can register as capabilities) |
| --- | --- |

## Goal

Split the sprawling `knowledge-graph-builder` into two cleanly scoped services: `knowledge-graph-service` (ingestion, schema, analytics, write-side) and `knowledge-retriever-service` (vector / hybrid / graph / temporal reads, federation traversal, modality-uniform NodeResult envelope). Build and retrieve are different responsibilities with different access patterns, scaling profiles, and audit needs; they share substrate but should be separate services. This is the most disruptive single phase; doing it cleanly here prevents the harness runtime in R4 from having to bridge a still-monolithic graph service.

## Scope

### In scope

* `knowledge-graph-service` created by renaming `knowledge-graph-builder`; retains ingestion (`pipeline_service.py`, `background_jobs.py`, ingestion endpoints), schema management, code parser, multi-tenant write components, analytics (community detection, centrality)
* `knowledge-retriever-service` created as a new deployment; receives retrieval modules (`retriever_service.py`, `retriever_factory.py`, retriever-specific multi-tenant components, full-text index service, query cache, retrieval-side federation per the LINKED_TO traversal work)
* Both services share the same Neo4j substrate with appropriately scoped roles (read-only for retriever, write for graph-service)
* Cross-service API contracts defined: retriever calls into graph-service for schema lookup only; graph-service does not call retriever
* The multi-tenant isolation test suite extended to run against both services independently and the organisation-boundary tests pass on each
* Customer-facing chat endpoints continue working: in this release the application gateway is not yet extracted, so chat APIs in the existing service routes through the retriever (gateway extraction happens in R6)
* Modality-uniform NodeResult envelope formalised: every retrieval shape (semantic, full-text, hybrid, graph traversal, temporal slice) returns the same envelope shape
* Retriever endpoints registered as capabilities in the registry (semantic_search, full_text_search, hybrid_search, graph_traverse, temporal_slice)

### Out of scope

* New modalities (image, audio, video, design, 3D) — additive per Section 3, deferred to R9 ongoing
* Harness runtime extraction (R4) — the runtime will call retriever endpoints but is not yet decomposed in this release
* Application Gateway extraction (R6) — chat endpoints stay where they are until then
* Cross-organisation federation gating beyond what R0.5 already enforces

## Deliverables

- [ ] **knowledge-graph-service deployed (renamed, ingest-only)** — verified by the renamed service running ingestion paths with green CI; retrieval modules removed; importers point to the retriever service for read operations
- [ ] **knowledge-retriever-service deployed as new service** — verified by a new deployment unit running the retrieval modules independently; its own observability surface; its own scaling profile
- [ ] **Shared substrate with role separation** — verified by retriever service connecting to Neo4j with a role that has read-only access; graph-service connects with a write-capable role; static analysis pass confirms retriever has no write paths
- [ ] **Cross-service API contracts** — verified by documented contracts for the small number of cross-service calls; integration tests cover the boundary; circuit breakers configured for graceful degradation
- [ ] **Isolation tests run against both services** — verified by the multi-tenant isolation test suite executing against each service independently and the organisation-boundary tests passing on both; cross-service tests confirm no leakage at the boundary
- [ ] **Customer chat endpoints continue working** — verified by regression test pass on existing chat APIs; latency parity within 5 percent of pre-R3 baseline; no breaking changes for current customer integrations
- [ ] **NodeResult envelope formalised** — verified by every retrieval endpoint returning the same envelope shape; modality-specific fields live inside the envelope, not alongside it; OHM-shaped per the spec
- [ ] **Retriever endpoints registered as capabilities** — verified by semantic_search, full_text_search, hybrid_search, graph_traverse, and temporal_slice each appearing in the capability registry as `kind: tool` with appropriate descriptors; harnesses can be allocated these capabilities (used in R4)

## Architecture references

* [Section 8 — Phase 3](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) — the phase narrative this release operationalises
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Substrate ownership; multi-modal substrate commitments; retriever as the layer where modality-appropriate retrieval converges
* [Section 2 — Conceptual Model](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393380) — knowledge graphs as workspace artifacts
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — Flow 4 (Traversal / federation) lives in the retriever

## ADRs implemented

* No new ADRs — R3 is a service-decomposition step that the existing ADR set (especially [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) for the four-layer split and [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) for federation) already covers at the architectural level. R3 is the implementation step.

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T1 — Data exfiltration | T1-M2 (ReBAC enforced on every retrieval; retriever service cannot read across organisation or workspace boundaries that the substrate does not permit) | Retriever-side enforcement complete; full T1 coverage continues from R0.5 |
| T6 — Operator-separation breach | T6-M2 (read-side has its own audit surface separable from the write side; cloud-mode operators with read-only roles cannot escalate to writes) | Partial — full T6 coverage continues to require R-Compliance |

## Governance impact

R3 makes the substrate's read and write surfaces independently governable. Before this release, a single role grants both read and write at the service boundary; after R3, the retriever service operates with a read-only Neo4j role and cannot mutate state regardless of code path. This is the most concrete operator-separation control the platform exposes — it is a structural guarantee enforced by the database, not just policy.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Decomposition introduces latency on chat paths that previously executed in-process | Medium | Cross-service calls are localised (same Kubernetes namespace, same cluster). Latency budget per request is defined and tested. If a hot path turns out to be cross-service-bound, in-memory result cache is added to the retriever side. | backend-implementer + devops-implementer |
| Shared Neo4j becomes a bottleneck because both services now hit it | Medium | Read role uses Neo4j's read replica when available; write role uses primary. Query patterns audited for index coverage. Scaling profile for each service tuned independently. | devops-implementer |
| A retrieval code path is missed during the extraction, leaving a hot path still in the old service | High | Static analysis identifies all retrieval-shaped functions. Each is moved individually with a deprecation shim left in the old location until R3 closes; the shim logs every call so any missed path surfaces in observability. | backend-implementer + code-reviewer |
| Cross-service contracts drift from documented shapes | Medium | Contracts are defined as OpenAPI specs; both services validate requests against the spec at the boundary; contract tests run in CI. | solution-architect + test-author |
| The chat regression risks customer-visible breakage | Medium | Regression test suite for chat APIs is the release gate. Canary deployment for chat to a fraction of traffic before full rollout. Rollback path documented. | qa-engineer + devops-implementer |
| The retriever service's read-only role is broken by a missed migration that still requires a write | Medium | Migration script audited for any write-from-retriever pattern. If any is found, the migration is rewritten before R3 ships. | security-architect |

## Dependencies

**Upstream:** R0 (architecture), R0.5 (organisation scoping must already be on all data before the service split, otherwise the split would have to repeat the tenancy work), R2 (registry exists so the retriever endpoints can register as capabilities).

**Downstream:** R4 (harness runtime calls retriever endpoints for graph reads instead of direct Neo4j queries from the toolkit). R5 (execution engine respects the read/write boundary for durable jobs). R6 (gateway extracts chat APIs and routes them through the retriever directly rather than through the proxy added in this release).

## Sprint references

Jira epics to be created during Group E. Each deliverable above maps to one or more epics; this release in particular benefits from explicit epic-level decomposition because of its size.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R3 as the knowledge graph decomposition release; matches Section 8 Phase 3 |
