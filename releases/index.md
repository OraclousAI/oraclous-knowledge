# 09. Releases

**Document status:** Active · **Maintained by:** tech-lead with input from solution-architect and product-planner

This is the home of **release-level planning**. Each child page is the execution contract for one release.

## Status overview

| Release | Title | Status |
| --- | --- | --- |
| R0 | Phase 0 — Documentation and stabilisation | Released |
| R0.5 | Phase 0.5 — Organisation tenancy and metering substrate | Done |
| R1 | Phase 1 — Auth and credential extensions | Done |
| R2 | Phase 2 — Capability registry consolidation | Planned |
| R3 | Phase 3 — Knowledge graph decomposition | Planned |
| R4 | Phase 4 — Harness runtime extraction | Planned |
| R5 | Phase 5 — Execution engine and runtime completion | Planned |
| R6 | Phase 6 — Application Gateway extraction | Planned |
| R7 | Phase 7 — Compiler harness and seed manifests | Planned |
| R8 | Phase 8 — Security hardening pass | Planned |
| RC | Cloud-mode compliance track | Planned |
| RF Phase A | Frontend Foundation | In progress |

## Agent Identity Convention (Section 6)

All agents share a single Atlassian account when interacting with Jira and Confluence.

**`Agent Owner` custom field:** `customfield_10074`, single-select, 13 options.

**`needs-human` flag:** `customfield_10075`, multi-checkbox, option id `10032`.

**Comment prefix:** every comment begins with `[agent:NAME]`.

**`escalate_to_human`:** (1) Set `Agent Owner = human`. (2) Tick `customfield_10075: [{id: "10032"}]`. (3) Transition to BLOCKED. (4) Post structured escalation comment. All four together.

## Migration source maps (Section 7)

### Project-specific defaults

- **Frontend:** default is **clone-and-refactor**
- **Backend:** default per service is **lift-and-reshape**

### Lift-vs-rewrite rubric

| Question | If yes | If no |
| --- | --- | --- |
| Does the legacy implement this behaviour? | Continue | **Greenfield** |
| Does the legacy already sit at the target layer boundary? | **Lift** directly | **Reshape** to fit |
| Is this behaviour entangled in a larger legacy service? | **Extract** | Lift or Reshape |
| Does the legacy have tests for this behaviour? | **Lift the tests first**, then the code | Author new tests |
