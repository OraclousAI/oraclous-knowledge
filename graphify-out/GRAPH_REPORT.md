# Graph Report - /private/tmp/wt-oraa-r35-docs  (2026-06-04)

## Corpus Check
- 2 files · ~240,929 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 566 nodes · 869 edges · 20 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.77)
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

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (93): Application Gateway layer, Capability Registry layer, ADR-001 Four-Layer Architecture, Harness Runtime layer, Rationale: strict downward-only dependencies for reasoning, Substrate (only stateful layer), ADR-002 OHM as Canonical Manifest Format, Rationale: single-document portability + atomic signing (+85 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (72): Actor Dispatch (agents + humans), LLM Client Factory (three protocol shapes, ADR-007), Policy Envelope Enforcement, harness-runtime-service (reference), NodeResult Envelope (uniform retrieval), ReBAC-Gated Retrieval + effective_graph_ids, knowledge-retriever-service (reference), Critical Paths to Instrument (Compile/Execute/Schedule/Traversal/Retrieval/HITL) (+64 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (70): be-test-reviewer Addition (28 May 2026), Agent and Skill Change Log, Material Change Definition, Agent Consciousness for Development, No Auto-Apply Without Human Review, Five Pattern Categories, Consciousness Permission Model, Three Scopes of Consciousness (+62 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (58): Audit Evidence and Records, Compliance Posture Overview, Rationale: Provenance is Evidence / Architectural Controls over Policy, Unified Control Framework (ISO + SOC 2), Customer Trust Resources, 06. Compliance (index), ISO 27001 Programme, Actor (+50 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (50): Agent Team Roster, security-architect (role), test-author (role), Rationale: Test-Author-First (ADR-010), Data Handling and Privacy, Git Workflow, Interface Contracts (mirror), Platform Architecture v1.1 (index) (+42 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (49): application-gateway-service, Chat APIs / Chat Persistence, Why consolidate public surfaces (single security boundary), MCP Client, MCP Server, Published Agents and Integration Keys, Rate Limiting per Integration Key, Webhook Receivers (+41 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (36): Change Log, Architecture v1.1 LOCKED, Initial KB structure (27 May 2026), Configuration Reference, Configuration Philosophy, How to write an ADR, How to update an architecture page, Contributing to Documentation (+28 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (32): Component Conventions, Accessibility Minimums, Boundary Discipline (data vs render), Compound Component Patterns, File and Folder Structure, Gateway-only public exposure, Design System, Dark-first, dark-only principle (+24 more)

### Community 8 - "Community 8"
Cohesion: 0.12
Nodes (25): build_outputs(), check_outputs(), count_md_files(), derive_title_from_section(), first_summary(), _is_prose(), main(), _normalise_summary() (+17 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (27): Why flows are coordinator-owned, Cross-cutting Agreement Protocol, 10. Engineering Flows hub, Interface Contracts, Migration Source Map, TDD Pair (tests + impl PR), Work Breakdown Hierarchy, BYOM (term) (+19 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (17): Agent Owner Custom Field (Group E), Build State — Group D Follow-up (3) CLOSED, Architecture v1.1 Locked, Eleven Founding ADRs, R0 — Documentation and Stabilisation, Structured Artifacts (OHM Spec, Governance Taxonomy, Threat Catalogue), Agent Identity Convention (canonical), Agent Owner Field (customfield_10074, 13 options) (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (14): Monitoring and Observability, Provenance-is-Primary Observability Philosophy, Standard Label Set (service/version/organization_id/workspace_id), Three Signals (Logs, Traces, Metrics), Eight-Service Deployment Topology, 05. Operations (index), Two Deployment Modes (Self-hosted, Cloud-hosted), Substrate-Level Metering (tokens/count/bytes) (+6 more)

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (9): api(), hours_since(), listy(), main(), paperclip_bin(), Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash, Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an, role_for() (+1 more)

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (3): build_kb_index.py (index.md + llms.txt generator), Git pre-commit Hook (index regeneration), scripts/ README (KB retrieval tooling)

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (2): be-test-reviewer persona, How dual residency was avoided

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): auth-service

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): credential-broker-service

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Multi-tenant Isolation Pattern

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Cypher Injection Prevention

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): AgentExecutor (powers sync and durable)

## Knowledge Gaps
- **191 isolated node(s):** `Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash`, `Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an`, `Return (frontmatter_lines, body_lines).      Frontmatter is a leading ``---`` ..`, `Extract ``title`` from frontmatter lines via regex, else return fallback.`, `True when a line is real summary prose, not heading/metadata/markup.` (+186 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (2 nodes): `be-test-reviewer persona`, `How dual residency was avoided`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `auth-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `credential-broker-service`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Multi-tenant Isolation Pattern`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Cypher Injection Prevention`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `AgentExecutor (powers sync and durable)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Section 2 — Conceptual Model` connect `Community 3` to `Community 4`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `Platform Architecture v1.1 (index)` connect `Community 4` to `Community 3`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `R2 through R8 and Compliance (aggregate)` connect `Community 1` to `Community 10`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **What connects `Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash`, `Fire one agent heartbeat (source=assignment) to start its assigned work, fire-an`, `Return (frontmatter_lines, body_lines).      Frontmatter is a leading ``---`` ..` to the rest of the system?**
  _191 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._