# Test Strategy

The platform's test strategy is built around the TDD workflow (ADR-010) and the security continuity commitment from Section 8 of the architecture.

## Test pyramid

1. **Unit tests** (`@pytest.mark.unit` / Vitest) — fast, isolated, no external dependencies
2. **Integration tests** (`@pytest.mark.integration`) — exercise multiple modules together with real database
3. **End-to-end tests** (Playwright for frontend; pytest with full service stack for backend)
4. **Security and isolation tests** (`@pytest.mark.security` / `@pytest.mark.isolation`) — adversarial tests

## Test markers

### Level markers
- `@pytest.mark.unit`
- `@pytest.mark.integration`
- `@pytest.mark.security`
- `@pytest.mark.isolation`
- `@pytest.mark.organization_isolation`
- `@pytest.mark.byom`
- `@pytest.mark.slow`

### Threat-dimension markers
- `@pytest.mark.rebac` — ReBAC access-decision and traversal tests
- `@pytest.mark.audit` — structured audit-event emission and retention
- `@pytest.mark.race` — relation-revocation and concurrency races
- `@pytest.mark.tool_dispatch` — validation of model-returned tool calls
- `@pytest.mark.capability_integrity` — capability-descriptor hashing
- `@pytest.mark.federation` — federated capability resolution
- `@pytest.mark.ohm_signature` — OHM signature verification
- `@pytest.mark.operator_separation` — operator-separation guarantees

## CI gates

Every PR must pass: all `unit` tests, all `integration` tests on touched services, all `security`/`isolation`/`organization_isolation` tests globally, type checking, lint and format.
