# execution-engine-service

**Layer:** 3 (Harness Runtime + Execution Engine) · **Port:** 8005 · **Status:** NEW in Phase 5

## Purpose

`execution-engine-service` handles work that lives outside a single request: long-running jobs with checkpoints, scheduled wake-ups, task board state, and durable execution context.

## Responsibilities

- Durable execution context (checkpointed harness state)
- Schedule registration and firing (per OHM `triggers` block)
- Job tracking (sync, async, progress streaming)
- Task board state management
- Pause / resume / cancel for durable executions
- Timeout enforcement
- Retry policy enforcement (declared count, no more)
