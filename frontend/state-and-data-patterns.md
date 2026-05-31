---
confluence_id: "983081"
title: "State and Data Patterns"
---

# State and Data Patterns

How data flows through the Oraclous frontend. This page is the authority on what kind of state goes where, and how the frontend talks to the backend.

## The three kinds of state

State in the frontend falls into exactly three categories. Each has one canonical home.

| Kind | Home | Examples |
| --- | --- | --- |
| Server state | React Query | List of harnesses, the current user, a knowledge graph, a task board, an in-flight execution |
| Client state | Zustand (per-feature stores) | Filter selections, sidebar collapsed state, multi-step form draft, selected node in a graph view |
| Component-local state | `useState` / `useReducer` | Hover state, controlled input value within one widget, ephemeral animations |

If a piece of state doesn't fit cleanly, the default answer is component-local. Promote to a Zustand store when more than one component needs it; promote to server state when the backend owns the truth.

## Server state: React Query

* **One query key per resource shape** — `['harness', harnessId]`, `['workspace', workspaceId, 'harnesses']`. Keys are arrays; the first segment is the resource type.
* **Mutations invalidate by key** — explicit invalidation, not blanket refetch
* **Optimistic updates for high-confidence mutations** — task transitions, manifest comments. Roll back on error.
* **No global staleTime defaults** — every query declares its own; defaults are documented per resource family
* **Suspense usage opt-in per query** — Suspense for first-load surfaces; conditional rendering with `isLoading` for in-place updates

## Client state: Zustand

* **One store per feature** — `useHarnessFiltersStore`, `useGraphViewStore`. Stores live in their feature folder.
* **No global store of stores** — there is no "app store"; stores are decoupled
* **Selectors are typed and explicit** — `useFooStore(state => state.bar)`, never selecting the whole state
* **Stores are not used for derived data** — derive from server state or compute in selectors
* **No persistence by default** — opt-in per store using `persist` middleware; never persist server data

## API layer

* **Generated types from OpenAPI** — backend OpenAPI spec is the contract; types live in `src/api/types/`. Never hand-roll API types.
* **Typed fetcher per endpoint** — wrapped functions per endpoint; React Query consumes the fetcher
* **Errors are structured** — backend errors follow a known shape; the fetcher parses them; consumers handle typed errors, never raw responses
* **Auth headers handled centrally** — single interceptor adds the token; never pass tokens through component props
* `organization_id` and `workspace_id` are URL or header values — set by the API client; components don't pass them explicitly

## Real-time updates

* **Server-Sent Events for streamed execution output** — used for live harness runs
* **WebSocket reserved for bidirectional needs** — round-tables, task board sync; not used unless bidirectional is actually required
* **React Query invalidation on server events** — incoming events trigger key invalidation rather than direct state mutation

## Forms

* **react-hook-form + zod** — the only form pattern
* **One zod schema per form** — colocated with the form component
* **Server-side validation is still authoritative** — frontend validation is for UX; backend errors override
* **Submission is a React Query mutation** — never a direct fetch in the submit handler

## Loading and error patterns

* `isLoading` for first-load — skeletons in place of content
* `isFetching` for refresh-in-place — subtle indicator; existing content remains visible
* **Errors get an error state UI** — never a thrown error to a parent unless an Error Boundary should catch
* **Mutation errors surface near the action** — inline error, not a toast (unless the action is non-local)

## What this page will cover

* **Query key catalogue** — every resource's query key shape
* **Mutation patterns** — optimistic, with-toast, with-redirect
* **Store boundary examples** — when something should be Zustand vs component-local
* **Real-time pattern walkthrough** — SSE for execution stream, WebSocket for round-table
* **Performance patterns** — memoisation guidelines, virtualisation for long lists, code-splitting per route
* **Error catalogue** — backend error codes and their UI mapping

## Related references

* **Frontend Stack Reference** — React Query, Zustand, react-hook-form versions
* **Component Conventions** — components consuming this data flow
* **Testing Approach (Frontend)** — how data layer is mocked in tests
