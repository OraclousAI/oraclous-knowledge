# Testing Approach (Frontend)

## Test pyramid

- **Unit (Vitest)** — fast, isolated; utilities, hooks, reducers, zod schemas, pure logic
- **Component (Vitest + Testing Library)** — render in jsdom; cover component behaviour with mocked data layer
- **End-to-end (Playwright)** — run against a real backend; cover critical user journeys

## Conventions

- Tests live next to source — `harness-card.tsx` next to `harness-card.test.tsx`
- Test names describe behaviour — "shows error when manifest is invalid"
- Use Testing Library's `userEvent.click()` over `fireEvent`
- Query by accessible role first — `getByRole('button', { name: 'Compile' })`
- No snapshot tests by default
- **Mock the network layer, not the components** — use MSW (Mock Service Worker)

## E2E posture

- Run against staging or local docker-compose stack
- Deterministic seed data — every E2E test starts from a known seed
- Trace capture on failure — Playwright traces saved as CI artifacts
