# Glossary

The canonical definitions of terms used throughout the Oraclous knowledge base.

## Conceptual model terms

**Actor** — A participant in a harness execution: an agent, a human member, or an external service granted delegated identity.

**Agent** — A non-human actor with a role, a skill set, a capability allocation, and (usually) a consciousness configuration. Defined in OHM.

**BYOM (Bring Your Own Model)** — The platform's model integration approach. Three protocol shapes for v1: Anthropic native, OpenAI-compatible, AWS Bedrock native.

**Capability** — A named, ReBAC-scoped resource an actor can invoke or compose with. Five kinds: tool, skill, agent, harness, human role.

**Capability Registry** — The platform layer that catalogues capabilities, manages versions, and resolves references during execution.

**Consciousness** — An actor's accumulated memory and learned patterns, configured as a skill. Bounded by explicit permissions.

**Harness** — The composition of actors, a task board, orchestration prose, triggers, and policies into a runnable unit. Replaces the older "workflow" concept.

**HITL (Human-in-the-Loop)** — Orchestration pause for human approval or input. Implemented as task assignment with notification.

**Manifest** — A signed, content-hashed OHM artifact. Versioned by content hash and optional semver tag.

**Metering** — Substrate-level recording of resource usage per organisation. Billing is a cloud-only consumer of metering.

**OHM (Oraclous Harness Manifest)** — The canonical manifest format — YAML with embedded Markdown. Five kinds share the same envelope.

**Organisation** — The outermost tenancy unit. Every customer is one organisation.

**Provenance** — The audit trail of who did what, when, with what authority.

**ReBAC (Relationship-Based Access Control)** — The access model used throughout the platform.

**Substrate** — Layer 1 of the architecture: identity, credentials, knowledge graph, knowledge retrieval, ReBAC, provenance.

**Workspace** — A sub-tenancy unit within an organisation. Has its own knowledge graph, task boards, members.

## Architecture and process terms

**ADR (Architecture Decision Record)** — A dated, immutable record of a decision and its context.

**Contract** — A Jira issue type (id `10049`) that tracks a cross-repository shared shape agreement. Sits between Epic and Story.

**Operator separation** — The principle that Oraclous-the-company staff cannot decrypt or access customer data.
