---
source_page_id: 688482|557322|622923|164225|196877|164260|66060|688523|753930
title: "R2 through R8 and R-Compliance and Build State"
---
# R2 — Phase 2: Capability registry consolidation

> **SUPERSEDED by [R3.5 — Make every service real](r3.5-make-every-service-real.md) (2026-06-04).** This bundle (R2 through R8 + compliance) captured the old roadmap. R2/R3 shipped hollow (stub endpoints, dead `oraclous-core-service` logic, dropped auth) and the old R4–R8 phasing is discarded; everything is rebuilt real, per service, under R3.5. Content below is retained for reference only.

| Release ID | R2 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| Window | Weeks 7-10 |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| Dependencies | R0 (architecture, OHM spec), R0.5 (tenancy), R1 (agent identity for descriptor authorship) — all Done |

## Goal

Evolve `oraclous-core-service` into `capability-registry-service` — the platform's Layer 2. Collapse the two existing tool registries (the in-memory `tool_registry.py` and the DB-backed `ToolRegistryService`) into a single source of truth. Generalise from "tools" to "capabilities" — the unified descriptor model that covers tools, skills, agents, harnesses, and human roles. Introduce OHM-shaped descriptors for everything. Retire the workflow stubs that were never implemented and would create more debt than starting clean.

## Scope

### In scope

* Service renamed from `oraclous-core-service` to `capability-registry-service`
* Unified capability descriptor schema with kind discrimination (`tool`, `skill`, `agent`, `harness`, `human_role`) — every capability shares one descriptor shape
* The two existing tool registries collapse into one resolution path with one storage backend
* OHM-shaped descriptors generated for every existing customer-registered tool (Google Drive Reader, Notion Reader, PostgreSQL Reader, MySQL Reader, etc.) — wrapper-style, original executor classes preserved
* Content-hash versioning on every descriptor; semver tags optional
* First inbound adapter shipped: MCP tool importer (translates external MCP tool definitions into OHM tool descriptors)
* The agent toolkit's schema registry (`agent_tool_schemas.py`) collapses into the capability registry; one descriptor, one place
* Retirement of `workflow_service.py`, `pipeline_generator.py`, and related stubs with retirement documentation noting what they were and why
* The instance manager's code is salvaged into the registry's invocation handle logic; the workflow-bound "instance" concept retires

### Out of scope

* Harness runtime extraction (R4) — capabilities are registered here but invoked there
* Execution engine extraction (R5)
* Outbound adapters (OHM → external formats) — first one ships in R6
* Codex agent definition adapter — deferred per [Section 9](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65988) until Codex format stabilises

## Deliverables

- [ ] **capability-registry-service deployed** — verified by the renamed service running with all its existing endpoints functional and a green CI pass; ports unchanged from `oraclous-core-service` to avoid disrupting callers
- [ ] **Unified capability descriptor schema** — verified by every capability (tool, skill, agent, harness, human_role) being stored under one schema with a `kind` field discriminator; descriptor validates against the OHM spec for the relevant kind
- [ ] **Single registry resolution path** — verified by every capability lookup routing through one code path; the in-memory and DB-backed dual-registry pattern is gone; the in-memory layer is a cache, not a separate source of truth
- [ ] **OHM descriptors for existing tools** — verified by every customer-registered tool having a generated OHM descriptor; existing executor classes still work; customer-facing API contracts preserved (no breaking changes for current integrations)
- [ ] **Content-hash versioning** — verified by every descriptor carrying a content hash that changes only when the descriptor's normalised form changes; identical descriptors produce identical hashes; semver tags accepted but optional
- [ ] **MCP tool importer working** — verified by registering an external MCP server, enumerating its tools, and seeing each tool appear in the registry as a first-class OHM capability with `implementation.type: mcp`
- [ ] **Agent toolkit schema registry collapsed** — verified by the agent toolkit consuming descriptors from the capability registry rather than its own schema source; no duplicate descriptor storage anywhere
- [ ] **Workflow stubs retired** — verified by removal of `workflow_service.py`, `pipeline_generator.py`, and related dead code; retirement documented (what they were, why retired, what replaces them) in the codebase docs and the Architecture Revision History
- [ ] **Instance manager salvaged** — verified by instance-manager code surviving as part of the registry's invocation handle logic; the workflow-bound "instance" concept no longer exists; existing per-workflow tool configurations migrate to per-harness capability allocations as a one-time data migration

## Migration source map

Per [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 7. **Completed 31 May 2026** from a read of the legacy backend worktree (`legacy-reference/old-backend`): [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) authored source paths + verdicts, [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) signed off the target-shape column, [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) flagged the threat-carrying rows. Default per Section 7.1: lift-and-reshape per service. Note: the R0.5 scaffold (ORA-13) already created the `services/capability-registry-service/` and `packages/ohm/` placeholder shells — R2 **populates** them rather than creating from zero.

| Deliverable | Source in legacy (confirmed path) | Target shape (solution-architect sign-off) | Verdict | Threat flags (security-architect) |
| --- | --- | --- | --- | --- |
| 1 — service deployed | R0.5 shell `services/capability-registry-service/` + `oraclous-core-service` entrypoint/routers | Populated Layer-2 service; ports unchanged; green CI | Reshape (`[impl-infra]`) | — |
| 2 — unified descriptor schema | `oraclous-core-service/app/schemas/tool_definition.py`, `app/schemas/common.py` → `packages/ohm/` | OHM descriptor with `kind` discriminator; `credential_requirements` = declared scope; validates vs OHM spec (ADR-002) | Reshape | T2-M3 (declaration) |
| 2 — descriptor DB | `oraclous-core-service/app/models/tool_definition.py`, `app/repositories/tool_definition_repository.py` | Single `capability_descriptor` table; JSONB search preserved | Reshape | — |
| 3 — single resolution path | `app/services/tool_registry.py`, `app/interfaces/tool_registry.py`, `app/tools/registry.py`, `app/services/tool_sync_service.py` | One DB-backed registry; in-memory = read-through cache; `tool_sync_service` deleted | Lift + Reshape | — |
| 4 — OHM-ify tools | `app/tools/implementations/ingestion/*`, `app/tools/base/*`, `app/tools/factory.py`, `app/tools/__init__.py` | OHM `kind: tool` wrappers; executors + customer APIs preserved; table/plugin registration | Extract + Reshape | T2-M3 |
| 5 — content-hash versioning | flat `version` string in `ToolDefinition` | Deterministic content hash over canonical descriptor; optional semver tag | Greenfield | T3-M2 |
| 6 — MCP importer | empty `app/tools/mcp_tool.py` | Inbound adapter → OHM descriptors, `implementation.type: mcp` | Greenfield | (T2-M3 if MCP declares creds) |
| 7 — agent-toolkit collapse | `knowledge-graph-builder/app/services/agent_tool_schemas.py` | Provider schemas generated from registry descriptors | Reshape | — |
| 8 — workflow retirement | `app/services/workflow_service.py`, `app/services/pipeline_generator.py`, `app/models/schemas/repositories` for workflow | Removed per ADR-005 + retirement docs; rows archived first | Reshape (delete) | retirement risk |
| 9 — instance salvage | `app/services/instance_manager.py`, `app/schemas/tool_instance.py`, `app/models/tool_instance.py`, `app/repositories/instance_repository.py` | Per-harness capability allocation + invocation handle; allocation ≤ declared scope | Reshape | T2-M3 |

**OHM descriptor shape (cross-cutting).** The unified descriptor `kind` discriminator + `credential_requirements`/declared-scope fields (Deliverable 2 / S0.2) are recorded canonically on the [OHM v1.0 Spec](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) / [Manifest Format](https://oraclous.atlassian.net/wiki/spaces/OP/pages/425993) page at agreement (solution-architect). This is **intra-backend cross-service** (consumed by the KGB agent toolkit via S5.1) — no `Contract` issue is opened. The **gateway/FE-facing** capability-descriptor Contract is **deferred to R6** when the gateway surfaces capabilities.

## Decomposition plan (executed 31 May 2026)

Authored by [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840). Backend release → full TDD flow: at Ready, Agent Owner → `test-author` (failing tests first) → `backend-implementer`; `be-test-reviewer` co-signs security-touching stories; `devops-implementer` owns `[impl-infra]`; `docs-writer` owns `[docs]`.

| Epic | Goal | Stories |
| --- | --- | --- |
| [ORA-57](https://oraclous.atlassian.net/browse/ORA-57) Epic 0 — Service & schema foundation | Populate the shells; define the OHM descriptor | [ORA-66](https://oraclous.atlassian.net/browse/ORA-66) S0.1 service shell/CI/ports (Reshape, `[impl-infra]`) · [ORA-67](https://oraclous.atlassian.net/browse/ORA-67) S0.2 OHM descriptor schema (Reshape, T2-M3) · [ORA-68](https://oraclous.atlassian.net/browse/ORA-68) S0.3 descriptor DB + migration (Reshape) |
| [ORA-58](https://oraclous.atlassian.net/browse/ORA-58) Epic A — Single resolution path | Collapse the dual registry | [ORA-69](https://oraclous.atlassian.net/browse/ORA-69) S1.1 single DB-backed registry (Lift) · [ORA-70](https://oraclous.atlassian.net/browse/ORA-70) S1.2 demote in-memory to cache + delete sync (Reshape) |
| [ORA-59](https://oraclous.atlassian.net/browse/ORA-59) Epic B — OHM-ify tools | OHM wrappers over preserved executors | [ORA-71](https://oraclous.atlassian.net/browse/ORA-71) S2.1 table/plugin registration (Reshape) · [ORA-72](https://oraclous.atlassian.net/browse/ORA-72) S2.2 OHM wrappers ×4 (Extract) |
| [ORA-60](https://oraclous.atlassian.net/browse/ORA-60) Epic C — Content-hash versioning | Tamper-evidence surface | [ORA-73](https://oraclous.atlassian.net/browse/ORA-73) S3.1 content-hash (Greenfield, T3-M2) |
| [ORA-61](https://oraclous.atlassian.net/browse/ORA-61) Epic D — MCP importer | First inbound adapter | [ORA-74](https://oraclous.atlassian.net/browse/ORA-74) S4.1 MCP → OHM importer (Greenfield) |
| [ORA-62](https://oraclous.atlassian.net/browse/ORA-62) Epic E — Agent-toolkit collapse | Generate provider schemas from descriptors | [ORA-75](https://oraclous.atlassian.net/browse/ORA-75) S5.1 collapse `agent_tool_schemas` (Reshape) |
| [ORA-63](https://oraclous.atlassian.net/browse/ORA-63) Epic F — Invocation handles | Salvage instance manager; T2-M3 allocation cap | [ORA-76](https://oraclous.atlassian.net/browse/ORA-76) S6.1 per-harness allocation + handle (Reshape, T2-M3) |
| [ORA-64](https://oraclous.atlassian.net/browse/ORA-64) Epic G — Workflow retirement | Delete stubs per ADR-005 | [ORA-77](https://oraclous.atlassian.net/browse/ORA-77) S7.1 delete stubs + dead code (Reshape/delete) · [ORA-78](https://oraclous.atlassian.net/browse/ORA-78) S7.2 retirement docs (`[docs]`) |
| [ORA-65](https://oraclous.atlassian.net/browse/ORA-65) Epic V — Verification gate | 9-deliverable acceptance | [ORA-79](https://oraclous.atlassian.net/browse/ORA-79) S8.1 R2 acceptance gate (`[impl-infra]`) |

### Sequencing (waves)

* **Wave 0:** S0.1 ([ORA-66](https://oraclous.atlassian.net/browse/ORA-66)) ∥ S0.2 ([ORA-67](https://oraclous.atlassian.net/browse/ORA-67)) → S0.3 ([ORA-68](https://oraclous.atlassian.net/browse/ORA-68)). **Both S0.1 + S0.2 are Ready now.**
* **Wave 1:** S1.1 ([ORA-69](https://oraclous.atlassian.net/browse/ORA-69)) → S1.2 ([ORA-70](https://oraclous.atlassian.net/browse/ORA-70))
* **Wave 2:** S2.1 ([ORA-71](https://oraclous.atlassian.net/browse/ORA-71)) → S2.2 ([ORA-72](https://oraclous.atlassian.net/browse/ORA-72)); S3.1 ([ORA-73](https://oraclous.atlassian.net/browse/ORA-73))
* **Wave 3:** S4.1 ([ORA-74](https://oraclous.atlassian.net/browse/ORA-74), after S3.1) ∥ S5.1 ([ORA-75](https://oraclous.atlassian.net/browse/ORA-75), early)
* **Wave 4:** S6.1 ([ORA-76](https://oraclous.atlassian.net/browse/ORA-76))
* **Wave 5:** S7.1 ([ORA-77](https://oraclous.atlassian.net/browse/ORA-77)) → S7.2 ([ORA-78](https://oraclous.atlassian.net/browse/ORA-78)) — **hard-sequenced after S6.1** (salvage before retirement); S7.1 is the highest-risk R2 story, its own PR
* **Wave 6:** S8.1 ([ORA-79](https://oraclous.atlassian.net/browse/ORA-79)) gate

Critical path: S0.2 → S0.3 → S1.1 → S6.1 → S7.1 → S8.1. Security-touching (be-test-reviewer co-sign): S0.2 (T2-M3 declaration), S3.1 (T3-M2), S6.1 (T2-M3 enforcement).

## Architecture references

* [Section 8 — Phase 2](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329) — the phase narrative this release operationalises
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Layer 2 (Capability Registry) ownership and exposed APIs
* [Section 4 — Manifest Format Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/425993) — the OHM shape that descriptors conform to
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — the implementation contract
* [Section 7 — Portability Story](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753728) — adapter pattern that inbound MCP importer follows

## ADRs implemented

* [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) — OHM as Canonical Manifest Format (R2 is where descriptors become OHM-shaped in production)
* [ADR-005](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772) — Workflow Concept Retirement; Harness as Replacement (R2 is where the workflow stubs are deleted)

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T2 — Privilege escalation | T2-M3 (descriptors declare credential requirements explicitly; registry enforces that an agent's allocation cannot include a capability whose credential scope exceeds the agent's declared scope) | Registry-side enforcement complete (S0.2 declaration + S6.1 enforcement); runtime-side per-invocation recheck lands in R4 |
| T3 — Prompt injection / capability misuse | T3-M2 (capability descriptions stored under content-hash versioning; tampering changes the hash; runtime can reject a capability whose hash does not match) | Versioning surface complete (S3.1); runtime enforcement lands in R4 |

## Governance impact

R2 makes the capability descriptor model match the OHM specification. Before this release, capabilities exist as DB rows with a tool-specific shape; after R2, every capability is an OHM document that the Governance Taxonomy can reason about uniformly. The taxonomy's `capability_kinds` binding becomes meaningful — policies can declare "skills require workspace admin to install" or "tools with credential scope `secrets:read` require a hardened policy set" and the registry can enforce these declaratively rather than per-tool.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Existing customer-registered tools break during the OHM-descriptor wrap | Medium | Wrapping is mechanical; existing executor classes are untouched. Integration tests for every shipped tool (Google Drive, Notion, PostgreSQL, MySQL) gate the release (S2.2). | backend-implementer |
| The two-registry collapse leaves dangling references in code that imported only one of them | Medium | Static analysis pass identifies all importers of either registry; each is migrated to the unified path before the old registries are deleted (S1.2 grep-clean gate). | code-reviewer |
| MCP importer translates a tool incorrectly, producing an OHM descriptor that the runtime later cannot invoke | Medium | Importer ships with a round-trip test against a known reference MCP server; rejects any tool it cannot translate cleanly; failures logged with the original MCP payload (S4.1). | backend-implementer |
| Workflow retirement deletes data that turns out to be needed | Low | Workflow DB rows exported to an archive table before deletion; retirement docs name workflow-dependent features (none in production). S7.1 hard-sequenced after the S6.1 salvage. | devops-implementer |
| Instance-manager salvage misses a code path that existing callers depend on | Low | Instance manager has few callers; each enumerated before salvage; per-harness allocation is API-compatible with per-workflow config for the in-production case (S6.1). | backend-implementer |

## Dependencies

**Upstream:** R0 (OHM spec), R0.5 (organisation scoping on every descriptor), R1 (agent identity for descriptor authorship and credential requirements) — all Done.

**Downstream:** R3 (knowledge graph decomposition uses the registry to declare retriever capabilities). R4 (harness runtime resolves capabilities from this registry; runtime per-invocation T2-M3/T3-M2 recheck). R5 (execution engine consumes capability invocation handles). R6 (gateway exposes registry-resolved capabilities as MCP tools; gateway-facing descriptor Contract). R7 (compiler harness surveys this registry to plan topologies).

## Sprint references

R2 transitioned **Planned → Briefed → In progress** on 31 May 2026 (product-planner took the gate on the tech-lead's authorisation). Five-plus epics + 14 stories created; the Wave-0 first wave (S0.1 [ORA-66](https://oraclous.atlassian.net/browse/ORA-66) → devops-implementer; S0.2 [ORA-67](https://oraclous.atlassian.net/browse/ORA-67) → test-author) is **Ready**; the remaining stories are in Backlog with `Blocks` links per the sequencing. Epics: [ORA-57](https://oraclous.atlassian.net/browse/ORA-57) … [ORA-65](https://oraclous.atlassian.net/browse/ORA-65); stories [ORA-66](https://oraclous.atlassian.net/browse/ORA-66) … [ORA-79](https://oraclous.atlassian.net/browse/ORA-79).

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R2 as the capability-registry-consolidation release; matches Section 8 Phase 2 |
| 31 May 2026 | Completed the Migration source map (source paths, target-shape sign-off, verdicts, threat flags) and the Decomposition plan (9 epics [ORA-57](https://oraclous.atlassian.net/browse/ORA-57)–[ORA-65](https://oraclous.atlassian.net/browse/ORA-65), 14 stories [ORA-66](https://oraclous.atlassian.net/browse/ORA-66)–[ORA-79](https://oraclous.atlassian.net/browse/ORA-79)) with lift-tags, owner-at-Ready, and `Blocks` links. Moved the Wave-0 first wave (S0.1, S0.2) to Ready. Status Planned → **Briefed** → **In progress**. | product-planner (coordinator; SA target-shape, SecA threat flags) | Take the Planned → Briefed gate on tech-lead authorisation and begin R2 execution |

---

<!-- source_page_id: 557322 | R3 — Phase 3: Knowledge graph decomposition -->

# R3 — Phase 3: Knowledge graph decomposition

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

---

<!-- source_page_id: 622923 | R4 — Phase 4: Harness runtime extraction -->

# R4 — Phase 4: Harness runtime extraction

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

---

<!-- source_page_id: 164225 | R5 — Phase 5: Execution engine and runtime completion -->

# R5 — Phase 5: Execution engine and runtime completion

| Release ID | R5 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 21-24 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0, R0.5, R1, R2, R3, R4 (the runtime must exist before the durable layer beneath it can be extracted) |
| --- | --- |

## Goal

Extract the durable execution side (tool execution service, job tracking, async progress) from `capability-registry-service` into a new `execution-engine-service`. Complete the harness runtime with HITL gates, round-tables, schedules, task boards, and cross-workspace federation traversal. After this release the runtime has every primitive the default compiler needs.

## Scope

### In scope

* `execution-engine-service` deployed as its own service with its own deployment unit and scaling profile
* Tool execution service code migrated from capability-registry-service: sync execution, async execution, job tracking, progress streaming
* Task board data model implemented in the Substrate; task board APIs exposed by the execution engine
* HITL primitive: task assignment to a human, notification dispatch through declared channels, execution pause and persistence, resumption on human action, timeout escalation
* Round-table primitive: lifecycle (open, contribute, close), invitation, contribution queue, decision capture, provenance
* Schedule firing: cron expressions registered with the execution engine; the engine fires triggers at scheduled times; scheduled wake-ups create execution contexts
* Multi-actor coordination via task boards: hand-offs, dependencies, status transitions, schedules
* Cross-workspace federation traversal in the runtime: every cross-workspace operation calls the substrate access decision API with the actor's delegated scope

### Out of scope

* Application gateway extraction (R6)
* Compiler harness (R7) — requires HITL and round-tables (this release) to exist first
* Schedule storm protection — deferred to R8
* Consciousness drift detection — deferred to R8
* Federation laundering audit reports — deferred to R8

## Deliverables

- [ ] **execution-engine-service deployed** — verified by the new service running with its own deployment unit; tool execution service code lives here; ports and APIs documented
- [ ] **Task board data model live** — verified by task boards persisting in the Substrate with full provenance and ReBAC enforcement; tasks can be queried, assigned, claimed, completed, escalated, cancelled
- [ ] **HITL primitive working** — verified by an integration test where a harness reaches a `policies.hitl.required_at` gate, execution pauses, a human is notified, the human acts via the task board, and execution resumes with the human's response
- [ ] **Round-table primitive working** — verified by an integration test where an actor opens a round-table, multiple invited actors contribute, a synthesiser proposes a decision, the round-table closes, and provenance captures the full conversation
- [ ] **Schedule firing live** — verified by a scheduled harness with a cron trigger waking at the declared time, the runtime loading the harness, the agent reading the task board and consciousness record, and the scheduled wake-up's work completing
- [ ] **Cross-workspace federation traversal in the runtime** — verified by an agent in workspace A reading from workspace B under a declared cross-workspace scope; the Substrate's access decision API gates the operation; provenance captures the cross-workspace action
- [ ] **Notification dispatch channels working** — verified by HITL notifications being dispatched via task board, email, and at least one of (Telegram, Slack, PagerDuty); test coverage for each declared channel
- [ ] **Checkpoints and resumability** — verified by a durable harness surviving a process restart mid-execution; state restored from the last checkpoint; the harness continues from where it paused

## Architecture references

* [Section 8 — Phase 5](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Execution Engine ownership, the two operational modes (synchronous vs durable)
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — Flow 3 (Schedule), Flow 4 (Traversal), Flow 5 (Round-Table), Flow 7 (HITL)
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — HITL gates are policy-declared

## ADRs implemented

* [ADR-004](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) — Federation via ReBAC Traversal (R5 is where federation becomes a runtime concern in production)

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T1 — Data exfiltration | T1-M2 (cross-workspace traversal is gated by the substrate at every operation) | Full T1 coverage operationally — what was a substrate guarantee from R0.5 is now also a runtime guarantee |
| T4 — Resource exhaustion | T4-M1 (durable execution checkpoints prevent infinite-loop budget burn; the execution engine bounds work per wake-up) | Partial — full schedule-storm protection lands in R8 |
| T5 — Notification spoofing | T5-M1 (notifications are dispatched only by the runtime/execution engine; recipients can verify via the task board, which is the canonical source) | Full T5 baseline |

## Governance impact

R5 makes HITL gates declarative and runtime-enforced. Before this release, HITL is a concept in the Governance Taxonomy; after R5, a manifest's `policies.hitl.required_at` field actually causes the runtime to pause at the named transition, dispatch notifications, and wait for human action. Round-tables also become governable — the orchestration prose can declare round-tables at specific decision points, and provenance captures the resulting deliberation.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Durable execution introduces state-consistency bugs across restarts | High | Checkpoint format is versioned. Restart tests cover every documented harness pattern. Idempotency keys on every external side effect prevent double-execution. | backend-implementer + test-author |
| Schedule firing produces a thundering herd under load | Medium | Jitter is applied to cron firing per harness. Per-organisation rate limits on scheduled wake-ups. Schedule storm protection (R8) hardens this further. | devops-implementer |
| HITL notification channels fail silently | Medium | Every dispatch records a provenance entry with delivery outcome. Failed deliveries trigger fallback to the next channel and surface as a task board annotation visible to the workspace admin. | backend-implementer |
| Round-tables persist beyond their declared maximum duration | Low | The execution engine owns round-table timeouts; on timeout, the declared fallback decision applies and the round-table closes automatically. Test coverage for the timeout path. | backend-implementer |
| Cross-workspace traversal is too permissive because the runtime trusts a stale ReBAC decision | Medium | Per-invocation recheck from R4 applies to traversal as well. Decision cache TTL is bounded; revocation events invalidate cached decisions immediately. | security-architect |

## Dependencies

**Upstream:** R0–R4 (every prior release).

**Downstream:** R6 (gateway exposes task board UIs, round-table UIs, HITL approval surfaces). R7 (compiler harness is the first production harness that exercises HITL, round-tables, and schedules in full).

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R5 as the execution engine + runtime completion release; matches Section 8 Phase 5 |

---

<!-- source_page_id: 196877 | R6 — Phase 6: Application Gateway extraction -->

# R6 — Phase 6: Application Gateway extraction

| Release ID | R6 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 25-28 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0–R5 (gateway sits in front of every layer; everything beneath must be in target shape first) |
| --- | --- |

## Goal

Lift the platform's public-facing surface — chat APIs, published agents, integration keys, embeddable widgets, the new MCP server, the new MCP client integrations, webhook receivers, task board UIs — into a new `application-gateway-service`. Consolidate the scattered external surface area into one place with one consistent security model. Until the gateway exists in target shape, the platform's portability story cannot be demonstrated end to end.

## Scope

### In scope

* `application-gateway-service` deployed as its own service with its own deployment unit
* Chat APIs migrated: the chat persistence layer (Postgres with RLS) lives in the gateway; the execution backing is delegated to the harness runtime
* Published agents and integration keys migrated from `knowledge-graph-builder` (now `knowledge-graph-service`) to the gateway
* New MCP server implementation: exposes the workspace's capabilities to MCP-compatible clients (Claude Desktop, Cursor, Continue); selective surface determined by ReBAC; three authentication modes (integration keys, member credentials, agent credentials)
* New MCP client integrations: external MCP servers can be registered and their tools imported into the capability registry as first-class OHM tools (uses the inbound adapter from R2)
* Webhook receivers for external triggers (Git pushes, calendar events, third-party integrations)
* Task board UI APIs exposed
* Embeddable widget surface for putting Oraclous-powered agents into customer applications

### Out of scope

* Compiler harness (R7) — the gateway hosts it but the harness itself is R7
* Billing Service (deferred to future release; pricing model is product strategy and the metering surface from R0.5 is the contract billing later consumes)
* Outbound exporters for harnesses to specific external runtimes beyond best-effort (Claude Code skills round-trip and OHM-to-Markdown are in scope; LangGraph, Codex exporters are out)

## Deliverables

- [ ] **application-gateway-service deployed** — verified by the new service running with its own deployment unit; all gateway-shaped concerns migrated; ports and APIs documented
- [ ] **Chat APIs migrated** — verified by chat traffic routing through the gateway; chat persistence with RLS works as before; the runtime is called for execution; no breaking changes for current customer integrations
- [ ] **Published agents and integration keys migrated** — verified by every existing published agent continuing to serve traffic; integration keys remain valid; rate limits and CORS scoping preserved
- [ ] **MCP server live** — verified by an MCP-compatible client connecting, authenticating with an integration key, enumerating the workspace's capabilities, and invoking one; provenance captures the MCP-initiated action
- [ ] **MCP client integration live** — verified by registering an external MCP server, its tools appearing in the capability registry as OHM tools, an agent being allocated one, and the runtime invoking it successfully
- [ ] **Webhook receivers live** — verified by at least three webhook source types working (Git push, calendar event, generic HTTP); each receiver triggers the correct harness via the execution engine
- [ ] **Task board UI APIs exposed** — verified by a member loading a task board view from the gateway; assignment, claim, hand-off, escalation, status transitions all work through the API
- [ ] **Embeddable widget surface working** — verified by a sample widget embedded in an external host application invoking a published agent through the gateway; CORS, rate limits, integration key enforcement all working

## Architecture references

* [Section 8 — Phase 6](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Layer 4 (Application Gateway) ownership and exposed APIs
* [Section 7 — Portability Story](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753728) — MCP server, MCP client, embeddable widgets, adapter pattern

## ADRs implemented

* No new ADRs — R6 implements the Layer 4 commitments from [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) and the portability commitments from [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) already covered at the architectural level.

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T1 — Data exfiltration | T1-M4 (every external API call carries an authenticated principal; the gateway never bypasses ReBAC on the way through to the substrate) | Full T1 coverage at the external boundary |
| T5 — Notification spoofing | T5-M2 (webhook receivers verify source signatures; webhooks from unknown sources are rejected and logged) | Full T5 coverage |
| T7 — Audit-log gap | T7-M2 (every external API request produces a gateway-level provenance entry; the entry chains to the runtime-level entries for the same execution context) | Full T7 baseline at the external boundary |

## Governance impact

R6 makes external access governable. Before this release, public-facing surfaces are scattered across services with inconsistent rate limits, CORS rules, and integration key handling. After R6, every external request passes through the gateway and is subject to a single consistent enforcement layer. The Governance Taxonomy's `exposure_policy` binding becomes meaningful — declarations like "this harness is published with rate limit X, CORS scope Y, and integration key required" are now enforced by code.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| The chat API migration introduces customer-visible latency or breakage | High | Regression tests for chat APIs are a release gate. Canary deployment to a fraction of traffic. Rollback path documented. Customer-facing API contracts preserved. | qa-engineer + devops-implementer |
| The new MCP server has security regressions vs the retired bespoke MCP work | Medium | Section 7's MCP server design is explicit about lessons learned from the retired work. Threat-model review by security-architect before R6 closes. Selective ReBAC-gated surface from day one. | security-architect |
| Webhook signature verification has provider-specific quirks that lead to false rejections | Medium | Each declared webhook source type has its own signature verifier and its own test fixture replaying real provider payloads. False rejections during testing trigger verifier review before R6 closes. | backend-implementer |
| The MCP client integration imports a malicious tool from an untrusted external server | Medium | MCP server registration requires workspace admin approval. The first invocation of a newly imported tool is gated by an HITL approval. Output redaction patterns apply uniformly to imported and native tools. | security-architect |
| Embeddable widget surface introduces XSS via untrusted host pages | Medium | Widgets use the host's origin only for postMessage targeting; all DOM rendering uses safe APIs; CORS is strictly origin-scoped. Penetration testing pass before R6 closes. | security-architect + frontend-implementer |

## Dependencies

**Upstream:** R0–R5 (every prior release).

**Downstream:** R7 (compiler harness is exposed through the gateway). R8 (security hardening pass extends gateway-level mitigations).

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R6 as the application gateway extraction release; matches Section 8 Phase 6 |

---

<!-- source_page_id: 164260 | R7 — Phase 7: Compiler harness and seed manifests -->

# R7 — Phase 7: Compiler harness and seed manifests

| Release ID | R7 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 29-32 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0–R6 (the compiler is a harness; the runtime, gateway, registry, retriever, and execution engine must all exist in target shape) |
| --- | --- |

## Goal

Build the default compiler harness. Define seed manifests for new workspaces. Implement the bootstrap update flow. This is the platform's "first turn" — before R7, workspaces have a runtime but no compiler. After R7, a workspace admin can describe a goal in prose and get a working harness back. The product loop closes.

## Scope

### In scope

* Default compiler harness in OHM — a team of agents (planner, capability-surveyor, manifest-drafter, reviewer) with allocated capabilities, deployed as the seed compiler for new workspaces
* Default consciousness skill in OHM — the bounded-learning pattern referenced from Section 5 Flow 6
* Default capability inventory definition — the standard set of tools and skills every new workspace ships with
* Default task board definition — the standard board structure every new workspace ships with
* Default policy template — references one of the founding policy sets from the Governance Taxonomy
* Reference catalog mechanism — the platform-published versions of seed artifacts, fetchable by workspaces during bootstrap and update
* Bootstrap update notification flow — when the reference catalog publishes a new version, each workspace using the prior version is notified through the gateway
* Diff-and-accept UI for platform-published updates — workspace admins can see what changed, accept, merge selectively, or reject
* The MCP server for the agent-Jira and agent-Confluence convention layer (the small standalone server discussed in Group D follow-up 3) — implemented as a real Capability Registry entry now that R2-R6 are done

### Out of scope

* Security hardening pass (R8) — anything from Section 6.5's Phase 2 or Phase 3 mitigation tiers
* Higher-order portability tooling beyond the inbound/outbound adapters that already exist
* Codex agent definition adapter — deferred per Section 9
* Visual workflow editor — deferred indefinitely per Section 9

## Deliverables

- [ ] **Default compiler harness deployed** — verified by a new workspace being created with the seed compiler pre-installed; the workspace admin can issue a goal in prose; the compiler emits a draft OHM manifest; review/edit dialog works; manifest commits to the substrate
- [ ] **Default consciousness skill deployed** — verified by every agent in a new workspace having the default skill in its capability allocation; the skill runs at end of turn; observations write to the consciousness record; suggestions surface as tasks
- [ ] **Default capability inventory live** — verified by a new workspace shipping with the standard tools (KG operations, file readers, web fetch) and standard skills (planning, summarisation, evaluation) immediately invokable
- [ ] **Default task board live** — verified by every new workspace shipping with a board configured to receive tasks from the compiler and runtime
- [ ] **Default policy template live** — verified by every new workspace shipping with a policy envelope that references one of the founding policy sets; budgets, HITL rules, output redaction all applied
- [ ] **Reference catalog mechanism live** — verified by the platform publishing a versioned reference catalog entry; workspaces can fetch the entry; content hashes match
- [ ] **Bootstrap update notification flow live** — verified by a published catalog update producing a notification on every affected workspace; the workspace admin sees the diff; accept/merge/reject options work
- [ ] **Agent-MCP server published** — verified by the small standalone MCP server (my_tasks, claim_next, handoff_to, escalate_to_human, complete, observe, review_request) registered as a Capability Registry entry; all 11 agent personas can consume it; Group D follow-up 3's skill-instruction convention is no longer the only enforcement

## Architecture references

* [Section 8 — Phase 7](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — the bootstrap problem and seeded default workspace template
* [Section 5 — Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426016) — Flow 1 (Compile), Flow 6 (Learn), Flow 8 (Bootstrap update)
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — every seed artifact is OHM
* [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) — Section 6 documents the agent identity convention that the MCP server replaces

## ADRs implemented

* [ADR-003](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884737) — Platform-as-Code, Actors-as-Harnesses (the compiler is the most prominent proof that intelligence runs as harnesses, not platform code)
* [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) — OHM as Canonical Manifest Format (the seed manifests are all OHM)

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T3 — Prompt injection / capability misuse | T3-M3 (the compiler's output is reviewable by the operator before commit; no manifest reaches the substrate without explicit operator approval) | Full T3 coverage with the compile-time review gate |
| T6 — Operator-separation breach | T6-M3 (platform-published updates require workspace admin acceptance; Oraclous-the-company cannot mutate a workspace's state by publishing updates) | Full T6 coverage for the bootstrap update path |

## Governance impact

R7 closes the recursion: the platform's default behaviour is now expressed as harnesses that customers can inspect, fork, and modify. There is no platform magic left. The Governance Taxonomy's `seed_artifact_versioning` binding becomes meaningful — every seed artifact carries a version, every workspace tracks which versions are installed, every update is auditable.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| The compiler harness is too brittle for v1 — produces low-quality manifests on common goals | High | The compiler is itself a harness and can be iterated continuously without architecture changes. v1 ships when the compiler handles a defined set of reference goals; iteration follows. The bar is "useful for early adopters" not "produces excellent manifests for all goals." | solution-architect + tech-lead |
| Bootstrap update flow fails on workspaces with heavy customisation | Medium | Merge-selectively path is the safety valve. Customisations are explicit OHM diffs against the reference; the merge tool surfaces conflicts for human resolution. Workspaces that reject all updates remain on their pinned versions indefinitely. | backend-implementer |
| Default consciousness skill creates noisy task lists from premature pattern detection | Medium | Skill ships with conservative thresholds (e.g., a pattern needs N occurrences before surfacing a suggestion). Workspace admins can tune thresholds. Skill is replaceable like any other. | solution-architect |
| Reference catalog versioning has a security gap (a published update gets accepted before its hash is verified) | Low | Updates are verified against the catalog's signed manifest before display in the diff UI. Acceptance writes the new content hash; the substrate verifies the hash matches the catalog's signed value before commit. | security-architect |
| The agent-MCP server lets agents bypass tech-lead approval gates by writing comments that mimic human authorship | Medium | The MCP server enforces the \[agent:NAME\] prefix on every comment; comments without the prefix are rejected. Static analysis on the Jira/Confluence audit stream surfaces any comment without a prefix as a violation. | security-architect |

## Dependencies

**Upstream:** R0–R6 (every prior release).

**Downstream:** R8 (security hardening). R-Compliance (the compiler's presence is a material input to SOC 2 Type II evidence about platform behaviour).

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R7 as the compiler harness + seed manifests release; matches Section 8 Phase 7 |

---

<!-- source_page_id: 66060 | R8 — Phase 8: Security hardening pass -->

# R8 — Phase 8: Security hardening pass

| Release ID | R8 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 33-36 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) |
| --- | --- |
| Dependencies | R0–R7 (every layer must be in target shape before the hardening pass; the compiler must exist before consciousness drift can be measured) |
| --- | --- |

## Goal

Implement the Phase 2 (hardening) and Phase 3 (advanced) mitigations from Section 6.5's phased mitigation plan that were not yet covered by earlier releases. Bring the platform's shipped security posture to parity with the architecture's documented commitments. After this release, every Tn-Mn entry from the Structured Threat Catalogue is implemented or has a documented compensating control.

## Scope

### In scope

* Indirect prompt injection sanitization extensions: capability inputs and outputs pass through sanitisation patterns that strip embedded prompt-injection markers
* Output redaction extensions: custom pattern support so customers can declare workspace-specific redaction rules beyond the platform defaults
* Cross-workspace traversal audit reports: scheduled reports that surface federation patterns suggestive of data laundering (T9.2)
* Service account principal type hardening: service accounts cannot delegate to agents; service-account-initiated executions have stricter HITL defaults
* Cache key isolation audits: scheduled checks that no cache key spans organisations; alerts on violation
* Consciousness drift detection: statistical baselines for agent behaviour; automated detection of drift patterns; periodic consciousness audits with anomaly reports
* Federation laundering audit reports: detection of high-volume cross-workspace reads followed by writes to less-restricted workspaces
* Adapter output validation: every adapter (Claude Code, MCP, OpenAPI) validates its output against the OHM spec; malformed output triggers a rejection with structured diagnostics
* Schedule storm protection: per-organisation rate limits on scheduled wake-ups; backoff on repeated failures; jitter on cron firing
* Penetration testing pass on the gateway and MCP server surfaces

### Out of scope

* SOC 2 Type II audit completion (R-Compliance — runs in parallel)
* ISO 27001 certification (R-Compliance)
* New mitigation categories not in Section 6.5 — these would be a v2 architecture revision

## Deliverables

- [ ] **Indirect prompt injection sanitisation live** — verified by integration tests where capability outputs containing embedded prompt-injection markers are sanitised before reaching downstream agents; test corpus from public injection databases passes
- [ ] **Custom output redaction patterns supported** — verified by a workspace declaring a custom regex; the runtime applies it on every dispatched output; provenance captures redaction applications
- [ ] **Cross-workspace traversal audit reports live** — verified by scheduled reports running daily; reports surface federation patterns above a configurable threshold; workspace admins can review
- [ ] **Service account hardening live** — verified by a test that proves a service account cannot mint a delegated token for an agent; service-account-initiated executions trigger HITL on every privileged transition
- [ ] **Cache key isolation audits live** — verified by a scheduled check across Redis and in-memory caches; any cross-org key triggers an alert and is logged for review
- [ ] **Consciousness drift detection live** — verified by behavioural baselines computed per agent over its operational history; drift beyond bounded thresholds surfaces as a security event in the workspace admin's queue
- [ ] **Federation laundering reports live** — verified by reports surfacing the read-then-write-to-less-restricted pattern; false positives bounded by configurable thresholds
- [ ] **Adapter output validation live** — verified by every shipped adapter rejecting malformed output rather than producing invalid OHM; malformed inputs logged with the original payload for review
- [ ] **Schedule storm protection live** — verified by integration tests where a deliberate burst of cron firings is rate-limited per organisation; backoff applied on repeated failures
- [ ] **Penetration testing pass** — verified by external pen-test report against the gateway and MCP server; all critical and high findings remediated before R8 closes

## Architecture references

* [Section 8 — Phase 8](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 6.5 — Security Threats and Mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/851990) — the source of every R8 deliverable
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — Tn-Mn IDs implemented here

## ADRs implemented

* No new ADRs — R8 closes out implementations of decisions already recorded in [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403), [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792), and the threat-driven review patterns documented in security-architect's skill.

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T3 — Prompt injection / capability misuse | T3-M4 (indirect prompt injection sanitisation extensions) | Closes T3 |
| T4 — Resource exhaustion | T4-M2 (schedule storm protection), T4-M3 (per-organisation rate limits) | Closes T4 |
| T6 — Operator-separation breach | T6-M4 (cache key isolation audits as a defence-in-depth backstop) | Closes T6 |
| T7 — Audit-log gap | T7-M3 (cross-workspace traversal audit reports), T7-M4 (federation laundering reports) | Closes T7 with the audit-side reporting |
| T6.2 — Consciousness drift | T6.2-M1 (consciousness drift detection) | Closes T6.2 (Section 6.5 Phase 3 advanced) |
| T9.2 — Federation laundering | T9.2-M1 (federation laundering audit reports) | Closes T9.2 (Section 6.5 Phase 3 advanced) |

## Governance impact

R8 closes the gap between the Governance Taxonomy's documented controls and the platform's shipped enforcement. After R8, every policy set in the taxonomy is enforceable end to end. Workspace admins can declare custom redaction patterns and have them apply uniformly. Cross-workspace traversal is auditable in addition to being permission-gated. The platform's commitments are now demonstrable, not aspirational.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Sanitisation patterns introduce false positives that block legitimate capability outputs | High | Patterns ship in shadow mode first (log but do not block) for a calibration period; thresholds tuned against real workspace traffic before enforcement is enabled. | security-architect |
| Consciousness drift detection produces too many false anomalies and is ignored | High | Baselines require N weeks of operational history before drift is reportable; thresholds are conservative; workspace admins can tune them; anomalies are surfaced with explanatory context not just raw scores. | security-architect |
| Penetration test surfaces critical findings that delay R8 | Medium | R8 has a 4-week window. If pen-test findings require more time than that, the release ships with the implementable mitigations and a follow-up release covers the remainder. R-Compliance can begin observation independently. | security-architect + tech-lead |
| Audit report volume overwhelms workspace admins | Medium | Reports default to weekly aggregates rather than per-event alerts. Workspace admins can subscribe to specific event types. Thresholds tunable. | security-architect |

## Dependencies

**Upstream:** R0–R7 (every prior release; consciousness drift requires the compiler and consciousness primitives from R5/R7).

**Downstream:** R-Compliance (R8 evidence feeds SOC 2 Type II audit). Phase 9 ongoing — post-R8 improvements are continuous, not release-gated.

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R8 as the security hardening pass release; matches Section 8 Phase 8 |

---

<!-- source_page_id: 688523 | R-Compliance — Cloud-mode compliance track -->

# R-Compliance — Cloud-mode compliance track

| Release ID | RC |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Parallel from R0.5 onward; first certifications expected after R8 closes, with the SOC 2 Type II audit window extending past R8 by the auditor's required observation period (typically 6-12 months) |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) |
| --- | --- |
| Dependencies | R0.5 (organisation tenancy is the cloud-mode prerequisite — the audit window cannot open before tenancy enforcement exists) |
| --- | --- |

## Goal

Achieve ISO 27001 and SOC 2 Type II certifications for the cloud-hosted deployment mode. The engineering work in R0 through R8 produces _evidence_ for these certifications; this release tracks the audit engagement, the operational controls documentation, the observation period, and the customer-facing attestation reports. Self-hosted customers do not require this work — they operate their own deployment and their own compliance posture; cloud customers receive the certifications as evidence of Oraclous-the-company's operational commitments.

## Scope

### In scope

* Audit firm selection and engagement (begins during R0.5)
* ISO 27001 scope agreement and gap assessment
* SOC 2 Type II observation period — typically 6-12 months from the time controls are mature
* Security controls documentation as formal policies (the Section 6.5 mitigations expressed in the auditor's required format)
* Operational controls implementation that engineering does not directly produce: access management, change management, incident response, business continuity, supplier management, vulnerability management
* Internal audit programme: scheduled reviews, evidence collection, remediation tracking
* Customer-facing attestation reports: SOC 2 Type II report shareable under NDA, ISO 27001 certificate publishable
* Trust centre setup: a public-facing page describing the platform's compliance posture and how to request attestation reports

### Out of scope

* Engineering deliverables — those are R0 through R8
* HIPAA, FedRAMP, or other certifications beyond ISO 27001 and SOC 2 Type II — deferred to future releases driven by customer demand
* Self-hosted compliance — that is the customer's concern

## Deliverables

- [ ] **Audit firm engaged** — verified by signed engagement letter; firm has SOC 2 and ISO 27001 expertise and is acceptable to enterprise customer base
- [ ] **Gap assessment complete** — verified by firm-produced gap report against ISO 27001 Annex A controls and SOC 2 Trust Services Criteria; remediation plan documented and prioritised
- [ ] **Security policies documented** — verified by a complete policy set covering access control, change management, incident response, business continuity, supplier management, vulnerability management, secure development, data handling, and acceptable use; policies reviewed and approved by tech-lead
- [ ] **Operational controls implemented** — verified by every control in the policy set having a documented procedure, an owner, and evidence of execution; access reviews run quarterly, change tickets follow approval workflow, incident response procedures rehearsed
- [ ] **Internal audit programme live** — verified by quarterly internal audits against the policy set; findings logged with owner and due date; remediation tracked to closure
- [ ] **SOC 2 Type II observation window opened** — verified by audit firm confirming controls are mature enough to begin observation; observation period running
- [ ] **ISO 27001 certification achieved** — verified by certification body issuing certificate; certificate is publishable on the trust centre
- [ ] **SOC 2 Type II report delivered** — verified by signed Type II report covering the full observation window; report shareable with enterprise customers under NDA
- [ ] **Trust centre live** — verified by a public page on oraclous.com describing the compliance posture, the certifications held, and how to request attestation reports under NDA

## Architecture references

* [Section 8 — Parallel track: Cloud-mode compliance work](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 6.5 — Security Threats and Mitigations](https://oraclous.atlassian.net/wiki/spaces/OP/pages/851990) — the engineering evidence base for the auditor
* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — Cloud-Hosted Mode with Equivalent Data Sovereignty

## ADRs implemented

* [ADR-008](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) — R-Compliance is the operationalisation of ADR-008's compliance commitments

## Threats addressed

R-Compliance does not directly implement Tn-Mn mitigations from the Structured Threat Catalogue. Instead, it produces auditable evidence that the mitigations implemented in R0 through R8 are operationally effective. The engineering releases satisfy "the control exists"; R-Compliance satisfies "the control has operated over the audit window with documented evidence."

## Governance impact

R-Compliance does not change the Governance Taxonomy — it adds external attestation of the taxonomy's operational effectiveness. Cloud customers can rely on the certifications as third-party evidence of platform commitments. Self-hosted customers continue to operate their own compliance posture; the platform makes self-hosted compliance easier by providing the same controls infrastructure but does not certify the customer's self-hosted deployment.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Audit firm finds material gaps that delay certification by quarters | Medium | Gap assessment runs early (during R0.5) so remediation has time to land alongside engineering. Pre-audit readiness review by the firm before observation opens. | tech-lead + security-architect |
| Engineering releases slip and push the observation window start past the engineering window close | Medium | Observation can begin on a defined subset of controls; subsequent controls join the observation window as they mature. Auditor consulted on partial observation models acceptable to enterprise customers. | tech-lead |
| Operational controls (change management, incident response, access reviews) are documented but not actually followed | High | Internal audit programme runs quarterly and produces findings. Findings track to closure. Lack of evidence is treated as a release-blocking issue for subsequent observation periods. | security-architect |
| A customer requires HIPAA, FedRAMP, or another framework not in v1 scope | Medium | Customer requirements are documented as inputs to future release planning. The R-Compliance work establishes the controls foundation; additional frameworks build on it rather than starting over. | tech-lead |
| An incident during the observation window invalidates evidence and forces re-observation | Medium | Incident response procedures include audit-evidence preservation. Some incidents reset specific control evidence; others (with documented remediation) are acceptable to auditors. Auditor consulted on edge cases. | tech-lead + security-architect |

## Dependencies

**Upstream:** R0.5 (cloud-mode prerequisite). R1, R3, R4, R6, R8 produce direct evidence for specific controls.

**Downstream:** None — R-Compliance is the terminal release in this cycle. Future compliance work (HIPAA, FedRAMP, regional certifications) builds on the foundation established here.

## Sprint references

R-Compliance is not Jira-ticket-shaped in the same way as the engineering releases. Audit milestones, policy reviews, gap remediation, and observation-window evidence collection are tracked in a parallel Confluence subspace (to be created when R-Compliance enters active work). Engineering work that contributes evidence is tracked via the engineering releases as usual.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R-Compliance as the parallel cloud-mode compliance track; matches Section 8 "Parallel track: Cloud-mode compliance work" |

---

<!-- source_page_id: 753930 | Build State — Group D follow-up (3) — CLOSED -->

# Build State — Group D follow-up (3) — CLOSED

**Status: Complete.** Group D follow-up (3) is fully done. All 11 release pages exist, all 11 agent skill pages carry the Agent Identity Convention (Section 11), and the Architecture Revision History is at v5 with the entry documenting this work. This page is retained as a historical record of the build session.

## Final status

| Item | Page ID | Status |
| --- | --- | --- |
| `09. Releases` hub | 164160 | <custom data-type="status" data-id="id-0">Done</custom> |
| R0 (canonical) | 622878 | <custom data-type="status" data-id="id-1">Done</custom> |
| R0 duplicate (superseded) | 131192 | <custom data-type="status" data-id="id-2">Marked superseded — awaiting trash from UI by tech-lead</custom> |
| R0.5 | 884934 | <custom data-type="status" data-id="id-3">Done</custom> |
| R1 | 557283 | <custom data-type="status" data-id="id-4">Done</custom> |
| R2 | 688482 | <custom data-type="status" data-id="id-5">Done</custom> |
| R3 | 557322 | <custom data-type="status" data-id="id-6">Done</custom> |
| R4 | 622923 | <custom data-type="status" data-id="id-7">Done</custom> |
| R5 | 164225 | <custom data-type="status" data-id="id-8">Done</custom> |
| R6 | 196877 | <custom data-type="status" data-id="id-9">Done</custom> |
| R7 | 164260 | <custom data-type="status" data-id="id-10">Done</custom> |
| R8 | 66060 | <custom data-type="status" data-id="id-11">Done</custom> |
| R-Compliance | 688523 | <custom data-type="status" data-id="id-12">Done</custom> |
| solution-architect Section 11 | 164068 | <custom data-type="status" data-id="id-13">Done</custom> |
| security-architect Section 11 | 557195 | <custom data-type="status" data-id="id-14">Done</custom> |
| product-planner Section 11 | 884840 | <custom data-type="status" data-id="id-15">Done</custom> |
| tech-lead Section 11 (with human/AI-persona split) | 983101 | <custom data-type="status" data-id="id-16">Done</custom> |
| test-author Section 11 | 294957 | <custom data-type="status" data-id="id-17">Done</custom> |
| backend-implementer Section 11 | 294995 | <custom data-type="status" data-id="id-18">Done</custom> |
| frontend-implementer Section 11 | 295035 | <custom data-type="status" data-id="id-19">Done</custom> |
| devops-implementer Section 11 | 164102 | <custom data-type="status" data-id="id-20">Done</custom> |
| code-reviewer Section 11 | 622800 | <custom data-type="status" data-id="id-21">Done</custom> |
| qa-engineer Section 11 | 884874 | <custom data-type="status" data-id="id-22">Done</custom> |
| docs-writer Section 11 | 557230 | <custom data-type="status" data-id="id-23">Done</custom> |
| Architecture Revision History v5 entry | 426111 | <custom data-type="status" data-id="id-24">Done</custom> |

## Outstanding human actions

* **Trash the duplicate R0 page** (131192) from the Confluence UI — the assistant cannot delete pages through the API. The canonical R0 is page 622878.

## Next phase

Group E (implementation handoff):

1. Create the `Agent Owner` custom field on Jira project ORA as single-select with 12 values: `solution-architect`, `security-architect`, `product-planner`, `tech-lead`, `test-author`, `backend-implementer`, `frontend-implementer`, `devops-implementer`, `code-reviewer`, `qa-engineer`, `docs-writer`, `human`.
2. Create Jira epics and stories for R0.5 and R1, sourced from those release pages' deliverables.
3. Author CLAUDE.md for `OraclousAI/oraclous-backend` and `OraclousAI/oraclous-frontend`.
4. (Deferred to R7) Build the small standalone agent-MCP server that codifies the Agent Identity Convention as a Capability Registry entry.
