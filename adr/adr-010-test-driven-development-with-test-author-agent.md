---
confluence_id: "557078"
title: "ADR-010 — Test-Driven Development with Test-Author Agent"
---

# ADR-010 — Test-Driven Development with Test-Author Agent

## Status

| Field | Value |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Accepted</custom> |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None (founding ADR) |
| Superseded by | None |
| Driving artifact | [Test Strategy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720940) |

## Context

The v1 development model is multi-agent: many agents working in parallel, with the human (tech-lead) in the loop at gate transitions. Multi-agent development has a specific failure mode that single-developer development avoids: the agent that writes the code is also tempted to write the tests, and the tests inevitably reflect what the code happens to do rather than what the code _should_ do. The result is high test coverage and low test validity. The bugs ship.

Single-developer TDD avoids this by discipline: the developer writes the test first, watches it fail, then writes the implementation. Discipline is harder in a multi-agent system because each agent's loaded skills determine what it tries to do; if test-writing is bundled with implementation, every implementation agent will gravitate toward tests-that-fit-my-code.

The cleanest fix is structural: split test authoring and implementation between different agents, with a merge gate between them. The agent that writes the tests does not write the code; the agent that writes the code cannot modify the merged tests to make them pass. The tests become a real contract because they are written by an agent whose only goal is "tests that describe what the brief asks for", not "tests that pass next to my implementation".

The same structural split has another consequence: every story produces two PRs (tests, then implementation) with a merge between them. That doubles the number of merge events but creates an unambiguous artifact at every gate: a Tests Review PR that has been approved is an executable contract that any implementer can be measured against.

## Decision

The platform's development workflow is test-driven with a dedicated **test-author** agent. Every story passes through these gates:

1. **Backlog → Ready**: product-planner authors the brief; solution-architect and security-architect review and approve.
2. **Ready → Tests Authoring**: test-author picks up the story.
3. **Tests Authoring → Tests Review**: test-author opens a `[tests]` PR containing failing tests (and only tests).
4. **Tests Review → Implementation**: solution-architect and security-architect (if security-marked) approve the tests PR; tests merge.
5. **Implementation → Code Review**: the appropriate implementer (backend, frontend, or devops) opens a `[impl]` PR making the tests pass.
6. **Code Review → Done**: code-reviewer, qa-engineer, and any required architects approve; tech-lead signs off; implementation merges.

Constraints that make the workflow real:

* test-author writes tests against the brief, not against any proposed implementation.
* Implementers may not modify merged tests to make them pass. If a test is wrong, the implementer escalates to test-author for a corrected test (which goes through a new tests PR).
* Bug-fix stories follow the same workflow with qa-engineer playing the test-author role for the regression test (per the qa-engineer skill page).
* Tests-only PRs are required to fail before they merge (the substrate test runner enforces this).

## Alternatives considered

### A. Implementer writes tests alongside implementation (conventional model)

Familiar from most teams. Rejected because of the multi-agent failure mode: tests that fit the implementation's accidents rather than the brief's intent. A single careful human developer can avoid this with discipline; an agent system without structural separation will not.

### B. Separate test-author per implementer (frontend test-author, backend test-author, etc.)

One test-author per implementer tier. Considered as a scaling choice. Rejected for v1 because the cross-tier consistency of test discipline matters more than the per-tier specialisation. A single test-author working across tiers internalises the test taxonomy as a unit; multiple specialised test-authors would drift apart in style.

### C. Tests written by solution-architect or security-architect, not by a dedicated test-author

Have the architects write the tests as part of their review. Considered seriously because it gives the architects more direct control. Rejected because architect review is a different mode of attention than test authoring: review is reactive (scrutinise this), authoring is generative (write the contract). Bundling them creates the same kind of conflict the test-author role exists to avoid.

### D. Tests as advisory, not as gates

Have test-author propose tests; let implementers modify them as needed. Easier to operate but defeats the purpose: the gate is exactly the thing that makes tests a real contract. Rejected.

## Consequences

### Positive

* Tests describe what the brief asks for, not what an implementation happens to do. Validity rises; coverage-without-validity drops.
* Every story produces a Tests Review PR that is an executable, reviewable contract before implementation begins. Architects review tests once, then trust the contract for implementation review.
* Bug regressions become first-class artifacts: qa-engineer authors the regression test before the fix, and the fix turns it green.
* The agent team's roles are unambiguous: tests are test-author's domain, code is implementer's domain, review is reviewer's domain. Cross-role friction is structurally low because the roles do not overlap.

### Negative

* Every story is two PRs instead of one. The merge cadence doubles; the agent team adapts to that rhythm.
* The Tests Authoring gate is a real wait state: implementation cannot start until tests merge. For stories where the implementation is small and obvious, the cost is felt; the platform accepts this as the price of contract clarity.
* test-author becomes a critical path. If test-author is slow or wrong, the whole workflow stalls. Quality of test-author's outputs is monitored as a first-class concern; consciousness skills (per the test-author skill page) watch for patterns that signal degradation.

## Implementation notes

* The Tests Review gate is enforced by GitHub branch protection: `[impl]` PRs cannot merge unless the corresponding `[tests]` PR is already merged.
* The substrate test runner ships a "tests must initially fail" assertion: a `[tests]` PR with all tests passing on first run is flagged for review, on the assumption that a passing test against unimplemented code is probably a wrong test.
* Story brief format (product-planner skill) is shaped to enable test-author to write tests without clarifying questions. The brief-authoring skill is tuned for test-authorability as a first-class quality criterion.
* The Test Strategy document (Phase 1 deliverable) defines marker conventions, fixture conventions, and the categorisation of tests (unit, integration, security, isolation, audit, etc.) that test-author uses.
* Bug-fix workflow: qa-engineer authors a `[regression]` PR (with the failing test), which follows the same review process as a `[tests]` PR.

## References

* [Test Strategy](https://oraclous.atlassian.net/wiki/spaces/OP/pages/720940)
* [test-author](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294957) — the agent whose role this ADR defines
* [qa-engineer](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884874) — the test-author counterpart for regression tests
* [Definition of Done](https://oraclous.atlassian.net/wiki/spaces/OP/pages/66010) — the Kanban gates this ADR defines
* [PR Conventions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393465) — the `[tests]`, `[impl]`, `[regression]` prefix conventions
* [Agent Skills Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753852) — the agent team that operates this workflow

## Revision history

| Date | Change |
| --- | --- |
| 27 May 2026 | Rewritten to uniform ADR template. Decision unchanged; references to agent pages and Group B artifacts added. |
