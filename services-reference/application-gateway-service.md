# application-gateway-service

**Layer:** 4 (Application Gateway) · **Port:** 8007 · **Status:** NEW in Phase 6

## Purpose

`application-gateway-service` is the platform's contract with the outside world. It exposes the public-facing surface: REST APIs, MCP server, MCP client, webhook receivers, published agents, embeddable widgets, and member-facing UIs.

## Responsibilities

- Public REST APIs
- Chat APIs (persistence here; execution via harness runtime)
- Published agents and integration keys (slug-based routing, key validation, rate limits)
- **MCP server** — exposes workspace capabilities to external MCP clients
- **MCP client** — connects to external MCP servers, imports their tools
- Webhook receivers
- Member-facing UIs
- Authentication enforcement, rate limiting, CORS scoping
