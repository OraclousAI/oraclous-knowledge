---
confluence_id: "688482"
title: "R2 — Phase 2: Capability registry consolidation"
---

# R2 — Phase 2: Capability registry consolidation

> **Shipped HOLLOW — re-done under [R3.5](r3.5-make-every-service-real.md).** What merged for R2 was scaffolding, not the real capability registry: stub endpoints, the real registry/tool/connector logic left **undeleted and dead** (~6,300 LOC) in `oraclous-backend/oraclous-core-service/`, and "done" stories that passed only stub-tests. The real logic is ported out of `oraclous-core-service` into a real `capability-registry-service` as **step 5** of R3.5, after which `oraclous-core-service` is salvaged-then-deleted under human sign-off. The plan below is retained as the original intent; the realness bar is now ORAA-4 §22 (8 gates + Reza sign-off).

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
