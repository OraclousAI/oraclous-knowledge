---
confluence_id: "131124"
title: "application-gateway-service"
---

# application-gateway-service

**Layer:** 4 (Application Gateway) · **Port:** 8006 · **Status:** **Real — R3.5-complete, §22-signed-off** (Reza ran `smoke.sh` over the full stack). Built as a **streaming reverse-proxy edge**: route table → proxy to seven lower services (the five substrate/capability services plus harness-runtime and execution-engine), edge JWT termination + identity forwarding with ADR-018 `X-Internal-Key` attestation, CORS, and health aggregation. It holds **no database** today (R6 Slice 3 adds a dedicated gateway store, ADR-019). **R6 hardening is underway:** the **versioned public OpenAPI contract** (Slice 1) and the **edge rate-limit + request-size guard** (Slice 2) are built; MCP, chat, webhooks, widgets, integration keys, and sole-ingress remain.

## What it is now (real today)

R3.5 service #6 built the gateway as a thin, stateless edge:

* **Reverse proxy** — a longest-prefix route table maps public paths to upstreams and streams requests/responses through (`httpx` send `stream=True` → `StreamingResponse` + `BackgroundTask` to close the upstream). Seven lower services sit behind it: auth (`/v1/auth`, `/v1/orgs`, `/v1/invitations`, `/oauth`), credential-broker (`/credentials`), knowledge-graph (`/api/v1/graphs`, `/api/v1/recipes`), knowledge-retriever (`/v1/search`, `/v1/graph`), capability-registry (`/api/v1/{capabilities,tools,instances,executions}`) on Layers 1–2, plus harness-runtime (`/v1/harnesses`) and execution-engine (`/v1/engine`) on Layer 3. Health aggregation (`/health/upstreams`) rolls up only the five substrate/capability services.
* **Edge JWT termination** — `GATEWAY_AUTH_MODE` (`dev` | `jwt`) verifies the caller's token at the edge, then forwards identity as `X-Principal-*` / `X-Organisation-Id` headers. Inbound copies of those trusted headers are **stripped first** (anti-spoof), so upstreams trust only what the gateway asserts. Only `/v1/auth` and `/oauth` bypass edge auth; `/v1/orgs` and `/v1/invitations` are proxied to auth-service but stay authenticated.
* **Edge-auth attestation (ADR-018)** — every forwarded request carries a shared `X-Internal-Key` (`INTERNAL_SERVICE_KEY`; any client-supplied copy stripped first) so upstreams in gateway-mode can prove the request actually transited the gateway and trust the `X-Principal-*` headers.
* **CORS** — `CORSMiddleware`, origins from config.
* **Health aggregation** — `GET /health` (self) and `GET /health/upstreams` (rolls up the five substrate/capability upstreams' health with a bounded timeout).
* **Canonical ORA-37 error envelope** — every 4xx/5xx the gateway returns (its own errors AND normalized upstream errors) is the canonical `{error:{code, message, requestId, retryable, details?}}` shape via the shared `oraclous_errors` emitter; upstream error bodies are drained and discarded so no upstream stack trace / SQL / internal host leaks through the edge (Interface Contracts §3 rule 8). `requestId` is the server-minted `req_*` correlation id set by `RequestIdMiddleware` and echoed in `X-Request-Id`.

It is the strictest case of the §21 no-logic-in-handlers rule: the gateway proxies and applies policy, it never executes business logic or touches substrate.

## R6 hardening — shipped so far

* **Versioned public OpenAPI contract (Slice 1, ADR-015)** — the gateway publishes the canonical `openapi/v1.yaml` at `/v1/openapi.json` + `/v1/openapi.yaml` + a Swagger UI at `/docs` (served before the proxy catch-all; FastAPI's leaky auto-spec is disabled). The spec carries the closed ORA-37 `ErrorEnvelope` (byte-identical to the cross-repo schema), per-operation `x-stability`, and only operations that actually route (no `/internal` plane). An `openapi-diff-gate` CI job blocks any breaking change to a `stable` operation. `openapi/v1.yaml` is now the source of truth for what the gateway exposes.
* **Edge rate-limit + request-size guard (Slice 2)** — two pure-ASGI edge middlewares (never `BaseHTTPMiddleware`, so the streaming proxy is never buffered):
  * **Request-size guard — FAIL-CLOSED:** `413 PAYLOAD_TOO_LARGE` when a body is not positively within `MAX_REQUEST_BODY_BYTES` — a Content-Length fast-path plus an authoritative byte counter that stops reading at `max+1` (catches chunked / omitted-length; never buffers an oversize upload to measure it).
  * **Rate limit — FAIL-OPEN:** a Redis-backed (own DB 2) per-client-IP fixed window (`INCR`+`EXPIRE` in a transactional pipeline) → `429 RATE_LIMITED` + `Retry-After`. A Redis outage logs + **allows** — the gateway is the sole ingress, so throttling on a Redis blip would self-DoS the platform; short Redis socket timeouts make the fail-open instant under a partition. Liveness + contract probes (`/health*`, `/v1/openapi.*`, `/docs`) are exempt.
  * **X-Forwarded-For trust boundary** (`TRUSTED_PROXY_COUNT`, default 0): at 0 the client-IP key is the socket peer and XFF is ignored (a rotating XFF can't fork buckets); at N>0 the (N+1)-th hop from the right, never the spoofable left-most. **Security ruling (recorded):** fail-open rate limit, fail-closed size guard, count-XFF-from-the-right — residual risks: no volumetric protection during a Redis outage (alert-driven), shared egress (NAT) shares a bucket, a misconfigured `TRUSTED_PROXY_COUNT` re-opens spoofing (default 0 is the safe floor). Both 429/413 are the ORA-37 envelope, carry `X-Request-Id`, and (CORS sits outside the guards) carry `Access-Control-Allow-Origin` so a browser can read them.

## R6 hardening targets (NOT built yet)

The following are the gateway's eventual contract surface and are **deferred to R6** (the "gateway-from-R5 vertical slices" plan is discarded; R6 owns these):

* Public REST APIs for harnesses/chats/capabilities/members; chat persistence
* Published agents and integration keys (slug routing, key validation)
* **MCP server** (expose workspace capabilities to external MCP clients) and **MCP client** (import external MCP tools into [capability-registry-service](capability-registry-service.md))
* Webhook receivers (+ signature verification); embeddable widget endpoints
* **Per-key / per-origin CORS scoping** (Slice 5 — the edge-wide rate-limit + size guard shipped in Slice 2; per-*key* limits/CORS ride the integration-key store)
* **Sole-ingress** posture (closing upstream host ports) — a security-architect call; upstream ports stay open today for per-service smokes + defense-in-depth.

## Dependencies

* **Upstream:** [auth-service](auth-service.md) (human + machine authentication), [capability-registry-service](capability-registry-service.md), [knowledge-graph-service](knowledge-graph-service.md), [knowledge-retriever-service](knowledge-retriever-service.md), [credential-broker-service](credential-broker-service.md), [harness-runtime-service](harness-runtime-service.md) (`/v1/harnesses`), [execution-engine-service](execution-engine-service.md) (`/v1/engine`) — all proxied; the gateway never reads their secrets or substrate directly
* **Downstream consumers:** all external callers (the frontend; later, customers, MCP clients, webhook senders)

## What does NOT live here

* **Capability execution** — [capability-registry-service](capability-registry-service.md); the gateway proxies, it does not execute
* **Substrate writes** — the gateway never writes Neo4j or the credential store directly; it goes through the owning service
* **Business logic** — the gateway is a thin shell; logic lives in the lower layers
* **A database** — by design, the gateway is stateless **today**. (Forward note: **R6 adds a dedicated gateway-owned, org-scoped Postgres** for the integration-key store, published-agent records, and chat persistence — per [ADR-019](../adr/adr-019-r6-gateway-datastore-and-integration-key-authz-floor.md). This reverses the no-DB invariant for those three surfaces only; the proxy/auth/health paths stay stateless.)

## Architecture conformance (ORAA-4 §21)

Layered shape: package root `services/application-gateway-service/src/oraclous_application_gateway_service/` with `routes/` (`health_routes`, `proxy_routes` — the catch-all uses `response_model=None`), proxy/policy logic in `services/` (`proxy_service`, `health_service`), the route table + auth policy in `domain/`, the upstream client in `repositories/`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan,auth}.py`. No business logic in handlers; no DB drivers anywhere (no DB). `structure_enforced: true`, `claimed_done: true`.

## Definition of Done (ORAA-4 §22) — MET

All 8 gates passed for the reverse-proxy edge: structurally conformant; not hollow (`check_no_stubs` zero findings, `claimed_done: true`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: a request proxied to a real upstream via an in-process ASGI upstream; 502/504 on connect/timeout); end-to-end smoke (`tests/smoke/smoke.sh` over the full stack, `r3_5_gate` job); Reza personally signed off. The R6 hardening targets above are tracked separately and are **not** part of this DoD.

## Related

* ADR-001 — Four-Layer Architecture (Layer 4)
* ADR-015 — Gateway Incremental Contract and Versioning
* [capability-registry-service](capability-registry-service.md) — capability source for future MCP exposure
* Section 7 — Portability Story (MCP server + client) — an R6 target
