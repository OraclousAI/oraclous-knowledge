---
title: "Service Architecture Standard"
---

# Service Architecture Standard

**This is the canonical internal structure every backend service MUST follow** (enacted with R3.5, 2026-06-04). It is the authoritative narrative of operating-contract **§21**; when this page and ORAA-4 §21 diverge, ORAA-4 wins.

It exists because R2/R3 were decomposed into **hollow shells**: stub endpoints, `raise NotImplementedError`, a `GraphNodeService` stub class defined *inside* a route file, three different per-service shapes, and "random" unwired utility files — while the real logic was left undeleted in `oraclous-core-service`. The legacy services already used a clean layered layout; the decomposition threw it away. R3.5 adopts that proven layout as the standard and makes drift/hollowness **mechanically impossible to mark done**.

## The required layout

Every service lives at `services/<svc>/` with package root `src/oraclous_<svc>_service/` and this internal shape:

```
services/<svc>/
├── Dockerfile                # pinned base image; runs main.py (uvicorn)
├── README.md                 # what it does, how to run, endpoints, the smoke runbook
├── pyproject.toml            # pinned deps; package = oraclous_<svc>_service
├── src/oraclous_<svc>_service/
│   ├── main.py               # app = create_app() — the uvicorn target, nothing else
│   ├── app/factory.py        # create_app(): build FastAPI, middleware, lifespan, include_router — NO handlers, NO logic
│   ├── routes/               # HTTP edge: APIRouter per resource
│   │   └── <resource>_routes.py
│   ├── services/             # ALL business logic / use-cases / orchestration
│   │   └── <domain>_service.py
│   ├── domain/               # pure entities / value objects (no I/O)  [omit if the service has no domain rules]
│   │   └── <aggregate>.py
│   ├── repositories/         # the ONLY DB/Neo4j/Redis access; ORM/table models live here
│   │   ├── models.py
│   │   └── <aggregate>_repository.py
│   ├── schema/               # Pydantic request/response DTOs only
│   │   └── <resource>_schemas.py
│   ├── core/                 # config + cross-cutting wiring
│   │   ├── config.py         # pydantic-settings: env → Settings
│   │   ├── dependencies.py   # FastAPI DI providers (get_<x>_service, get_current_*)
│   │   └── lifespan.py       # startup/shutdown: open/close substrate connections
│   └── migrations/           # Alembic (Postgres) / Cypher (Neo4j) if the service owns storage
└── tests/                    # NOT inside src/
    ├── unit/                 # service/domain tests, repositories faked
    ├── integration/          # real substrate via testcontainers (docker-required)
    └── smoke/                # the documented end-to-end curl/script sequence (smoke.sh)
```

`domain/` and `migrations/` are required only if the service has domain rules / owns storage. Everything else is mandatory.

### Documented deviations (read-only services)

Because `domain/` and `models/` are optional, a service that legitimately has neither is **not** a structure violation — but the absence is recorded as **intentional** rather than left implicit. A service declares the optional layers it deliberately omits in `tools/lint/service_status.yaml` under `structure_exceptions` (`[{layer, reason}]`); `check_service_structure` prints each as an *accepted* exception, and re-flags it as **STR006** if that layer is ever added (so a resolved deviation can't leave a stale note behind).

The canonical example is the **knowledge-retriever-service** (read-only): it has no `domain/` (a request is *parse query → read substrate → shape response*, no business-logic aggregates) and no `models/` (it owns no relational schema; its only persistence is a Redis query cache, which is repository-layer access). The deviation is recorded in `service_status.yaml` and noted in the service's `__init__`/README.

A second recorded case is the **knowledge-graph-service**: its ORM table declarations live in `repositories/models.py` (the *colocated* form) rather than a sibling `models/` package. STR004 treats the two as equivalent ("Both `repositories/models.py` (colocated) and a sibling `models/` package are accepted"), so the absent `models/` dir is the same accepted-deviation pattern — not a layering defect, and not worth a churn-only refactor to split out.

## What belongs in each layer (and what is forbidden there)

| Layer | Contains | MUST NOT contain |
|---|---|---|
| `routes/` | `APIRouter`; one handler per endpoint; handler = resolve a service via `Depends` → call **one** service method → map result/exception to HTTP. Route-local Pydantic request models allowed. | Any business logic; any DB/Neo4j/Redis driver call; any non-`BaseModel` class definition; any `_stub_`; branching beyond HTTP-status mapping. |
| `services/` | Use-case orchestration, domain rules, fail-closed checks, provenance/ReBAC calls, transaction boundaries. Depends on repositories via injected interface. | Direct DB driver objects (`neo4j.GraphDatabase`, `psycopg`, `asyncpg`, `redis`); FastAPI types; raw SQL/Cypher strings. |
| `domain/` | Entities, value objects, enums, pure functions. | Any I/O, any framework import, any persistence. |
| `repositories/` | The ONLY place importing a DB/Neo4j/Redis driver or `oraclous_substrate` storage seam; SQL/Cypher; ORM models. Each method carries `organisation_id` (ADR-006). | Business decisions; HTTP types; cross-org traversal without ReBAC. |
| `schema/` | Pydantic request/response DTOs. | Logic; persistence; `organisation_id` as an inbound request field (ORG001). |
| `core/` | `config.py`, `dependencies.py` (DI providers), `lifespan.py`, auth/rate-limit helpers. | Resource-specific business logic. |
| `app/factory.py` | `create_app()`: instantiate FastAPI, middleware, lifespan, `include_router(...)`. | Inline route handlers; business logic; DB access. |
| `main.py` | `app = create_app()` + uvicorn entrypoint. | Anything else. |

## The three non-negotiable rules

1. **No business logic in route handlers.** A handler is *parse → one service call → HTTP map*.
2. **No non-`BaseModel` class defs and no DB drivers in `routes/`.** (This is exactly what killed us: a `GraphNodeService` stub class living in the route file.)
3. **Repositories are the ONLY DB/Neo4j/Redis access** (connection setup excepted in `core/lifespan.py`).

## Dependency injection / wiring

Wiring lives in exactly two places: `core/dependencies.py` (the providers — `get_<x>_repository`, `get_<x>_service`, `get_current_user`) and `app/factory.py` (assembly — middleware, lifespan, `include_router`). Routes obtain their service via `Depends(get_<x>_service)`. Repositories are constructed from the connection opened in `core/lifespan.py` and held on `app.state`.

## Enforcement (mechanical — see ORAA-4 §20)

Structure and hollowness are not discipline; they are checked in the CI `lint` job (the always-green required gate) and `.githooks/pre-push`:

- **`tools/lint/check_service_structure.py`** (STR001–005): required layer dirs present; `routes/` contains no non-`BaseModel` class defs and no DB-driver imports; no DB driver imported outside `repositories/` (+ `core/lifespan.py`); scattered top-level `*_service.py` files flagged.
- **`tools/lint/check_no_stubs.py`** (HOL001–005): fails on `raise NotImplementedError`, `_stub_`, `TODO: implement` / `not yet implemented` / `deferred to R\d`, pass-only or `return None|[]|{}|False`-only function bodies (non-abstract), and route handlers returning `501`. Enforced on services marked `claimed_done: true` in `tools/lint/service_status.yaml` — so a service cannot be flipped to done while hollow.
- **Per-service internal import contracts** (`pyproject.toml [tool.importlinter]`, one `layers` contract per service): `routes → services → domain → repositories → core`, never upward; a `forbidden` contract keeps `schema` from importing `repositories`/`services`. Enforced by the existing `lint-imports` step.

The pattern to copy when writing the checkers: `tools/lint/check_org_scoping.py`.

## Conformance — how a service is measured

A service is structurally conformant when: required dirs + `main.py` + `app/factory.py` exist; `routes/` has no non-`BaseModel` classes and no DB drivers; no DB driver outside `repositories/`+`core/lifespan.py`; zero hollowness markers for a `claimed_done` service; the per-service import contract passes. All five are mechanical (the checks above) — never a judgement call.

## Tooling reference (what devops builds; ORAA-4 §20)

These are specified here so the devops-implementer builds to spec (the pattern to copy for the AST checkers is `tools/lint/check_org_scoping.py`):

- **`tools/lint/service_status.yaml`** — the source of truth for which services are claimed done. One entry per service:
  ```yaml
  services:
    knowledge-graph-service:   { release: R3.5, claimed_done: false, port_source: false, deletable: true }
    capability-registry-service: { release: R2,  claimed_done: false }
    oraclous-core-service:     { port_source: true, deletable: false }   # dead shadow; salvage-then-delete (human-gated)
  ```
  `check_no_stubs` enforces HOL rules ONLY on services with `claimed_done: true` — so a service cannot be flipped to done while hollow, and a deliberately-incomplete shell can exist pre-claim.
- **`tools/lint/check_service_structure.py`** (STR001–005) and **`tools/lint/check_no_stubs.py`** (HOL001–005) — AST checkers added as steps in the CI `lint` job and `.githooks/pre-push`. Exit non-zero on any violation; emit `Violation(path, line, code, msg)` like the existing checkers.
- **Per-service `[tool.importlinter]` contracts** in the repo-root `pyproject.toml` — one `layers` contract per service (`routes → services → domain → repositories → core`) + a `forbidden` contract (schema imports neither repositories nor services). Run by the existing `lint-imports` step.
- **`r3_5_gate`** — a CI job (modelled on the existing `r2-gate`) that runs, in order: structure-lint + no-stub + import contracts → `docker compose up <svc>` + `/health` → `pytest -m integration` (testcontainers) → `services/<svc>/tests/smoke/smoke.sh`. Docker-required. It is the mechanical half of the §22 DoD (gates 1–5); gate 6 (Reza sign-off) is the GitHub issue `needs-human` label.
- **`tools/audit/hollowness_audit.py`** (read-only) — runs `check_no_stubs`, scans for stub classes, compares each new service's src-LOC + endpoint count vs its legacy port-source, and asserts each route reaches a real repository SQL/Cypher call. Emits the true-completion map and re-opens hollow "done" GitHub issues.

See also: [Definition of Done](./definition-of-done.md) (the hardened per-service 8-gate DoD), [ADR-016](../adr/adr-016-canonical-service-architecture-and-hardened-definition-of-done.md), ORAA-4 §21/§22.
