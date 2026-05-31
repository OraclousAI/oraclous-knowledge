# Releases R2 through R8 and R-Compliance

These releases are planned but not yet briefed. See [09. Releases index](./index.md) for status.

## R2 — Phase 2: Capability registry consolidation (Weeks 7-10)

Evolve `oraclous-core-service` into the Capability Registry. Consolidate tool registries. Generalise from tools to capabilities. Introduce OHM-shaped descriptors.

## R3 — Phase 3: Knowledge graph decomposition (Weeks 11-16)

Split `knowledge-graph-builder` into `knowledge-graph-service` (build) and `knowledge-retriever-service` (read).

## R4 — Phase 4: Harness runtime extraction (Weeks 17-20)

Lift `AgentExecutor` and related code from `knowledge-graph-builder` into a new `harness-runtime-service`.

## R5 — Phase 5: Execution engine and runtime completion (Weeks 21-24)

Extract the durable execution side into a new `execution-engine-service`. Complete the harness runtime with HITL, round-tables, schedules, and task boards.

## R6 — Phase 6: Application Gateway extraction (Weeks 25-28)

Lift the public-facing surface into a new `application-gateway-service`. New MCP server and client.

## R7 — Phase 7: Compiler harness and seed manifests (Weeks 29-32)

Build the default compiler harness. Define seed manifests for new workspaces. Implement the bootstrap update flow.

## R8 — Phase 8: Security hardening pass (Weeks 33-36)

Implement the Phase 2 and Phase 3 mitigations from Section 6.5.

## R-Compliance — Cloud-mode compliance track

ISO 27001 and SOC 2 Type II audit programme. Runs in parallel from R0.5 onward.
