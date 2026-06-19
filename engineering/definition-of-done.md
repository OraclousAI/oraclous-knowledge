---
confluence_id: "66010"
title: "Definition of Done"
---

# Definition of Done

This page enumerates the gates a story must clear before it can move to **Done** on the Kanban board. Sign-off gates are owned by specific agent roles (see Agent Team Roster). A story that fails any gate stays in its current column until the gate clears.

## Hardened per-service Definition of Done (R3.5 — the gate that matters now)

R2/R3 shipped **hollow** — stub endpoints and `raise NotImplementedError` passed the story-level DoD because the tests were written against the stubs. R3.5 adds a **service-level** DoD so that can never happen again. This is the authoritative narrative of operating-contract **§22**; when this and ORAA-4 §22 diverge, ORAA-4 wins.

For R3.5, a **SERVICE** is Done only when **all 8 gates** pass. **"Merged PR + green stub-tests" satisfies NONE of gates 2–6.**

1. **Structurally conformant** — `check_service_structure` + the per-service import contract pass ([Service Architecture Standard](./service-architecture-standard.md), §21).
2. **Not hollow** — the service is flipped to `claimed_done: true` in `tools/lint/service_status.yaml` and `check_no_stubs` (HOL001–005) returns **zero** findings over its non-test src: no `raise NotImplementedError`, no `_stub_`, no `501` route returns, no `TODO: implement`, no pass-only / `return None|[]|{}|False`-only bodies.
3. **It runs** — `docker compose up <svc>` reaches healthy; `GET /health` returns 200.
4. **Real endpoints** — every endpoint returns a real, persistence-backed response (no stub/501), verified by the integration suite against **real substrate via testcontainers**.
5. **End-to-end smoke vs real substrate** — a checked-in `services/<svc>/tests/smoke/smoke.sh` exercises the actual feature top-to-bottom against the running stack (e.g. ingest a file → see real nodes in Neo4j → read them back). It runs in CI as the docker-required **`r3_5_gate`** job (modelled on the existing `r2-gate`) and is documented in the service README.
6. **Reza personally tests it and signs off** — the CTO hands Reza the running stack + the smoke runbook; the GitHub issue carries the **`needs-human`** label until Reza runs/accepts the smoke himself. **No service is R3.5-Done while `needs-human` is set.**

Gates 1–5 are mechanical (CI-enforceable); gate 6 is the hard human gate. A smoke test that hits a stub/mock instead of real substrate does not count. Closing the service's R3.5 issue while `needs-human` is set is forbidden.

The story-level checklist below still applies to each slice within a service.

---

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
- [ ] The PR was **mergeable** (`mergeable = MERGEABLE`, clean merge state) — a green CI run alone is not enough
- [ ] On completing each stage, the issue was **handed off to its next named owner** (see "The flow is part of Done") — no stage ended with the issue left parked
- [ ] **`docker-required` integration tests ran on Docker** where the functionality is multi-service/integration (see "Docker-tested functionality") — never skipped
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

## The flow is part of Done — the handoff chain

A story is not Done when the *code* is finished; it is Done when it has travelled the full handoff chain and reached merge. The flow itself is a Done criterion. Every story moves through this sequence of named owners:

1. **product-planner / architects** — brief, decomposition, architecture review to Ready.
2. **test-author** — writes the `[tests]` PR (ADR-010), which merges first.
3. **be-test-reviewer** (and **security-architect** if the CTO flagged the story security-touching) — reviews the `[tests]` PR at the Tests Review gate.
4. **backend-implementer / frontend-implementer** — writes the `[impl]` PR against the merged tests.
5. **code-reviewer + qa-engineer** (and **solution-architect / security-architect** if the change touches an architectural or threat surface) — review the implementation.
6. **CTO** — merges.

**At each stage, the acting agent MUST reassign the issue to the next named owner on completion.** Finishing your part is not the end of your obligation; *handing off* is. An agent that finishes its part — **or that wakes, picks up an issue, and finds nothing for it to do** — MUST either hand the issue to its next owner or escalate it. It must **never** end its run leaving the issue parked on itself with no owner advancing it.

A **parked, fully-worked issue** — work complete, nobody assigned to carry it forward — is the **single biggest cause of stalls** on the board. The whole chain can be green and the story still never ships because no one was told it was their turn. Treat "did I hand this off?" as the last question of every run.

## Conflicts and misalignments — fold, don't spawn

When work surfaces a **small conflict or misalignment** with the brief or the tests — a minor mismatch, an off-by-one in an assertion's expectation, a brief detail that doesn't quite line up — the fix belongs **in the current PR / current run**, not in a new `[fix]` ticket. Fold it in and keep moving.

A new (and deduped — see PR Conventions) issue is created **only for genuinely new scope**: work that is materially beyond what the current story set out to do. The test is "is this the same piece of work, or a different one?" — not "is this annoying to fix here?"

The one exception: a **wrong test** does not get quietly patched by the implementer. Per ADR-010 the tests are authored first, by a different agent; if a test is wrong, it goes **back to test-author** to correct, preserving the two-PR independence. The implementer folds in alignment fixes to *their own* code, not to the test contract.

## Docker-tested functionality

Multi-service and integration functionality is flagged **`docker-required`** — by the task creator at decomposition time, or by the CTO when the cross-service nature surfaces later. For a `docker-required` task, the integration tests **run on Docker**; that is how the functionality is actually exercised.

If the Docker daemon is **not running** when such a task needs its integration tests, the agent does **not** skip the tests and does **not** mark the task done on the strength of the unit tests alone. It **raises an error and BLOCKS the task `needs-human`** so the environment can be fixed. Silently skipping Docker-gated tests — or declaring Done without them — is forbidden: it ships untested integration paths under a green-looking board.

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
