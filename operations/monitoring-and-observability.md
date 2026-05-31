<!-- source page id: 852031 | title: Monitoring and Observability -->
# Monitoring and Observability

What the platform emits, what to monitor, and how to interpret what you see. The observability contract is platform-wide: every service follows the same conventions so dashboards and alerts compose across services.

## Status

Placeholder — content lands as each service ships and observability conventions stabilise

## The three signals

The platform emits the standard three signals for every service:

* **Structured logs** — JSON, line-delimited, with stable field names; one event per line; never multi-line payloads inside a single log record
* **Distributed traces** — OpenTelemetry-format spans; trace ids propagate across service boundaries; every external request gets a trace
* **Metrics** — Prometheus-format; per-service `/metrics` endpoint; standard labels (`service`, `version`, `organization_id`, `workspace_id`) on every series

In addition, the platform's substrate is its own observability surface for domain-level questions:

* **Provenance** — the canonical audit trail of _what the platform did and why_, queryable via the knowledge graph
* **Task boards** — the canonical record of _what work was queued, who acted on it, when_

## Observability philosophy

* **Provenance is primary** — for _what happened in a harness execution_, query provenance, not logs. Logs are for infrastructure; provenance is for domain behaviour.
* **High-cardinality labels are bounded** — labels per metric series are kept under control to avoid metric explosion; `organization_id` and `workspace_id` are allowed; arbitrary actor ids and capability ids are not used as labels.
* **Errors include trace ids** — every error log line carries the trace id of the request that produced it, so log → trace navigation is one click
* **Public dashboards are versioned** — the dashboards the on-call operator uses are stored as code (JSONnet / Grafana-as-code) and reviewed via PR

## What this page will cover

* **Logging conventions** — structured-log field standard, severity levels, sensitive-data redaction, retention policy
* **Tracing conventions** — span naming, attribute standards, sampling strategy, trace context propagation
* **Metrics catalogue** — service-by-service list of emitted metrics, their meaning, recommended alerting thresholds
* **Service-level objectives** — SLOs per critical path (compile, execute, retrieve), error budgets, burn-rate alerting
* **Dashboards** — the standard dashboards every operator should have on the wall: gateway latency, runtime saturation, execution backlog, retrieval p99, ingestion lag, KMS access rate
* **Alerts** — the standard alerts every deployment should configure: SLO burn, infrastructure unavailability, security signals
* **Provenance queries** — common questions answered via the substrate ("show me every execution of harness X in the last week", "show me all cross-workspace accesses from agent Y")
* **PII and redaction** — what is and is not allowed to appear in logs; how the credential broker keeps secrets out of telemetry
* **Self-hosted vs. cloud-hosted differences** — telemetry shipping in cloud mode (centralised observability stack); self-hosted operators bring their own stack

## Standard label set

Every metric and log line carries a baseline label set:

* `service` — service name (e.g. `harness-runtime-service`)
* `version` — platform version
* `environment` — `dev` | `staging` | `production`
* `organization_id` — for multi-org cloud deployments (omitted in single-org self-hosted)
* `workspace_id` — when the signal is scoped to a workspace
* `trace_id` — when the signal is part of a traced request

## Critical paths to instrument

Per Section 5 of Architecture v1.1, the platform's critical paths are:

1. **Compile** — gateway → runtime → registry → substrate — operator-perceived latency
2. **Execute** — trigger → runtime → execution-engine — durable job throughput and stall rate
3. **Schedule** — execution-engine wake-up rate, drift from scheduled fire time
4. **Traversal** — cross-workspace access decisions per second, denial rate
5. **Retrieval** — knowledge-retriever-service p99, cache hit rate
6. **HITL** — task-creation rate, time-to-resolution, escalation rate

Each gets a dedicated dashboard once Phase 6 lands.

## Related references

* **Section 5** — the flows that drive what we need to observe
* **Configuration Reference** — observability-specific config flags (logging, tracing, metrics)
* **Incident Response** — the alerts and dashboards drive the incident response process
