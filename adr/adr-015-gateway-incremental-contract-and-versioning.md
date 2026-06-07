---
confluence_id: TBD
title: "ADR-015 — Gateway Incremental Contract and Versioning (R5→R8)"
---

# ADR-015 — Gateway Incremental Contract and Versioning (R5→R8)

## Status

| Field | Value |
|---|---|
| Status | **Accepted** |
| Date | 2026-06-01 (accepted 2026-06-08) |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Supersedes | None |
| Superseded by | None |
| Amended by | [ADR-019](adr-019-r6-gateway-datastore-and-integration-key-authz-floor.md) (R6 gateway datastore + integration-key authz floor; the gateway is no longer purely stateless) |
| Driving artifact | ORAA-31; ORAA-28 (gateway thin-service decision) |

> **Accepted 2026-06-08** to unblock R6 Slice 1 (publish `openapi/v1.yaml` + the `openapi-diff-gate`). As-built reconciliation: the actual proxied paths are heterogeneous (`/v1/auth`, `/api/v1/graphs`, `/credentials`, `/oauth`), not the uniform `/v1/` this ADR assumes — the published spec documents the **real** surface; normalising every proxied path to a uniform `/v1/` is tracked as a follow-up within R6 (gateway path-rewriting + FE/Postman updates), not a Slice-1 deliverable. The R5 REST-table rows (`POST /v1/executions`, `/v1/taskboards/{id}`) are superseded by the as-built engine surface (`/v1/engine/jobs`, `/v1/engine/tasks`); §4's tables are the planning intent, the published `openapi/v1.yaml` is the source of truth.

## Context

ORAA-28 locked a key deployment decision: the `application-gateway-service` (Layer 4, Section 3) stands up as a thin, **provisional** service immediately after R4, adding its newly-introduced endpoints release-by-release through R5→R8. R6 is gateway consolidation and hardening — the moment provisional becomes stable.

This creates three interacting design problems with no prior architectural answer:

1. **The gateway surfaces two distinct protocol shapes** — REST and MCP — and endpoints do not always map cleanly to one. Without a stated boundary, each release's implementer will decide independently, producing an inconsistent surface.

2. **The contract must evolve incrementally** (R5 provisional → R6 stable → R7/R8 hardening) without breaking the FE api-client. The `packages/api-client` typed shell (ORA-88, RF Phase A) is in-flight now, before the live gateway exists. Its maintainers need to know: how will provisional endpoints be marked? What enforcement gates apply at each release?

3. **URL versioning** has not been decided. A `/v1/` prefix assumed in passing in multiple documents (`application-gateway-service.md`, RF Phase A) needs to be explicit and the alternatives formally rejected.

This ADR covers all five design surfaces. It does not cover billing (deferred per Section 3 Layer 4), internal service-to-service communication (not gateway-exposed), or the MCP protocol version (a protocol-spec concern, not an API design concern).

## Decision

### 1. Versioning scheme: `/v1/` URL prefix on the REST surface

All public REST endpoints exposed by `application-gateway-service` are rooted at `/v1/`. The gateway does not support multiple simultaneous major URL prefixes; `/v2/` is not created until a formal breaking-change ADR explicitly requires it.

**Rejected alternatives:**

- **`Accept` header versioning:** Invisible in logs and load-balancer routing rules, not supported by most OpenAPI tooling without custom extensions, incompatible with CDN caching (cache keying requires URL-addressable version signals). Rejected.
- **No versioning (bare paths):** Leaves implementers without a mechanism for a future non-backwards-compatible change. The `/v1/` prefix is cost-free and migration-enabling. Rejected.

**MCP surface versioning:** The MCP server negotiates protocol version using the MCP spec mechanism (`initialize` → `protocolVersion`). This is a protocol-level, not a URL-level, concern and is not subject to the `/v1/` convention.

### 2. Provisional endpoint marking: `x-stability` OpenAPI extension

Every OpenAPI operation object in the gateway's published spec carries an `x-stability` field:

```yaml
x-stability: "provisional" | "stable"
```

If the field is absent, the default is `stable`. The published spec therefore always has an unambiguous stability signal per endpoint.

**Semantics:**

- `provisional`: the endpoint exists, is callable, and is tested — but its request/response shape may change within the R5→R6 window. Breaking changes to provisional endpoints are allowed between releases; they are not allowed within a release. On promotion to `stable` in R6, the diff gate treats `provisional → stable` as a non-breaking promotion.
- `stable`: the endpoint's shape is locked. Breaking changes require a new major API version (a new ADR). The OpenAPI diff gate (R6+) blocks merges that introduce breaking changes to stable endpoints.

**api-client enforcement:** The FE api-client typed shell marks every provisional endpoint stub with `// Contract: provisional - [issue ref]`. The api-client boundary CI gate (ORA-83) enforces that no package outside `packages/api-client` calls gateway endpoints directly. When the provisional endpoint's shape changes in R5→R6, only `packages/api-client` needs to be updated; all feature code is insulated.

### 3. Contract enforcement mechanism per release

**R5 (provisional, Weeks 21–24):** Shared-fixture approach.

- A fixture module at `oraclous-backend/tests/shared_fixtures/gateway_contract.py` declares the accepted request schemas and response envelopes for each provisional endpoint as Python TypedDicts.
- BE integration tests assert that the live endpoint accepts and returns these shapes.
- FE typed stubs in `packages/api-client` are kept in sync manually with the fixture shapes; divergence is caught at R6 when the generated types are compared.
- The fixture is the contract document during R5. It is checked in and reviewed like production code.

**R6 (consolidation, Weeks 25–28):** OpenAPI diff gate.

- `devops-implementer` publishes `oraclous-backend/openapi/v1.yaml` as a CI artifact, generated from the running gateway's FastAPI metadata.
- A CI job (`openapi-diff-gate`) using `oasdiff` or equivalent runs on every BE PR and fails on any breaking change to a `stable` endpoint.
- FE CI imports the published spec and runs `openapi-typescript` to produce generated types; a separate CI check diffs the generated types against the checked-in `packages/api-client` stubs.
- At R6 close, all R5 provisional endpoints are promoted to `stable` (or removed if not yet ready). The promotion PR is reviewed by solution-architect.

**R7 / R8 (hardening, Weeks 29–36):**

- The stable endpoint set is frozen. No new stable endpoints without solution-architect review.
- New endpoints introduced in R7 (compiler harness gateway exposure) begin as `x-stability: provisional` and follow the same cycle.
- R8 is a security hardening pass with no new endpoint surface; the spec is amended only for security-relevant field additions or restrictions (non-breaking by convention).

### 4. MCP vs REST surface boundary

**MCP surface (MCP server endpoint, new in R6):**

| Operation | MCP method | Auth modes | Stability (R6) |
|---|---|---|---|
| Workspace capability enumeration | `tools/list` | Integration key, Member credentials | stable |
| Capability invocation | `tools/call` | Integration key, Member credentials, Agent credentials | stable |
| Knowledge resource listing | `resources/list` | Integration key, Member credentials | stable |
| Harness prompt enumeration | `prompts/list` | Integration key, Member credentials | stable |

The MCP surface is **MCP-exclusive**: these operations are not duplicated as REST endpoints.

**REST surface (by release):**

| Release | Endpoint | Auth modes | Stability |
|---|---|---|---|
| R5 | `POST /v1/executions` | Integration key, Agent credentials | provisional |
| R5 | `GET /v1/executions/{id}/status` | Integration key, Member, Agent credentials | provisional |
| R5 | `GET /v1/executions/{id}/stream` (SSE) | Integration key, Member, Agent credentials | provisional |
| R5 | `GET /v1/taskboards/{id}` | Member credentials | provisional |
| R5 | `PUT /v1/tasks/{id}/assign` | Member credentials | provisional |
| R6 (migrated) | `POST /v1/chat/conversations` | Member credentials | stable |
| R6 (migrated) | `GET+POST /v1/chat/{id}/messages` | Member credentials | stable |
| R6 (migrated) | `GET /v1/agents/{slug}` | Integration key (scoped) | stable |
| R6 (migrated) | `POST /v1/agents/{slug}/invoke` | Integration key (scoped) | stable |
| R6 | `POST+GET+DELETE /v1/integration-keys` | Member credentials (admin) | stable |
| R6 | `POST /v1/webhooks` | Member credentials (admin) | stable |
| R6 | `POST /v1/webhooks/{id}/receive` | Unsigned (sig-verified server-side) | stable |
| R6 | `GET /v1/members` | Member credentials | stable |
| R6 | `POST /v1/members/invite` | Member credentials (admin) | stable |
| R6 | `GET+POST /v1/widget/{slug}` | Integration key (widget-scoped) | stable |
| R7 | Compiler harness endpoints (TBD at R7 briefing) | Integration key, Member credentials | provisional |
| R8 | No new endpoints; security hardening only | — | — |

*R5 provisional endpoints promote to `stable` at R6 open.*

**Authentication mode definitions:**

- **Integration key** — workspace-scoped bearer token; used by machine-to-machine integrations and external MCP clients.
- **Member credentials** — short-lived JWT issued by `auth-service`; used by the React frontend (console app).
- **Agent credentials** — workspace-scoped agent identity token; used by running harnesses calling back to the gateway.

**No dual-surface endpoints.** The two surfaces have different protocol semantics, versioning schemes, and error formats; unified handlers would produce a leaky abstraction.

### 5. api-client churn absorption

The `packages/api-client` typed shell (ORA-88) insulates all feature code from gateway contract churn during the R5→R6 provisional period via three components:

**Component A — Import boundary enforcement (CI gate, ORA-83)**

No file outside `packages/api-client/` may import from gateway URLs or from `packages/api-client/internal/`. Impact radius is bounded to one package regardless of endpoint stability.

**Component B — Provisional stub convention**

Every provisional endpoint stub is marked:

```typescript
// Contract: provisional — [endpoint] — resolves at R6
// Shape: [brief inline schema comment]
// Tracking: ORA-NNNN
```

Returns typed mock data in dev (mock seam); returns typed `ProvisionalEndpointNotYetAvailable` error in production CI until the live gateway accepts the call. Feature code gets a compile-time signal, not a silent runtime failure.

**Component C — R6 promotion**

1. `devops-implementer` publishes `openapi/v1.yaml`.
2. `frontend-implementer` runs `openapi-typescript` to generate types into `packages/api-client/generated/`.
3. CI diff check compares generated types against checked-in stubs; failures addressed in api-client only.
4. Provisional stubs replaced by re-exported generated types; mock seam wired to live transport.

Single, isolated PR to `packages/api-client`. Feature code unchanged if shapes promoted cleanly.

## Consequences

### Positive

- **One versioning scheme, mechanically enforced.** `/v1/` URL prefix detectable at router and CI; OpenAPI diff gate enforces stable endpoint immutability automatically from R6.
- **FE track absorbs R5 churn without feature breakage.** Import-boundary gate + provisional stub convention isolate shape changes to one package.
- **MCP/REST boundary is explicit.** No endpoint is ambiguously "both." Callers know which surface to target based on auth mode and protocol stack.
- **R6 promotion path defined ahead of time.** `devops-implementer` and `frontend-implementer` each have a clear deliverable.

### Negative

- **Shared-fixture approach (R5) is manual.** Drift undetected until R6 codegen diff. solution-architect spot-checks fixture coverage at R5 Tests Review gate.
- **Two contract documents exist simultaneously during R5** (Python fixture for BE, manual stub for FE). Known cost; accepted to avoid blocking RF Phase A on the live spec.
- **MCP surface not covered by OpenAPI diff gate.** MCP surface changes must be caught in MCP-specific integration tests (R6 work); solution-architect reviews MCP PRs at Code Review.
- **`x-stability` is an informal extension.** Enforcement is CI-only, not spec-native; tooling unaware of it will ignore the field.

## See also

- Section 3 — Layered Architecture: Layer 4 (Application Gateway) — the layer this ADR governs the external surface of
- ADR-001 — Four-Layer Architecture — the founding commitment placing the gateway at Layer 4
- ADR-007 — BYOM with Three Protocol Shapes — the `protocol_shape` enum used when the gateway invokes harnesses
- ADR-009 — Metering at Substrate, Billing as Separable — billing surface deliberately absent from the gateway contract scope
- ORAA-28 — the decision to stand up the gateway incrementally (the driving context this ADR responds to)
- RF Phase A release page — the api-client typed shell (ORA-88) this ADR's churn-absorption strategy targets
- R5 release page — the first provisional endpoint window this ADR governs
- R6 release page — the consolidation/hardening window where provisional → stable promotion happens
