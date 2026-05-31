# Section 2 — Conceptual Model

This is the platform's dictionary. Every term has a precise definition.

## Organisation

An organisation is the **outermost tenancy unit** of Oraclous. **Cross-organisation data flow is structurally impossible.** Every node, relationship, query, cache entry, and audit log carries an `organization_id`.

## Workspace

A workspace is the **primary working unit** nested inside an organisation. It contains members, agents, tools, knowledge graphs, harnesses, task boards, and policies. Workspaces are arranged in a **hierarchy** within an organisation.

## Actor

An **actor** is any entity — human member or AI agent — that can be assigned work in a harness. Actors share a common interface: they have an identity, a scope, a capability allocation.

## Agent

An agent is a **non-human actor** with its own identity, role, capability allocation, scope, and consciousness record. Agents are not the LLM — the LLM is a _resource_ the agent uses.

## Capability

A capability is **anything an actor can invoke**. Five kinds: **Tools**, **Skills**, **Agents**, **Harnesses**, **Human roles**.

## Harness

A harness is a **workspace artifact describing how a goal gets done across humans and agents**. It contains: a goal statement, a roster of actors, an orchestration spec, triggers, a task board reference, a policy envelope, and a provenance link.

## Manifest

The manifest is the **serialised form of a harness** in OHM format. Two zones: **Structured zone** (machine-validated) and **Prose zone** (model-interpreted).

## ReBAC

**Relationship-Based Access Control.** Permissions are defined by _relationships_ between entities, not by static roles.

## Metering

Metering is the **substrate-level tracking of resource consumption** per organisation and per workspace. It captures tokens, tool invocations, storage, execution time, and cross-workspace traversals. Metering does NOT assign prices.

## LLM Provider (BYOM)

Oraclous is **BYOM (Bring Your Own Model provider)**. Supported v1 shapes: Anthropic native, OpenAI-compatible, AWS Bedrock native.
