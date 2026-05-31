# PR Conventions

## PR sizing

- **Target:** under 300 lines of net change
- **Acceptable:** 300–600 lines, if cohesive
- **Requires justification:** 600+ lines
- **Almost always too big:** 1,000+ lines

## PR description template

1. **Summary** — one or two sentences naming what changes and why
2. **Architectural context** — references to the architecture section or ADR
3. **Test PR reference** — for implementation PRs, link to the test-author PR
4. **Scope of change** — bulleted list of what changed at the architectural level
5. **Out of scope** — explicit list of things the PR deliberately does _not_ do
6. **Testing notes** — any non-obvious aspects of how the change is tested
7. **Deployment notes** — anything special the devops-implementer needs to know

## Review expectations

- **code-reviewer** — architecture conformance, test alignment, code quality
- **security-architect** — isolation guarantees, credential handling, threat catalogue alignment
- **solution-architect** — layer respect, service boundary contracts, OHM shape
- **qa-engineer** — tests actually exercise the behaviour, edge cases covered
