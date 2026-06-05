---
confluence_id: "131124"
title: "application-gateway-service"
---

# application-gateway-service

**Layer:** 4 (Application Gateway) · **Port:** 8006 · **Status:** **Real — R3.5-complete, §22-signed-off** (Reza ran `smoke.sh` over the full stack). Built as a **streaming reverse-proxy edge**: route table → proxy to the five lower services, edge JWT termination + identity forwarding, CORS, and health aggregation. It holds **no database**. The richer gateway surface (MCP, chat, webhooks, widgets, rate-limiting, API keys, versioned public OpenAPI) is **R6 hardening — not built yet**.

## What it is now (real today)

R3.5 service #6 built the gateway as a thin, stateless edge:

* **Reverse proxy** — a longest-prefix route table maps public paths to upstreams and streams requests/responses through (`httpx` send `stream=True` → `StreamingResponse` + `BackgroundTask` to close the upstream). All five lower services sit behind it: auth, credential-broker, knowledge-graph, knowledge-retriever, capability-registry.
* **Edge JWT termination** — `GATEWAY_AUTH_MODE` (`dev` | `jwt`) verifies the caller's token at the edge, then forwards identity as `X-Principal-*` / `X-Organisation-Id` headers. Inbound copies of those trusted headers are **stripped first** (anti-spoof), so upstreams trust only what the gateway asserts. Public paths (`/v1/auth`, `/oauth`) bypass auth.
* **CORS** — `CORSMiddleware`, origins from config.
* **Health aggregation** — `GET /health` (self) and `GET /health/upstreams` (rolls up every upstream's health with a bounded timeout).

It is the strictest case of the §21 no-logic-in-handlers rule: the gateway proxies and applies policy, it never executes business logic or touches substrate.

## R6 hardening targets (NOT built yet)

The following are the gateway's eventual contract surface and are **deferred to R6** (the "gateway-from-R5 vertical slices" plan is discarded; R6 owns these):

* Public REST APIs for harnesses/chats/capabilities/members; chat persistence
* Published agents and integration keys (slug routing, key validation)
* **MCP server** (expose workspace capabilities to external MCP clients) and **MCP client** (import external MCP tools into [capability-registry-service](capability-registry-service.md))
* Webhook receivers; embeddable widget endpoints
* Rate limiting, request-size limits, webhook signature verification, per-key CORS scoping
* A **versioned public OpenAPI** as the canonical interface home (replacing `flows/interface-contracts.md`)
* The **unified ORA-37 error envelope.** The contract is pinned at `packages/errors/contract/error-envelope.schema.json` (`{error: {code, message, requestId, retryable, details?}}`). The gateway's own-error body is currently the non-conformant `{error_code, message, request_id}` — corrected by the **error-contract slice pulled forward** ahead of the frontend (build the `oraclous_errors` emitter; make the gateway emit the canonical envelope for its own errors and normalize upstream 4xx/5xx into it).
* **Sole-ingress** posture (closing upstream host ports) — a security-architect call; upstream ports stay open today for per-service smokes + defense-in-depth.

## Dependencies

* **Upstream:** [auth-service](auth-service.md) (human + machine authentication), [capability-registry-service](capability-registry-service.md), [knowledge-graph-service](knowledge-graph-service.md), [knowledge-retriever-service](knowledge-retriever-service.md), [credential-broker-service](credential-broker-service.md) — all proxied; the gateway never reads their secrets or substrate directly
* **Downstream consumers:** all external callers (the frontend; later, customers, MCP clients, webhook senders)

## What does NOT live here

* **Capability execution** — [capability-registry-service](capability-registry-service.md); the gateway proxies, it does not execute
* **Substrate writes** — the gateway never writes Neo4j or the credential store directly; it goes through the owning service
* **Business logic** — the gateway is a thin shell; logic lives in the lower layers
* **A database** — by design, the gateway is stateless

## Architecture conformance (ORAA-4 §21)

Layered shape: package root `services/application-gateway-service/src/oraclous_application_gateway_service/` with `routes/` (`health_routes`, `proxy_routes` — the catch-all uses `response_model=None`), proxy/policy logic in `services/` (`proxy_service`, `health_service`), the route table + auth policy in `domain/`, the upstream client in `repositories/`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan,auth}.py`. No business logic in handlers; no DB drivers anywhere (no DB). `structure_enforced: true`, `claimed_done: true`.

## Definition of Done (ORAA-4 §22) — MET

All 8 gates passed for the reverse-proxy edge: structurally conformant; not hollow (`check_no_stubs` zero findings, `claimed_done: true`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: a request proxied to a real upstream via an in-process ASGI upstream; 502/504 on connect/timeout); end-to-end smoke (`tests/smoke/smoke.sh` over the full stack, `r3_5_gate` job); Reza personally signed off. The R6 hardening targets above are tracked separately and are **not** part of this DoD.

## Related

* ADR-001 — Four-Layer Architecture (Layer 4)
* ADR-015 — Gateway Incremental Contract and Versioning
* [capability-registry-service](capability-registry-service.md) — capability source for future MCP exposure
* Section 7 — Portability Story (MCP server + client) — an R6 target
