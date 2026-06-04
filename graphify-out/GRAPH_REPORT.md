# Graph Report - oraclous-knowledge  (2026-06-04)

## Corpus Check
- 155 files · ~241,669 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1125 nodes · 1767 edges · 29 communities detected
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 133 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Section 2 — Conceptual Model|Section 2 — Conceptual Model]]
- [[_COMMUNITY_ADR-001 Four-Layer Architecture|ADR-001 Four-Layer Architecture]]
- [[_COMMUNITY_Test Strategy|Test Strategy]]
- [[_COMMUNITY_Section 2 — Conceptual Model|Section 2 — Conceptual Model]]
- [[_COMMUNITY_R5 — Execution Engine and Runtime Comp|R5 — Execution Engine and Runtime Comp]]
- [[_COMMUNITY_R3.5 — Make every service real|R3.5 — Make every service real]]
- [[_COMMUNITY_09. Releases hub|09. Releases hub]]
- [[_COMMUNITY_Cross-cutting agreement protocol|Cross-cutting agreement protocol]]
- [[_COMMUNITY_Frontend Stack Reference|Frontend Stack Reference]]
- [[_COMMUNITY_Glossary|Glossary]]
- [[_COMMUNITY_build_kb_index.py|build_kb_index.py]]
- [[_COMMUNITY_application-gateway-service|application-gateway-service]]
- [[_COMMUNITY_knowledge-retriever-service|knowledge-retriever-service]]
- [[_COMMUNITY_main()|main()]]
- [[_COMMUNITY_toolslintcheck_no_stubs.py (HOL001-0|tools/lint/check_no_stubs.py (HOL001-0]]
- [[_COMMUNITY_Docs Process & Deployment|Docs Process & Deployment]]
- [[_COMMUNITY_Engineering Flows & Board|Engineering Flows & Board]]
- [[_COMMUNITY_build_kb_index.py|build_kb_index.py]]
- [[_COMMUNITY_build_kb_index.py (index.md + llms.txt|build_kb_index.py (index.md + llms.txt]]
- [[_COMMUNITY_Frontend & Design System|Frontend & Design System]]
- [[_COMMUNITY_TDD & KB Canonicalisation|TDD & KB Canonicalisation]]
- [[_COMMUNITY_be-test-reviewer persona|be-test-reviewer persona]]
- [[_COMMUNITY_auth-service|auth-service]]
- [[_COMMUNITY_credential-broker-service|credential-broker-service]]
- [[_COMMUNITY_Multi-tenant Isolation Pattern|Multi-tenant Isolation Pattern]]
- [[_COMMUNITY_Cypher Injection Prevention|Cypher Injection Prevention]]
- [[_COMMUNITY_AgentExecutor (powers sync and durable|AgentExecutor (powers sync and durable]]
- [[_COMMUNITY_Cypher Injection Prevention|Cypher Injection Prevention]]
- [[_COMMUNITY_Multi-tenant Isolation Pattern|Multi-tenant Isolation Pattern]]

## God Nodes (most connected - your core abstractions)
1. `ADR-001 Four-Layer Architecture` - 21 edges
2. `Section 2 — Conceptual Model` - 21 edges
3. `R3.5 — Make every service real` - 21 edges
4. `04. Services Reference (hub)` - 20 edges
5. `Test Strategy` - 19 edges
6. `knowledge-retriever-service` - 19 edges
7. `ADR-007 BYOM with Three Protocol Shapes for v1` - 18 edges
8. `Section 2 — Conceptual Model` - 18 edges
9. `Glossary` - 18 edges
10. `test-author` - 17 edges

## Surprising Connections (you probably didn't know these)
- `Claude Code setup (11-agent team)` --conceptually_related_to--> `role_for() title-tag role mapping`  [INFERRED]
  meta/tooling-and-integration-map.md → operations/fleet_keeper.py
- `04. Services Reference (hub)` --references--> `build_kb_index.py — KB index generator`  [INFERRED]
  services-reference/index.md → scripts/build_kb_index.py
- `PaperClip master board` --semantically_similar_to--> `Coordination layer: work-breakdown hierarchy + cross-cutting agreement protocol`  [INFERRED] [semantically similar]
  adr/ADR-014-repo-canonical-knowledge-base.md → architecture/architecture-revision-history.md
- `RLS backstop preconditions (NOSUPERUSER/NOBYPASSRLS, GUC lifetime)` --semantically_similar_to--> `Foundational security principles (S1-S4: defence-in-depth, fail-closed, untrusted input, provenance)`  [INFERRED] [semantically similar]
  adr/adr-012-substrate-tenancy-enforcement-seam-and-rls-backstop-preconditions.md → architecture/section-65-security-threats-and-mitigations.md
- `Harness as the actor (descriptor-led behaviour)` --semantically_similar_to--> `OHM document structure (8 top-level sections)`  [INFERRED] [semantically similar]
  adr/adr-003-platform-as-code-actors-as-harnesses.md → architecture/ohm-v1.0-standalone-specification.md

## Communities

### Community 0 - "Section 2 — Conceptual Model"
Cohesion: 0.02
Nodes (157): ADR-001 — Four-Layer Architecture, ADR-002 — OHM as Canonical Manifest Format, ADR-004 — Federation via ReBAC, ADR-006 — Organisation as Outermost Tenancy Unit, ADR-007 — BYOM with Three Protocol Shapes, ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty, ADR-009 — Metering at Substrate, Billing as Separable, Audit Evidence and Records (+149 more)

### Community 1 - "ADR-001 Four-Layer Architecture"
Cohesion: 0.02
Nodes (154): Application Gateway layer, Application Gateway layer, Capability Registry layer, Capability Registry layer, Strict downward-only layer dependency rule, ADR-001 Four-Layer Architecture, Harness Runtime layer, Harness Runtime layer (+146 more)

### Community 2 - "Test Strategy"
Cohesion: 0.03
Nodes (147): be-test-reviewer Addition (28 May 2026), Agent and Skill Change Log, Enforcement Program ORAA-250 (rev14), Flow Hardening v2 (ORAA-208, rev12), Governance Surface-Sync Discipline, Hollowness Audit, Material Agent-Team Change, R2→R3 Seam Hardening (+139 more)

### Community 3 - "Section 2 — Conceptual Model"
Cohesion: 0.03
Nodes (108): Agent Team Roster, security-architect (role), test-author (role), Rationale: Test-Author-First (ADR-010), Audit Evidence and Records, Compliance Posture Overview, Rationale: Provenance is Evidence / Architectural Controls over Policy, Unified Control Framework (ISO + SOC 2) (+100 more)

### Community 4 - "R5 — Execution Engine and Runtime Comp"
Cohesion: 0.03
Nodes (102): Agent Owner Custom Field (Group E), Build State — Group D Follow-up (3) CLOSED, Actor Dispatch (agents + humans), LLM Client Factory (three protocol shapes, ADR-007), Policy Envelope Enforcement, harness-runtime-service (reference), NodeResult Envelope (uniform retrieval), ReBAC-Gated Retrieval + effective_graph_ids (+94 more)

### Community 5 - "R3.5 — Make every service real"
Cohesion: 0.04
Nodes (82): application-gateway-service, Chat APIs / Chat Persistence, Why consolidate public surfaces (single security boundary), MCP Client, MCP Server, Published Agents and Integration Keys, Rate Limiting per Integration Key, application-gateway-service (Layer 4, port 8007) (+74 more)

### Community 6 - "09. Releases hub"
Cohesion: 0.04
Nodes (75): Eleven release pages (R0-R8, RC), Build State — Group D follow-up (3) — CLOSED, Agent Identity Convention Section 11 inserts, Architecture v1.1 LOCKED (27 May 2026), Change Log, Material Change (what gets logged), Deployment — Cloud-hosted, Configuration philosophy (safe defaults, one way, explicit secrets) (+67 more)

### Community 7 - "Cross-cutting agreement protocol"
Cohesion: 0.04
Nodes (70): Boundary enforcement: contract test / shared fixture (not Done until it exists), Canonical home per shape kind (Interface Contracts / OHM Spec / Governance Taxonomy / ADR), Contract Flow (Tier 2, six steps), Contract Jira issue type (between Epic and Story), Cross-cutting agreement protocol, Enforcement at the Boundary (CI contract test), Governing principle: record once, link many, Three Tiers of Agreement (+62 more)

### Community 8 - "Frontend Stack Reference"
Cohesion: 0.07
Nodes (52): Component Conventions, Accessibility minimums (keyboard-reachable, labels, focus, aria-live), Boundary discipline (data vs render; no business logic in components), Component shape (function components, named exports, typed props), Compound Component Patterns, Component Conventions, File/folder structure (ui, domain, features, pages, lib, hooks, api), File and Folder Structure (+44 more)

### Community 9 - "Glossary"
Cohesion: 0.07
Nodes (47): Change Log, Architecture v1.1 LOCKED, Initial KB structure (27 May 2026), Cloud operational posture (org isolation, per-org KMS, audited access), Configuration Reference, Configuration Philosophy, How to write an ADR, How to update an architecture page (+39 more)

### Community 10 - "build_kb_index.py"
Cohesion: 0.16
Nodes (26): build_outputs(), check_outputs(), count_md_files(), derive_title_from_section(), first_summary(), index_rel(), _is_prose(), main() (+18 more)

### Community 11 - "application-gateway-service"
Cohesion: 0.07
Nodes (29): application-gateway-service, Why consolidate public surfaces (single security boundary), auth-service, capability_pack (bundling artifact), The Five Capability Kinds, capability-registry-service, ADR-001 Four-Layer Architecture, ADR Registry / Hub (+21 more)

### Community 12 - "knowledge-retriever-service"
Cohesion: 0.11
Nodes (20): ADR-001 (Four-Layer Architecture), ADR-022 (recipe / primitive / unified-graph model), application-gateway-service, auth-service, Chat Retrieval, Full-text Search (Lucene-style), Graph Traversal (Cypher, ReBAC-bounded), Hybrid Search (vector + full-text rerank) (+12 more)

### Community 13 - "main()"
Cohesion: 0.4
Nodes (9): api(), hours_since(), listy(), main(), paperclip_bin(), Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash, Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an, role_for() (+1 more)

### Community 14 - "tools/lint/check_no_stubs.py (HOL001-0"
Cohesion: 0.22
Nodes (11): tools/lint/check_no_stubs.py (HOL001-005), tools/lint/check_service_structure.py (STR001-005), Service Architecture Standard, tools/audit/hollowness_audit.py (read-only true-completion map), Per-service importlinter layers contracts (routes->services->domain->repositories->core), r3_5_gate CI job (structure-lint + docker + integration + smoke), Rationale: R2/R3 decomposed into hollow shells; adopt proven legacy layout, Required service layout (routes/services/domain/repositories/schema/core) (+3 more)

### Community 15 - "Docs Process & Deployment"
Cohesion: 0.5
Nodes (4): Docs Process & Deployment, Deployment Topology, Documentation Conventions, Glossary

### Community 16 - "Engineering Flows & Board"
Cohesion: 0.5
Nodes (4): be-test-reviewer persona, Engineering Flows & Board, Jira Board and Workflow Mapping, Session Topology and Persona Residency

### Community 17 - "build_kb_index.py"
Cohesion: 0.5
Nodes (4): build_kb_index.py, KB Index Generator (code), KB Retrieval Tooling, Git pre-commit Hook (index regeneration)

### Community 18 - "build_kb_index.py (index.md + llms.txt"
Cohesion: 1.0
Nodes (3): build_kb_index.py (index.md + llms.txt generator), Git pre-commit Hook (index regeneration), scripts/ README (KB retrieval tooling)

### Community 19 - "Frontend & Design System"
Cohesion: 0.67
Nodes (3): Frontend & Design System, Design System, Frontend Stack Reference

### Community 20 - "TDD & KB Canonicalisation"
Cohesion: 0.67
Nodes (3): ADR-010 TDD with Test-Author Agent, ADR-014 Repo-canonical Knowledge Base, TDD & KB Canonicalisation

### Community 21 - "be-test-reviewer persona"
Cohesion: 1.0
Nodes (2): be-test-reviewer persona, How dual residency was avoided

### Community 22 - "auth-service"
Cohesion: 1.0
Nodes (1): auth-service

### Community 23 - "credential-broker-service"
Cohesion: 1.0
Nodes (1): credential-broker-service

### Community 24 - "Multi-tenant Isolation Pattern"
Cohesion: 1.0
Nodes (1): Multi-tenant Isolation Pattern

### Community 25 - "Cypher Injection Prevention"
Cohesion: 1.0
Nodes (1): Cypher Injection Prevention

### Community 26 - "AgentExecutor (powers sync and durable"
Cohesion: 1.0
Nodes (1): AgentExecutor (powers sync and durable)

### Community 27 - "Cypher Injection Prevention"
Cohesion: 1.0
Nodes (1): Cypher Injection Prevention

### Community 28 - "Multi-tenant Isolation Pattern"
Cohesion: 1.0
Nodes (1): Multi-tenant Isolation Pattern

## Knowledge Gaps
- **416 isolated node(s):** `Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash`, `Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an`, `Knowledge Space Structure (01-08 sections)`, `Confluence OP one-way downstream mirror`, `docs-writer sole-writer rule` (+411 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `be-test-reviewer persona`** (2 nodes): `be-test-reviewer persona`, `How dual residency was avoided`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `auth-service`** (1 nodes): `auth-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `credential-broker-service`** (1 nodes): `credential-broker-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Multi-tenant Isolation Pattern`** (1 nodes): `Multi-tenant Isolation Pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cypher Injection Prevention`** (1 nodes): `Cypher Injection Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `AgentExecutor (powers sync and durable`** (1 nodes): `AgentExecutor (powers sync and durable)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cypher Injection Prevention`** (1 nodes): `Cypher Injection Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Multi-tenant Isolation Pattern`** (1 nodes): `Multi-tenant Isolation Pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Test Strategy` connect `Test Strategy` to `Frontend Stack Reference`, `tools/lint/check_no_stubs.py (HOL001-0`, `Cross-cutting agreement protocol`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `Testing Approach (Frontend)` connect `Frontend Stack Reference` to `Test Strategy`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `Cross-cutting agreement protocol` connect `Cross-cutting agreement protocol` to `Test Strategy`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **What connects `Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash`, `Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an`, `Knowledge Space Structure (01-08 sections)` to the rest of the system?**
  _416 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Section 2 — Conceptual Model` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `ADR-001 Four-Layer Architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `Test Strategy` be split into smaller, more focused modules?**
  _Cohesion score 0.03 - nodes in this community are weakly interconnected._