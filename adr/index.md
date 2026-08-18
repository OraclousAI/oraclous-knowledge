---
confluence_id: "589826"
title: "02. ADRs — Architecture Decision Records"
---

# 02. ADRs — Architecture Decision Records

This hub indexes every Architecture Decision Record for the Oraclous Platform. Each ADR captures a single material decision with its context, the decision itself, and the consequences. ADRs supersede the architecture document where they are newer and explicitly named as superseding; otherwise the architecture document is canonical.

## ADR registry

| ID | Title | Status | Date |
| --- | --- | --- | --- |
| ADR-001 | [Four-Layer Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) | Accepted | 2026-05-27 |
| ADR-002 | [OHM as Canonical Manifest Format](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) | Accepted | 2026-05-27 |
| ADR-003 | [Platform-as-Code, Actors-as-Harnesses](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884737) | Accepted | 2026-05-27 |
| ADR-004 | [Federation via ReBAC Traversal](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131083) | Accepted | 2026-05-27 |
| ADR-005 | [Workflow Concept Retirement; Harness as Replacement](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753772) | Accepted | 2026-05-27 |
| ADR-006 | [Organisation as Outermost Tenancy Unit](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) | Accepted | 2026-05-27 |
| ADR-007 | [BYOM with Three Protocol Shapes for v1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920) | Accepted | 2026-05-27 |
| ADR-008 | [Cloud-Hosted Mode with Equivalent Data Sovereignty](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753792) | Accepted | 2026-05-27 |
| ADR-009 | [Metering at Substrate, Billing as Separable](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393423) | Accepted | 2026-05-27 |
| ADR-010 | [Test-Driven Development with Test-Author Agent](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557078) | Accepted | 2026-05-27 |
| ADR-011 | [External Jira and Confluence (Not Local Wiki)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393443) | <custom data-type="status" data-id="id-0">Superseded by ADR-014</custom> | 2026-05-27 |
| ADR-012 | [Substrate Tenancy Enforcement Seam and RLS Backstop Preconditions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) | <custom data-type="status" data-id="id-1">Proposed</custom> | 2026-05-29 |
| ADR-013 | [Fail-Closed Authority Placement at the Substrate ReBAC Seam](https://oraclous.atlassian.net/wiki/spaces/OP/pages/3702787) | Accepted | 2026-05-31 |
| ADR-014 | [Repo-canonical knowledge base; Confluence as mirror; GitHub Issues + PRs as master board](https://oraclous.atlassian.net/wiki/spaces/OP/pages/4685826) | <custom data-type="status" data-id="id-2">Accepted</custom> | 2026-05-31 |
| ADR-015 | [Gateway Incremental Contract and Versioning (R5→R8)](adr-015-gateway-incremental-contract-and-versioning.md) | Accepted | 2026-06-01 (accepted 2026-06-08) |
| ADR-016 | [Canonical Service-Internal Architecture and Hardened Definition of Done (No Hollow Services)](adr-016-canonical-service-architecture-and-hardened-definition-of-done.md) | Accepted | 2026-06-04 |
| ADR-017 | [Identity/Org Service Split](adr-017-identity-org-service-split.md) | Superseded by as-built (R3.5 — identity consolidated into auth-service) | 2026-06-04 |
| ADR-018 | [Edge Authentication (Trusted Gateway) — single auth boundary; services trust forwarded identity + X-Internal-Key](adr-018-edge-authentication-trusted-gateway.md) | Accepted | 2026-06-05 |
| ADR-019 | [R6 Gateway: dedicated datastore + integration-key authorization floor](adr-019-r6-gateway-datastore-and-integration-key-authz-floor.md) | Accepted | 2026-06-08 |
| ADR-020 | [Per-Org Envelope Encryption with a KMS-Held KEK (extends ADR-008; R7-SEC S5)](adr-020-per-org-envelope-encryption-kms-held-kek.md) | Accepted | 2026-06-10 |
| ADR-021 | [Fail-Closed Operational Defaults and a Shared Degradation-Alert Seam (extends ADR-013; epic #292)](adr-021-fail-closed-operational-defaults-and-degradation-alert-seam.md) | Accepted | 2026-06-12 |
| ADR-022 | [Concern-Driven Ingestion — Recipes, Primitives, Unified Source→Structure→Entity Model](adr-022-recipe-primitive-unified-graph-ingestion.md) | Accepted (ported) | 2026-06-04 |
| ADR-023 | [Community Detection via In-DB Neo4j GDS Louvain (Community Edition) (epic #294 / #303)](adr-023-community-detection-in-db-gds-louvain.md) | Accepted | 2026-06-12 |
| ADR-024 | [Graph Versioning & Rollback — Deferred Pending a Write-Path Soft-Invalidation Prerequisite (epic #294 / #304)](adr-024-graph-versioning-rollback-deferred.md) | Deferred | 2026-06-12 |
| ADR-025 | [SQL Database Connector: Egress and Credential Posture (epic #294 / #307)](adr-025-sql-connector-egress-and-credential-posture.md) | Accepted | 2026-06-12 |
| ADR-026 | [Federated Cross-Graph Query: an Aggregator over Already-Accessible Graphs (epic #312 / #330)](adr-026-federated-cross-graph-query.md) | Accepted | 2026-06-12 |
| ADR-027 | [Agent Memory: a Complete Ebbinghaus Store with a Fail-Soft Harness Write Path and Tool-Based Recall (epic #312 / #332)](adr-027-agent-memory-ebbinghaus-store.md) | Accepted | 2026-06-12 |
| ADR-028 | [Recipe Draft → Promote Lifecycle (a stored recipe is a draft until promoted)](adr-028-recipe-draft-promote-lifecycle.md) | Accepted | 2026-06-14 |
| ADR-029 | [Workspace↔Harness Binding (a curation edge in the capability registry, not a manifest field) (epic #121 / FE #127 / Contract G2)](adr-029-workspace-harness-binding.md) | Accepted | 2026-06-16 |
| ADR-030 | [Realize the Postgres RLS Backstop (per-service policies + async GUC seam + non-bypassing role) (grade-A WP-5 / epic oraclous-backend#353)](adr-030-realize-postgres-rls-backstop.md) | Accepted | 2026-06-17 |
| ADR-031 | [OHM v1.1 Team Manifest (Team Harness) (R7 product-loop / epic oraclous-backend#382)](adr-031-ohm-v1.1-team-manifest.md) | Accepted | 2026-06-19 |
| ADR-032 | [Capability-Absence as a Structural Gate (R7 product-loop / epic oraclous-backend#382)](adr-032-capability-absence-structural-gate.md) | Accepted | 2026-06-19 |
| ADR-033 | [Orchestrator Capabilities Status (ADR-005 L77) and Original-Primitive Retirement (R7 product-loop / epic oraclous-backend#382)](adr-033-orchestrator-capabilities-status-and-retirement.md) | Accepted | 2026-06-19 |
| ADR-034 | [Adoption-First: import an existing agent setup to a runnable OHM v1.1 Team Harness without re-authoring (R7 product-loop / epic oraclous-backend#383)](adr-034-adoption-first-import.md) | Accepted | 2026-06-20 |
| ADR-035 | [Coordination Control & Media: the team runtime spine — orchestrators + fan-in barrier + hand-off envelope + media taxonomy + dispatch-time ceiling (R7 product-loop / epic oraclous-backend#384)](adr-035-coordination-control-and-media.md) | Accepted | 2026-06-20 |
| ADR-036 | [Cross-Org Foreign-Row Read under a Fail-Closed ReBAC Read Grant — completes the #446 federation gate; amends ADR-026/ADR-004 (E7-SEC / issue oraclous-backend#446)](adr-036-cross-org-foreign-row-read-under-rebac-grant.md) | Accepted | 2026-06-20 |
| ADR-037 | [Flow-Level Evaluation, Named Gate Batteries, and Run-Tree Correlation — the E4 contract for core/evaluate + named batteries + trace_id/parent_execution_id + the re-dispatch policy boundary (R7 E4 / epic oraclous-backend#385, issue #468)](adr-037-flow-level-evaluation-named-batteries-run-tree.md) | Accepted | 2026-06-21 |
| ADR-038 | [Tool & Data Adoption Primitives (E5) — script-as-scheduled-ingestion + library-as-tool-group + connector/MCP adoption as first-class registry citizens bound to the deny-by-default capability ceiling; the E5 chain-starter (R7 E5 / epic oraclous-backend#386, issue #484)](adr-038-tool-data-adoption-primitives.md) | Accepted | 2026-06-21 |
| ADR-039 | [Batteries-Included Registry + O1 Secret Onboarding (E5) — the curated credential-ready tool set (web-research battery + starter connectors + scheduler + delivery sink) seeded via plugin_sync, and the paste-once per-org secret-onboarding contract with no auth-prompt wall (R7 E5 / epic oraclous-backend#386, issue #485)](adr-039-batteries-included-registry-o1-secret-onboarding.md) | Accepted | 2026-06-21 |
| ADR-040 | [Dual Coordination Substrate + Hierarchy-of-Truth Adoption (E6) — file-native git-markdown vs graph-adopt as peer blackboard substrates (the source decides), the adopted precedence/Hierarchy-of-Truth with the derived CONTRADICTS index disposable and graph-as-truth a mode not the default, and the source-format deliver-back sink contract; amends ADR-027/ADR-022 (R7 E6 / epic oraclous-backend#387, issue #511)](adr-040-dual-coordination-substrate-hierarchy-of-truth.md) | Accepted | 2026-06-24 |
| ADR-041 | [Artifacts Live on Oraclous; Storage Sinks are Pluggable Connected Tools; the Graph is the Universal Index (E6) — a team's artifacts live on Oraclous by default (the platform is the home, not a passthrough); storage destinations are pluggable connected tools/connectors/MCPs bound at team creation (the github-sink is one sink, deliver-back is not special); the graph is the always-on universal index so agents retain visibility regardless of where bytes physically live; extends ADR-040 from inputs to outputs (R7 E6 / epic oraclous-backend#387)](adr-041-artifact-home-pluggable-sinks-graph-index.md) | Accepted | 2026-06-25 |
| ADR-042 | [Team-Run Completion: Per-Member Status + Re-run-from-Checkpoint (amends ADR-035) — each member run has its own status (`SUCCEEDED`/`FAILED`/…) + a durable checkpoint; a failed member is re-run from its checkpoint (succeeded members preserved + not re-run, blocked downstream dependents re-run, independent members untouched); a team run is `SUCCEEDED` only when EVERY member delivered — never a head-count, and no partial-success that masks a missing piece; recovery is re-run, not tolerance; replaces ADR-035's strict fail-closed team-run completion state (R7 E6 / oraclous-backend#551, gates #549)](adr-042-dependency-aware-team-run-verdict.md) | Accepted | 2026-06-26 |
| ADR-043 | [Conductor for Cyclic Imported Teams + Flow-6 Consciousness Learn Loop (builds on ADR-042 + ADR-027; amends ADR-035) — a cyclic imported team converges via a deterministic skeleton + a bounded coordinator seam at each Tarjan-SCC-isolated loop, governed by coded termination (coverage-floor + landed-artifacts + a separate-evaluator grade) and four runaway bounds (rounds/wall-clock/cost/no-progress); a bounded within-run recalibration loop gets a stalled team unstuck (closed action set, external-signal-driven, never self-grade, hard-capped); and the cross-run Flow-6 consciousness Learn loop over the shipped ADR-027 Ebbinghaus memory makes performance compound (consult-before-turn + five-family write + `consciousness.permissions` gating + a compounding proof); invariant — the team never satisfies its own done-check (R7 E3+E6 / oraclous-backend#552)](adr-043-conductor-imported-teams-and-consciousness.md) | Accepted | 2026-06-26 |
| ADR-051 | [Workspace Listing Matches the Org-Scoped Read Gate; the Access Ladder Is Not Yet Implemented — the workspace list widens to the read gate it already grants, mutation stays owner/admin-scoped, and it is recorded plainly that no per-workspace member set exists, so every graph in an organisation is readable by every member (UC-D1 PoC / oraclous-backend#734, §5.3 capability 27)](adr-051-workspace-list-matches-the-org-scoped-read-gate.md) | Accepted — Realized 2026-08-10 (#736) | 2026-08-08 |
| ADR-052 | [An App-Descriptor Layer Maps a Generated App's Shape onto a Team Run's Inputs — a separate descriptor (not the OHM run manifest) declares an app's own input/output shape and its mapping onto the run's declared `inputs`; "this input is a hypothesis, not a premise" becomes a general platform concept; the validation desk ships a one-off field now and migrates later (Contract oraclous-backend#845, first consumer #846)](adr-052-app-descriptor-layer-for-generated-apps.md) | Proposed | 2026-08-18 |

> **Table gap (2026-08-08).** Rows for **ADR-044 – ADR-050** are missing from this table; their files exist in this directory and are canonical. Backfilling them is a `docs-writer` job, deliberately not folded into the ADR-051 change.

> **ADR-022** is **ported from the legacy `develop` branch @ `84152635de05c105765cfe6b631bb5ba81f2f4aa` (TASK-237)** and kept at its **original legacy number** for traceability to the binding spec. It is the binding ingestion specification for the R3.5 knowledge-graph-service (service #1). The next NEW number is **ADR-053** (ADR-031–052 taken; ADR-052 app-descriptor layer for generated apps, Proposed 2026-08-18; 022 is the ported legacy ADR).

## ADR conventions

* **One decision per ADR.** If a decision is compound, it gets split into multiple ADRs that may reference each other.
* **Status lifecycle:** `Proposed` → `Accepted` → optionally `Superseded by ADR-NNN`. Rejected ADRs are kept (as `Rejected`) for the historical record.
* **No silent supersession.** When a new ADR overrides an existing one, the new ADR names it explicitly and the old ADR's status is updated.
* **Numbering is monotonic.** ADR-053 is the next number for NEW decisions (ADR-031–052 taken; ADR-052 app-descriptor layer for generated apps, Proposed); numbers are not reused even if an ADR is rejected. (ADR-022 is a **ported legacy ADR** kept at its original number for traceability.)

## When to write an ADR

Write an ADR when:

* A decision is being made that future contributors will need to understand the reasoning behind
* A decision overrides or refines something in the architecture document
* A decision is contested and the resolution should be recorded so it isn't re-litigated
* A decision is non-obvious in retrospect — "why did we do it this way?" deserves an answer

Do not write an ADR for:

* Implementation details that follow naturally from an architecture commitment
* Decisions that are fully covered by an existing ADR or architecture section
* Routine engineering choices (library selection, code style) — those belong in Engineering docs, not ADRs

## Template

Every ADR follows the same structure:

* **Status** — Proposed / Accepted / Rejected / Superseded
* **Context** — what situation is being addressed
* **Decision** — what is being decided (with concrete commitments)
* **Consequences** — what changes downstream as a result
* **See also** — related architecture sections, ADRs, or external references
