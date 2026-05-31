---
source_page_id: 65944
title: "07. Frontend"
---

# 07. Frontend

The frontend stack, design system, and code-level conventions for the Oraclous user interface. This section is the authority on how the frontend is built; the visual side is governed by the Design System page within.

## Repository

`OraclousAI/oraclous-frontend` — the active frontend repository. Migrated from the legacy `Jahankohan/oraclous-app` `develop` branch.

## What's here

* [Frontend Stack Reference](https://oraclous.atlassian.net/wiki/spaces/OP/pages/852051) — every locked technology choice; what's in, what's out
* [Design System](https://oraclous.atlassian.net/wiki/spaces/OP/pages/852071) — tokens, principles, voice, visual conventions
* [Component Conventions](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557154) — file structure, naming, composition patterns, accessibility minimums
* [State and Data Patterns](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983081) — server state vs client state vs local state; API layer rules
* [Testing Approach (Frontend)](https://oraclous.atlassian.net/wiki/spaces/OP/pages/294936) — Vitest + Playwright; pyramid; MSW for component tests

## Status

The structural conventions are locked. Substantive design-system content (token reference, component gallery) lands as the v1 UI takes shape. Stack-level decisions are reflected in the legacy repo and carry over to `OraclousAI/oraclous-frontend`.

## Core posture

* **Dark-only for v1** — light mode is not supported
* **OpenAPI is the contract** — backend OpenAPI spec generates frontend types; backend wins all schema disagreements
* **React Query for server state, Zustand for client state, useState for local** — three categories, three homes
* **TDD applies here too** — tests in a separate PR before implementation, per ADR-010
* **No alternative state libraries, no alternative form libraries, no alternative UI kits** — stack changes go through ADRs

## Boundary with the rest of the platform

The frontend is one of two consumers of the Application Gateway (the other being MCP clients). All frontend behaviour ultimately resolves to gateway requests. The frontend does not talk to internal services directly — even in development.

## Related references

* **Section 3 (Layered Architecture)** — the Application Gateway is the frontend's only backend contact point
* **Test Strategy (under 03. Engineering)** — platform-wide testing principles, applied here for the UI
* **ADR-010** — TDD with test-author agent
* **ADR-011** — External tooling decisions also shape frontend choices
