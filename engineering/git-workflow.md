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

## Rebasing onto main

Branches rebase onto `main` rather than merging `main` into them. Force-push to the branch is fine (and expected after rebase). Force-push to `main` is impossible (protected branch rule).

When a rebase produces conflicts, the branch author resolves them on their branch and re-runs the test suite locally before pushing again.

## Pre-push gate

Before **any** `git push`, run locally the same cheap checks that CI's `quality` job runs, and push only if they are clean. This catches the failures that otherwise burn a CI round-trip and an `[agent:NAME]` re-push.

* **Backend:** `uv run ruff check . && uv run ruff format --check . && uv run pytest --collect-only`
* **Frontend:** the `package.json` lint, type-check, and format-check scripts.

`pytest --collect-only` is part of the gate deliberately: it imports every test module, which surfaces function-local-import violations and collection-time errors before they reach CI.

A failure found by the pre-push gate is the **implementer's to fix before re-pushing** — it does not become a new `[fix]` issue. The gate exists precisely so the push is clean the first time.

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

`main` has the following protection rules:

* Direct pushes blocked
* PRs require at least one approving review (more depending on sign-off gates)
* All CI checks must pass (unit, integration, security/isolation/organization_isolation gates)
* Branch must be up to date with `main` before merging
* Force-push and deletion blocked

## Tags and releases

Releases follow semver: `v0.1.0`, `v0.2.0`, etc. The architecture's Phase 0.5 ships as `v0.1.0`; subsequent phases each bump the minor version. Patch releases (`v0.1.1`) handle bug fixes between phase boundaries.

Tags are annotated, not lightweight: `git tag -a v0.1.0 -m "Phase 0.5: Organisation tenancy and metering substrate"`.
