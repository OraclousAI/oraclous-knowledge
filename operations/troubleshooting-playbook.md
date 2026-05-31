<!-- source page id: 557099 | title: Troubleshooting Playbook -->
# Troubleshooting Playbook

The operator's reference for diagnosing common problems. Each entry follows a symptom → diagnostic-steps → resolution structure so an on-call operator can move from "something is wrong" to "fixed" without spelunking through code.

## Status

Placeholder — entries land as patterns are observed in operation

This playbook grows from operational experience, not from upfront speculation. Each entry is added when a real problem has been diagnosed at least once, so the playbook reflects what actually breaks rather than what might theoretically break.

## Entry format

Each entry will follow the same shape:

* **Symptom** — what the operator observes (error message, metric anomaly, behavioural pattern)
* **Likely causes** — ranked by frequency
* **Diagnostic steps** — what to check, in order, to confirm the cause
* **Resolution** — how to fix it
* **Prevention** — what change (config, code, monitoring) would have caught this earlier
* **Related** — links to runbooks, ADRs, observability dashboards

## Categories (to be populated)

* **Startup and bootstrap problems** — service won't start, missing default seeds, infrastructure connection failures
* **Authentication and authorisation** — login failures, ReBAC permission denials, delegated-identity misconfigurations
* **Capability resolution failures** — manifest references a missing capability, version mismatch, registry unavailable
* **Manifest compilation errors** — OHM validation failures, content-hash conflicts, unsupported manifest versions
* **Execution failures** — harness execution stalls, runaway budgets, infinite-loop guards, durable job stuck
* **Knowledge graph issues** — ingestion stalls, retrieval timeouts, schema-evolution problems, embedding-model issues
* **BYOM and provider problems** — Anthropic/OpenAI/Bedrock failures, credential issues, rate limits, model deprecation
* **Performance degradation** — slow queries, high latency at the gateway, runtime saturation, retrieval-service backpressure
* **Cross-workspace traversal denials** — ReBAC graph inconsistencies, delegated-scope confusion
* **HITL stuck waiting** — notifications not delivered, assignee not resolving, escalation chains broken
* **Migration-phase-specific problems** — issues unique to in-flight migration phases per Section 8 of Architecture v1.1

## Severity guidance

* **P0** — platform unavailable for one or more organisations; security incident
* **P1** — major feature unavailable; degraded availability; one execution flow broken
* **P2** — minor feature unavailable; workarounds exist
* **P3** — cosmetic issue; documentation gap

Severity determines incident-response posture (see Incident Response page).

## When to escalate vs. when to fix in place

* **Fix in place** — well-understood problems with a known resolution path; severity P2 or P3; resolution time under 30 minutes
* **Escalate** — unknown root cause; possible data integrity issue; possible security implication; P0 or P1; resolution requires a code or config change in production

## Related references

* **Incident Response** — what to do when troubleshooting reveals an incident
* **Monitoring and Observability** — the dashboards and signals the playbook references
* **Configuration Reference** — for config-related resolutions
