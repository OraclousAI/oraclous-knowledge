---
confluence_id: "720940"
title: "Test Strategy"
---

# Test Strategy

The platform's test strategy is built around the TDD workflow (ADR-010) and the security continuity commitment from Section 8 of the architecture. This page is the reference for how tests are organised, marked, and gated.

## Test pyramid

The platform uses a conventional pyramid with four levels:

1. **Unit tests** (`@pytest.mark.unit` / Vitest `describe` blocks) — fast, isolated, no external dependencies. Every service module has unit tests for its pure logic.
2. **Integration tests** (`@pytest.mark.integration` / Vitest integration suites) — exercise multiple modules together, possibly with a real database, real Redis, real Neo4j. Each service has integration tests for its API surface.
3. **End-to-end tests** (Playwright for frontend; pytest with full service stack for backend) — exercise a full user flow across services. Reserved for critical paths; not every story has an end-to-end test.
4. **Security and isolation tests** (`@pytest.mark.security` / `@pytest.mark.isolation`) — adversarial tests that attempt to breach platform guarantees. Run as CI gate on every PR.

## Test markers

Backend tests are marked with pytest markers for selective execution. There are two axes: a **level** marker (how the test runs) and, for threat-driven tests, a **threat-dimension** marker (which threat surface it exercises). They compose.

### Level markers

* `@pytest.mark.unit` — fast, isolated unit tests
* `@pytest.mark.integration` — multi-module integration tests
* `@pytest.mark.security` — adversarial security tests (Cypher injection, prompt injection, schema confusion, etc.)
* `@pytest.mark.isolation` — multi-tenant isolation tests (`graph_id` and per-workspace separation)
* `@pytest.mark.organization_isolation` — organisation-level isolation tests (the outer cloud-mode boundary)
* `@pytest.mark.byom` — LLM provider integration tests across the three v1 protocol shapes
* `@pytest.mark.slow` — tests that take more than 10 seconds (excluded from pre-commit runs)

### Threat-dimension markers

Threat-driven tests additionally carry a marker naming the threat surface they exercise; it composes with a level marker (for example `@pytest.mark.security` together with `@pytest.mark.rebac`). These markers are mandated by the [Structured Threat Catalogue](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983129) `required_tests`, which is authoritative for which dimension marker a test for a given threat must carry. The full set:

* `@pytest.mark.rebac` — ReBAC access-decision and traversal tests, fail-closed on ambiguous resolution (T1-M2, T2)
* `@pytest.mark.audit` — structured audit-event emission and retention (T7; T6-M3)
* `@pytest.mark.race` — relation-revocation and other concurrency races (T2-M2)
* `@pytest.mark.tool_dispatch` — validation of model-returned tool calls against the harness allowlist (T3-M3)
* `@pytest.mark.capability_integrity` — capability-descriptor hashing and tamper rejection (T4-M1)
* `@pytest.mark.federation` — federated capability resolution gated by cross-organisation agreements (T4-M2; ADR-004)
* `@pytest.mark.ohm_signature` — OHM signature verification (T5)
* `@pytest.mark.operator_separation` — operator-separation guarantees in cloud-hosted mode (T6; ADR-008)

Every marker a test uses must be registered in the repo-root `pytest.ini`, which runs `--strict-markers`; the threat-dimension markers are registered there alongside the level markers.

Frontend tests use Vitest for unit and integration, Playwright for end-to-end.

## CI gates

Every PR must pass:

* All `unit` tests on every service touched
* All `integration` tests on every service touched
* All `security`, `isolation`, and `organization_isolation` tests **globally** — these are platform-wide guarantees and run on every PR regardless of which service is touched
* Type checking (mypy for Python, tsc for TypeScript) where configured
* Lint and format checks (ruff for Python, Biome for TypeScript)

A PR cannot merge with any of these failing. Skipping a test requires an explicit annotation and a linked ticket explaining why and when the skip will be removed.

## Test authorship

Per ADR-010, the test-author agent writes the test suite for a story in its own PR, **before** implementation begins. The test PR is reviewed and merged first; the implementation PR references it and shows the previously-failing tests now passing.

### Two-PR independence is load-bearing — do not collapse it

ADR-010's value comes from the tests being written **first, by a different agent, and left untouched by the implementer**. The implementer cannot weaken a test to make their code pass, because they do not own the test PR and it has already merged. This independence is the whole point; it is what makes the green test signal trustworthy.

A recurring temptation is to "simplify" the workflow by putting tests and implementation in a single PR. **Do not.** Combining them returns ownership of the tests to the implementer and destroys the independence guarantee.

The genuine problem that the single-PR idea was trying to solve — add/add conflicts between the tests branch and the implementation branch — is solved a different way, **without** sacrificing independence: the **branch-from-merged-tests** sequencing rule. The implementation PR branches from / rebases onto the *exact `main` commit where the `[tests]` PR merged* before it opens, so the implementation is built on top of the merged tests rather than alongside them. The test-author records that merge SHA on the story; the implementer asserts their base is at or after it; reviewers reject an impl PR whose base predates it. Full mechanics are on the [Git Workflow](https://oraclous.atlassian.net/wiki/spaces/OP/pages/131103) and [PR Conventions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393465) pages.

### Behaviour, not implementation

Tests should describe **behaviour**, not **implementation**. A test that says "verify the function calls `_internal_helper` once" is brittle and tests the mechanism. A test that says "verify a user without `harness.author` permission receives 403 when posting to the compile endpoint" is durable and tests the behaviour.

## Test data and fixtures

* Fixtures live alongside test files, not in a global fixture directory, unless they are genuinely cross-test (e.g., the test database setup).
* Fixtures are deterministic — no randomness unless the test is specifically testing randomised behaviour.
* Test data references real-looking but fake values. Personally identifiable information, real API keys, real credentials never appear in test fixtures.

## When tests break

A failing test on `main` is the team's highest-priority issue. The branch is blocked from new merges until the test passes again. Whoever last merged is responsible for either fixing the test or reverting their change.

Persistently flaky tests are not tolerated. A test that is observed to fail intermittently must be either fixed (root cause addressed) or quarantined (skipped with an explicit ticket to fix). Letting flaky tests stay green-on-average undermines the entire CI signal.
