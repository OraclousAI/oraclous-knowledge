---
confluence_id: "786454"
title: "Section 1 — Platform Overview"
---

# Section 1 — Platform Overview

## What Oraclous is, in one paragraph

Oraclous is an open-source platform that lets organisations form a **second mind** — a unified operational fabric where human members and AI agents work side by side, governed by the organisation's own access rules and orchestrated by goals written in natural language. The platform is **data-sovereign by design** and deployable in two modes: customers can self-host it on their own infrastructure, or have Oraclous-the-company host it on their behalf under equivalent data-sovereignty guarantees backed by ISO 27001 and SOC 2 Type II compliance. It combines a knowledge-graph substrate (data and access control), a capability registry (what humans and agents can do), a harness compiler (turns goals into mixed human-agent teams), and a harness runtime (executes those teams under coded governance). Harnesses, task boards, and capabilities are portable across runtimes via an open manifest format, so work defined in one environment — Oraclous, Claude Code, Codex, others — can flow across the rest. Customers bring their own model providers (BYOM): Anthropic, OpenAI, OpenRouter, Azure OpenAI, AWS Bedrock, or any OpenAI-compatible self-hosted endpoint — the platform never locks customers into a specific LLM vendor.

## The thesis

Inspired by the concept of singularity at the organisational scale: Oraclous treats the merger of human and AI work inside a company as a design target, not an afterthought. Today, enterprises have scattered data, scattered tools, scattered AI integrations, and humans doing the integration work in their heads. Oraclous lets organisations form a **harness** around all of it — a unified structure where humans and agents share task boards, hand work back and forth, escalate to each other, and operate under one coherent governance model. The organisation's work and its AI become operationally one fabric.

## What problem it solves

Today, organisations that want to deploy agentic systems face three bad choices:

* **Build bespoke pipelines in code** — slow, brittle, requires engineers for every change.
* **Adopt a closed SaaS platform** — loses data sovereignty, loses portability, gets locked in.
* **Wire together frameworks like LangChain** — gains code reuse but inherits the framework's opinions and still requires engineering work per use case.

None of these scale across departments with different needs, different data, and different access boundaries. None of them treat human members as first-class participants in agent workflows.

Oraclous solves this by separating **what work needs doing** (prose, written by operators) from **how the runtime enforces it** (code, written once by the platform), and by making humans and agents symmetric actors in that work. Operators describe goals; the platform compiles those goals into harnesses; the runtime executes harnesses while routing work to humans or agents as each step requires, all under the organisation's ReBAC, credentials, budgets, and policies. Engineering effort moves from per-use-case orchestration to platform-level guarantees.

## What Oraclous is not

* Not a chatbot framework
* Not a workflow tool with an agent skin
* Not a LangChain alternative
* Not a fine-tuning-only platform (FTOps is one application built on the platform)
* Not a "replace your humans with AI" tool
* Not a vendor-locked LLM platform — customers bring their own provider
* Not a closed-source proprietary platform — open-source at every layer

It is a substrate for **mixed human-agent work over organisational data**, and a format for making that work portable. It is **operationally available in both self-hosted and cloud-hosted deployment modes** under the same data-sovereignty commitments — the difference is who operates the substrate, not what guarantees it provides.

## Deployment modes

The platform is the same code in both modes. What changes is operational responsibility:

### Self-hosted mode

The customer deploys Oraclous on their own infrastructure — on-premises servers, their own cloud account, an air-gapped environment, anywhere they choose. They operate the substrate, manage the upgrade cadence, control their data physically and logically. This is the original deployment mode and remains a first-class commitment.

### Cloud-hosted mode

Oraclous-the-company operates the platform on behalf of customers who prefer not to run their own infrastructure. The platform is deployed on dedicated infrastructure operated to ISO 27001 and SOC 2 Type II compliance standards. **Data-sovereignty guarantees are identical to self-hosted mode** — customer data never crosses organisation boundaries, is never used by Oraclous-the-company for any purpose beyond operating the customer's own platform, and is never aggregated across customers. The operational difference is who handles deployment, upgrades, and infrastructure — not what happens to the data.

The architectural principle: **same code, same guarantees, different operator.** Cloud mode is not a separate platform; it is a deployment configuration of the same platform, with explicit compliance commitments by Oraclous-the-company to enterprise customers who require them.

## High-level shape — the four layers

The platform divides into four layers, each owning a distinct concern. A foundational design principle threads through all of them: **the platform is code; the actors and orchestration on top are harnesses.** Everything that _enforces or executes_ is platform code. Everything that _reasons and acts_ is a harness running on top of that platform. The compiler, consciousness agents, self-modification agents, FTOps, digital twins — all of these are harnesses, not platform layers.

### Substrate Layer

Knowledge graphs, ReBAC, identity (human and agent, symmetric), credentials, audit, workspace hierarchy. The trust root. Everything else delegates here for "who — human or agent — can do what with what."

### Capability Registry

The single source of truth for what tools, skills, agents, harnesses, **and human roles** exist in a workspace. Carries both structured schemas (for runtime) and natural-language descriptions (for harnesses that need to reason about available capabilities — including the compiler). Human roles appear here as a capability kind — _"the brand lead can review copy"_ is a capability the compiler can route to.

### Harness Runtime + Execution Engine

Executes committed harnesses. Drives the model → tool → model loop for agents, manages task boards (shared with humans), routes tasks to human assignees and waits on their completion, runs schedules and triggers, enforces policies, handles HITL gates, traverses workspaces under delegated identity. The Execution Engine is the durable side — long-running jobs, retries, checkpoints, pause/resume.

This is the layer the platform's recursive design rests on: it must be powerful enough to host the compiler, consciousness agents, and self-modification agents as harnesses from day one.

### Application Gateway

The public-facing surface — for both external API consumers and internal members. Task board UIs for members, published agents, integration keys, embeddable widgets, the API consumed by applications built on the platform.

## What sits on top of the platform (not part of it)

Several systems that might intuitively feel like "platform features" are deliberately **not** platform layers in Oraclous. They are harnesses installed by default on every workspace, running on the same runtime customers use for their own harnesses:

* The **Harness Compiler** — agents that turn goals into manifests
* The **Consciousness System** — skills or specialised agents that record and consult experiential memory
* The **Self-Modification System** — agents that propose harness mutations
* The **Harness Review System** — agents that surface proposed changes for HITL approval
* All **end-user applications** — FTOps, digital twins, customer support, code audit

This is the recursion principle: nothing the platform does is hidden from customers. The same primitives that built the default compiler are the primitives customers use to build their own. There is no platform-layer magic.

## How the layers relate

**A goal flows down through the platform:**

1. Operator states a goal in natural language
2. Operator invokes the default compiler harness (or a custom one they've installed)
3. The compiler harness — executing on the runtime, like any other harness — reads workspace capabilities from the registry
4. The compiler surveys available data via the substrate (ReBAC-bounded)
5. The compiler emits a draft manifest
6. Operator reviews and edits (often through dialog with the compiler)
7. Manifest commits to the substrate as a new harness

**An execution flows similarly:**

1. A trigger fires (event, schedule, manual, external)
2. Runtime loads the harness from substrate
3. Runtime resolves capability allocations via the registry
4. Runtime asks substrate for ReBAC checks and credential resolution
5. Runtime executes — dispatching tools, assigning tasks to humans or agents, waiting on results
6. Runtime writes provenance back to substrate

The Application Gateway sits outside this loop, exposing committed harnesses, capabilities, and task boards to external consumers and internal members without giving them direct substrate access.

Note the symmetry: **the compiler running is the same operation as any harness running.** The compiler is not a privileged platform component; it is a privileged-by-default harness with appropriate scopes.
