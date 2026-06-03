# Graph Report - /Users/reza/workspace/OraclousAI/oraclous-knowledge  (2026-06-03)

## Corpus Check
- 117 files · ~173,178 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 556 nodes · 854 edges · 18 communities detected
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.77)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Compliance & Agent Governance|Compliance & Agent Governance]]
- [[_COMMUNITY_Four-Layer Architecture & OHM|Four-Layer Architecture & OHM]]
- [[_COMMUNITY_Agent Skills & Consciousness|Agent Skills & Consciousness]]
- [[_COMMUNITY_Harness Runtime & Retrieval|Harness Runtime & Retrieval]]
- [[_COMMUNITY_Application Gateway & Auth|Application Gateway & Auth]]
- [[_COMMUNITY_Docs Process & Deployment|Docs Process & Deployment]]
- [[_COMMUNITY_Releases & Build State|Releases & Build State]]
- [[_COMMUNITY_Frontend & Design System|Frontend & Design System]]
- [[_COMMUNITY_KB Index Generator (code)|KB Index Generator (code)]]
- [[_COMMUNITY_Engineering Flows & Board|Engineering Flows & Board]]
- [[_COMMUNITY_TDD & KB Canonicalisation|TDD & KB Canonicalisation]]
- [[_COMMUNITY_KB Retrieval Tooling|KB Retrieval Tooling]]
- [[_COMMUNITY_be-test-reviewer Residency|be-test-reviewer Residency]]
- [[_COMMUNITY_auth-service|auth-service]]
- [[_COMMUNITY_credential-broker-service|credential-broker-service]]
- [[_COMMUNITY_Multi-tenant Isolation|Multi-tenant Isolation]]
- [[_COMMUNITY_Cypher Injection Prevention|Cypher Injection Prevention]]
- [[_COMMUNITY_AgentExecutor|AgentExecutor]]

## God Nodes (most connected - your core abstractions)
1. `Section 2 — Conceptual Model` - 21 edges
2. `ADR Registry / Hub (02. ADRs)` - 16 edges
3. `capability-registry-service` - 16 edges
4. `application-gateway-service` - 16 edges
5. `Section 4 — OHM Manifest Format` - 14 edges
6. `OHM v1.0 Standalone Specification` - 13 edges
7. `Structured Governance Taxonomy` - 13 edges
8. `Agent Index (11 agents + narrow persona)` - 13 edges
9. `ADR-007 BYOM with Three Protocol Shapes` - 12 edges
10. `Structured Threat Catalogue` - 12 edges

## Surprising Connections (you probably didn't know these)
- `PaperClip as master board` --semantically_similar_to--> `Coordination layer: work-breakdown hierarchy + cross-cutting agreement protocol`  [INFERRED] [semantically similar]
  adr/ADR-014-repo-canonical-knowledge-base.md → architecture/architecture-revision-history.md
- `RLS backstop preconditions (NOSUPERUSER/NOBYPASSRLS, GUC lifetime)` --semantically_similar_to--> `Foundational security principles (S1-S4: defence-in-depth, fail-closed, untrusted input, provenance)`  [INFERRED] [semantically similar]
  adr/adr-012-substrate-tenancy-enforcement-seam-and-rls-backstop-preconditions.md → architecture/section-65-security-threats-and-mitigations.md
- `Harness as the actor (descriptor-led behaviour)` --semantically_similar_to--> `OHM document structure (8 top-level sections)`  [INFERRED] [semantically similar]
  adr/adr-003-platform-as-code-actors-as-harnesses.md → architecture/ohm-v1.0-standalone-specification.md
- `Frontend Asymmetry` --conceptually_related_to--> `Frontend as gateway-only consumer`  [INFERRED]
  flows/session-topology-and-persona-residency.md → frontend/index.md
- `Voice and Copy conventions` --semantically_similar_to--> `Writing Principles`  [INFERRED] [semantically similar]
  frontend/design-system.md → meta/documentation-conventions.md

## Hyperedges (group relationships)
- **Four-layer platform stack** — adr001_substrate_layer, adr001_capability_registry_layer, adr001_harness_runtime_layer, adr001_application_gateway_layer [INFERRED 0.90]
- **Substrate tenancy + ReBAC enforcement** — adr006_organisation_id_anchor, adr012_access_seam, adr013_access_decision_client, adr004_federation_rebac, section65_cross_org_leakage [INFERRED 0.85]
- **OHM document governance binding** — ohmspec_ohm_v1_specification, govtax_policy_set, adr007_protocol_shapes, ohmspec_owner_organization_anchor, section65_threat_catalogue [INFERRED 0.80]
- **Four-Layer Architecture** — section_3_layered_architecture_substrate, section_3_layered_architecture_capability_registry, section_3_layered_architecture_runtime_engine, section_3_layered_architecture_application_gateway [INFERRED 0.90]
- **OHM Document Kinds** — section_4_manifest_format_specification_kind_tool, section_4_manifest_format_specification_kind_skill, section_4_manifest_format_specification_kind_agent, section_4_manifest_format_specification_kind_harness, section_4_manifest_format_specification_kind_capability_pack [INFERRED 0.85]
- **Knowledge-Graph-Builder Decomposition** — section_8_consolidation_and_migration_plan_knowledge_graph_builder, section_8_consolidation_and_migration_plan_knowledge_retriever_service, section_8_consolidation_and_migration_plan_harness_runtime_service [INFERRED 0.80]
- **Founding Threat Families T1-T7** — structured_threat_catalogue_t1_data_exfiltration, structured_threat_catalogue_t2_privilege_escalation, structured_threat_catalogue_t5_manifest_tampering, structured_threat_catalogue_t6_operator_separation_breach, structured_threat_catalogue_t7_audit_log_gap [INFERRED 0.85]
- **TDD Workflow Personas and Gates** — test_author_doc, backend_implementer_doc, code_reviewer_doc, qa_engineer_doc, be_test_reviewer_doc, definition_of_done_doc [INFERRED 0.85]
- **Agent Consciousness Loaded by All Personas** — agent_consciousness_for_development_doc, test_author_doc, backend_implementer_doc, frontend_implementer_doc, devops_implementer_doc, code_reviewer_doc, qa_engineer_doc, solution_architect_doc, security_architect_doc, product_planner_doc, docs_writer_doc, be_test_reviewer_doc [EXTRACTED 0.90]
- **Cross-Repo Contract Flow Participants** — cross_cutting_agreement_protocol_contract_flow, solution_architect_doc, security_architect_doc, product_planner_doc, interface_contracts_doc [EXTRACTED 0.90]
- **Work-breakdown flow across hierarchy, board, and sessions** — flows_index_work_breakdown_hierarchy, jira_board_eight_columns, session_topology_persona_residency, session_topology_agent_owner_field [INFERRED 0.85]
- **Frontend stack, conventions, state, and testing form one frontend system** — frontend_stack_reference, component_conventions, state_data_patterns, testing_approach_frontend, design_system [INFERRED 0.80]
- **Three kinds of state map to React Query, Zustand, and useState** — state_data_three_kinds_of_state, frontend_stack_react_query, frontend_stack_zustand [INFERRED 0.90]
- **Phased Service-Decomposition Migration (R0.5→R8)** — r0_5_release_doc, r2_release_doc, r3_release_doc, r4_release_doc, r5_release_doc, r6_release_doc, r7_release_doc, r8_release_doc [INFERRED 0.85]
- **Agent Identity Convention Mechanisms** — releases_agent_owner_field, releases_needs_human_flag, releases_comment_prefix_convention, releases_agent_jira_operations, r7_agent_mcp_server [INFERRED 0.80]
- **T1 Organisation-Isolation Enforcement** — r0_5_organisation_id_scoping, r0_5_isolation_gate, runbook_org_backfill_verification_t1, knowledge_retriever_rebac_gated, r3_role_separation [INFERRED 0.80]
- **Four-Layer Service Topology (ADR-001)** — auth_service_auth_service, knowledge_graph_service_knowledge_graph_service, capability_registry_service_capability_registry_service, execution_engine_service_execution_engine_service, application_gateway_service_application_gateway_service [INFERRED 0.90]
- **Services lifting from oraclous-core-service** — capability_registry_service_capability_registry_service, execution_engine_service_execution_engine_service, application_gateway_service_application_gateway_service [INFERRED 0.85]
- **Cross-service Patterns (tenancy, ReBAC, provenance, capability/credential resolution)** — index_multi_tenant_isolation, index_rebac_checks, index_provenance_write_through, index_capability_resolution_pattern, index_credential_resolution_pattern [INFERRED 0.80]

## Communities

### Community 0 - "Compliance & Agent Governance"
Cohesion: 0.03
Nodes (108): Agent Team Roster, security-architect (role), test-author (role), Rationale: Test-Author-First (ADR-010), Audit Evidence and Records, Compliance Posture Overview, Rationale: Provenance is Evidence / Architectural Controls over Policy, Unified Control Framework (ISO + SOC 2) (+100 more)

### Community 1 - "Four-Layer Architecture & OHM"
Cohesion: 0.05
Nodes (79): Application Gateway layer, Capability Registry layer, ADR-001 Four-Layer Architecture, Harness Runtime layer, Rationale: strict downward-only dependencies for reasoning, Substrate (only stateful layer), ADR-002 OHM as Canonical Manifest Format, Rationale: single-document portability + atomic signing (+71 more)

### Community 2 - "Agent Skills & Consciousness"
Cohesion: 0.05
Nodes (70): be-test-reviewer Addition (28 May 2026), Agent and Skill Change Log, Material Change Definition, Agent Consciousness for Development, No Auto-Apply Without Human Review, Five Pattern Categories, Consciousness Permission Model, Three Scopes of Consciousness (+62 more)

### Community 3 - "Harness Runtime & Retrieval"
Cohesion: 0.04
Nodes (66): Actor Dispatch (agents + humans), LLM Client Factory (three protocol shapes, ADR-007), Policy Envelope Enforcement, harness-runtime-service (reference), NodeResult Envelope (uniform retrieval), ReBAC-Gated Retrieval + effective_graph_ids, knowledge-retriever-service (reference), Critical Paths to Instrument (Compile/Execute/Schedule/Traversal/Retrieval/HITL) (+58 more)

### Community 4 - "Application Gateway & Auth"
Cohesion: 0.06
Nodes (49): application-gateway-service, Chat APIs / Chat Persistence, Why consolidate public surfaces (single security boundary), MCP Client, MCP Server, Published Agents and Integration Keys, Rate Limiting per Integration Key, Webhook Receivers (+41 more)

### Community 5 - "Docs Process & Deployment"
Cohesion: 0.07
Nodes (38): Change Log, Architecture v1.1 LOCKED, Initial KB structure (27 May 2026), Configuration Reference, Configuration Philosophy, How to write an ADR, How to update an architecture page, Contributing to Documentation (+30 more)

### Community 6 - "Releases & Build State"
Cohesion: 0.07
Nodes (37): Agent Owner Custom Field (Group E), Build State — Group D Follow-up (3) CLOSED, Usage-Reporting Aggregation Primitive (HTTP deferred to R6), Architecture v1.1 Locked, Eleven Founding ADRs, R0 — Documentation and Stabilisation, Structured Artifacts (OHM Spec, Governance Taxonomy, Threat Catalogue), MCP Tool Importer (first inbound adapter) (+29 more)

### Community 7 - "Frontend & Design System"
Cohesion: 0.1
Nodes (32): Component Conventions, Accessibility Minimums, Boundary Discipline (data vs render), Compound Component Patterns, File and Folder Structure, Gateway-only public exposure, Design System, Dark-first, dark-only principle (+24 more)

### Community 8 - "KB Index Generator (code)"
Cohesion: 0.12
Nodes (25): build_outputs(), check_outputs(), count_md_files(), derive_title_from_section(), first_summary(), _is_prose(), main(), _normalise_summary() (+17 more)

### Community 9 - "Engineering Flows & Board"
Cohesion: 0.1
Nodes (25): Why flows are coordinator-owned, Cross-cutting Agreement Protocol, 10. Engineering Flows hub, Interface Contracts, Migration Source Map, TDD Pair (tests + impl PR), Work Breakdown Hierarchy, BLOCKED means human action required (+17 more)

### Community 10 - "TDD & KB Canonicalisation"
Cohesion: 0.16
Nodes (14): Rationale: split test/impl to avoid tests-fit-my-code failure, ADR-010 TDD with Test-Author Agent, test-author agent (separate from implementer), Tests Review gate (two-PR workflow), ADR-011 External Jira and Confluence (Superseded), Portability foresight (artifacts survive migration), Rationale: off-the-shelf tooling on day one without bootstrap cost, Confluence OP as one-way downstream mirror (+6 more)

### Community 11 - "KB Retrieval Tooling"
Cohesion: 1.0
Nodes (3): build_kb_index.py (index.md + llms.txt generator), Git pre-commit Hook (index regeneration), scripts/ README (KB retrieval tooling)

### Community 12 - "be-test-reviewer Residency"
Cohesion: 1.0
Nodes (2): be-test-reviewer persona, How dual residency was avoided

### Community 13 - "auth-service"
Cohesion: 1.0
Nodes (1): auth-service

### Community 14 - "credential-broker-service"
Cohesion: 1.0
Nodes (1): credential-broker-service

### Community 15 - "Multi-tenant Isolation"
Cohesion: 1.0
Nodes (1): Multi-tenant Isolation Pattern

### Community 16 - "Cypher Injection Prevention"
Cohesion: 1.0
Nodes (1): Cypher Injection Prevention

### Community 17 - "AgentExecutor"
Cohesion: 1.0
Nodes (1): AgentExecutor (powers sync and durable)

## Knowledge Gaps
- **189 isolated node(s):** `Return (frontmatter_lines, body_lines).      Frontmatter is a leading ``---`` ..`, `Extract ``title`` from frontmatter lines via regex, else return fallback.`, `True when a line is real summary prose, not heading/metadata/markup.`, `Collapse whitespace and strip markdown link syntax to plain text.`, `First non-empty prose paragraph as a normalised one-liner, else fallback.` (+184 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `be-test-reviewer Residency`** (2 nodes): `be-test-reviewer persona`, `How dual residency was avoided`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `auth-service`** (1 nodes): `auth-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `credential-broker-service`** (1 nodes): `credential-broker-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Multi-tenant Isolation`** (1 nodes): `Multi-tenant Isolation Pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cypher Injection Prevention`** (1 nodes): `Cypher Injection Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `AgentExecutor`** (1 nodes): `AgentExecutor (powers sync and durable)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `R2 through R8 and Compliance (aggregate)` connect `Harness Runtime & Retrieval` to `Releases & Build State`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **What connects `Return (frontmatter_lines, body_lines).      Frontmatter is a leading ``---`` ..`, `Extract ``title`` from frontmatter lines via regex, else return fallback.`, `True when a line is real summary prose, not heading/metadata/markup.` to the rest of the system?**
  _189 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Compliance & Agent Governance` be split into smaller, more focused modules?**
  _Cohesion score 0.03 - nodes in this community are weakly interconnected._
- **Should `Four-Layer Architecture & OHM` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `Agent Skills & Consciousness` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `Harness Runtime & Retrieval` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Application Gateway & Auth` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._