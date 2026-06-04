---
confluence_id: "66010"
title: "Definition of Done"
---

# Definition of Done

This page enumerates the gates a story must clear before it can move to **Done** on the Kanban board. Sign-off gates are owned by specific agent roles (see Agent Team Roster). A story that fails any gate stays in its current column until the gate clears.

## The Definition of Done checklist

A story is Done when **all** of these are true:

### Brief and tests

- [ ] The product-planner's brief is linked to the story and references the relevant architecture section(s) and ADR(s)
- [ ] The test-author PR has merged, and its tests describe the brief's acceptance criteria
- [ ] All tests in the test PR were previously failing (red) and now pass (green) after implementation

### Implementation

- [ ] Implementation PR references the merged test PR
- [ ] Implementation PR squash-merged to `main` with a Conventional Commit message
- [ ] All CI checks passed at merge time: unit, integration, security, isolation, organization_isolation, type checking, lint
- [ ] The PR cleared the **mergeability gate** (see below) before the `in_review` handoff and again before merge
- [ ] No new TODOs without a linked Jira ticket
- [ ] No new dead code or commented-out blocks

#### The mergeability gate

**CI-green is necessary but NOT sufficient.** A PR (and the issue it implements) is not "ready" on a green CI run alone — it must also be mergeable into its current base. This gate is checked **twice**: before the `in_review` handoff, and again immediately before merge.

Check it with:

```
gh pr view <n> --json mergeable,mergeStateStatus
```

The PR clears the gate only when **both**:

* `mergeable = MERGEABLE`, and
* `mergeStateStatus ∈ {CLEAN, HAS_HOOKS}`.

GitHub computes `mergeable` **asynchronously**. Right after a push, or after the base branch moves, it returns `UNKNOWN`. **Poll until it resolves** — never treat `UNKNOWN` as ready, and never merge on it.

Handling the other states:

* `DIRTY` / `BEHIND` ⇒ the branch has conflicts or has fallen behind base. **Rebase onto the current base and re-run CI**, then re-check the gate.
* `BLOCKED` ⇒ required reviews or required checks are unsatisfied. Satisfy them, then re-check.

### Review sign-offs

- [ ] code-reviewer approved
- [ ] qa-engineer validated the tests against the brief and approved
- [ ] security-architect approved (if the story is marked `security`, `isolation`, or `organization_isolation`)
- [ ] solution-architect approved (if the story touches an architectural boundary — layer interfaces, service boundaries, OHM shape)
- [ ] tech-lead final sign-off recorded

### Documentation

- [ ] Confluence documentation updated where platform behaviour changed (docs-writer)
- [ ] In-repo documentation updated where developer-facing behaviour changed (READMEs, [CLAUDE.md](http://CLAUDE.md), in-repo ADRs)
- [ ] If a new ADR was needed, the ADR is merged in Confluence before story closure

### Operational

- [ ] No new uncovered code paths in observability (logs, traces, metrics where applicable for the service)
- [ ] Migration scripts (if any) ran successfully in the staging environment
- [ ] Feature flags (if any) documented in the deployment notes
- [ ] Rollback plan documented if the change is risky

### Security posture

- [ ] No new query path missing `organization_id` or `graph_id` filter
- [ ] No new credential handling that bypasses the credential broker
- [ ] No new logging that could leak secrets (detect-secrets clean)
- [ ] No new threat surface unaccounted for in Section 6.5

## What "Done" does NOT mean

Done does not mean:

* The feature is exposed to customers (that requires a separate deployment decision)
* The work is final (subsequent stories may build on or refactor it)
* All possible edge cases are handled (only those the brief named)
* Performance is optimised (unless performance is part of the brief's acceptance criteria)

The bar is **the story does what the brief said it would do, with the platform's guarantees intact, in a form the team can review and maintain**. It is not perfection.

## Story closure procedure

1. The implementing agent moves the story to **Code Review** when the implementation PR is ready
2. Reviewers add sign-offs as they complete their reviews
3. When code-reviewer approves and CI is green, the PR merges
4. The implementing agent moves the story to **Done**, with all sign-offs recorded in the story's comments
5. The docs-writer takes the story handoff and updates Confluence as needed
6. tech-lead records final sign-off on the story; the story closes

## Unblocking dependents on closure (fail-closed)

Closing an issue often unblocks others that depend on it. Doing this carelessly strands work — a dependent gets unblocked while a predecessor it silently relied on is still open. The rule is **fail-closed**: when in doubt, the dependent stays blocked.

On closing an issue, before unblocking and assigning any dependent:

1. **Read the dependent's description for prose dependencies.** `blockedByIssueIds` is not the whole story — descriptions carry sequencing in prose ("salvage before", "hard-sequenced after", "after ORAA-NN"). Honour those.
2. **Back-fill `blockedByIssueIds`** from any prose dependency you find, so the graph matches reality.
3. **Verify every predecessor is `done`** — not merely "the one you just closed". A dependent is unblocked only when *all* of its predecessors are done.
4. **Never auto-unblock destructive or irreversible work.** Deletes, migrations, archival, retirements route to **human sign-off** (see the destructive-change protocol below), never to automatic unblocking.
5. **Ambiguous ⇒ stay blocked.** If you cannot establish that every predecessor is done, leave the dependent blocked.

Do not retry a blocked issue that has no live path to completion — **escalate** it instead of churning on it.

## Destructive-change protocol

Destructive changes — **deletes, database migrations, archival, retirements** — carry irreversible risk and are gated more strictly than ordinary work. Before such a change may leave `blocked`:

1. **Predecessor-salvage is `done` and verified.** Whatever must be preserved (data exported, behaviour re-homed, callers migrated) is complete and checked — not merely planned.
2. **Explicit HUMAN sign-off** is recorded before the issue leaves `blocked`. The CTO *sequences* destructive work but **never self-approves** it; only a human approves the destructive step.
3. **A forward-only plan exists.** Because the change cannot be cleanly rolled back, the path forward (including how to recover if it goes wrong) is documented in advance.

**Prefer reversible over irreversible.** Where the goal can be met by archival behind a flag rather than a hard deletion, choose the reversible form. Hard deletion is the last resort, not the default. (This aligns with the Release Process page's treatment of irreversible migrations as exceptional and human-approved.)

## When a story cannot be Done

If a story turns out to be larger or different than expected:

* **Split:** create new stories for the unfinished work, link them as related, and close the current story with what's actually complete
* **Replan:** if the brief itself was wrong, return the story to **Ready** with an updated brief and re-run the workflow from test-author
* **Block:** if external blockers prevent completion, move the story to **Blocked** with the blocker linked

The anti-pattern is closing a story as "Done with caveats." A story is Done or it is not. Caveats become their own stories.
