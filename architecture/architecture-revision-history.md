---
confluence_id: "426111"
title: "Architecture Revision History"
---

# Architecture Revision History

**Document status:** <custom data-type="status" data-id="id-0">Active</custom> · **Current architecture version:** v1.1 · **Maintained by:** [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) with [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) sign-off

This page is the chronological audit trail for the Platform Architecture document and its structured artifacts (OHM specification, Governance Taxonomy, Threat Catalogue). Whenever any of those documents materially changes, an entry is recorded here. This page is to the architecture what the [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) is to the agent team.

## 1. What this page tracks

An entry is required for any material change to:

* The [Platform Architecture document](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753707) — any of its sections (1 through 9)
* The [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501) — field additions, semantic changes, version bumps
* The [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439) — policy-set additions, modifications, deprecations
* The [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) — threat additions, mitigation changes, test requirement changes
* The [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) hub when Section 6 (the canonical Agent Identity Convention) or Section 7 (the migration source map convention) changes
* The [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) hub when a flow that binds agent behaviour (the cross-cutting agreement protocol, the work-breakdown hierarchy) changes

What does _not_ require an entry:

* Typo fixes, formatting changes, link target updates that do not alter meaning
* Cross-reference additions that do not change the surface contract
* Layout reorganisations within a section that preserve the section's content

When in doubt: if a downstream agent, implementer, or operator would behave differently because of the change, it is material and gets an entry.

## 2. Relationship to ADRs

ADRs and architecture revisions are distinct artifacts with distinct lifecycles. Every accepted ADR _may_ drive an architecture revision; not every architecture revision _requires_ an ADR. The relationship:

| Situation | ADR needed? | Revision entry needed? |
| --- | --- | --- |
| New decision affecting platform behaviour | Yes | Yes (when ADR is reflected in the document) |
| Clarification of existing decision; surface-level wording change | No | Yes if material; no if purely cosmetic |
| Structured artifact (OHM, Governance, Threats) extended with new entries | Yes for governance and threat changes; not always for OHM minor versions | Yes |
| Section rewrite that preserves all decisions but improves clarity | No | Yes (revision entry notes "clarifying rewrite, no semantic change") |

An accepted ADR is referenced from the revision entry that reflects it in the document. The reverse link (ADR → revision entry) lives in the ADR's status section.

## 3. Revision process

1. **Trigger** — an accepted ADR, a discovered drift between shipped reality and the document, or a periodic clarity pass.
2. **Draft** — solution-architect drafts the section revision (or, for security-relevant content, security-architect drafts and solution-architect reviews).
3. **Review** — the other architect (and any tier whose work touches the section) reviews. [docs-writer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557230) reviews for operator-facing implications and downstream documentation impact.
4. **Tech-lead sign-off** — required before publication. The architecture document is high-stakes; the gate is human.
5. **Publish and version** — the affected page is updated; the architecture document version is bumped if the revision is material (see Section 4).
6. **Entry** — an entry is added to this page recording the change.
7. **Propagation** — downstream artifacts (service references, ADR cross-refs, agent skill pages if relevant) are updated to match.

## 4. Versioning

The Platform Architecture document is versioned at major.minor:

| Change type | Version bump |
| --- | --- |
| Structural change (new section, removed section, renumbered sections) | Major (1.x → 2.0) |
| Material change to layer model, governance model, threat model, or BYOM model | Major |
| New or substantially-revised ADR reflected in a section | Minor (1.1 → 1.2) |
| New optional field in OHM, governance taxonomy, or threat catalogue | Minor (and the artifact's own minor version bumps; see its own versioning section) |
| Clarifying rewrite, no semantic change | None (Confluence version history records the edit) |

The structured artifacts (OHM, Governance Taxonomy, Threat Catalogue) version independently of the architecture document. Their version columns live in their own change-history tables; this page aggregates references.

## 5. Revision history

### 31 May 2026 — Threat Catalogue T6-M5 accepted: usage-event dimensions as bounded scalar metering metadata

| Field | Value |
| --- | --- |
| Type | Threat Catalogue addition. No change to architecture sections, the OHM Spec, the Governance Taxonomy, or any ADR. Refines T6 (operator-separation breach) by codifying the structural constraint that makes [ADR-009](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393423)'s "metering events are operator-readable metadata" safe across implementation drift. |
| Affected — Threat Catalogue | T6 mitigations gain **T6-M5**; T6 `required_tests` gains one entry pinning the ORA-21 implementation tests; T6's existing "plaintext customer payload in any log/metric/trace output" detection signal is clarified to name the usage stream explicitly (no new signal). Catalogue version **1.0 → 1.1**. |
| What changed — codification | The constraint that usage-event `dimensions` is bounded scalar metering metadata — bounded key length (64), bounded value length (256), bounded cardinality (16), no whitespace/control-character keys — was previously only prose in [ADR-009](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393423) plus test pins in the merged [ORA-21](https://oraclous.atlassian.net/browse/ORA-21) implementation. T6-M5 codifies it as a citable mitigation so future security reviews of the usage-event surface — and the R6 gateway exposure of that stream — can cite T6-M5 directly rather than reconstructing the argument from ADR-009 prose and test code. |
| Architecture version | v1.1 (unchanged). The Threat Catalogue's own version is bumped to **1.1**; no architecture-document section was modified. |
| Driving source | [ORA-42](https://oraclous.atlassian.net/browse/ORA-42) ("\[threat-catalogue\] Codify T6-M5"), itself a follow-up from the security-architect review of [ORA-21](https://oraclous.atlassian.net/browse/ORA-21) at Tests Review. Implementation shape verified against the merged ORA-21 code: module `oraclous_substrate.usage`, class `UsageEventStream.emit`, constants `MAX_DIMENSION_KEY_LENGTH = 64` / `MAX_DIMENSION_VALUE_LENGTH = 256` / `MAX_DIMENSIONS = 16`, tests `test_dimensions_rejects_nested_customer_payload`, `test_dimension_value_length_is_bounded`, `test_dimension_key_length_is_bounded`, `test_dimension_key_rejects_whitespace_and_control_characters`, `test_dimensions_entry_count_is_capped` (markers `security` + `operator_separation`). |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 31 May 2026 |
| Downstream propagation | Catalogue version bumped 1.0 → 1.1; the `# Proposed` YAML comment removed; security-architect's review checklist for usage-event-touching PRs cites T6-M5; ADR-009 may gain a cross-reference to T6-M5 in a follow-on revision (flagged, not blocking). No agent skill-page behaviour changes today. |
| Rollback considered | No — T6-M5 is additive and codifies what already shipped in ORA-21. Reverting would not undo the implementation; it would only remove the citable mitigation. |

### 29 May 2026 — ADR-012 accepted: substrate tenancy-enforcement seam and RLS backstop preconditions

| Field | Value |
| --- | --- |
| Type | New ADR ([ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396)) refining [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403). No change to any Platform Architecture v1.1 section, the OHM Spec, the Governance Taxonomy, or the Threat Catalogue. ADR-012 makes concrete two things ADR-006 left implicit: the named substrate enforcement seam, and the preconditions under which the row-level-security backstop actually holds in production. |
| Affected — ADRs | [ADR-012](https://oraclous.atlassian.net/wiki/spaces/OP/pages/2490396) created and accepted; listed in the [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) registry. [ADR-006](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) gains a "Refined by ADR-012" status row, an implementation note, and cross-references — no change to its decision. |
| What changed — three commitments | (1) All tenant-scoped substrate access goes through one module, `oraclous_substrate.access` (the `scoped_*` seam: connection, write-node, traverse, fulltext-search, cache get/set), failing closed when no organisation context is bound. (2) The production Postgres role MUST be `NOSUPERUSER` + `NOBYPASSRLS`, or RLS (Threat Catalogue T1-M3) is silently bypassed and ADR-006's defense-in-depth commitment is void in production. (3) The org-GUC (`app.current_organisation_id`) MUST be transaction-local (`SET LOCAL`) or reset before a pooled connection is reused, or a stale GUC leaks one organisation's scope to the next caller. |
| Architecture version | v1.1 (unchanged). A new refining ADR; no architecture-document section or structured artifact was modified, so no version bump. |
| Driving source | [ORA-20](https://oraclous.atlassian.net/browse/ORA-20) (the R0.5 substrate organisation-boundary release gate) Tests Review: the solution-architect ratification of the enforcement seam and the security-architect T1 co-sign surfaced the two RLS-backstop preconditions, which a per-connection test gate could not catch on its own. |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 29 May 2026 |
| Downstream propagation | Jira [ORA-17](https://oraclous.atlassian.net/browse/ORA-17) (A2, implements the seam), [ORA-18](https://oraclous.atlassian.net/browse/ORA-18) (A3, consumes it), and [ORA-20](https://oraclous.atlassian.net/browse/ORA-20) (verifies it) link the ADR. Agent skill pages [backend-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294995) and [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) updated with ADR-012 references. The `oraclous-backend/CLAUDE.md` §3.3/§3.5 reference is added via a docs-writer `[docs]` PR. |
| Rollback considered | No — ADR-012 is additive and closes a latent production hole (an RLS backstop that a superuser/`BYPASSRLS` connection or a stale pooled GUC would silently void). Reverting would re-open it. |

### 28 May 2026 — Coordination layer: work-breakdown hierarchy, migration source maps, and the cross-cutting agreement protocol

| Field | Value |
| --- | --- |
| Type | Process tooling additions; no semantic change to any architecture v1.1 section, ADR, OHM Spec, Governance Taxonomy, or Threat Catalogue. This revision documents _how_ work is broken down and _how_ cross-cutting agreements are reached and recorded — the verbs the system previously lacked. |
| Affected — new Confluence hub | [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) (page 1212418) created at the space root, with two child pages: [Cross-cutting agreement protocol](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1245185) (1245185) and [Interface Contracts](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1277953) (1277953). The hub documents the full work-breakdown hierarchy (Architecture → Release → Migration source map → Epic → Contract → Story → TDD pair → gates) with the owning agent and gate at each level. |
| Affected — 09. Releases | [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) → v3. New **Section 7 — Migration source maps: the lift-vs-rewrite convention**: the project-specific defaults (frontend = clone-and-refactor; backend = lift-and-reshape per service; greenfield only for genuinely new surfaces), the four-verdict rubric (Lift / Reshape / Extract / Greenfield), the "legacy is always the behavioural specification" principle, the lift-tests-first rule, and the per-release Migration source map table owned by product-planner with solution-architect and security-architect sign-off. The release-page template (Section 3) gains a Migration source map row; the lifecycle (Section 4) makes the source map part of the Planned → Briefed gate; the operation set (Section 6.4) gains `open_contract`; the status table (Section 8) gains the RF (frontend) row. |
| Affected — R0.5 | [R0.5](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884934) → v3. Migration source map section added with provisional per-deliverable verdicts (template pending completion by product-planner in the coordinator session after reading the legacy backend worktree). Sprint references tied to the Planned → Briefed gate. |
| What changed — the cross-cutting agreement protocol | The system previously recorded the _outcomes_ of agreements (ADRs, the OHM Spec, the Governance Taxonomy) but not the _flow_ by which two implementers in separate repository sessions reach agreement on a shared shape (a data structure, an API response, an OHM field, a ReBAC relation). The protocol defines three tiers: Tier 1 (internal to one repo — implementer decides), Tier 2 (a contract between two repos/services — the new Contract flow), Tier 3 (a platform-wide principle — an ADR). The Contract flow: the surfacing session opens a `Contract` Jira issue owned by solution-architect and stops; solution-architect drafts the shape; security-architect reviews if security-touching; the agreed shape is recorded once in its canonical home (Interface Contracts page for API shapes until R6 then the gateway OpenAPI spec; OHM Spec for manifest fields; Governance Taxonomy for ReBAC relations); product-planner creates the paired implementing stories linking the canonical home; a CI contract test or shared fixture enforces the boundary. Governing principle: **record once, link many**. Defining a cross-repo shape locally is now an explicit process violation. |
| What changed — the work-breakdown hierarchy | The full descent from raw Release to assignable Story is now documented with owning agents: Release and Migration source map and Epic and Story are planning/architecture artifacts (the coordinator cluster: product-planner, solution-architect, security-architect, docs-writer); Tests through Done are execution artifacts (the repo cluster: test-author, implementers, code-reviewer, qa-engineer). The fault line is the Story → Tests boundary. This hierarchy is the basis for the forthcoming separation of agents into a workspace-root coordinator session and the two repository sessions (not yet executed; this revision lays the documentation foundation for it). |
| Affected — new Jira issue type | A `Contract` issue type is introduced (sitting between Epic and Story). Until it is created in the Jira admin UI, the interim is a Story labelled `contract` with the same ownership and Done criteria. Creating the issue type is a human admin-UI action. |
| Affected — repo files (out of Confluence scope) | Both `CLAUDE.md` files (§10 never-do list, §11 rewritten to "Legacy reference and the lift-vs-rewrite default" with the rubric, project defaults, lift-tag honouring, and the cross-repo Contract rule) and both handoff prompts (§4 reference-codebase sections) updated for the human to commit. Versioned in git, propagated in the repositories rather than here. |
| Architecture version | v1.1 (unchanged). No section of the Platform Architecture document, the OHM Spec, the Governance Taxonomy, or the Threat Catalogue was modified. Process tooling, not an architectural change. |
| Driving source | Tech-lead observations during Group E: (1) the release pages decompose by platform deliverable but not by frontend/backend responsibility, so each repo session was silently re-deciding lift-vs-rewrite and drifting toward greenfield (the frontend should clone-and-refactor the working legacy app; most backend services should be lifted-and-reshaped, not rewritten) — this drift was not captured anywhere; (2) there was no documented flow for how team members agree on shared data structures and other cross-cutting shapes, nor where such agreements are recorded. |
| Approved by | tech-lead (Reza Jahankohan) — "please affect all above discussions in the Confluence and in the claude md and agents for now" |
| Effective from | 28 May 2026 |
| Downstream propagation | The 11 agent skill pages do not yet describe the lift-vs-rewrite rubric, the lift-tests-first rule, or the cross-cutting agreement protocol in their bodies. This is acknowledged drift, folded into the same first `docs-writer` ticket that reconciles the `needs-human` wording (see the prior entry and 09. Releases Section 6.5). The specific skill pages needing the lift-rubric insert are test-author, backend-implementer, frontend-implementer, and solution-architect; solution-architect additionally needs the Contract-ownership flow. Until reconciliation, 09. Releases Section 7 and the Cross-cutting agreement protocol page are canonical. The separation of agents into a coordinator session is the planned next step and will have its own revision entry when executed. |
| Rollback considered | No — these are additive conventions that close two real gaps (silent greenfield drift; undocumented cross-cutting agreement). The new pages are net-new; the 09. Releases and R0.5 changes are additive sections plus a renumber. Reversion would re-open both gaps. |

### 27 May 2026 — Group E bootstrap: `needs-human` shape correction; field IDs codified

| Field | Value |
| --- | --- |
| Type | Documentation correction — Section 6 of [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) brought into agreement with shipped Jira reality. No semantic change to any agent's behaviour, sign-off authority, or skill set; the convention's _intent_ was always to be a controlled escalation flag, and the multi-checkbox custom field is the correct implementation of that intent. The previous wording (Jira "label") was a documentation error. |
| Affected — canonical convention | [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) (page 164160) → v2. Section 6 rewritten with explicit Jira field IDs (`Agent Owner` = `customfield_10074`; `needs-human` = `customfield_10075`, multi-checkbox), option IDs (`human` = 10031, `needs-human` = 10032), corrected `escalate_to_human`, and a new Section 6.5 documenting skill-page drift. |
| Affected — agent skill pages | The 11 agent skill pages carry the old "add the `needs-human` label" wording in their Section 11. Deliberately not rewritten in that revision (token cost; canonical source is correct; reconciliation is the first `docs-writer` ticket). |
| What changed — semantic | Nothing. The escalation pattern is unchanged; only the Jira write for the flag step changed from a label to `customfield_10075: [{id: "10032"}]`. |
| Architecture version | v1.1 (unchanged). Process tooling, not an architectural change. |
| Driving source | Discovery during Group E bootstrap; the frontend Claude Code session flagged the discrepancy between the bootstrap text (label) and Jira reality (multi-checkbox) and stopped at the gate — the discipline the handoff is designed to produce. |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 27 May 2026 |
| Downstream propagation | Section 6.5 of 09. Releases tracks the deferred skill-page reconciliation, now bundled with the lift-rubric reconciliation from the 28 May entry above. No [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) entry required — no agent behaviour changes. |
| Rollback considered | No. The multi-checkbox shape is the correct implementation of the convention's intent. |

### 27 May 2026 — Group D follow-up (3): Releases sub-directory established; Agent Identity Convention codified across all 11 agent skill pages

| Field | Value |
| --- | --- |
| Type | Process tooling additions; no semantic change to any architecture v1.1 section, ADR, OHM Spec, Governance Taxonomy, or Threat Catalogue |
| Summary | The [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) hub plus 11 release pages were created, and all 11 agent skill pages received a Section 11 (Agent Identity Convention). The convention has two parts: the `Agent Owner` custom field (12 values) and the `[agent:NAME]` comment prefix with structured action trailers, with the operation set (`my_tasks`, `claim_next`, `handoff_to`, `escalate_to_human`, `complete`, `observe`, `review_request`) documented in 09. Releases Section 6. Architecture version unchanged at v1.1. |

### 27 May 2026 — Sections 2, 3, 5, 7, 8 callout pass (Group D follow-up audit)

| Field | Value |
| --- | --- |
| Type | Clarifying revisions; no semantic change to any section |
| Summary | Five sections received a single `panel-info` callout block immediately after the H1, matching the pattern established in Group C for Sections 4, 6, and 6.5. Sections 1 and 9 were audited and intentionally left without callouts. Architecture version unchanged at v1.1. |

### 27 May 2026 — Group C: 11 founding ADRs rewritten to uniform template; Sections 4, 6, 6.5 clarifying revisions

| Field | Value |
| --- | --- |
| Type | ADR set establishment + clarifying revisions (no semantic change to any decision) |
| Summary | All 11 founding ADRs unified onto a single template under [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826). Sections 4, 6, 6.5 received callout blocks linking to the corresponding Group B structured artifacts. Architecture version unchanged at v1.1. |

### 27 May 2026 — Group B structured artifacts published

| Field | Value |
| --- | --- |
| Type | Artifact addition (no change to existing sections) |
| Summary | Three structured artifacts extracted from prose sections and published as standalone references: [OHM v1.0 Spec](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501), [Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439), [Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129). |

### 27 May 2026 — Platform Architecture v1.1 locked

| Field | Value |
| --- | --- |
| Type | Baseline establishment |
| Summary | Architecture v1.1 locked as the foundation document for the project restart. Founding ADRs 1–11 drafted in parallel. |

## 6. How to add an entry

1. Apply the revision to the affected page(s) following the revision process in Section 3 above.
2. Add an entry here in reverse chronological order, using the table format above.
3. Cross-link: the entry references the driving ADR (if any) and the affected pages; the driving ADR's status section references this entry.
4. If the entry affects a structured artifact (OHM, Governance Taxonomy, Threat Catalogue), also update that artifact's own change-history table.
5. If the entry changes downstream agent behaviour, propagate through the [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) as appropriate.

## 7. Related references

* [Platform Architecture v1.1](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753707) — the document this page tracks
* [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501)
* [Structured Governance Taxonomy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688439)
* [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129)
* [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) — release-level planning hub; Section 6 is the Agent Identity Convention, Section 7 is the migration source map convention
* [10. Engineering Flows](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1212418) — work-breakdown hierarchy and the cross-cutting agreement protocol
* [02. ADRs](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589826) — the parallel decision-record audit trail
* [Agent and Skill Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/426078) — the parallel agent-team audit trail
