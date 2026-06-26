# Graph Report - /private/tmp/claude-501/-Users-reza-workspace-OraclousAI-oraclous-backend/4a02db10-2aed-4711-8530-c9e99a5d3358/scratchpad/kb-wt-adr043  (2026-06-26)

## Corpus Check
- 2 files · ~364,006 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1178 nodes · 1830 edges · 34 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 136 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]

## God Nodes (most connected - your core abstractions)
1. `R3.5 — Make every service real (Released)` - 22 edges
2. `ADR-001 Four-Layer Architecture` - 21 edges
3. `Section 2 — Conceptual Model` - 21 edges
4. `R3.5 — Make every service real` - 21 edges
5. `Test Strategy` - 19 edges
6. `04. Services Reference (hub)` - 19 edges
7. `knowledge-retriever-service` - 19 edges
8. `ADR-007 BYOM with Three Protocol Shapes for v1` - 18 edges
9. `Section 2 — Conceptual Model` - 18 edges
10. `Glossary` - 18 edges

## Surprising Connections (you probably didn't know these)
- `PaperClip master board` --semantically_similar_to--> `Coordination layer: work-breakdown hierarchy + cross-cutting agreement protocol`  [INFERRED] [semantically similar]
  adr/ADR-014-repo-canonical-knowledge-base.md → architecture/architecture-revision-history.md
- `RLS backstop preconditions (NOSUPERUSER/NOBYPASSRLS, GUC lifetime)` --semantically_similar_to--> `Foundational security principles (S1-S4: defence-in-depth, fail-closed, untrusted input, provenance)`  [INFERRED] [semantically similar]
  adr/adr-012-substrate-tenancy-enforcement-seam-and-rls-backstop-preconditions.md → architecture/section-65-security-threats-and-mitigations.md
- `Harness as the actor (descriptor-led behaviour)` --semantically_similar_to--> `OHM document structure (8 top-level sections)`  [INFERRED] [semantically similar]
  adr/adr-003-platform-as-code-actors-as-harnesses.md → architecture/ohm-v1.0-standalone-specification.md
- `Frontend is a gateway-only consumer (never talks to internal services)` --conceptually_related_to--> `Gateway-only public exposure`  [INFERRED]
  frontend/index.md → operations/deployment-topology.md
- `Voice and Copy conventions` --semantically_similar_to--> `Writing Principles`  [INFERRED] [semantically similar]
  frontend/design-system.md → meta/documentation-conventions.md

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (157): ADR-001 — Four-Layer Architecture, ADR-002 — OHM as Canonical Manifest Format, ADR-004 — Federation via ReBAC, ADR-006 — Organisation as Outermost Tenancy Unit, ADR-007 — BYOM with Three Protocol Shapes, ADR-008 — Cloud-Hosted Mode with Equivalent Data Sovereignty, ADR-009 — Metering at Substrate, Billing as Separable, Audit Evidence and Records (+149 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (154): Application Gateway layer, Application Gateway layer, Capability Registry layer, Capability Registry layer, Strict downward-only layer dependency rule, ADR-001 Four-Layer Architecture, Harness Runtime layer, Harness Runtime layer (+146 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (148): be-test-reviewer Addition (28 May 2026), Agent and Skill Change Log, Enforcement Program ORAA-250 (rev14), Flow Hardening v2 (ORAA-208, rev12), Governance Surface-Sync Discipline, Hollowness Audit, Material Agent-Team Change, R2→R3 Seam Hardening (+140 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (110): Agent Team Roster, security-architect (role), test-author (role), Rationale: Test-Author-First (ADR-010), Audit Evidence and Records, Compliance Posture Overview, Rationale: Provenance is Evidence / Architectural Controls over Policy, Unified Control Framework (ISO + SOC 2) (+102 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (108): Agent Owner Custom Field (Group E), Build State — Group D Follow-up (3) CLOSED, Actor Dispatch (agents + humans), LLM Client Factory (three protocol shapes, ADR-007), Policy Envelope Enforcement, harness-runtime-service (reference), Incident Response, Blameless post-mortem process (+100 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (80): application-gateway-service, Chat APIs / Chat Persistence, Why consolidate public surfaces (single security boundary), MCP Client, MCP Server, Published Agents and Integration Keys, Rate Limiting per Integration Key, application-gateway-service (Layer 4, port 8007) (+72 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (66): Eleven release pages (R0-R8, RC), Build State — Group D follow-up (3) — CLOSED, Agent Identity Convention Section 11 inserts, Architecture v1.1 LOCKED (27 May 2026), Change Log, Material Change (what gets logged), Deployment — Cloud-hosted, Configuration philosophy (safe defaults, one way, explicit secrets) (+58 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (59): Boundary enforcement: contract test / shared fixture (not Done until it exists), Canonical home per shape kind (Interface Contracts / OHM Spec / Governance Taxonomy / ADR), Contract Flow (Tier 2, six steps), Contract Jira issue type (between Epic and Story), Cross-cutting agreement protocol, Enforcement at the Boundary (CI contract test), Governing principle: record once, link many, Three Tiers of Agreement (+51 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (58): ADR-004 Federation via ReBAC Traversal, ADR-006 Organisation as Outermost Tenancy Unit, ADR-007 BYOM with Three Protocol Shapes, ADR-008 Cloud-Hosted Mode / KMS posture, ADR-015 Gateway Incremental Contract and Versioning, ADR-016 Canonical Service Architecture + Hardened DoD, ADR-017 Identity/Org Service Split (superseded by as-built), ADR-017 core boundary fix (orgs leave the graph service) (+50 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (57): Change Log, Architecture v1.1 LOCKED, Initial KB structure (27 May 2026), Cloud operational posture (org isolation, per-org KMS, audited access), Configuration Reference, Configuration Philosophy, How to write an ADR, How to update an architecture page (+49 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (51): Component Conventions, Accessibility minimums (keyboard-reachable, labels, focus, aria-live), Boundary discipline (data vs render; no business logic in components), Component shape (function components, named exports, typed props), Compound Component Patterns, Component Conventions, File/folder structure (ui, domain, features, pages, lib, hooks, api), File and Folder Structure (+43 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (25): build_outputs(), check_outputs(), count_md_files(), derive_title_from_section(), first_summary(), _is_prose(), main(), _normalise_summary() (+17 more)

### Community 12 - "Community 12"
Cohesion: 0.07
Nodes (27): application-gateway-service, Why consolidate public surfaces (single security boundary), auth-service, capability_pack (bundling artifact), five capability kinds (tool/skill/agent/harness/human_role), capability-registry-service, ADR-001 Four-Layer Architecture, ADR Registry / Hub (+19 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (20): ADR-001 (Four-Layer Architecture), ADR-022 (recipe / primitive / unified-graph model), application-gateway-service, auth-service, Chat Retrieval, Full-text Search (Lucene-style), Graph Traversal (Cypher, ReBAC-bounded), Hybrid Search (vector + full-text rerank) (+12 more)

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (11): gh(), hours_since(), labels_of(), list_issues(), main(), milestone_of(), Move an issue to the ready/queued state: drop `blocked`/`backlog`, add `ready`., Run a `gh` CLI command and return stdout (JSON parsed when the output is JSON). (+3 more)

### Community 15 - "Community 15"
Cohesion: 0.22
Nodes (11): tools/lint/check_no_stubs.py (HOL001-005), tools/lint/check_service_structure.py (STR001-005), Service Architecture Standard, tools/audit/hollowness_audit.py (read-only true-completion map), Per-service importlinter layers contracts (routes->services->domain->repositories->core), r3_5_gate CI job (structure-lint + docker + integration + smoke), Rationale: R2/R3 decomposed into hollow shells; adopt proven legacy layout, Required service layout (routes/services/domain/repositories/schema/core) (+3 more)

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (4): Docs Process & Deployment, Deployment Topology, Documentation Conventions, Glossary

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (4): be-test-reviewer persona, Engineering Flows & Board, Jira Board and Workflow Mapping, Session Topology and Persona Residency

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (3): build_kb_index.py (index.md + llms.txt generator), Git pre-commit Hook (index regeneration), scripts/ README (KB retrieval tooling)

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (3): Frontend & Design System, Design System, Frontend Stack Reference

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (3): ADR-010 TDD with Test-Author Agent, ADR-014 Repo-canonical Knowledge Base, TDD & KB Canonicalisation

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (2): be-test-reviewer persona, How dual residency was avoided

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (2): KB Retrieval Tooling, Git pre-commit Hook (index regeneration)

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): auth-service

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): credential-broker-service

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Multi-tenant Isolation Pattern

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Cypher Injection Prevention

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): AgentExecutor (powers sync and durable)

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Cypher Injection Prevention

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): KB Index Generator (code)

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): Multi-tenant Isolation Pattern

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): scripts/ tooling README

## Ambiguous Edges - Review These
- `auth-service (single identity authority)` → `ADR-017 Identity/Org Service Split (superseded by as-built)`  [AMBIGUOUS]
  adr/index.md · relation: supersedes

## Knowledge Gaps
- **444 isolated node(s):** `Run a `gh` CLI command and return stdout (JSON parsed when the output is JSON).`, `All open issues with the fields we need.`, `Move an issue to the ready/queued state: drop `blocked`/`backlog`, add `ready`.`, `Return (frontmatter_lines, body_lines).      Frontmatter is a leading ``---`` ..`, `Extract ``title`` from frontmatter lines via regex, else return fallback.` (+439 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 21`** (2 nodes): `be-test-reviewer persona`, `How dual residency was avoided`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (2 nodes): `KB Retrieval Tooling`, `Git pre-commit Hook (index regeneration)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `auth-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `credential-broker-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Multi-tenant Isolation Pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Cypher Injection Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `AgentExecutor (powers sync and durable)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Cypher Injection Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `KB Index Generator (code)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `Multi-tenant Isolation Pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `scripts/ tooling README`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `auth-service (single identity authority)` and `ADR-017 Identity/Org Service Split (superseded by as-built)`?**
  _Edge tagged AMBIGUOUS (relation: supersedes) - confidence is low._
- **Why does `Test Strategy` connect `Community 2` to `Community 10`, `Community 7`, `Community 15`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `Cross-cutting agreement protocol` connect `Community 7` to `Community 2`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `Provenance-is-primary philosophy` connect `Community 4` to `Community 9`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **What connects `Run a `gh` CLI command and return stdout (JSON parsed when the output is JSON).`, `All open issues with the fields we need.`, `Move an issue to the ready/queued state: drop `blocked`/`backlog`, add `ready`.` to the rest of the system?**
  _444 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.02 - nodes in this community are weakly interconnected._