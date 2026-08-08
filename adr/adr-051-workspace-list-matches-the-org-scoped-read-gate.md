# ADR-051 — Workspace Listing Matches the Org-Scoped Read Gate; the Access Ladder Is Not Yet Implemented

## Status

| | |
| --- | --- |
| Status | Proposed |
| Date | 2026-08-08 |
| Deciders | solution-architect (drafted) — CTO accepts |
| Driving evidence | UC-D1 proof of concept, [oraclous-backend#734](https://github.com/OraclousAI/oraclous-backend/issues/734), §5.3 capability 27 |
| Builds on | [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (org-scoped trust) · [ADR-026](adr-026-federated-cross-graph-query.md) §1 (federation composes the single-graph gate) |

## Context

The UC-D1 proof of concept found that workspace **management** is owner-scoped while workspace **content** is org-scoped. The same user, on the same graph id, gets three different answers:

* `GET /api/v1/graphs` → `[]` for an invited member (`list_for_user`, filtered on `KnowledgeGraph.user_id`).
* `GET /api/v1/graphs/{id}/documents` → `404` for that member (`_owned_or_404`).
* `POST /v1/search/hybrid` on that same id → `200` with the full content (org-scoped only).

So an employee cannot find the company knowledge base through the product, but can read all of it once someone hands them the UUID.

**The read path is broader than the management path. It is also the deliberate one.** ADR-018 sets an org-scoped trust floor, and ADR-026 §1 pins federation to "exactly the graphs the caller can already read individually under the current org-scoped floor". `list_for_org` already exists in the graph repository and its docstring states the intent explicitly. The owner-gated list is the outlier, and its narrowness is security by obscurity: it hides a workspace it does not protect.

UC-D1 and UC-E1 both describe a root workspace that **every employee** queries, at access level L2 (organisation). Narrowing the read gate to the owner would break that premise and would break ADR-026 federation, which composes this exact gate.

## Decision

1. **Org-scoped read is correct for workspace content, and stands.** It is the ADR-018 floor, and it is what UC-D1/UC-E1 require of a root workspace. This ADR does not widen it.

2. **The listing gate must equal the read gate.** `GET /api/v1/graphs` returns the caller organisation's graphs (the existing `list_for_org` set), each row carrying an ownership marker so the console can separate "mine" from "the organisation's". `GET /api/v1/graphs/{id}/documents` becomes org-scoped for **read**, matching search. This grants no data access that an org member does not already have; it removes a discovery gap, not a control.

3. **Mutation stays owner/admin-scoped and is not widened.** Rename, delete, ingest, and configure keep their current gate. Read and manage are separate gates; today they are accidentally fused into one owner check, and separating them is the substance of this ADR.

4. **Recorded plainly: the access ladder is not implemented for workspace content.** There is no per-workspace member set — `KnowledgeGraph` carries an owner `user_id` and nothing else — so **every graph in an organisation is readable by every member of that organisation**. L0 (private) and L1 (workspace-scoped) do not exist for graph content; everything is effectively L2. Decision 2 does not create this condition. It makes it visible, which is the point: a team that believed a private workspace existed was already wrong.

5. **Consequently, per-workspace membership is a prerequisite, not a refinement.** Any workspace holding restricted material — §5.3 capability 39, UC-D6 audit findings that "must not be reachable from marketing" — cannot be built on today's model. Per-user permission mirroring from source systems (capability 27) is a second, separate layer on top of it. Both are out of the UC-D1 first slice and are tracked as their own decision.

## Alternatives considered

* **Narrow the read gate to the owner instead.** Rejected. It contradicts ADR-018 and ADR-026 §1, it breaks federation, and it makes UC-D1's "every employee queries the root workspace" impossible. The inconsistency is real, but the list is the wrong half.
* **Leave the list owner-scoped and document the gap.** Rejected. It is security by obscurity: the data is already readable to any org member holding the UUID, so the narrow list protects nothing while hiding the workspace from the people meant to use it. It also blocks the UC-D1 demo outright.
* **Build per-workspace membership now, before the first slice.** Rejected for sequencing, not for merit. It is a new authorization model touching every graph read path, and the citation Contract is what actually blocks the slice. It is opened as its own decision rather than folded in.

## Consequences

* The console shows every organisation workspace, with ownership visible; the invited-member path stops requiring an out-of-band UUID.
* Document listing and search agree, so a member never sees `404` on a graph they can search.
* Federation (ADR-026) is unchanged — it already aggregates exactly this set.
* Until per-workspace membership lands, **no workspace is private**. Any use case needing isolated content is blocked on that decision, and this must be stated to any customer before a restricted workspace is promised.

## See also

* ADR-018 (org-scoped trust) · ADR-026 §1 (no-new-access aggregator)
* `oraclous-backend#734` (UC-D1 PoC) · §5.3 capabilities 27 and 39
* [Interface Contracts §CITE](../flows/interface-contracts.md) — the citation's `permission_ref` is the seam capability 27 fills
