---
confluence_id: "164260"
title: "R7 — Phase 7: Compiler harness and seed manifests"
---

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
