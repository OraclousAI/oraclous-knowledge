# Section 1 — Platform Overview

## What Oraclous is, in one paragraph

Oraclous is an open-source platform that lets organisations form a **second mind** — a unified operational fabric where human members and AI agents work side by side, governed by the organisation's own access rules and orchestrated by goals written in natural language. The platform is **data-sovereign by design** and deployable in two modes: customers can self-host it on their own infrastructure, or have Oraclous-the-company host it on their behalf under equivalent data-sovereignty guarantees backed by ISO 27001 and SOC 2 Type II compliance.

## The thesis

Oraclous treats the merger of human and AI work inside a company as a design target, not an afterthought. It lets organisations form a **harness** around all of it — a unified structure where humans and agents share task boards, hand work back and forth, escalate to each other, and operate under one coherent governance model.

## What problem it solves

Today, organisations that want to deploy agentic systems face three bad choices:

- **Build bespoke pipelines in code** — slow, brittle
- **Adopt a closed SaaS platform** — loses data sovereignty and portability
- **Wire together frameworks like LangChain** — gains code reuse but requires engineering work per use case

Oraclous solves this by separating **what work needs doing** (prose, written by operators) from **how the runtime enforces it** (code, written once by the platform), and by making humans and agents symmetric actors in that work.

## Deployment modes

### Self-hosted mode

The customer deploys Oraclous on their own infrastructure. They operate the substrate, manage the upgrade cadence, control their data physically and logically.

### Cloud-hosted mode

Oraclous-the-company operates the platform on behalf of customers. **Data-sovereignty guarantees are identical to self-hosted mode** — customer data never crosses organisation boundaries.

## High-level shape — the four layers

1. **Substrate Layer** — Knowledge graphs, ReBAC, identity, credentials, audit. The trust root.
2. **Capability Registry** — The single source of truth for what tools, skills, agents, harnesses, and human roles exist.
3. **Harness Runtime + Execution Engine** — Executes committed harnesses. Drives the model → tool → model loop for agents.
4. **Application Gateway** — The public-facing surface for external API consumers and internal members.
