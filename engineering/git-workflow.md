---
confluence_id: "131103"
title: "Git Workflow"
---

# Git Workflow

This page defines the branching, commit, and merge conventions for the Oraclous backend and frontend repositories. The model is **trunk-based** with short-lived feature branches, optimised for the multi-agent team and the test-author-first workflow (ADR-010).

## Repositories

* `OraclousAI/oraclous-backend` — Python services (substrate, capability registry, harness runtime, execution engine, application gateway)
* `OraclousAI/oraclous-frontend` — React + TypeScript application

Both repositories live under the `OraclousAI` GitHub organisation.

## Branching model

The trunk is `main`. It is always deployable. Direct pushes to `main` are forbidden; every change flows through a PR.

Branches follow a naming convention that links them back to Jira:

* `ORA-NNN/short-description` — story or task work, where `ORA-NNN` is the Jira key
* `tests/ORA-NNN/short-description` — test-author PR for story `ORA-NNN` (per ADR-010, this PR merges first)
* `chore/short-description` — chores not tied to a Jira ticket (dependency bumps, docs, CI config)
* `hotfix/ORA-NNN/short-description` — urgent production fixes

Branches are short-lived. The expected lifespan is hours to days, not weeks. A branch that has not merged within a week of its first commit is reviewed for either rebasing onto current `main` or splitting into smaller pieces.

## Commit messages

Commit messages follow Conventional Commits. The first line is `<type>(<scope>): <description>`, where:

* `<type>` is one of `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`
* `<scope>` names the service or area (`substrate`, `registry`, `runtime`, `gateway`, `frontend`, etc.)
* `<description>` is a present-tense imperative ("add", not "added")

The body, if present, explains the _why_ not the _what_. The footer references the Jira key: `Refs: ORA-NNN` (for partial work) or `Closes: ORA-NNN` (for completion).

Example:

```
feat(substrate): add organization_id to capability table

Phase 0.5 requires organization_id on every storage primitive.
This adds the column, the parameterised filter on read/write paths,
and the migration script for existing data.

Closes: ORA-123
```

### One commit per concern

Each commit is a **single logical change**. Mixed work is split into separate commits — a refactor and the feature it enables are two commits, not one; a lint cleanup and a behaviour change are two commits, not one. If you find yourself writing "and" in the imperative subject, that is a signal to split.

Commits carry **no attribution trailers**. Do not append `Co-Authored-By:`, `Generated-with:`, robot-emoji lines, or any similar trailer. For agent work the operating contract mandates the commit subject form:

```
[ORAA-xx] [agent:NAME] <imperative>
```

where `ORAA-xx` is the issue key, `NAME` is the persona acting, and the imperative is present-tense ("add", not "added"). This is enforced by a commit-msg hook. (This agent form coexists with Conventional Commits for the squashed merge record; the per-commit agent form is what the implementer writes locally.)

### Attribution is forbidden everywhere, and the hook is wired in every repo

The no-attribution rule is **not limited to commit subjects**. Attribution — `Co-Authored-By:`, `Generated-with:`, robot-emoji lines, tool credit, or any equivalent — is forbidden in **commit messages, PR titles, PR descriptions, and comments** alike. There is no surface on which it is acceptable.

Enforcement is two-layered:

* **A wired `commit-msg` hook.** Every repository sets `core.hooksPath=.githooks` (committed to the repo), so the hook that rejects malformed subjects and attribution trailers runs on every commit for every clone — not on an opt-in basis. A repo whose `core.hooksPath` is unset, or whose `.githooks` is missing, is itself a defect to fix, because it means the gate is silently off.
* **A CTO pre-merge grep.** Before merging, the CTO greps the full commit range **and** the PR body for attribution patterns. A match blocks the merge; the implementer strips the attribution and re-pushes (fixed in place — not a new ticket).

## Pull requests

Every PR description includes:

* A reference to the Jira ticket (`ORA-NNN`)
* A reference to the architecture section or ADR that motivates the change (where applicable)
* A test-PR reference (for implementation PRs) showing which prior test PR this implements against
* A summary of what changed at the architectural level (not a code diff in prose — the diff itself tells that story)

Per the agent team roster, sign-off gates are: code-reviewer (always), security-architect (when security/isolation/organization_isolation markers apply), solution-architect (when architectural boundaries are touched), qa-engineer (before story closure), and tech-lead (final).

## Merge strategy

PRs merge via **squash-merge** by default. The squashed commit message becomes the canonical record of the change on `main`. This keeps `main`'s history linear and reviewable.

Exceptions:

* Multi-commit PRs with logically separable commits (e.g., refactor commit + feature commit) can merge with **rebase-merge** to preserve the granularity. The PR description must explicitly request this.
* Merge commits (`merge --no-ff`) are never used. The history stays linear.

The mandated merge command is `oraclous-knowledge/operations/gated_merge.sh <backend|frontend|knowledge> <pr#>` — it re-checks CI-green + a non-author approval + an up-to-date base, then calls `gh pr merge --delete-branch`. It is the client-side companion to the `main` ruleset (see Protected branches): the ruleset blocks a bad merge server-side, `gated_merge.sh` refuses to attempt one and reports the reason.

## Rebasing onto main

Branches rebase onto `main` rather than merging `main` into them. Force-push to the branch is fine (and expected after rebase). Force-push to `main` is impossible (protected branch rule).

When a rebase produces conflicts, the branch author resolves them on their branch and re-runs the test suite locally before pushing again.

## Pre-push gate

Before **any** `git push`, run locally the same cheap checks that CI's `quality` job runs, and push only if they are clean. This catches the failures that otherwise burn a CI round-trip and an `[agent:NAME]` re-push.

As of ORAA-250 (2026-06-04) this gate is an **enforced git hook**, not a manual step: each repo ships `.githooks/pre-push` and sets `core.hooksPath=.githooks`, so a push that fails the checks is **blocked locally**. The backend hook mirrors the **full CI `quality` job** (not just a subset):

* **Backend:** `ruff check`, `ruff format --check`, `mypy tools`, `lint-imports` (import contracts), org-scoping + org-scoped-labels-schema linters, test-import hygiene, neo4j write-role check, and contract-fixture checksum verification — the same nine checks CI runs.
* **Frontend:** `lint`, `typecheck`, `format:check` (the `package.json` scripts that exist).
* **Knowledge:** `build_kb_index.py --check` (KB index/llms.txt currency).

The hook imports every test module on the backend path too, surfacing function-local-import violations and collection-time errors before they reach CI.

A failure found by the pre-push gate is the **implementer's to fix before re-pushing** — it does not become a new `[fix]` issue. The gate exists precisely so the push is clean the first time.

## R3.5 enforcement: structure, no-stubs, and import contracts at push and merge

The R3.5 release (ORAA-4 §21–§23) exists because R2/R3 shipped **hollow** — stub endpoints, `raise NotImplementedError`, a service class defined inside a route file, and ~6,300 LOC of real logic left dead in `oraclous-core-service/`. To make "merged PR + green tests" no longer satisfy a hollow service, R3.5 adds two enforcement surfaces — one cheap, one docker-required — on top of the existing pre-push gate and `main` ruleset.

### The `lint` job (cheap; mirrored in `pre-push`)

A CI `lint` job — also mirrored in `.githooks/pre-push` so it blocks locally before a push — runs three checks that enforce the [canonical service architecture standard](service-architecture-standard.md) (ORAA-4 §21):

* **`tools/lint/check_service_structure.py` (STR001–005)** — asserts the layered package shape: `main.py` is `app = create_app()` only, `app/factory.py` wires with no handlers/logic, no business logic in route handlers, no non-`BaseModel` class defs or DB drivers in `routes/`, and repositories are the only DB/Neo4j/Redis access.
* **`tools/lint/check_no_stubs.py` (HOL001–005)** — fails on stub endpoints, `NotImplementedError`, `501`/`pass`-body handlers, and other hollowness markers. It is **gated on `tools/lint/service_status.yaml`**: a service's no-stub findings become blocking once its `claimed_done` flag flips, so a service is held to the no-hollowness bar exactly when it claims to be finished.
* **Per-service import contracts** — each service declares `[tool.importlinter]` contracts in its `pyproject.toml` enforcing the one-way layer dependency `routes → services → domain → repositories → core`, checked by `lint-imports` (the same tool the backend pre-push already runs).

These are the three non-negotiable rules of §21, mechanized: no business logic in routes, no non-`BaseModel`/DB-driver code in `routes/`, repositories as the sole data-access layer.

### The `r3_5_gate` job (docker-required)

R3.5's hardened per-service Definition of Done (ORAA-4 §22) has eight gates, and "merged PR + green stub-tests" satisfies **none** of gates 2–6. The first three (structure, no-stubs, import contracts) are covered by the `lint` job above; the runtime gates are covered by a new **docker-required `r3_5_gate` CI job**, modelled on the existing `r2-gate`. It runs:

* **structure + no-stub + import** (the `lint` checks, re-asserted in the gate),
* **docker-up** — `docker compose up` healthy, `GET /health` returns 200,
* **integration** — real endpoints exercised against real substrate via testcontainers (no stub/`501`),
* **smoke** — `services/<svc>/tests/smoke/smoke.sh`, an end-to-end pass against the real substrate.

Because it requires Docker, the §9.3 docker-required / block-if-Docker-down rule applies: if Docker is unavailable the gate blocks rather than passing vacuously. The two human-facing gates of §22 sit outside CI: the service stays `claimed_done: false` in `service_status.yaml` until it is genuinely not hollow, and the issue carries `needs-human` until **Reza personally tests and signs off** — no service is done while `needs-human` is set.

### R3.5 work ships as coarse vertical slices, not micro-tickets

Per ORAA-4 §23, one service is **one deliverable**, decomposed into **at most six coarse vertical slices**. Each slice cuts through all layers (`routes → services → repositories`), ends in a passing smoke, and is a single `[tests]` + `[impl]` pair — the same two-PR shape ADR-010 mandates elsewhere. There is **no ticket per file, per import, or per endpoint-shell**, and no giant interlocked task graph. This keeps the §21/§22 gates above attached to a slice that actually runs end-to-end, rather than to a shell that only compiles.

## Pre-open readiness — a PR is opened ready, not opened to be fixed

The pre-push gate keeps each *push* clean. Pre-open readiness raises the bar one level: before the implementer **opens a PR for review** — not merely before merge — the branch MUST be all three of:

1. **Clean on the local pre-push gate** (the cheap `quality`-job checks above pass locally).
2. **Green on CI** (the pushed branch's CI run is passing, not pending or red).
3. **Rebased onto current `main`** — neither `BEHIND` nor `DIRTY`. The branch base is the live tip of `main` (and, for `[impl]` PRs, at or after the recorded `[tests]` merge SHA).

The **opening implementer owns all three.** A reviewer must **never** be the one to discover red CI or a needed rebase: the moment a reviewer is asked to look at a branch, the branch's own house is already in order. Opening a red or behind PR is an **implementer failure to fix in place** — the implementer makes CI green and rebases onto current `main` on the same branch — **not** a new `[fix]`/`[rebase]` ticket and not a job handed to the reviewer.

This is the opening counterpart to the **mergeability gate** in the [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010): the mergeability gate is re-checked at the `in_review` handoff and again at merge; pre-open readiness is the same three-part discipline applied earlier still, at the instant the PR first becomes reviewable.

## Branch from merged tests (impl PRs)

Per ADR-010 the `[tests]` PR for a story is authored first, by a different agent, and merges before implementation begins (see Test Strategy). To keep the two PRs independent **and** conflict-free, an `[impl]` PR MUST branch from — or be rebased onto — the **exact `main` commit where its `[tests]` PR merged**, *before* the impl PR opens.

* The test-author records that merge SHA on the story when the `[tests]` PR merges.
* The implementer asserts their branch base is **at or after** that SHA before opening the impl PR.
* The be-test-reviewer / code-reviewer **reject** an impl PR whose base predates the recorded merge SHA.

This sequencing rule does not collapse the two PRs into one — ADR-010's two-PR independence (tests written first, by a different agent, untouched by the implementer) stays intact. It only fixes the base-commit sequencing that previously produced add/add conflicts between the tests and the implementation. **Do not "fix" this by combining tests and implementation into a single PR.**

## Rebase on merge

When any PR merges to `main`, open PRs whose changes **overlap the same files** get a rebase task before they are reviewed. The merged change has moved their base; reviewing or merging them against a stale base risks silent conflicts and re-introduced regressions. The implementer of the overlapping PR owns the rebase (see the mergeability gate in the Definition of Done — `DIRTY`/`BEHIND` is exactly this situation).

> **See also:** the **mergeability gate** in the [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010). A green CI run is necessary but not sufficient to merge; the PR must also be GitHub-`MERGEABLE` with a clean merge state.

## Protected branches

`main` is protected by an **active GitHub ruleset** on each repo (ORAA-250, 2026-06-04). The repos are public, so rulesets are enforced server-side with an empty `bypass_actors` list — the rules apply to **everyone, including org admins**. There is no manual-discipline gap; a red, unreviewed, or stale PR **cannot** be merged. Required CI contexts: backend `quality`/`lint`/`integration`/`security-tests` plus the docker-required `r3_5_gate` (see [R3.5 enforcement](#r35-enforcement-structure-no-stubs-and-import-contracts-at-push-and-merge)); frontend `Lint / Type-check / Format` + the five gate jobs (`oraclous-knowledge` has no CI workflow — its quality is covered by the `pre-push` hook + review). The legacy bullet list below describes the same intent the ruleset now enforces:

* Direct pushes blocked
* PRs require at least one approving review (more depending on sign-off gates)
* All CI checks must pass (unit, integration, security/isolation/organization_isolation gates)
* Branch must be up to date with `main` before merging
* Force-push and deletion blocked

## Tags and releases

Releases follow semver: `v0.1.0`, `v0.2.0`, etc. The architecture's Phase 0.5 ships as `v0.1.0`; subsequent phases each bump the minor version. Patch releases (`v0.1.1`) handle bug fixes between phase boundaries.

Tags are annotated, not lightweight: `git tag -a v0.1.0 -m "Phase 0.5: Organisation tenancy and metering substrate"`.
