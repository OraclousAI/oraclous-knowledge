# harness-runtime-service

**Layer:** 3 (Harness Runtime + Execution Engine) · **Port:** 8004 · **Status:** NEW in Phase 4 (lifted from `knowledge-graph-builder`)

## Purpose

`harness-runtime-service` is the platform's central nervous system. It executes harnesses. The compiler, consciousness agents, and customer harnesses all run on this same runtime — there is no privileged code path.

## Responsibilities

- Harness execution (loads OHM, runs to completion or escalation)
- Actor dispatch (agents → tool-use loop; humans → task board assignments)
- Multi-mode tool-use loop (`AgentExecutor` lifted from `knowledge-graph-builder`)
- Capability and credential resolution at every invocation
- Policy envelope enforcement (budget caps, HITL gates, output redaction)
- Round-table primitive (Phase 5)
- HITL primitive (Phase 5)
- Provenance write-through
- LLM client factory supporting three v1 protocol shapes (ADR-007)
- LLM config resolution (agent → workspace → organisation)
