---
confluence_id: "426037"
title: "Code Style Guide"
---

# Code Style Guide

This page defines language-level style conventions for backend (Python) and frontend (TypeScript) code. Where automated tooling (ruff, mypy, Biome, tsc) enforces a rule, the rule is in tool configuration first and this document second. Where judgement is required, this document is the reference.

## Python

### Tooling

* **ruff** for linting and formatting. Configuration lives in `pyproject.toml` under `[tool.ruff]`. Run on every save and on every pre-commit hook.
* **mypy** for static type checking. Strict mode enabled (`strict = true` in `pyproject.toml`). New code must type-check cleanly; legacy code is incrementally raised to strict.
* **pytest** for testing (see Test Strategy).

### Type hints

* Every function and method has type hints on parameters and return type. No implicit `Any`.
* Use `from __future__ import annotations` at the top of every file. This defers annotation evaluation and lets you reference forward classes without quoting.
* Prefer `list[str]` over `List[str]`, `dict[str, int]` over `Dict[str, int]` (PEP 585).
* Use `Sequence`, `Mapping`, `Iterable` from `collections.abc` for parameter types (read-only contracts). Use `list`, `dict` for return types and locals (read-write).
* `Optional[X]` is written as `X | None` (PEP 604).

### Naming

* `snake_case` for functions, methods, variables, modules
* `PascalCase` for classes, type aliases, NamedTuples
* `SCREAMING_SNAKE_CASE` for module-level constants
* `_leading_underscore` for module-private and class-private. Use sparingly; `__double_leading` is reserved for genuine name mangling needs (rare).

### Module organisation

Each service follows this directory shape:

```
service-name/
  app/
    api/           # FastAPI routers
    services/      # business logic
    models/        # Pydantic + ORM models
    db/            # database access
    config/        # settings
    main.py        # entry point
  tests/
    unit/
    integration/
    security/
  pyproject.toml
  Dockerfile
  README.md
```

API layer is thin (routing + validation + response shaping). Business logic lives in services. Database access is wrapped in repository-pattern classes; raw SQL or raw Cypher does not appear in services.

### Async vs. sync

The platform is async-first. Use `async def` for any function that does I/O. Reserve `def` for pure computation. Mixing is acceptable but the boundary should be deliberate (sync function called from async, never the reverse without explicit `asyncio.to_thread`).

### Error handling

* Use specific exception types from the service's own exception module. Catching `Exception` is forbidden except at the outermost API boundary.
* Errors that surface to API responses go through a single error-handling middleware. Services raise typed exceptions; the middleware maps them to HTTP responses.
* Never silently swallow exceptions. If a recovery path is intentional, log the recovery and document why.
* Per Principle S2 (fail closed), uncertain permission decisions raise `PermissionDeniedError`, not `False`.

### Logging

* Use structured logging (`structlog` configured at service startup). Log entries are JSON-shaped with consistent keys (`event`, `service`, `request_id`, `organization_id`, `workspace_id`, etc.).
* Never log secrets. The `detect-secrets` baseline plus a logging filter that strips known credential patterns prevents accidents.
* Log levels: `DEBUG` for development verbosity, `INFO` for normal operation, `WARNING` for recoverable issues, `ERROR` for issues requiring attention, `CRITICAL` for issues requiring immediate response.

## TypeScript

### Tooling

* **Biome** for linting and formatting. Configuration in `biome.json`. Run on save and pre-commit.
* **tsc** for type checking. `strict: true` in `tsconfig.json`.
* **Vitest** for unit/integration tests; **Playwright** for end-to-end.

### Type system

* `strict: true` is non-negotiable. No `any` unless wrapped in a comment explaining why and a follow-up ticket.
* Prefer `unknown` to `any` when the type is genuinely unknown at compile time.
* Use discriminated unions for state machines and message shapes: `type Result = { kind: 'ok'; value: T } | { kind: 'err'; error: E }`.
* Type-only imports use `import type` syntax: `import type { Foo } from './foo'`. This helps Biome separate type imports from runtime imports.

### Naming

* `camelCase` for variables, functions, methods, props
* `PascalCase` for components, types, interfaces, enums
* `kebab-case` for filenames
* One exported component per file; the file name matches the component name in kebab-case (`user-profile.tsx` exports `UserProfile`)

### Components

* Functional components with hooks. Class components are not used.
* Props typed as named interface (`interface UserProfileProps { ... }`), not inline.
* Default exports for components, named exports for utilities and types.
* Stateful components keep state minimal; lift state up rather than duplicating.

### Forms

* `react-hook-form` for form state, `zod` for validation. Form schema lives next to the component as a `*.schema.ts` file.
* Submit handlers are async functions that explicitly handle success and error states.

### State management

* Local component state (`useState`, `useReducer`) for component-scoped state
* `zustand` for cross-component shared state
* `@tanstack/react-query` for server state (queries, mutations, cache)
* Avoid Context for global state; prefer zustand for cross-cutting concerns

### Styling

* Tailwind utility classes for layout and spacing
* shadcn/ui primitives for interactive components
* Custom CSS only when Tailwind cannot express the design — and then in a co-located `*.module.css` file, not global stylesheets

## Universal

### Comments

* Comments explain _why_, not _what_. The code shows what.
* TODOs include a Jira reference: `// TODO(ORA-NNN): description`. Untracked TODOs are removed.
* Doc comments (Python docstrings, TypeScript JSDoc) document public APIs — anything imported from another module gets a doc comment.

### File length

* Files longer than 500 lines are a smell. Consider splitting by responsibility.
* Functions longer than 50 lines are a smell. Consider extracting helpers.
* These are not hard rules. A 600-line file that genuinely covers one cohesive concept is fine.

### Dead code

* Unused imports, unused variables, commented-out blocks: removed, not preserved. Git remembers what we deleted.
* Feature-flagged dead code is acceptable; the flag itself is the documentation of why.
