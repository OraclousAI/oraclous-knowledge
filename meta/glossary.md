---
confluence_id: "720981"
title: "Glossary"
---

# Glossary

The canonical definitions of terms used throughout the Oraclous knowledge base. Anywhere two pages might disagree about what a term means, this page wins.

## Conceptual model terms

These mirror Section 2 of Architecture v1.1. The architecture document is the source of truth; this page is a compact index.

**Actor**  
A participant in a harness execution: an agent, a human member, or an external service granted delegated identity. The Runtime treats actors symmetrically — the orchestration logic for waiting on a human is the same as waiting on an agent.

**Agent**  
A non-human actor with a role, a skill set, a capability allocation, and (usually) a consciousness configuration. Defined in OHM.

**Application**  
A consumer of the platform's Gateway: a UI, an MCP client, or any service that calls the platform's external surface.

**Capability**  
A named, ReBAC-scoped resource an actor can invoke or compose with. Five kinds: tool, skill, agent, harness, human role.

**Capability Registry**  
The platform layer that catalogues capabilities, manages versions, and resolves references during execution.

**Compiler**  
The platform-level harness that turns prose goals into OHM harness manifests. The default compiler ships with Oraclous and is itself customisable by customers.

**Consciousness**  
An actor's accumulated memory and learned patterns, configured as a skill. Bounded by explicit permissions (`can_record_observations`, `can_suggest_tools`, etc).

**Delegated Identity**  
The mechanism by which an actor takes action on behalf of another identity, with explicit, time-bounded, audited scope.

**Execution Engine**  
The substrate component that manages durable execution state — schedule firing, in-flight job persistence, retry handling, resume-after-restart.

**Harness**  
The composition of actors, a task board, orchestration prose, triggers, and policies into a runnable unit. Replaces the older "workflow" concept (ADR-005).

**Manifest**  
A signed, content-hashed OHM artifact: harness, agent, skill, tool, or capability. Versioned by content hash and optional semver tag.

**Member**  
A human participant in an organisation, with a workspace assignment and a role.

**Metering**  
Substrate-level recording of resource usage (LLM tokens, tool invocations, storage, executions) per organisation. Billing is a cloud-only consumer of metering.

**OHM (Oraclous Harness Manifest)**  
The canonical manifest format — YAML with embedded Markdown. Five kinds (harness, agent, skill, tool, capability) share the same envelope.

**Organisation**  
The outermost tenancy unit. Every customer is one organisation. In cloud-hosted mode many organisations share a substrate, isolated by `organization_id` scoping (ADR-006).

**Provenance**  
The audit trail of who did what, when, with what authority. Every flow writes to the same provenance spine. The substrate's primary observability surface for domain behaviour.

**ReBAC (Relationship-Based Access Control)**  
The access model used throughout the platform. Permissions emerge from typed relationships in a graph, not from role bindings.

**Round-Table**  
A synchronous (or near-synchronous) multi-actor conversation to resolve a question or alignment issue. A Runtime primitive distinct from task boards.

**Runtime**  
The platform layer that loads harnesses, resolves capabilities, dispatches actors, enforces policies, and writes provenance. Includes the harness-runtime-service and execution-engine-service.

**Skill**  
A named behaviour bundle an agent can load. Consciousness is a skill. Defined in OHM.

**Substrate**  
Layer 1 of the architecture: identity, credentials, knowledge graph, knowledge retrieval, ReBAC, provenance. Shared by everything above.

**Task Board**  
The structured queue of work attached to a harness. Each harness has its own board with declared columns and transitions.

**Tool**  
A leaf capability that performs a discrete action (call an API, run a query, send a notification). Defined in OHM as a manifest with declared inputs, outputs, and credentials.

**Workspace**  
A sub-tenancy unit within an organisation. Has its own knowledge graph, its own task boards, its own members. Cross-workspace traversal happens via federation under ReBAC (ADR-004).

## Architecture and process terms

**ADR (Architecture Decision Record)**  
A dated, immutable record of a decision and its context. Stored under 02. ADRs. Superseded by reference, never edited in place.

**Bootstrap update**  
The flow by which Oraclous-published default artifacts (compiler, consciousness skill, etc) reach customer workspaces. Always opt-in.

**BYOM (Bring Your Own Model)**  
The platform's model integration approach. Three protocol shapes for v1: Anthropic native, OpenAI-compatible, AWS Bedrock native (ADR-007).

**Cloud-hosted**  
The deployment mode operated by Oraclous-the-company on behalf of customers. Same code as self-hosted with equivalent data-sovereignty guarantees (ADR-008).

**HITL (Human-in-the-Loop)**  
Orchestration pause for human approval or input. Implemented as task assignment with notification, not a separate subsystem.

**Self-hosted**  
The deployment mode operated by the customer on their own infrastructure.

## Platform conventions

**Content hash**  
The cryptographic hash of an OHM manifest's canonical form. The primary identifier for manifest versions.

**Semver tag**  
An optional human-readable version label attached to a content hash (e.g. `default-compiler@2.1.0`).

**Operator separation**  
The principle that Oraclous-the-company staff cannot decrypt or access customer data; technical enforcement via per-organisation KMS keys with split control.

## Related references

* **Section 2 of Architecture v1.1** — full conceptual model with detail
* **02. ADRs** — decisions referenced by glossary entries
* **Documentation Conventions** — when to define a term inline vs. add it here

