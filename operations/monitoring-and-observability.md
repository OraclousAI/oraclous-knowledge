# Monitoring and Observability

**Status:** Placeholder — content lands as each service ships and observability conventions stabilise

## The three signals

- **Structured logs** — JSON, line-delimited, stable field names
- **Distributed traces** — OpenTelemetry-format spans; trace ids propagate across service boundaries
- **Metrics** — Prometheus-format; per-service `/metrics` endpoint

## Critical paths to instrument

1. **Compile** — gateway → runtime → registry → substrate — operator-perceived latency
2. **Execute** — trigger → runtime → execution-engine — durable job throughput and stall rate
3. **Schedule** — execution-engine wake-up rate, drift from scheduled fire time
4. **Traversal** — cross-workspace access decisions per second, denial rate
5. **Retrieval** — knowledge-retriever-service p99, cache hit rate
6. **HITL** — task-creation rate, time-to-resolution, escalation rate
