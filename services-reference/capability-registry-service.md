# capability-registry-service

**Layer:** 2 (Capability Registry) · **Port:** 8001 · **Status:** Evolved from `oraclous-core-service` in Phase 2

## Purpose

The single source of truth for what can be composed in a workspace — tools, skills, agents, harnesses, human roles. Every capability has a uniform descriptor model.

## Responsibilities

- Unified capability descriptor model (one schema with kind discrimination)
- Capability resolution: name → descriptor → invocation handle
- Versioning: content hash + optional semver tags
- Adapter contracts (inbound: external format → OHM; outbound: OHM → external format)
- ReBAC-gated visibility
- MCP tool importer (first inbound adapter)

## The five kinds

- **tool** — invokable function with input/output schemas
- **skill** — Markdown-shaped prose loaded into an agent's context
- **agent** — actor with role, capability allocation, consciousness config, LLM config
- **harness** — orchestrated assembly of actors
- **human_role** — declared participation slot resolved against the workspace member directory
