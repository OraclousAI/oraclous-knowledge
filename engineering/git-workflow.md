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
