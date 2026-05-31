# Section 7 — Portability Story

**Related structured artifact:** [OHM v1.0 — Standalone Specification](../ohm-v1.0-standalone-specification.md)

## The thesis

Oraclous publishes a manifest format (OHM) and a reference runtime, but does not lock customers into either.

## OHM as the canonical hub

Every portability operation routes through OHM. All inbound translations produce OHM. All outbound translations start from OHM.

## Oraclous as an MCP server

Oraclous exposes itself as an MCP server through the Application Gateway. Any MCP-compatible client (Claude Desktop, Cursor, Continue) can connect. The MCP server surface is determined by ReBAC.

## Oraclous as an MCP client

Oraclous can consume external MCP servers, bringing their tools into the Capability Registry as native OHM tools.

## Inbound adapters: external → OHM

- **Claude Code SKILL.md adapter** — translates SKILL.md files to OHM skills
- **MCP tool adapter** — translates MCP tool definitions to OHM tools
- **OpenAPI / REST adapter** — translates OpenAPI 3.x specs to OHM tools (one tool per operation)

## What portability does NOT cover

- **Knowledge graph data** — handled through standard export formats (Neo4j dumps, RDF, JSON-LD)
- **Member directory and ReBAC graph** — platform-internal
- **Credentials** — never leave the credential broker
- **Per-actor consciousness records** — substrate-anchored; exporting exports the OHM definition but not accumulated consciousness
