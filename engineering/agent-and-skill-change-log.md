---
confluence_id: "426078"
title: "Agent and Skill Change Log"
---

# Agent and Skill Change Log

The audit trail for changes to the Oraclous development agent team itself. Whenever an agent is added, retired, repurposed, or has its skill set materially changed, an entry is recorded here. This page is to the agent team what the knowledge-base [Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557174) is to the documentation.

**Why this exists.** The agent team is the production tooling that builds Oraclous. Its behaviour determines the quality, security posture, and architectural integrity of every shipped service. Changes to that team need the same audit discipline we apply to architecture and code.

## What counts as a material change

A material change requires an entry here:

* Adding a new agent to the team
* Retiring an existing agent
* Renaming an agent or changing its role boundary
* Materially changing an agent's skill set — adding a skill, removing a skill, replacing a skill, or updating a skill's behaviour in a way that changes outputs
* Changing an agent's consciousness permissions
* Changing the sign-off gates owned by an agent
* Changing the model an agent uses (per [ADR-007](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720920))

What does _not_ require an entry: typo fixes to skill prose, formatting changes, link updates, or any change that does not alter agent behaviour.

## Entry format

Each entry follows the same shape:

* **Date** — when the change took effect
* **Type** — addition / retirement / rename / skill change / permission change / gate change / model change
* **Agent(s) affected** — link(s) to the agent skill page(s)
* **What changed** — concrete description of the change
* **Why** — the reason, with links to the consciousness entry, ADR, or Jira ticket that drove it
* **Approved by** — tech-lead (always; agent changes are tech-lead's sole authority)
* **Effective from** — the date/sprint the change is active
* **Rollback considered** — yes / no, and how if yes

## How changes get proposed

There are three legitimate sources of agent-team changes:

1. **Consciousness-surfaced** — the consciousness skill on an agent (or the team-level sweep) identifies a recurring pattern that justifies a change, proposes it as a draft, and tech-lead reviews. See [Agent Consciousness for Development](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688403).
2. **Tech-lead-initiated** — tech-lead identifies a process problem and directly proposes a change.
3. **ADR-driven** — an accepted ADR has implications for the agent team (e.g. ADR-007 set BYOM protocol shapes, which constrains agent model selection).

All three flow through the same approval gate: tech-lead approval, entry here.

## Process

1. Change is proposed (via consciousness, tech-lead, or ADR)
2. If proposed via consciousness, the proposal is a Confluence draft updating the relevant agent skill page(s)
3. Tech-lead reviews the draft alongside the consciousness evidence (or ADR/ticket that drove the proposal)
4. On approval: tech-lead publishes the draft, adds an entry to this log, links the entry from both the consciousness record and the relevant Jira ticket
5. The change takes effect from the start of the next sprint unless flagged for immediate effect

## Rollback

A change can be rolled back at any sprint boundary. Rollback creates a new entry here referencing the original change, the reason for rollback, and any consciousness observations that motivated it. The original entry stays in place; the rollback supersedes it by reference.

## Change log

### 28 May 2026 — Agent added: be-test-reviewer (narrow BE Tests Review persona)

| Field | Value |
| --- | --- |
| Type | Addition — a new, deliberately narrow review persona |
| Agents affected | New: [be-test-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1703937) (1703937). Indirectly clarifies the residency of [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) and [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) (now coordinator-only). |
| What changed | A twelfth persona, `be-test-reviewer`, was added. It owns exactly one gate — the backend Tests Review gate (TESTS REVIEWS → IMPLEMENTATION) — verifying that `[tests]` PRs assert the architectural boundary the brief names and that security-marked tests genuinely exercise the tagged threat. It has no authority to originate architecture, ADRs, or Contracts; decision-level problems escalate to the root `solution-architect`/`security-architect`. A 13th `Agent Owner` field option (`customfield_10074`) was created for it. It is a Review-tier persona resident only in the backend session. |
| Why | The separation of the agent team into three Claude Code sessions (coordinator at the workspace root, backend repo, frontend repo) moved `solution-architect` and `security-architect` entirely into the coordinator session. The backend Tests Review gate still needs an architecture-and-security check performed from inside the backend session. Rather than make the two architect personas dual-resident — which would allow two sessions to act as the same `Agent Owner` on one ticket — a distinct narrow persona owns that gate. This removes the ambiguity at the source instead of with a coordination rule. Tech-lead-initiated during the session-separation design. Canonical rationale: [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705) Section 3. |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 28 May 2026 |
| Rollback considered | Yes — if dual-residency turns out to be a non-issue in practice, the gate could revert to a coordinator-loaded architect and the persona retired. Recorded as a possibility; not anticipated. |

### 27 May 2026 — Per-agent skill pages published (Group A complete)

| Field | Value |
| --- | --- |
| Type | Addition (documentation artifact; no behaviour change) |
| Agents affected | All 11 agents now have published skill pages under the [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852): [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) (164068) [security-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557195) (557195) [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) (884840) [tech-lead (human)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) (983101) [test-author](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294957) (294957) [backend-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294995) (294995) [frontend-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/295035) (295035) [devops-implementer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164102) (164102) [code-reviewer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/622800) (622800) [qa-engineer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884874) (884874) [docs-writer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557230) (557230) |
| What changed | Each agent now has a full skill page documenting identity, role boundary, loaded skills (3-4 per agent plus the standing Agent Consciousness for Development skill), tool access, sign-off authority per Kanban gate, model selection (Anthropic native per ADR-007), consciousness configuration, interaction patterns, failure modes, and quality criteria. The Agent Skills Catalogue index table was updated to mark all 11 agents as "Skill page current" with direct page links. |
| Why | The 27 May initial team-formation entry below established _that_ the 11-agent team exists; this entry records _that the skill contracts for each agent are now in writing and readable_. Without the per-agent pages, the team is a roster without contracts; with them, every agent's behaviour is auditable against a published surface. |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 27 May 2026 |
| Rollback considered | No — this is a documentation artifact; rollback would mean un-publishing the pages, which has no operational benefit. Skill changes will be tracked via subsequent entries. |

### 27 May 2026 — Initial team established

| Field | Value |
| --- | --- |
| Type | Initial team formation |
| Agents affected | All 11 agents (see [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848)) |
| What changed | The 11-agent team was established with the role boundaries and tier structure defined in the Agent Team Roster. Each agent loads the [Agent Consciousness for Development](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688403) skill plus its role-specific skills (documented on each agent's page in the Agent Skills Catalogue). |
| Why | Project restart per the Oraclous V1 plan; agent team designed against the TDD workflow established by [ADR-010](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557078) |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 27 May 2026 |
| Rollback considered | N/A — initial team |

## How to add an entry

When making a material change:

1. Update the affected agent skill page(s) with the change
2. Add an entry here in reverse chronological order, using the table format above
3. Cross-link: the entry references the source (consciousness/ADR/ticket); the source references this entry
4. Update the relevant agent skill page's "Change History" section at the bottom of the agent page

## Related references

* [Agent Team Roster](https://oraclous.atlassian.net/wiki/spaces/OP/pages/589848) — the agent team itself
* [Session topology and persona residency](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1736705) — which session each agent runs in
* [Agent Consciousness for Development](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688403) — the meta-skill that surfaces change proposals
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852) — the per-agent skill pages
* [Change Log](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557174) — knowledge-base-wide change log
* [Contributing to Documentation](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688383) — general contribution process
