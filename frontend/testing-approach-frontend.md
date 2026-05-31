---
confluence_id: "294936"
title: "Testing Approach (Frontend)"
---

# Testing Approach (Frontend)

How the Oraclous frontend is tested. The principles match the backend's TDD posture (see Test Strategy under 03. Engineering) but the tools and trade-offs differ for a UI.

## Test pyramid

* **Unit (Vitest)** — fast, isolated; cover utilities, hooks, reducers, zod schemas, pure logic. Bulk of tests.
* **Component (Vitest + Testing Library)** — render in jsdom; cover component behaviour with mocked data layer. Moderate count.
* **End-to-end (Playwright)** — run against a real backend (or a high-fidelity mock backend); cover critical user journeys. Small count, high value.

The shape is a pyramid, not an hourglass and not an inverted pyramid. E2E tests are expensive; we use them where they earn it (auth, compile, execute, the few flows where regression would be catastrophic).

## What gets tested at which level

**Unit-level (Vitest)**

* Pure utility functions
* Custom hooks (using `@testing-library/react`'s `renderHook`)
* Zustand store logic
* Zod schemas (round-trip parse/serialise)
* Selectors and derived state

**Component-level (Vitest + Testing Library)**

* Component behaviour given props (data display, conditional rendering, callbacks invoked)
* Form validation paths
* Error and loading states
* Accessibility behaviour (focus management, keyboard navigation)

**End-to-end (Playwright)**

* Authentication flow (login, logout, session expiry)
* Harness compile end-to-end
* Harness execute end-to-end (smoke; not every actor path)
* Task board interactions (HITL-relevant)
* Knowledge graph view (loading, navigating, basic query)
* Cross-workspace traversal UI

## Conventions

* **Tests live next to source** — `harness-card.tsx` next to `harness-card.test.tsx`; co-location aids discovery
* **Test names describe behaviour** — "shows error when manifest is invalid" not "test1"
* **Use Testing Library's user-event** — `userEvent.click()` over `fireEvent`; real user interactions
* **Query by accessible role first** — `getByRole('button', { name: 'Compile' })`; falling back to `getByText`, then `getByTestId` as a last resort
* **No snapshot tests by default** — snapshots are brittle and obscure intent; allowed only for tightly controlled known shapes (e.g. zod schema output)
* **Mock the network layer, not the components** — use MSW (Mock Service Worker) for component tests so the typed fetcher remains under test

## Network mocking

* **MSW (Mock Service Worker)** — intercepts fetch at the network layer
* **Handlers live in** `src/test/handlers/` — organised by resource
* **OpenAPI-aligned mock shapes** — mock responses validate against the generated types

## E2E posture

* **Run against staging or local stack** — Playwright targets either a staging deployment or a `docker-compose` stack from `OraclousAI/oraclous-backend`
* **Deterministic seed data** — every E2E test starts from a known seed; tests do not depend on side effects of other tests
* **Trace capture on failure** — Playwright traces are saved as CI artifacts
* **Parallelism** — tests are independent; CI runs them in parallel with no cross-test state

## What this page will cover

* **Examples of each test level** — annotated code samples for unit, component, E2E
* **MSW handler examples** — typical patterns for query and mutation mocks
* **Playwright fixture patterns** — authenticated user fixture, workspace fixture, harness fixture
* **Accessibility testing** — automated checks via `axe-core` + manual checks on PR
* **Visual regression** — considered but not required for v1; revisited as design system stabilises
* **CI integration** — Vitest in PR checks, Playwright in scheduled and pre-deploy runs

## Cross-references to backend testing

* **TDD enforcement is uniform** — backend and frontend both follow TDD (tests in a separate PR before implementation per ADR-010); the test-author agent serves both
* **Contract tests live with the backend** — schema-level contract tests run in the backend repo; the frontend consumes generated types and trusts the contract

## Related references

* **Test Strategy (under 03. Engineering)** — the platform-wide testing posture
* **ADR-010** — TDD with test-author agent
* **Frontend Stack Reference** — Vitest, Playwright, Testing Library versions
* **State and Data Patterns** — what gets mocked for component tests
