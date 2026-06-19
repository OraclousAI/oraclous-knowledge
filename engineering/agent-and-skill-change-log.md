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

### 13 June 2026 — Agent added: experience-architect (Design tier) — design → direct → review FE loop

| Field | Value |
| --- | --- |
| Type | Addition — a new coordinator-tier persona + a new sign-off gate |
| Agents affected | New: [experience-architect](personas/experience-architect.md) (Design tier, Coordinator-resident). Touches product-planner (its FE brief must cite a journey+IA spec) and frontend-implementer (it builds against that spec) and the human tech-lead (gains a parallel user-lens review at FE code review). |
| What changed | A new **Design tier** was added with a single persona, **experience-architect** — the discipline the team did not have: a role that owns the forward-looking product surface (end-user personas, the information-architecture / navigation model, user journeys, and UI/UX design) grounded in the **live** gateway capability surface, never the legacy app. It is a Coordinator-session persona modelled on solution-architect (a 12-section persona page + a companion `/xa` Claude Code skill at `~/.claude/skills/experience-architect/SKILL.md`). Its ten loaded skills: capability-surface inventory · persona/segment definition · IA/navigation design · journey/task-flow mapping · UI/UX interaction & visual design (wireframes, component composition, interaction states, microcopy; may invoke the `frontend-design` skill for mockups) · usability/heuristic evaluation · design-system re-grounding · FE implementation review from the user lens · journey→backend-gap Contract filing · the standing consciousness skill. It produces the signed **journey+IA spec** that is the gate artifact. The FE loop is deliberately simple and **gate-free**: experience-architect **designs** a surface, **opens/assigns the GitHub issue** to the frontend agent with the design as the brief, and after the agent opens the PR **reviews + validates it from the user's perspective and approves via the `johnkennII` GitHub identity** (a genuine non-author approval that lets the PR merge under branch protection). The CTO is the parallel craft reviewer; the two reviews together are the whole check on an FE product-surface PR — there is **no separate process gate** and **no journey-spec CI check**. The automated FE invariant CI (gateway-only, no-token-in-storage, axe-core AA, bundle budget, no-`dangerouslySetInnerHTML`, lint/types/format) is unchanged — those are machine checks, not agent gates. The persona has `can_propose_adr: False` (architecture-implying decisions are escalated to solution-architect as gap Contracts) and never writes application or design-system code (CLAUDE.md §10). |
| Why | A post-R6 audit established that the frontend is a re-skin of a legacy graph-RAG-chat app (rooted at `/graphs/{id}`) whose information architecture is the wrong product's skeleton: the Tools page is browse-only though the backend exposes a full tool lifecycle through the gateway; Recipes is a read-only JSON viewer though the backend exposes templates/dry-run/run; agent-tool connections only accept manual API keys though auth-service already captures OAuth tokens and the broker has a full resolver (only a bridge + a "Connect" affordance are missing). Root cause: the team had architecture, planning, implementation, review, and docs tiers but **no design tier**, so the only "what should the UI be" signal was the migration default ("clone-and-refactor the legacy app"), faithfully executed on top of a backend that had moved past it. experience-architect closes the gap by owning the user journey/IA/UI-UX grounded in the live capability surface, directing the frontend agent to build each surface, and reviewing/validating the resulting PR (with the CTO) so the grounding actually sticks. Tech-lead-initiated (Reza); see the approved plan and the prior audit. |
| Approved by | tech-lead (Reza Jahankohan) |
| Effective from | 13 June 2026 |
| Rollback considered | Yes, and clean: the role wrote only KB pages, issues, specs, and PR reviews. Rollback = remove experience-architect from the coordinator loadable-persona allow-list (the three CLAUDE.md), drop the Design tier from the roster/catalogue/session-topology, and retire the `/xa` skill. No application code, CI gate, or irreversible step is involved. |

Operating model: work is tracked as **GitHub Issues + PRs** in the repos (no external board) — the frontend agent picks up a ready issue, opens a PR, and the other agents (experience-architect's user-lens review + the craft review) check it. This role is governed entirely by the **KB engineering pages + the `CLAUDE.md` files + frontend CI**, not by any ORAA-4 surface. Surfaces synced together for this change: **these KB engineering pages** (this change-log, [agent-team-roster.md](agent-team-roster.md), [agent-skills-catalogue.md](agent-skills-catalogue.md), the new [personas/experience-architect.md](personas/experience-architect.md), [index.md](index.md), and [session-topology-and-persona-residency.md](../flows/session-topology-and-persona-residency.md)), the **three `CLAUDE.md` files**, and the **companion `/xa` skill**. No new CI gate is added: an FE product-surface PR is judged by the two agent reviewers (experience-architect for product + the CTO for craft), who approve via the `johnkennII` GitHub identity; the existing automated FE invariant CI is unchanged.

### 4 June 2026 — R3.5 — make every service real (ORAA-4 rev15: §21 architecture, §22 hardened per-service DoD, §23 per-service delivery)

| Field | Value |
| --- | --- |
| Type | Skill change / gate change + tooling — team-wide governance, all personas |
| Agents affected | All personas (enforced via the operating contract, the bundles, and the new structure/hollowness/DoD mechanisms) |
| What changed | A **hollowness audit** (`tools/audit/hollowness_audit.py`) confirmed that R2/R3 — and R2's capability-registry — **shipped hollow**: stub endpoints, `raise NotImplementedError`, a `GraphNodeService` stub class defined *inside* a route file, ~6,300 LOC of real logic left undeleted/dead in `oraclous-backend/oraclous-core-service/`, and auth that dropped human/email/OAuth/org management. **R3.5** was opened to rebuild every service **real, end-to-end, per service**, enacted as **ORAA-4 rev15**. **§21 canonical service architecture** (adopted from the legacy `app/{core,models,repositories,routes,schema,services}` layout): each service is a package at `services/<svc>/src/oraclous_<svc>_service/` with `main.py` (only `app=create_app()`), `app/factory.py` (build+wire+`include_router`, no handlers/logic), `routes/` (handler = parse → one service call → HTTP map), `services/` (all business logic), `domain/` (pure entities, no I/O; optional), `repositories/`(+`models.py`, the only DB/Neo4j/Redis access), `schema/` (Pydantic DTOs only), `core/{config,dependencies,lifespan}.py`, and `migrations/`; `tests/{unit,integration,smoke}/` live outside `src/`. **Three non-negotiable rules:** no business logic in route handlers; no non-`BaseModel` class defs and no DB drivers in `routes/`; repositories are the only DB/Neo4j/Redis access (connection setup in `core/lifespan.py` excepted). **Enforcement** (CI `lint` job + pre-push): `tools/lint/check_service_structure.py` (STR001-005), `tools/lint/check_no_stubs.py` (HOL001-005, gated on the `claimed_done` flag in `tools/lint/service_status.yaml`), and per-service internal import contracts in `pyproject.toml [tool.importlinter]` (`routes→services→domain→repositories→core`). **§22 hardened per-service Definition of Done** — a *service* is done only when all **8 gates** pass, and "merged PR + green stub-tests" satisfies **none** of gates 2-6: (1) structurally conformant; (2) not hollow (`check_no_stubs` zero findings, service flipped `claimed_done` in `service_status.yaml`); (3) it runs (docker compose up healthy; `GET /health` 200); (4) real endpoints (integration vs real substrate via testcontainers; no stub/501); (5) end-to-end smoke vs real substrate (`services/<svc>/tests/smoke/smoke.sh`, runs in CI as the docker-required `r3_5_gate` job, modelled on the r2-gate); (6) **Reza personally tests it and signs off** (the issue carries `needs-human` until accepted; no service is done while `needs-human` is set). **§23 anti-micro-ticket:** one service = one deliverable, ≤6 coarse vertical slices (each cuts all layers, ends in a passing smoke, is a single `[tests]`+`[impl]` pair); no ticket per file/import/endpoint-shell, no giant interlocked task graphs. **Spec is pinned** to legacy `develop` @ commit `84152635de05c105765cfe6b631bb5ba81f2f4aa` (TASK-237; ADR-022 recipe/primitive/unified-graph ingestion model) — read via `git show develop:<path>`, never write to `legacy-reference`. **Graph-first per-service order:** (1) knowledge-graph-service (ingest) → (2) knowledge-retriever-service (read) → (3) identity/org service (NEW: users + email + OAuth Google/GitHub/Notion + orgs/members/roles/invites; orgs *leave* the graph service) → (4) credential-broker-service → (5) capability-registry + tools + connectors (port from `oraclous-core-service`, then **salvage-then-delete** it) → (6) application-gateway. Until the gateway exists, services are reached **directly by host IP:port** (legacy parity; legacy had no gateway). `oraclous-core-service` stays (`port_source:true`, `deletable:false`) until its logic is ported+tested into capability-registry; deletion is destructive → **human sign-off required** (§15). The hollowness audit re-opens hollow R2/R3 "done" stories under R3.5. Full architecture narrative: [service-architecture-standard.md](service-architecture-standard.md). |
| Why | R2/R3 were marked done on "merged PR + green tests" while the services were hollow — stub endpoints, `NotImplementedError`, a service stub class living inside a route file, thousands of lines of real logic stranded dead in the legacy `oraclous-core-service`, and an auth surface missing human/email/OAuth/org management. Green stub-tests proved nothing about whether a service runs or does real work, and "done" never required the human to actually exercise it. R3.5 makes *real, running, human-verified* the bar: §21 forces a layered structure that can hold real logic (and bans stubs/DB-in-routes mechanically), §22 replaces the paper DoD with 8 gates ending in Reza's hands-on sign-off, and §23 stops the work fragmenting into micro-tickets that each pass while the service as a whole stays hollow. The old **R4–R8 roadmap (incl. the "gateway-from-R5 vertical slices" plan) is discarded** — superseded by R3.5's per-service rebuild. |
| Approved by | CTO (technical authority); tech-lead (Reza Jahankohan) — owns the per-service §22 gate-6 sign-off and the destructive `oraclous-core-service` deletion gate |
| Effective from | 4 June 2026 |
| Rollback considered | Partial. The structure/no-stubs linters, import contracts, and the `r3_5_gate` smoke job are reversible (remove the checks, drop the CI job). The pinned-spec discipline, the 8-gate per-service DoD, and the discarded R4–R8 roadmap are deliberate direction changes, not toggles; rolling them back would re-admit the hollow-but-"done" failure mode R3.5 exists to close. The `oraclous-core-service` salvage-then-delete is itself gated on human sign-off and is the one genuinely irreversible step, deferred until its logic is ported and tested. |

Surfaces synced together for this change: **ORAA-4** (the contract, rev15 — new §21/§22/§23; §15 destructive-change gate applied to `oraclous-core-service`), the **agent bundles** (instances + roster templates), and **these KB engineering docs** (this change-log + the new [service-architecture-standard.md](service-architecture-standard.md)). New tooling lives under `tools/`: `tools/audit/hollowness_audit.py`, `tools/lint/check_service_structure.py`, `tools/lint/check_no_stubs.py`, and `tools/lint/service_status.yaml`. The old R4–R8 roadmap is discarded in favour of R3.5's graph-first per-service order.

### 4 June 2026 — Enforcement program (ORAA-250): mechanisms, not rules — ORAA-4 rev14

| Field | Value |
| --- | --- |
| Type | Skill change / gate change + tooling — team-wide governance, all personas |
| Agents affected | All personas (enforced via the operating contract, the bundles, and now running mechanisms) |
| What changed | The recurring "rules don't stop failures" problem was addressed by converting advisory rules into **running mechanisms**, enacted as **ORAA-4 rev14** plus tooling. **Pre-push hooks (T1.1):** each repo now ships `.githooks/pre-push` with `core.hooksPath=.githooks`, blocking red pushes locally; the backend hook mirrors the **full CI `quality` job** (ruff check/format, mypy, import-contracts, org-scoping, labels-schema, test-import hygiene, neo4j write-role, contract checksums), frontend runs lint/typecheck/format:check, knowledge runs the KB-index currency check. **Merge gate (T1.2):** all three repos were made **public**, which (a) cleared the GitHub Actions spending-limit block that had halted all CI (ORAA-246) and (b) unlocked **rulesets** — an active ruleset on each `main` with empty `bypass_actors` (binds admins) requires the CI checks + a non-author approving review + an up-to-date base and blocks force-push/deletion. `operations/gated_merge.sh` is the mandated client-side merge path; GitHub **secret-scanning + push-protection** were enabled (free on public repos). **Fleet-keeper (T1.3):** `operations/fleet_keeper.py` runs every 600s via launchd `com.oraclous.fleet-keeper`, performing the §13.3 guarded unblock-and-assign sweep and ready-work intake automatically (fail-closed on destructive/`[needs-human]`/unverifiable-prose), digesting stalls to `/tmp/fleet-keeper.log`. **§19 decomposition checklist (T2):** product-planner applies a flatter-decomposition checklist at the brief gate (vertical slices, one-owner-one-file-surface, no micro-tickets, right-size 1–3 PRs). **§20 enforced-mechanisms registry:** a single table mapping each rule to the mechanism that enforces it. |
| Why | Across R2/R3 the team kept hitting failing CIs and a dead-ending board despite repeated rule additions, because the rules were discipline, not enforcement: the documented pre-push gate wasn't a hook and under-specified the checks, "ready" work stranded ownerless, cleared blocks stayed blocked, and nothing prevented a red/unreviewed PR from merging. The acute blocker turned out to be a GitHub Actions billing wall (free-tier minutes exhausted) that no rule could clear. Going public fixed billing **and** enabled true server-side gating; the hooks, ruleset, and fleet-keeper turn the prior prose into mechanisms that fail closed. |
| Approved by | CTO (technical authority); tech-lead (Reza Jahankohan) — authorised making the repos public |
| Effective from | 4 June 2026 |
| Rollback considered | Partial. Rulesets/hooks/fleet-keeper are reversible (delete ruleset, unset hooksPath, `launchctl unload`). Making the repos **public** is the consequential, less-reversible step (history is now exposed); a full git-history secret scan is the recommended follow-up. Rollback to private would re-impose the free-tier Actions wall and remove server-side gating. |

Surfaces synced together for this change: **ORAA-4** (the contract, rev14 — §6/§13.1/§13.3 updated to reference the mechanisms; new §19 + §20), **14 agent bundles** (live instances, incl. CTO) + **11 roster templates** (uniform mechanisms pointer), these KB engineering docs (`git-workflow.md`, this change-log; see also `operations/fleet-keeper.md`), and the three repo CLAUDE.md files. New tooling lives in `oraclous-knowledge/operations/` (`fleet_keeper.py`, `gated_merge.sh`, `fleet-keeper.md`, `com.oraclous.fleet-keeper.plist`).

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
