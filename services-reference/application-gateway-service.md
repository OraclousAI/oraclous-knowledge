---
confluence_id: "131124"
title: "application-gateway-service"
---

# application-gateway-service

**Layer:** 4 (Application Gateway) · **Port:** 8007 · **Status:** **Placeholder — built last (R3.5 step 6).** It does not exist yet. Until it is built, every service is reached **directly by host IP:port** (legacy parity — legacy had no gateway).

## Honest current reality

There is no gateway today, and there is no gateway for most of R3.5. It is **step 6**, the final service in the per-service order, built only after the graph, retriever, identity-org, credential-broker, and capability-registry services are each rebuilt REAL and Reza-signed-off. Until then there is **no single public edge**: the frontend and external callers reach each service **directly by host IP:port**, exactly as the legacy stack did (legacy had no gateway). The old "gateway-from-R5 vertical slices" plan is **discarded** — superseded by R3.5.

## Purpose (R3.5 target, when built last)

`application-gateway-service` is the platform's contract with the outside world: the public REST surface, MCP server, MCP client, webhook receivers, published agents, embeddable widgets, and member-facing UI routing. Everything an external caller touches goes through this one layer, giving the platform a single security boundary and a single rate-limiting policy — replacing the direct IP:port access used until it ships.

## Responsibilities (R3.5 target)

* Public REST APIs for harnesses, chats, capabilities, members
* Chat APIs (persistence here; execution backing stays in the lower services)
* Published agents and integration keys (slug routing, key validation, rate limits)
* **MCP server** — exposes the workspace's capabilities to external MCP clients
* **MCP client** — imports external MCP tools into [capability-registry-service](capability-registry-service.md)
* Webhook receivers (external events trigger executions)
* Embeddable widget endpoints
* Member-facing UI routing (the frontend talks here once it exists)
* CORS scoping per integration key; auth enforcement; rate limiting; request-size limits; webhook signature verification

## Dependencies

* **Upstream:** [identity-org-service](identity-org-service.md) + [auth-service](auth-service.md) (human + machine authentication), [capability-registry-service](capability-registry-service.md) (capability discovery for MCP exposure), [knowledge-retriever-service](knowledge-retriever-service.md) (chat retrieval), [credential-broker-service](credential-broker-service.md) (no direct secret access — proxies through)
* **Downstream consumers:** all external callers (customers, MCP clients, webhook senders, the frontend)

## What does NOT live here

* **Capability execution** — [capability-registry-service](capability-registry-service.md); the gateway proxies, it does not execute
* **Substrate writes** — the gateway never writes Neo4j or the credential store directly; it goes through the owning service
* **Business logic** — the gateway is a thin shell; logic lives in the lower layers

## MCP server

The MCP server surface is ReBAC-determined: a connected client authenticates (integration key or member credentials) and the server exposes only the capabilities that actor can access in the connected workspace. It deliberately does **not** expose substrate internals, the full registry, other workspaces' capabilities, or platform-update mechanisms.

## Architecture conformance (ORAA-4 §21)

Layered shape: package root `services/application-gateway-service/src/oraclous_application_gateway_service/` with `routes/` (parse → one service call → HTTP map), thin proxy/policy logic in `services/`, no direct DB drivers in `routes/`, Pydantic-only `schema/`, `core/{config,dependencies,lifespan}.py`. The gateway holds no business logic and is the strictest case of the no-logic-in-handlers rule.

## Definition of Done (ORAA-4 §22)

Done only when all 8 gates pass: structurally conformant; not hollow (`check_no_stubs` zero findings + `claimed_done` flipped in `service_status.yaml`); runs (`docker compose up` healthy, `GET /health` 200); real endpoints (integration: a public REST + MCP call proxied to real lower services via testcontainers, no stub/501); end-to-end smoke (`tests/smoke/smoke.sh`, run as the docker-required `r3_5_gate` job); Reza personally tests and signs off. Per §23: one service, ≤6 coarse vertical slices.

## Related

* ADR-001 — Four-Layer Architecture (Layer 4)
* ADR-015 — Gateway Incremental Contract and Versioning
* [capability-registry-service](capability-registry-service.md) — capability source for MCP exposure
* Section 7 — Portability Story (MCP server + client)
