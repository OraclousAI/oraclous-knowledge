# ADR-013 — Fail-Closed Authority Placement at the Substrate ReBAC Seam

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 31 May 2026 |
| Proposed by | solution-architect |
| Approved by | tech-lead (Reza Jahankohan) |
| Refines | ADR-012 §1 (substrate enforcement seam); ADR-004 |
| Driving artifact | ORA-46 |

## Decision

The substrate seam — `AccessDecisionClient` — is the **single authority** for fail-closed translation in the ReBAC slice.

### Resolver return-value contract

A resolver implementing `async def resolve(AccessRequest) -> bool | None` returns:
- `True` — the relation is definitively present
- `False` — the relation is definitively absent
- `None` — the resolver cannot answer (inputs map to a domain the resolver does not own)
- Or it raises (backend failure)

The resolver MUST NOT catch its own backend errors and return `False`.

### Seam translation contract

`AccessDecisionClient.check(request) -> AccessDecision` performs all fail-closed translation in exactly one place:
- `True` → `AccessDecision(allowed=True, …)`
- `False` → `AccessDecision(allowed=False, reason="<definitive-deny>")`
- `None` → `AccessDecision(allowed=False, reason="<ambiguous>")`
- Raised → `AccessDecision(allowed=False, reason="<backend-error>")`
