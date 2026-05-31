# Incident Response

**Status:** Placeholder — substantive procedures land in Phase 6 alongside compliance work

## Definitions

- **Incident** — any unplanned event that degrades the platform's availability, integrity, confidentiality, or performance
- **Security incident** — an incident that affects confidentiality, integrity, or access control
- **Severity** — P0 (platform unavailable) through P3 (cosmetic)

## Response posture

- **Blameless** — post-mortems focus on systemic causes, not individual fault
- **Loud failure** — the platform should break loudly; silent degradation is worse than a clear outage
- **Provenance preservation** — never delete or alter substrate state until the post-mortem is complete

## Severity → response posture

| Severity | Response time | Communication |
| --- | --- | --- |
| P0 | Immediate, full incident command | Customer notification within agreed SLA; status page updated |
| P1 | Within business hours; on-call paged outside hours | Customer notification per SLA |
| P2 | Within one business day | Affected customers notified |
| P3 | Tracked in backlog | No notification unless customer raises it |
