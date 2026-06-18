---
confluence_id: "393465"
title: "PR Conventions"
---

# PR Conventions

This page defines the structure, sizing, and review expectations for pull requests in both repositories. It complements the Git Workflow page (which covers branching and commits) by focusing on the _review experience_.

> **⚠️ PR-BUNDLING LAW (non-negotiable).** **Never ship a one-commit-per-PR stream.** "One commit per concern" means **multiple commits inside ONE PR** — NOT one PR per commit. Bundle related concerns into a single PR: CI (~6 min) + non-author review + redeploy run **once per PR**, so opening a separate PR for each commit multiplies that cost and wastes wall-clock. An issue with N sub-tasks ships as **one PR with N commits, never N PRs** (e.g. a `mypy + OTel + Celery` issue = one PR / three commits, not three PRs). Default to **fewer, bigger PRs**; the only exception is changes in different repos, which can't share a PR. (This sits above the line-count target below — reviewability is served by one cohesive PR with well-separated commits, not by fragmenting one issue into many tiny PRs.)

## PR sizing

PRs should be small enough to review carefully in one sitting. Concretely:

* **Target:** under 300 lines of net change (additions + deletions, excluding generated files and lock files)
* **Acceptable:** 300–600 lines, if the change is cohesive (one concern, one architectural area)
* **Requires justification:** 600+ lines, with the PR description explaining why splitting is not possible
* **Almost always too big:** 1,000+ lines, except for mechanical refactors (renames, type-only changes, generated code)

The goal is not the line count itself; the goal is reviewability. A 1,500-line PR that adds one new file with clear structure may be easier to review than a 200-line PR that touches twelve files across three services.

## PR description template

Every PR has a description following this structure:

**Summary** — one or two sentences naming what changes and why. The reader should understand the _intent_ without scrolling.

**Architectural context** — references to the architecture section or ADR that motivates the change. If the PR introduces new architectural decisions, those are written as ADRs (in this Confluence space) before the PR opens, not in the PR description.

**Test PR reference** — for implementation PRs, link to the test-author PR that this implements against. Show that the previously-failing tests now pass.

**Base-commit assertion** — for implementation PRs, assert that the branch base is **at or after the `main` commit where the `[tests]` PR merged** (the merge SHA the test-author recorded on the story). Per ADR-010 the tests are authored first by a different agent and merge first; the impl PR must branch from or rebase onto that exact merge commit *before opening* so the two PRs stay independent without producing add/add conflicts. A reviewer (be-test-reviewer / code-reviewer) rejects an impl PR whose base predates the recorded merge SHA. See the Git Workflow page's "Branch from merged tests" section. **Do not combine tests and implementation into one PR to sidestep this** — that defeats ADR-010's two-PR independence.

**Scope of change** — bulleted list of what changed at the architectural or service-boundary level. Not a line-by-line diff explanation; the diff is the diff.

**Out of scope** — explicit list of things the PR deliberately does _not_ do. Prevents reviewer scope creep ("could you also fix X while you're in here?") and documents the limited intent.

**Testing notes** — any non-obvious aspects of how the change is tested (specific markers run, manual steps for integration tests, etc.).

**Deployment notes** — anything special the devops-implementer needs to know (migration scripts, feature flags, ordering constraints).

## Open the PR ready — pre-open readiness

A PR is opened **ready for review**, not opened so a reviewer can find what's wrong with it. Before the author marks a PR ready, the branch MUST satisfy all three of:

* **Clean on the local pre-push gate** — the cheap `quality`-job checks pass locally.
* **Green on CI** — the branch's CI run is passing, not pending or red.
* **Rebased onto current `main`** — neither `BEHIND` nor `DIRTY` (and, for `[impl]` PRs, base at or after the recorded `[tests]` merge SHA).

The **opening author owns all three.** A reviewer must never be the first to discover red CI or a needed rebase; if they do, that is an author failure, fixed **in place** on the same branch — not a `[fix]`/`[rebase]` ticket and not the reviewer's job. See the Git Workflow page's "Pre-open readiness" section and the mergeability gate in the Definition of Done; pre-open readiness is the same discipline applied at the moment the PR first becomes reviewable.

## No attribution anywhere in a PR

Attribution — `Co-Authored-By:`, `Generated-with:`, robot-emoji lines, tool credit, or any equivalent — is **forbidden in the PR title, the PR description, and PR comments**, exactly as it is forbidden in commit messages (see the Git Workflow page). There is no PR surface on which it is acceptable. The CTO greps both the commit range **and** the PR body before merge; a match blocks the merge until the author strips it and re-pushes.

## Review expectations

The code-reviewer (always) reviews for:

* Architecture conformance (does this respect the four-layer model and named ADRs?)
* Test alignment (does the implementation actually satisfy the merged test PR?)
* Code quality (readability, naming, error handling, edge cases)
* Performance and security implications visible in the diff

The security-architect (when security markers apply) reviews for:

* Isolation guarantees preserved (no query path missing `organization_id` or `graph_id`)
* Credential handling (no plaintext leakage, no logging of secrets)
* Threat catalogue alignment (does the change introduce any of the threats in Section 6.5?)

The solution-architect (when architectural boundaries are touched) reviews for:

* Layer respect (no Layer 4 code reaching into Layer 1 internals)
* Service boundary contracts (cross-service calls go through documented APIs, not internals)
* OHM-shaped artifacts (capabilities, harnesses, etc. conform to the manifest spec)

The qa-engineer (before story closure) reviews for:

* Tests actually exercise the behaviour the brief describes
* Edge cases covered (empty inputs, boundary values, concurrent access, failure modes)
* Regression risk (does this PR potentially affect features outside its declared scope?)

## Review etiquette

* **Comments are observations or questions, not demands.** A reviewer saying "I'd find this clearer as X" is a suggestion; the author can accept or push back with reasoning.
* **Blocking changes are explicit.** A reviewer who believes a change must not merge as-is uses GitHub's "Request changes" status, not just a comment.
* **Author has the final say within their PR's scope.** Reviewers who think the architecture should be different escalate to an ADR or doc revision, not to a PR comment thread.
* **Reviews happen within 24 working hours** of the PR being marked ready. PRs that age without review are escalated to tech-lead.

## When PRs sit too long

A PR open for more than three working days without merge is reviewed for:

* Is it blocked on a review? — ping the reviewer; escalate if unresponsive
* Is it blocked on a question the author hasn't answered? — close or update
* Has `main` moved significantly under it? — rebase
* Is it the wrong size or scope? — split or close in favour of a fresh PR

Long-lived PRs are an anti-pattern in trunk-based development. They accumulate merge conflicts, lose context, and discourage future small PRs.

## Dedup before opening a fix ticket

Before opening a `[fix]`, `[fix-lint]`, `[regression]`, or `[rebase]` issue, **search the open issues for the same PR + the same problem**. If one already exists, **extend it** — add the new occurrence, context, or failing check to the existing issue — rather than creating a duplicate.

Duplicate fix tickets are a recurring source of churn: two issues track one problem, two agents claim them, and the board misrepresents how much real work is outstanding. One problem on one PR is one issue.

## Draft PRs

Draft PRs are encouraged for early feedback or for parking work-in-progress that needs to survive an environment change. Draft PRs do not require reviews and do not appear in review queues. When ready for review, the author marks the PR as ready and requests reviewers.

## Stacked PRs

For changes that genuinely cannot be split into independent PRs (rare), stacked PRs are acceptable: PR B branches off PR A, PR C branches off PR B, etc. Each PR in the stack is reviewed independently. The stack merges bottom-up; each merge triggers a rebase of the PR above.

Stacked PRs are an advanced pattern and should be rare. Prefer splitting work to be genuinely independent where possible.

## R3.5 PR & decomposition conventions

R3.5 rebuilds every service **real, end-to-end, per service** (ORAA-4 §23). The decomposition rules below override the generic PR-sizing guidance above for R3.5 service work: a vertical slice that genuinely cuts all layers will routinely exceed 300 lines, and that is correct — reviewability comes from the slice being _cohesive_ (one concern through every layer), not from a line ceiling.

**One service = one deliverable, in ≤ 6 coarse vertical slices.** A service is decomposed into at most six slices. Each slice:

* **Cuts all layers** — `routes/` → `services/` → `repositories/`/`domain/` → `schema/`, per the [Service Architecture Standard](service-architecture-standard.md) (ORAA-4 §21). A slice is a working end-to-end path, not a single layer.
* **Ends in a passing smoke** — the slice is not complete until `services/<svc>/tests/smoke/smoke.sh` exercises the new path against real substrate (testcontainers / docker compose) and passes in the `r3_5_gate` CI job.
* **Is a single `[tests]` + `[impl]` PR pair** — the test-author authors and merges the `[tests]` PR first, the implementer branches from that merge SHA (ADR-010; see the **Base-commit assertion** above), and the pair lands the whole slice. No third PR to "finish" a slice.

**Micro-tickets are forbidden** (ORAA-4 §23). Do **not** open:

* a PR per file or per import,
* a PR for a single endpoint _shell_ (a route with no service logic behind it),
* a giant interlocked task graph of one-layer tickets that only integrates at the end.

These produce hollow, stub-shaped increments — exactly the failure R3.5 exists to undo. If a slice feels too large for one pair, the service likely needs fewer, better-drawn slices, not more tickets.

**A service PR set is not done until the §22 per-service DoD passes.** Merging the six slices' PRs green is **not** completion. The service is done only when all eight gates of the [hardened per-service Definition of Done](definition-of-done.md) (ORAA-4 §22) pass: structurally conformant; not hollow (`check_no_stubs` zero findings, `claimed_done` flipped in `tools/lint/service_status.yaml`); it runs (docker compose healthy, `GET /health` → 200); real endpoints (integration vs real substrate, no stub/501); end-to-end smoke vs real substrate; and **Reza personally tests it and signs off**. The service's issue carries `needs-human` until Reza accepts — no service is done while `needs-human` is set, and the next dependent service does not start until the prior one is signed off.
