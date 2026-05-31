# Interface Contracts

This page is the single canonical home for every API shape that crosses the repo boundary, until R6 when the gateway OpenAPI spec takes over.

## Index

| Contract | Jira | Status | Canonical shape |
| --- | --- | --- | --- |
| Auth token claims | — (backfill pending) | Done | See §1 |
| OHM manifest envelope | — (backfill pending) | Done | See §2 |
| Gateway error envelope | ORA-56 | Agreed & enforced (fixture ORA-53 Done); BE ORA-54 → R6, FE ORA-55 → R-Frontend | See §3 |

## §1 — Auth token claims

```json
{ "sub": "usr_...", "org": "org_...", "roles": [...], "exp": 1234567890 }
```

## §2 — OHM manifest envelope

Frozen. See OHM v1.0 Standalone Specification.

## §3 — Gateway error envelope (ORA-56)

Owner: security-architect.

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

**Error code taxonomy:**

| code | HTTP | retryable |
| --- | --- | --- |
| VALIDATION_FAILED | 400 | false |
| UNAUTHENTICATED | 401 | false |
| UNAUTHORIZED | 403 | false |
| NOT_FOUND | 404 | false |
| RATE_LIMITED | 429 | true |
| INTERNAL_ERROR | 500 | false* |
| SERVICE_UNAVAILABLE | 503 | true |
| GATEWAY_TIMEOUT | 504 | true |

**Must NEVER appear in error body:** stack traces, internal hostnames, SQL, tokens/secrets, framework versions, PII, auth differential messaging.
