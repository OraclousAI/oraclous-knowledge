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

### 4 June 2026 — Flow hardening v2 (ORAA-208): ORAA-4 rev12 — pre-open readiness, handoff chain, fold-don't-spawn, docker-required, KB currency, repo structure, goal status hygiene, attribution enforcement

| Field | Value |
| --- | --- |
| Type | Skill change / gate change — team-wide governance, all personas |
| Agents affected | All personas (the rules are enforced for every agent via the operating contract and the bundles) |
| What changed | Flow hardening v2 (ORAA-208), enacted as **ORAA-4 rev 12**. **§13.1 pre-open readiness:** before *opening* a PR for review (not just before merge) the branch must be clean on the local pre-push gate, green on CI, and rebased onto current `main` (not `BEHIND`/`DIRTY`); the opening implementer owns all three, a reviewer must never discover red CI or a needed rebase, and a red/behind PR is an implementer failure to fix in place — not a new ticket. **§9.1 handoff chain (the flow IS part of Done):** every story moves product-planner/architects → test-author (`[tests]`) → be-test-reviewer (+ security-architect if CTO-flagged) → backend/frontend-implementer (`[impl]`) → code-reviewer + qa-engineer (+ architects if surface-touching) → CTO (merge); at each stage the acting agent must reassign to the next named owner on completion, and an agent that finishes its part (or wakes and finds nothing to do) must hand off or escalate — never leave the issue parked (the #1 cause of stalls). **§9.2 fold-don't-spawn:** small conflicts/misalignments with brief or tests are fixed in the current PR/run, not a new `[fix]` ticket; only genuinely new scope becomes a new (deduped) issue; a wrong test goes back to test-author (ADR-010). **§9.3 docker-required:** multi-service/integration functionality is flagged `docker-required` (by task creator or CTO) and its integration tests run on Docker; if the Docker daemon is down the agent raises an error and BLOCKS the task `needs-human` — never skips or marks done. **§16 KB currency:** any agent writing the KB keeps docs current in the same change and refreshes graphify (`graphify oraclous-knowledge --update`); docs-writer owns this end-to-end; a KB/docs story isn't done until docs updated + graph refreshed. **§17 repository structure:** new code under `services/<service>/` (ADR-001); never extend the legacy `oraclous-core-service` (retiring per ADR-005, relocation tracked separately); never commit `__pycache__`/`*.pyc`. **§8 goal status hygiene + sequencing:** only the highest unfinished release is workable; before the next goal opens the CTO marks the completed goal `achieved` and ALL its projects `completed` (a delivered goal must never stay `active`), tied to the release-seam retrospective. **§5 attribution:** forbidden in commits AND PR titles/descriptions AND comments, enforced by a wired `commit-msg` hook (`core.hooksPath=.githooks` in every repo) plus a CTO pre-merge grep of the commit range and PR body. |
| Why | The R2 delivery and seam surfaced a residual class of stalls and churn that the rev11 hardening did not close: PRs opened red or behind for reviewers to discover, fully-worked issues left parked with no next owner, small misalignments spawned as separate `[fix]` tickets, integration tests skipped when Docker was down, KB prose updated without refreshing the graph, code added to the retiring legacy service, delivered goals left `active` with open projects, and attribution leaking into PR titles/bodies/comments where the commit-only rule didn't reach. Rev12 closes each at the source. |
| Approved by | CTO (technical authority); tech-lead (Reza Jahankohan) at the release seam |
| Effective from | 4 June 2026 |
| Rollback considered | No — these tighten existing gates and add discipline with no behaviour they remove; rollback would re-open the stall/churn paths they close. Synced surfaces (below) keep instances and templates consistent. |

Surfaces synced together for this change: **ORAA-4** (the contract, rev12), **12 agent bundles** (live instances), **11 roster templates** (the clone sources), and **these KB engineering docs** (`git-workflow.md`, `definition-of-done.md`, `pr-conventions.md`, `release-process.md`, `index.md`). R2 was marked **achieved** with all its projects **completed** at the seam.

### 4 June 2026 — R2→R3 seam hardening: anti-churn made fail-closed + sequencing, retro, and destructive-change protocols added

| Field | Value |
| --- | --- |
| Type | Skill change / gate change — team-wide governance, all personas |
| Agents affected | All personas (the rules are enforced for every agent via the operating contract and the bundles) |
| What changed | At the R2→R3 release seam the operating contract (ORAA-4) was hardened in several ways. **§13.3** (no stranded issues) was made **fail-closed**: on closing an issue, dependents are unblocked and assigned only after reading their description for prose dependencies ("salvage before", "hard-sequenced after", "after ORAA-NN"), back-filling `blockedByIssueIds`, and verifying *every* predecessor is `done`; destructive/irreversible work is never auto-unblocked; ambiguous cases stay blocked; a blocked issue with no live path is escalated, not retried. **§13.4 branch-from-merged-tests** was added: an `[impl]` PR must branch from / rebase onto the exact `main` commit where its `[tests]` PR merged before opening; the test-author records the merge SHA, implementers assert base ≥ it, reviewers reject impl PRs whose base predates it — preserving ADR-010's two-PR independence while fixing the add/add-conflict sequencing. **§13.5 rebase-on-merge** was added: when any PR merges, open PRs with overlapping files get a rebase task before review. **§14 release-seam retrospective** was added: at each release gate the CTO runs a retrospective that must output concrete deltas (ORAA-4 / bundles / KB) or a logged "won't fix"; the gate issue cannot close until deltas are applied or waived (generalises the hotfix-retrospective hook). **§15 destructive-change protocol** was added: deletes / DB migrations / archival / retirements require predecessor-salvage `done` and verified, explicit human sign-off before leaving `blocked` (the CTO sequences but never self-approves), and a forward-only plan; reversible (archival behind a flag) is preferred over hard deletion. |
| Why | The R2 delivery surfaced recurring churn at issue and release seams: stranded dependents auto-unblocked past incomplete predecessors, add/add conflicts between tests and implementation branches, stale-base PRs reviewed against moved bases, process friction noticed but never converted into fixes, and destructive work sequenced without explicit human approval. Hardening the contract at the R2→R3 seam closes these at the source rather than via per-incident remediation. |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 4 June 2026 |
| Rollback considered | No — these tighten existing gates and add protocols with no behaviour they remove; rollback would re-open the churn paths they close. Synced surfaces (below) keep instances and templates consistent. |

Surfaces updated together for this change: **ORAA-4** (the contract), **12 agent bundles** (live instances), **11 roster templates** (the clone sources), and **these KB engineering docs** (`git-workflow.md`, `definition-of-done.md`, `pr-conventions.md`, `test-strategy.md`, `release-process.md`, `index.md`).

### 3 June 2026 — Bucket A: pre-push gate + ORAA-4 §13 anti-churn (mergeability / dedup / no-stranded)

| Field | Value |
| --- | --- |
| Type | Skill change / gate change — team-wide governance, all personas |
| Agents affected | All personas (enforced via the operating contract and the bundles) |
| What changed | The **pre-push gate** was established: before any `git push`, an agent runs locally the same cheap checks CI's `quality` job runs (backend: `uv run ruff check . && uv run ruff format --check . && uv run pytest --collect-only`; frontend: the `package.json` lint + type-check + format-check scripts) and pushes only if clean — a failure is the implementer's to fix before re-pushing, not a new `[fix]` issue. The **ORAA-4 §13 anti-churn** rules were added: the **mergeability gate** (§13.1 — a PR/issue is not ready on CI-green alone; before the `in_review` handoff and before merge, check `gh pr view <n> --json mergeable,mergeStateStatus`, require `mergeable=MERGEABLE` and `mergeStateStatus ∈ {CLEAN, HAS_HOOKS}`, poll past `UNKNOWN`, rebase on `DIRTY`/`BEHIND`, satisfy required reviews/checks on `BLOCKED`); **dedup-before-fix-ticket** (§13.2 — search open issues for the same PR + problem and extend rather than duplicate before opening a `[fix]`/`[fix-lint]`/`[regression]`/`[rebase]` issue); and the first form of **no-stranded-issues** (§13.3). |
| Why | Round-trip churn from avoidable CI failures, PRs treated as ready on a green run that were not actually mergeable, and duplicate fix tickets were measurably inflating the board and the CI queue. Bucket A moved these checks left (to the local push) and into the contract (the mergeability and dedup rules). |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 3 June 2026 |
| Rollback considered | No — these add pre-push and pre-merge checks with no removed behaviour; the 4 June entry above supersedes §13.3 by making it fail-closed. |

Surfaces updated together for this change: **ORAA-4** (the contract), the **agent bundles**, and **these KB engineering docs**.

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
