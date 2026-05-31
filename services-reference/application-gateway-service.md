---
confluence_id: "131124"
title: "application-gateway-service"
---

# application-gateway-service

**Layer:** 4 (Application Gateway) · **Port:** 8007 · **Status:** NEW in Phase 6 (lifted from `knowledge-graph-builder` and `oraclous-core-service`)

## Purpose

`application-gateway-service` is the platform's contract with the outside world. It exposes the public-facing surface: REST APIs, MCP server, MCP client, webhook receivers, published agents, embeddable widgets, and member-facing UIs. Everything an external caller interacts with goes through this layer.

The gateway pulls together public surfaces that previously lived scattered across `knowledge-graph-builder` (chat APIs, published agents, integration keys) and `oraclous-core-service` (some workflow-era endpoints). Consolidating them gives the platform a single security boundary and a single consistent rate-limiting policy.

## Responsibilities

* Public REST APIs for harnesses, chats, capabilities, members
* Chat APIs (the persistence layer lives here; the execution backing remains the harness runtime)
* Published agents and integration keys (slug-based routing, key validation, rate limits)
* **MCP server** — exposes the workspace's capabilities to external MCP clients (Claude Desktop, Cursor, custom integrations)
* **MCP client** — connects to external MCP servers and imports their tools into the capability registry
* Webhook receivers (incoming events from external systems trigger harness executions)
* Embeddable widget endpoints (iframe-loadable UIs for customer-side embedding)
* Member-facing UIs (the React frontend communicates here)
* CORS scoping per integration key
* Authentication enforcement for external callers (integration keys, member credentials, agent credentials)
* Rate limiting per integration key and per published agent
* Request size limits
* Webhook signature verification

## Dependencies

* **Upstream:** `auth-service` (authentication), `capability-registry-service` (capability discovery for MCP exposure), `harness-runtime-service` (execution backing for customer-facing flows), `knowledge-retriever-service` (chat retrieval)
* **Downstream consumers:** all external callers (customers, customer-side integrations, MCP clients, webhook senders)

## What lifts in (Phase 6)

From `knowledge-graph-builder`:

* Chat persistence (`chat_history_service.py`, chat endpoints, RLS policies on Postgres tables)
* Published agents and integration keys (`integration_key_service.py`, public endpoints)
* Embeddable widget endpoints

New work in Phase 6:

* MCP server implementation (drawing lessons from the retired MCP work but written fresh per Section 7 — `docs/RETIRED-mcp-substrate.md` documents what to avoid)
* MCP client integration (importing external MCP tools into the registry)
* Webhook receivers
* Task board UI APIs

## What does NOT live here

* **Capability execution** — that's the runtime + execution engine; the gateway proxies, it does not execute
* **Substrate writes** — the gateway never writes directly to Neo4j or the credential broker; it goes through the appropriate substrate service
* **Business logic** — the gateway is a thin shell; the logic lives in the lower layers

## MCP server

The MCP server surface is determined by ReBAC. A connected MCP client authenticates with an integration key (or member credentials), and the server exposes only the capabilities the authenticated actor has access to in the connected workspace. The MCP server deliberately does NOT expose the substrate's internals, the full registry, other workspaces' capabilities, or platform-update mechanisms (Section 7).

## Security commitments

* Authentication required on every endpoint (no anonymous access except clearly-marked public endpoints like login)
* Rate limiting at the integration-key level prevents DoS via published agents (Section 6.5 Threat 7)
* Indistinguishable 404s on unauthorised resources (Section 6.5 Threat 8.1)
* Request size limits
* CORS strictly scoped per integration key
* Webhook signatures verified before triggering execution
* Inbound MCP tool imports go through adapter validation; output schema enforcement applies to MCP-imported capabilities like any other

## Related

* ADR-001 — Four-Layer Architecture (Layer 4)
* ADR-011 — External Jira and Confluence (gateway exposes integration but does not depend on Atlassian for platform functioning)
* Section 3 — Application Gateway layer
* Section 7 — Portability Story (MCP server + client)
* Section 8 — Phase 6 (gateway extraction)
