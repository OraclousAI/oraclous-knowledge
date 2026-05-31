# ADR-010 — Test-Driven Development with Test-Author Agent

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Decision

The platform's development workflow is test-driven with a dedicated **test-author** agent. Every story passes through these gates:

1. **Backlog → Ready**: product-planner authors the brief; architects review and approve.
2. **Ready → Tests Authoring**: test-author picks up the story.
3. **Tests Authoring → Tests Review**: test-author opens a `[tests]` PR with failing tests only.
4. **Tests Review → Implementation**: be-test-reviewer approves; tests merge.
5. **Implementation → Code Review**: implementer opens a `[impl]` PR making the tests pass.
6. **Code Review → Done**: code-reviewer, qa-engineer, architects approve; tech-lead signs off.

Implementers may not modify merged tests to make them pass.
