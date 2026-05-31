<!-- source page id: 983041 | title: Incident Response -->
# Incident Response

How the team responds when something breaks. The process is the same in self-hosted and cloud-hosted modes — only the operator differs. For cloud-hosted, the operator is Oraclous-the-company; for self-hosted, the customer.

## Status

Placeholder — substantive procedures land in Phase 6 alongside compliance work

The incident response process exists from day one — even if rough. Phase 6 formalises it for cloud-hosted operation with the formal compliance posture (ISO 27001, SOC 2 Type II) per ADR-008.

## Definitions

* **Incident** — any unplanned event that degrades the platform's availability, integrity, confidentiality, or performance below its service-level commitments
* **Security incident** — an incident that affects confidentiality, integrity, or access control
* **Near-miss** — an event that _would have been_ an incident if a safeguard had not caught it; still recorded
* **Severity** — see Troubleshooting Playbook (P0–P3)

## What this page will cover

* **Escalation paths** — who is on-call, how to reach them, what to do when the on-call is unresponsive
* **Communication templates** — internal status updates, customer-facing notifications, status page messaging
* **Incident command structure** — incident commander, scribe, communications lead (for P0 / P1 only)
* **Customer notification** — when, how, what to say (cloud-hosted)
* **Post-mortem process** — timeline reconstruction, blameless analysis, action item tracking
* **Security incident handling** — additional steps for incidents with security implications: forensics, evidence preservation, regulator notification thresholds
* **Tabletop exercises** — cadence and scenarios for proactive practice

## Response posture

* **Blameless** — post-mortems focus on systemic causes, not individual fault; the goal is preventing recurrence, not assigning responsibility
* **Loud failure** — when the platform breaks, it should break loudly; silent degradation is worse than a clear outage
* **Customer-first communication** — for cloud-hosted P0/P1, customer notification goes out within agreed timeframes regardless of resolution status
* **Provenance preservation** — during an incident, never delete or alter substrate state until the post-mortem is complete; rotate around it instead

## Severity → response posture

| Severity | Response time | Communication |
| --- | --- | --- |
| P0 | Immediate, full incident command | Customer notification within agreed SLA; status page updated |
| P1 | Within business hours; on-call paged outside hours | Customer notification per SLA |
| P2 | Within one business day | Affected customers notified; no status page entry |
| P3 | Tracked in backlog | No notification unless customer raises it |

## Post-mortem template

Every P0 and P1 incident gets a post-mortem within five business days of resolution. The template covers:

1. **Summary** — what happened, when, who was affected, how long
2. **Timeline** — events in chronological order, with timestamps and trace ids where relevant
3. **Root cause** — the underlying systemic cause (not the proximate trigger)
4. **Contributing factors** — what made this incident possible or worse
5. **What went well** — detection, response, communication
6. **What went poorly** — gaps in detection, response time, knowledge
7. **Action items** — concrete changes (each tracked in Jira), each owned by one person with a due date
8. **Lessons learned** — what this changes about how we operate

## Cross-references

* **Troubleshooting Playbook** — diagnostic procedures invoked during response
* **Monitoring and Observability** — alerts and dashboards that detect incidents
* **Section 6.5** — security threat catalogue (security incidents map to threat families)
* **Deployment — Cloud-hosted** — cloud-mode-specific operational commitments
* **06. Compliance** — formal incident reporting obligations under ISO 27001 / SOC 2

## Self-hosted note

Self-hosted operators implement their own incident response. This page provides the template Oraclous-the-company uses for cloud-hosted; self-hosted operators are welcome to adapt it.
