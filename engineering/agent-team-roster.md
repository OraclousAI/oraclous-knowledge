# Agent Team Roster

The Oraclous engineering team operates as a multi-agent system with eleven role-bounded agents plus a human tech lead.

## Architecture tier

- **solution-architect** — Owns architectural coherence. Reviews briefs against the architecture document. Sign-off gate for stories that touch architectural boundaries.
- **security-architect** — Owns security review. Has veto authority on PRs that compromise isolation, governance, or credential safety.

## Planning tier

- **product-planner** — Decomposes features and epics into stories. Writes briefs.
- **tech-lead (human — Reza)** — Final sign-off authority. Resolves cross-tier disputes. Owns sprint planning.

## Implementation tier

- **test-author** — Writes the test suite for a story **before** implementation begins.
- **backend-implementer** — Writes Python service code.
- **frontend-implementer** — Writes TypeScript / React code.
- **devops-implementer** — Writes infrastructure code (Docker, deployment manifests, CI configuration).

## Review tier

- **code-reviewer** — Reviews implementation PRs for code quality.
- **qa-engineer** — Reviews tests and validates that they actually exercise the brief's behaviour.

## Documentation tier

- **docs-writer** — Updates Confluence documentation when stories or features change platform behaviour.

## Narrow verification persona

- **be-test-reviewer** — Owns the backend Tests Review gate (TESTS REVIEWS → IMPLEMENTATION). Resident only in the backend session.

## Hand-off pattern

1. **product-planner** writes the brief
2. **test-author** writes the test PR; **be-test-reviewer** and **security-architect** review it
3. **backend-implementer** / **frontend-implementer** / **devops-implementer** writes the implementation PR
4. **code-reviewer** reviews; **security-architect** reviews if any security marker applies
5. **qa-engineer** validates
6. **docs-writer** updates documentation
7. **tech-lead** final sign-off
