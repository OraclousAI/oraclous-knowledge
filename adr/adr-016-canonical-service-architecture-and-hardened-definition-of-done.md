---
confluence_id: TBD
title: "ADR-016 — Canonical Service-Internal Architecture and Hardened Definition of Done (No Hollow Services)"
---

# ADR-016 — Canonical Service-Internal Architecture and Hardened Definition of Done (No Hollow Services)

## Status

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-06-04 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | ORAA-4 operating contract §21, §22, §23 (rev15); R3.5 release |

## Context

R2 and R3 — and R2's capability-registry — shipped **hollow**. The `tools/audit/hollowness_audit.py` pass produced a true-completion map that is unambiguous: stub endpoints, `raise NotImplementedError` bodies, a `GraphNodeService` stub class defined *inside* a route file, roughly 6,300 LOC of real logic left undeleted and dead in `oraclous-backend/oraclous-core-service/`, and an auth surface that dropped human/email/OAuth/org management entirely. Every one of those stories was marked "done" on the board. None of them ran end-to-end against real substrate.

The failure was not that any one engineer wrote a stub. The failure was that the platform had **no structural definition of a service and no completion bar that a stub could fail**. "Merged PR + green tests" was the whole of "done," and a green test suite over stub endpoints is green. There was no enforced shape, so a `GraphNodeService` could legally live inside a route handler; there was no hollowness check, so `NotImplementedError` shipped; there was no end-to-end gate against real substrate, so nothing forced the code to actually work. The result is that the board's "done" column lied, and a release built on those services inherited the lie.

R3.5 rebuilds every service real and end-to-end, one service at a time, in the graph-first order (knowledge-graph-service → knowledge-retriever-service → identity/org service → credential-broker-service → capability-registry → application-gateway). That rebuild is only safe if two things are decided once and enforced mechanically: **what a service's internals must look like**, and **what makes a service actually done**. This ADR records both. It is the structural counterpart to [ADR-001 — Four-Layer Architecture](adr-001-four-layer-architecture.md): ADR-001 fixed the *cross-service* layering (substrate → registry → runtime → gateway); this ADR fixes the *service-internal* layering and the per-service completion bar.

## Decision

### 1. Canonical service-internal architecture (ORAA-4 §21)

Every service is a package rooted at `services/<svc>/src/oraclous_<svc>_service/`, adopting the legacy `app/{core,models,repositories,routes,schema,services}` layout that R3.5 ports from. The internal layout is fixed:

| Path | Responsibility |
|---|---|
| `main.py` | `app = create_app()` **only** — no handlers, no wiring, no logic. |
| `app/factory.py` | `create_app`: build, wire, and `include_router`. **No handlers or business logic.** |
| `routes/` | `APIRouter` modules. A handler does exactly: **parse → one service call → HTTP map.** Nothing else. |
| `services/` | **All** business logic lives here. |
| `domain/` | Pure entities, no I/O. Optional. |
| `repositories/` (+ `models.py`) | The **only** place DB / Neo4j / Redis access happens; ORM/driver code lives here. |
| `schema/` | Pydantic DTOs only. |
| `core/{config,dependencies,lifespan}.py` | Configuration, dependency providers, and connection setup/teardown. |
| `migrations/` | Schema migrations. |
| `tests/{unit,integration,smoke}/` | Tests live **outside** `src/`. |

**The internal dependency direction is strict and one-way:** `routes → services → domain → repositories → core`. This mirrors ADR-001's downward-only cross-service rule, applied inside a single service.

### 2. Three non-negotiable rules

These three rules are not style preferences; they are the structural invariants that make a service reasoning-friendly and that the hollowness failure violated:

1. **No business logic in route handlers.** A handler parses input, makes one service call, and maps the result to an HTTP response. If a handler branches on domain state, computes, or orchestrates, that logic belongs in `services/`.
2. **No non-`BaseModel` class definitions and no DB drivers in `routes/`.** The `GraphNodeService`-inside-a-route anti-pattern is structurally illegal. The only classes a route module may define are Pydantic `BaseModel` request/response shapes.
3. **Repositories are the only DB / Neo4j / Redis access.** No service, route, or domain module opens a connection or issues a query. Connection *setup* is the single exception, and it lives in `core/lifespan.py`.

### 3. Enforcement (ORAA-4 §21)

The rules are enforced by mechanism, not discipline. A CI `lint` job — mirrored in `.githooks/pre-push` so it blocks locally before a push — runs:

- **`tools/lint/check_service_structure.py` (STR001–005)** — asserts the layered package shape and the three rules above: `main.py` is `app = create_app()` only, `app/factory.py` wires with no handlers/logic, no business logic in route handlers, no non-`BaseModel` class defs or DB drivers in `routes/`, repositories are the only DB/Neo4j/Redis access.
- **`tools/lint/check_no_stubs.py` (HOL001–005)** — fails on stub endpoints, `raise NotImplementedError`, `501`/`pass`-body handlers, and the other hollowness markers. It is **gated on `tools/lint/service_status.yaml`**: a service's no-stub findings become *blocking* the moment that service's `claimed_done` flag flips to `true`. A service is held to the no-hollowness bar exactly when — and only when — it claims to be finished.
- **Per-service internal import contracts** declared in each service's `pyproject.toml` `[tool.importlinter]`, enforcing `routes → services → domain → repositories → core`.

The full narrative lives in [Service Architecture Standard](../engineering/service-architecture-standard.md).

### 4. Hardened per-service Definition of Done (ORAA-4 §22)

A **service** is done only when **all eight gates** pass. The point of the gate set is that **"merged PR + green stub-tests" satisfies none of gates 2–6** — the exact failure mode of R2/R3:

1. **Structurally conformant** — `check_service_structure.py` passes (the §21 shape and the three rules).
2. **Not hollow** — `check_no_stubs.py` reports zero findings, and the service has flipped `claimed_done: true` in `tools/lint/service_status.yaml` (which arms the gate against it).
3. **It runs** — `docker compose up` is healthy; `GET /health` returns 200.
4. **Real endpoints** — integration tests run against **real substrate** via testcontainers; no stub, no 501.
5. **End-to-end smoke vs real substrate** — `services/<svc>/tests/smoke/smoke.sh` passes, run in CI as the docker-required `r3_5_gate` job (modelled on the existing r2-gate).
6. **Reza personally tests it and signs off** — the service's issue carries `needs-human` until accepted. **No service is done while `needs-human` is set**, and the next dependent service does not open until the prior one has cleared this gate.

(Gates 1–6 are the six named §22 gates; gates 7–8 — merged PR and §9.1 handoff — are the ordinary §9 Definition-of-Done gates that every issue already observes. A green merge is necessary but, post-R3.5, no longer sufficient.)

Because gates 3–5 require Docker, the §9.3 docker-required / block-if-Docker-down rule applies: if Docker is unavailable the gate **blocks** rather than passing vacuously. The full DoD narrative lives in [Definition of Done](../engineering/definition-of-done.md).

### 5. Anti-micro-ticket decomposition (ORAA-4 §23)

One service is **one deliverable**, decomposed into **at most six coarse vertical slices**. Each slice cuts all internal layers (route → service → repository), ends in a passing smoke, and is a single `[tests]` + `[impl]` pair. There is no ticket per file, per import, or per endpoint-shell, and no giant interlocked task graph. This keeps the rebuild legible and ties each slice's "done" to a working end-to-end path rather than a layer fragment. The detail of ADR-016 §5 is recorded as its own decision in [ADR-017](adr-017-identity-org-service-split.md)'s sibling context; the canonical statement is ORAA-4 §23.

## Alternatives considered

### A. Keep "merged PR + green tests" as the completion bar; rely on review to catch hollowness

This is the status quo that produced the hollowness. Review is discipline, and discipline is exactly what failed at scale across R2/R3. A reviewer can miss a stub; a CI gate that fails on `NotImplementedError` cannot. Rejected on the evidence of the audit.

### B. Enforce shape with code-review checklists rather than linters

A checklist is unenforced prose. The `GraphNodeService`-in-a-route pattern passed review once already. Mechanisms over discipline (the ORAA-250 principle): if a rule matters, it gets a check that blocks. Rejected.

### C. A single platform-wide "integration" gate instead of a per-service DoD

R3.5 rebuilds services one at a time, with a human sign-off between each. A platform-wide gate cannot express "knowledge-graph-service is genuinely done before knowledge-retriever-service starts." The DoD has to be per-service to match the rebuild cadence and the dependency order. Rejected.

### D. Define the internal shape per-service rather than once

Letting each service invent its own internal layout reproduces the v0 reasoning problem one level down: no two services would be navigable the same way, and no single linter could enforce all of them. One canonical shape, one linter. Rejected.

## Consequences

### Positive

- **"Done" stops lying.** A service that passes the eight gates actually runs end-to-end against real substrate. The board's done column regains meaning.
- **Hollowness is structurally illegal**, not merely discouraged: `check_no_stubs.py` blocks it the moment a service claims completion, and `check_service_structure.py` makes the `GraphNodeService`-in-a-route pattern un-mergeable.
- **Every service is navigable the same way.** "Where does the business logic live?" has one answer (`services/`); "where does the DB get touched?" has one answer (`repositories/`). Onboarding, review, and cross-service reasoning all get cheaper.
- **The internal import linter mechanizes the layer boundary**, closing the gap that let logic leak upward into routes.
- **The human sign-off gate (gate 6) is sequenced**, so a hollow service can no longer unblock the service that depends on it.

### Negative

- **The eight-gate bar is heavier than a green merge.** Standing up Docker + testcontainers + a smoke script per service is real work that a stub avoided. This cost is the point — it is what a stub was skipping — but it is a cost.
- **The `claimed_done` flag is a manual flip.** A service held at `claimed_done: false` is not yet armed against hollowness; the gate protects honesty only once a service claims to be finished. Flipping it dishonestly is possible, but then gates 3–6 fail loudly.
- **Docker-required gates block when Docker is down** (§9.3). This is deliberate fail-closed behaviour, but it means a local Docker outage halts completion, not just slows it.
- **The canonical shape constrains genuinely-different services.** A service with an unusual concern still threads its logic through the same `routes → services → repositories` layering, which will occasionally feel like overhead — the same trade-off ADR-001 accepted at the cross-service level.

## See also

- [ADR-001 — Four-Layer Architecture](adr-001-four-layer-architecture.md) — the cross-service layering this ADR mirrors inside a single service
- [ADR-017 — Identity/Org Service Split](adr-017-identity-org-service-split.md) — the R3.5 service whose creation this DoD governs, and which the auth-hollowness drove
- [ADR-022 — Concern-Driven Agent Ingestion (recipe/primitive/unified-graph)](../adr/) — the binding ingestion spec the knowledge-graph-service (R3.5 service #1) is built to; pinned to legacy `develop` @ `84152635de05c105765cfe6b631bb5ba81f2f4aa` (TASK-237)
- [Service Architecture Standard](../engineering/service-architecture-standard.md) — the §21 layered-structure narrative and the lint-check reference
- [Definition of Done](../engineering/definition-of-done.md) — the §22 eight-gate narrative
- [Release Process](../engineering/release-process.md) — the R3.5 per-service cadence this DoD is sequenced against
- ORAA-4 operating contract §21 / §22 / §23 (rev15) — the canonical source; when this ADR and ORAA-4 diverge, ORAA-4 wins

## Revision history

| Date | Change |
|---|---|
| 2026-06-04 | Initial publication. Captures ORAA-4 §21/§22/§23 (rev15) — canonical service-internal architecture, the three non-negotiable rules + their lint enforcement, and the eight-gate hardened per-service Definition of Done. |
