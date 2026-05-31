# State and Data Patterns

## The three kinds of state

| Kind | Home | Examples |
| --- | --- | --- |
| Server state | React Query | List of harnesses, the current user, a knowledge graph, a task board |
| Client state | Zustand (per-feature stores) | Filter selections, sidebar collapsed state, multi-step form draft |
| Component-local state | `useState` / `useReducer` | Hover state, controlled input value within one widget |

## API layer

- **Generated types from OpenAPI** — backend OpenAPI spec is the contract; types in `src/api/types/`
- **Typed fetcher per endpoint** — wrapped functions per endpoint; React Query consumes the fetcher
- **Errors are structured** — backend errors follow a known shape (ORA-56 gateway error envelope)
- **Auth headers handled centrally** — single interceptor adds the token; never through component props

## Gateway error envelope (ORA-56)

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "One or more fields are invalid.",
    "requestId": "req_01J9Z...",
    "retryable": false,
    "details": [
      { "field": "email", "issue": "INVALID_FORMAT" }
    ]
  }
}
```
