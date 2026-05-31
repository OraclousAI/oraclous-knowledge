# RF Phase A — Frontend Foundation

| Release ID | RF — Phase A |
| --- | --- |
| Status | In progress |
| Window | Parallel track from R0.5 onward |
| Owner | tech-lead |

## Goal

Stand up `oraclous-frontend` as a working pnpm-workspace monorepo with the console app shell that builds, lints, type-checks, and renders the ported Oraclous design system and layouts against mocked/empty data — with zero live backend dependency — so feature work can begin the moment the Application Gateway lands at R6.

## Scope

### In scope (Phase A)

- pnpm-workspace monorepo scaffold
- CI that enforces FE invariants (api-client boundary, no-token-in-storage, WCAG AA, bundle budget)
- `packages/design-system` — tokens + shadcn/ui primitives
- Layout port (DashLayout/Sidebar/TopBar) on design-system tokens
- `packages/api-client` — typed contract shell (no live calls, not generated)
- `apps/console` — app shell rendering on mocked data

### Out of scope (deferred)

- All live backend-bound feature pages (need live gateway at R6)
- OpenAPI-generated api-client (R6)
- FE test agents until RF Phase B

## Jira epics

- ORA-80 — Epic A1: Repo scaffold & CI (ORA-82, ORA-83, ORA-84)
- ORA-81 — Epic A2: Frontend Foundation (ORA-85 through ORA-89)
