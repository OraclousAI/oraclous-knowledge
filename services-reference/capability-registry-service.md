---
source_page_id: 884757
title: "capability-registry-service"
---

# capability-registry-service

**Layer:** 2 (Capability Registry) · **Port:** 8001 · **Status:** Evolved from `oraclous-core-service` in Phase 2

## Purpose

`capability-registry-service` is the substrate's discovery surface. It is the single source of truth for what can be composed in a workspace — tools, skills, agents, harnesses, human roles. Every capability has a uniform descriptor model with kind discrimination; every resolution goes through one path.

## Responsibilities

* Unified capability descriptor model (one schema with kind discrimination)
* Capability resolution: name → descriptor → invocation handle
* Versioning: content hash for every descriptor, optional semver tags
* Adapter contracts (inbound: external format → OHM; outbound: OHM → external format)
* ReBAC-gated visibility (capabilities scoped to workspaces; cross-workspace sharing requires explicit relationships)
* Capability registration API (workspace admins can add tools, skills, agents)
* MCP tool importer (Phase 2 deliverable — the first inbound adapter)
* Validation: input/output schema conformance, credential-requirement accuracy

## The five kinds

* **tool** — invokable function with input/output schemas (e.g., `google_drive_reader`, `cypher_query`)
* **skill** — Markdown-shaped prose loaded into an agent's context (e.g., `code_review_skill`, `consciousness_skill`)
* **agent** — actor with role, capability allocation, consciousness configuration, LLM config
* **harness** — orchestrated assembly of actors with task board, policies, orchestration prose
* **human_role** — declared participation slot in a harness, resolved against the workspace member directory

A `capability_pack` (sixth OHM kind from Section 4) is a bundling artifact, not a separately-typed capability — it expands into its contained capabilities on registration.

## Dependencies

* **Upstream:** Postgres (descriptor storage), `auth-service` (for ReBAC visibility checks), `knowledge-graph-service` (for `:Agent` Neo4j nodes that some kinds persist into the graph)
* **Downstream consumers:** `harness-runtime-service` (heavy reader — every actor turn resolves capabilities), `execution-engine-service` (for tool invocations), customer-facing APIs via gateway

## What lifts in, what retires

From `oraclous-core-service`:

* **Tool registry** lifts and consolidates with the in-memory `tool_registry.py` (the dual-registry pattern goes away)
* **Validation service** lifts as-is
* **Credential client** stays as the bridge to `credential-broker-service`
* **Instance manager** salvages into invocation-handle logic, but the concept of an "instance" tied to a workflow node retires

What retires entirely (Section 8 retire list):

* `workflow_service.py` and `pipeline_generator.py` (stubs)
* The workflow DB schema (replaced with OHM-shaped storage for harnesses)
* The instance-manager-as-workflow-node-configurator concept

## Security commitments

* Capability registration requires `capability.register` permission (workspace-admin-scoped by default)
* Content hashing on every capability; modification is a new version, never an overwrite
* Strict schema validation on inputs and outputs (Section 6.5 Threat 2.3)
* Workspace scoping: cross-workspace capability visibility requires explicit relationships (Section 6.5 Threat 2.1)
* Provenance on every capability invocation (with hash) — past invocations queryable for incident response

## Related

* ADR-001 — Four-Layer Architecture (Layer 2)
* ADR-002 — OHM as Canonical Manifest Format
* ADR-005 — Workflow Concept Retirement
* Section 3 — Capability Registry layer
* Section 4 — Manifest Format Specification (all five kinds)
* Section 8 — Phase 2 (registry consolidation)
