---
source_page_id: 852051
title: "Frontend Stack Reference"
---

# Frontend Stack Reference

The canonical stack for the Oraclous frontend. Every choice listed here is locked unless an ADR retires it. New dependencies and new patterns require justification against this baseline.

## Repository

`OraclousAI/oraclous-frontend` — migrated from the legacy `Jahankohan/oraclous-app` repo. The legacy repo's `develop` branch is the seed; further development happens only in the new repo.

## Core stack

| Concern | Choice | Why |
| --- | --- | --- |
| Framework | React 18.3 | Concurrent rendering, suspense, broad ecosystem |
| Language | TypeScript 5.5 | Type safety; no `any` without explicit justification |
| Build tool | Vite 5.4 | Fast HMR, ESM-native, sane production builds |
| Router | react-router-dom 6.26 | De-facto router; data-router patterns for nested loaders |
| Server state | @tanstack/react-query 5.56 | Query caching, mutation lifecycle, optimistic updates |
| Client state | zustand 5.0 | Lightweight; no boilerplate; no provider tree |
| Forms | react-hook-form 7.53 | Performant, uncontrolled-first, integrates with zod |
| Validation | zod 3.23 | Type inference; runtime + compile-time agreement |
| UI primitives | Radix + shadcn/ui | Accessible primitives; composable; no design-system lock-in |
| Styling | Tailwind 3.4 | Utility-first; design tokens via theme; dark mode forced |
| Icons | lucide-react | Tree-shakeable; broad coverage; consistent stroke |
| Toasts | sonner | Minimal API; accessible; replaces older toast libraries |
| Theming | next-themes (dark forced) | Single dark theme; no light-mode toggle for v1 |
| Fonts | Syne (display) + DM Mono (code) | Distinctive without being eccentric |
| Graph/canvas | @xyflow/react 12.8 | Knowledge graph and harness topology views |
| Charts | recharts | Lightweight, declarative; sufficient for analytics |
| Unit tests | Vitest | Vite-native; fast; Jest-compatible API |
| E2E tests | Playwright | Cross-browser; tracing; deterministic |

## Conventions

* **OpenAPI is the contract** — when the frontend and backend disagree on a schema, the backend's OpenAPI definition wins. Frontend types are generated from the OpenAPI spec, not hand-rolled.
* **No CSS files outside the design tokens** — utility classes via Tailwind; the few necessary global styles live in one file
* **Dark mode is the only mode** — light mode is not supported for v1; do not add light-mode variants
* **No alternative state libraries** — React Query for server state, Zustand for client state, useState for component-local state; if a feature seems to need more, raise an ADR
* **No alternative form libraries** — react-hook-form + zod schema is the only form pattern

## Out of scope (do not add)

* Redux, MobX, Recoil, Jotai — replaced by Zustand + React Query
* Formik, Final Form — replaced by react-hook-form
* styled-components, Emotion, vanilla-extract — replaced by Tailwind
* Material UI, Ant Design, Chakra — replaced by shadcn + Radix primitives
* Jest — replaced by Vitest
* moment.js — replaced by date-fns where needed

## Boundary with the design system

This page lists _technology_ choices. The visual design system (colours, typography, spacing scale, motion, copy conventions) lives in the Design System page. Stack changes go through an ADR; design system changes go through normal PR review.

## Related references

* **Component Conventions** — file structure, prop patterns, naming
* **State and Data Patterns** — React Query and Zustand patterns
* **Design System** — visual design tokens
* **Testing Approach (Frontend)** — Vitest + Playwright patterns
* **ADR-011** — External tooling decisions also drive frontend choices
