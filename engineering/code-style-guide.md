# Code Style Guide

## Python

- **ruff** for linting and formatting
- **mypy** for static type checking (strict mode)
- **pytest** for testing
- Every function and method has type hints. No implicit `Any`.
- `Optional[X]` is written as `X | None` (PEP 604)
- API layer is thin (routing + validation + response shaping). Business logic lives in services.
- Async-first: use `async def` for any function that does I/O.
- Structured logging with `structlog`. Never log secrets.

## TypeScript

- **Biome** for linting and formatting. `strict: true` in tsconfig.
- `unknown` over `any` when type is genuinely unknown
- Discriminated unions for state machines: `type Result = { kind: 'ok'; value: T } | { kind: 'err'; error: E }`
- Functional components with hooks. No class components.
- `react-hook-form` + `zod` for forms.

## Universal

- Comments explain _why_, not _what_
- TODOs include a Jira reference: `// TODO(ORA-NNN): description`
- Files longer than 500 lines are a smell. Functions longer than 50 lines are a smell.
