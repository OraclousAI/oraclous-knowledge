# Section 6 — Governance Model

**Related structured artifact:** [Structured Governance Taxonomy](../structured-governance-taxonomy.md)

> **A prose instruction that contradicts a structured policy never overrides the policy.** Governance lives in code; flexibility lives in prose; code wins.

## The two-layer enforcement model

**Coded enforcement** — Implemented in platform code. Deterministic, predictable, audit-anchored. Examples: ReBAC checks, credential scope enforcement, budget caps, HITL gates, output redaction.

**Prose interpretation** — Implemented as Markdown inside OHM manifests, interpreted by LLMs. Examples: role descriptions, orchestration rules, hand-off conditions, escalation criteria.

## Where each layer enforces what

**Substrate enforces:** ReBAC graph integrity, identity verification, credential resolution, manifest commit validation, provenance writes, versioning, storage isolation.

**Runtime + Execution Engine enforces:** Capability allocation, budget caps, HITL gates, output redaction, timeout enforcement, retry policy, round-table lifecycle, consciousness permission gates.

**Application Gateway enforces:** Rate limits, CORS scoping, integration key validation, webhook signature verification, MCP protocol conformance.

## Adversarial scenarios

- **Prose attempts to bypass HITL:** The Runtime enforces the gate regardless.
- **Prose attempts to expand capability allocation:** The Runtime checks the agent's allocation and refuses.
- **Prose attempts to consume more budget:** The Runtime halts when the budget is exhausted.
