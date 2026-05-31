# 07. Frontend

The frontend stack, design system, and code-level conventions for the Oraclous user interface.

**Repository:** `OraclousAI/oraclous-frontend` — migrated from legacy `Jahankohan/oraclous-app` `develop` branch.

## What's here

- [Frontend Stack Reference](./frontend-stack-reference.md)
- [Design System](./design-system.md)
- [Component Conventions](./component-conventions.md)
- [State and Data Patterns](./state-and-data-patterns.md)
- [Testing Approach (Frontend)](./testing-approach-frontend.md)

## Core posture

- **Dark-only for v1** — light mode is not supported
- **OpenAPI is the contract** — backend OpenAPI spec generates frontend types; backend wins all schema disagreements
- **React Query for server state, Zustand for client state, useState for local**
- **TDD applies here too** — per ADR-010
- **No alternative state/form/UI kit libraries** — stack changes go through ADRs

## Boundary with the rest of the platform

The frontend is a consumer of the Application Gateway. All frontend behaviour ultimately resolves to gateway requests.
