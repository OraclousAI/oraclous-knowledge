---
confluence_id: "557154"
title: "Component Conventions"
---

# Component Conventions

How components are structured, named, and composed in the Oraclous frontend codebase. This page covers code-level conventions; the Design System page covers the visual side.

## File and folder structure

* `src/components/ui/` — shadcn-derived primitives; minimal customisation; one component per file
* `src/components/<domain>/` — domain components grouped by feature area (e.g. `harness/`, `workspace/`, `knowledge-graph/`)
* `src/features/<feature>/` — feature folders containing pages, hooks, and feature-local components for a vertical slice
* `src/pages/` — route-level page components; thin shells that compose feature components
* `src/lib/` — pure utilities, no React
* `src/hooks/` — cross-cutting hooks (those tied to a feature live in the feature folder)
* `src/api/` — generated OpenAPI types and the typed API client

## Component shape

* **Function components only** — no class components anywhere
* **Named exports for shared components** — `export function HarnessCard(...)`; default exports only for route components
* **Co-located types** — props interface in the same file, named `<Component>Props`
* **Props are typed, not inferred** — explicit prop type declarations everywhere
* **One component per file by default** — small helpers can co-locate when they have no other consumer

## Naming

* `PascalCase` for components and types
* `camelCase` for hooks, functions, variables
* `SCREAMING_SNAKE_CASE` for true constants
* `kebab-case` for file names — `harness-card.tsx`, `use-harness-list.ts`
* Hooks always start with `use`; selectors start with `select`; event handlers with `handle` or `on`

## Composition patterns

* **Compound components for grouped UI** — `Card.Header`, `Card.Body`, `Card.Footer` rather than 12 boolean props
* **Render props sparingly** — only when behaviour needs to invert; default to composition
* **No HOCs** — `forwardRef` and hooks cover the gap
* **Avoid prop drilling beyond two levels** — promote to a feature-level Zustand store or React Query cache

## Boundary discipline

* **Domain components don't know how data is fetched** — they receive data and callbacks; the feature folder owns the data plumbing
* **Generic components don't know domain shape** — `<DataTable>` takes columns and rows; it doesn't know what a harness is
* **No business logic in components** — components render; hooks and pure functions decide

## Accessibility minimums

* Every interactive element is keyboard-reachable
* Every input has a label (visible or `aria-label`)
* Focus rings are never removed without an equivalent replacement
* Colour is never the only signal for state
* Modal dialogs trap focus and restore it on close
* `aria-live` regions for asynchronous status updates

## What this page will cover

* **Folder tree** — annotated example from the actual codebase
* **Naming examples** — good and bad
* **Compound component examples** — full code for the `Card`, `DataTable`, `EmptyState` patterns
* **Hook patterns** — when to write a custom hook vs inline `useEffect`
* **Form patterns** — the canonical react-hook-form + zod composition
* **Error boundary placement** — feature-level and global error boundaries
* **Suspense usage** — when to use Suspense vs. React Query's `isLoading`

## Related references

* **Frontend Stack Reference** — the technology baseline these conventions build on
* **Design System** — visual side of components
* **State and Data Patterns** — where data plumbing lives
* **Testing Approach (Frontend)** — how components are tested
