# ADR-051 — Workspace Listing Matches the Org-Scoped Read Gate; the Access Ladder Is Not Yet Implemented

## Status

| | |
| --- | --- |
| Status | Accepted — **Realized 2026-08-10** (issue [#736](https://github.com/OraclousAI/oraclous-backend/issues/736) closed) |
| Date | 2026-08-08 (accepted 2026-08-13) |
| Deciders | solution-architect (drafted), Reza (accepted 2026-08-13) |
| Driving evidence | UC-D1 proof of concept, [oraclous-backend#734](https://github.com/OraclousAI/oraclous-backend/issues/734), §5.3 capability 27 |
| Builds on | [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (org-scoped trust) · [ADR-026](adr-026-federated-cross-graph-query.md) §1 (federation composes the single-graph gate) |

> **✅ Realized 2026-08-10 ([`oraclous-backend#736`](https://github.com/OraclousAI/oraclous-backend/issues/736) closed).** Decisions 2 and 3 shipped in PR [#765](https://github.com/OraclousAI/oraclous-backend/pull/765) (`393ae5ae`), against the tests merged in #764. `GraphService._owned_or_404` had twelve call sites mixing reads with writes, so relaxing it in place would have widened ingest and the ontology write — a decision-3 violation. There are now **two gates, each named for its job**: `_owned_or_404` is **unchanged** and still owner-scoped (create, rename, delete, ingest submit, SQL ingest, ontology write, community detect, summarise, resolution decisions, cross-org grant); the new `_readable_or_404` is organisation-scoped (graph list, graph detail, documents, artifacts list, artifact content, ingest-job status, ontology read, analytics reads). The widening is **additive** — new methods taken up only by read call sites, no write call site touched — so a write path can only lose its owner gate by someone deliberately rewriting that line. **Boundary ruled on #736 before implementation:** the read gate covers *every* pure read in the service, graph detail included, not only the two endpoints this ADR names. A half-applied version is worse than the old behaviour, because the console would render a workspace row the member cannot open; and it grants nothing new, since `GET /v1/artifacts/{id}` serves the same content the member can already retrieve through the org-scoped `POST /v1/search/*` with only the UUID. **Decision 1 is unchanged and still not implemented:** no per-workspace member set exists, so every graph in an organisation remains readable by every member.

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

2. **The listing gate must equal the read gate.** `GET /api/v1/graphs` returns the caller organisation's graphs (the existing `list_for_org` set), each row carrying an ownership marker so the console can separate "mine" from "the organisation's". `GET /api/v1/graphs/{id}/documents` becomes org-scoped for **read**, matching search. This grants no access to workspace **content** that an org member does not already have; it removes a discovery gap, not a control.

   **The content claim is exact; it does not extend to all metadata.** Verified against source on [`oraclous-backend#765`](https://github.com/OraclousAI/oraclous-backend/pull/765): `POST /v1/search/{semantic,fulltext,hybrid}` consults no graph table and no owner gate at all — its only scope is the caller's organisation — and `GET /v1/graph/{graph_id}/subgraph` returns full node property bags on the same org-only scope. So verbatim chunk text and filenames were already reachable by any org member holding the UUID, more completely than this ADR originally claimed. **Three classes of metadata are not returnable by any search path, and the widened read gate does disclose them:** the `error_message` on a FAILED ingest (a bare `str(exc)`, so it can carry a content excerpt, a path or a host, and a failed ingest writes no chunks at all); the [`#728`](https://github.com/OraclousAI/oraclous-backend/issues/728) artifact provenance columns (`producer_kind`, `team_run_id`, `member_role`, `execution_id`, `team_id`, `ordinal`, `content_hash`), which live only in Postgres and are never stamped into Neo4j; and the **original source bytes**, since `get_artifact` serves the decoded source while search serves extracted chunk text — identical for a text ingest, different for a PDF or any binary upload.

   **Accepted as non-material, and recorded rather than left implied.** The disclosure is intra-organisation, and decision 4 already records that every member reads every graph's content in full — "which teammate produced this artifact" is a smaller disclosure than the document body those members can already open. The correction still had to be made, because the original sentence is the one someone will quote to a customer, and an unqualified "grants no data access" is a claim this ADR cannot support.

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
* When describing this change to a customer, say it grants no access to workspace **content**, and stop there. The three metadata classes named in decision 2 are new disclosure to an org member, accepted as non-material, and the unqualified form of the sentence overstates what this ADR can support.

## See also

* ADR-018 (org-scoped trust) · ADR-026 §1 (no-new-access aggregator)
* `oraclous-backend#734` (UC-D1 PoC) · §5.3 capabilities 27 and 39
* Implementation of decisions 2 and 3: [`oraclous-backend#736`](https://github.com/OraclousAI/oraclous-backend/issues/736)
* The status bump and the decision-2 qualification: [`oraclous-backend#769`](https://github.com/OraclousAI/oraclous-backend/issues/769), off the `security-architect` review on PR #765
* The prerequisite decision named in decision 5: [`oraclous-backend#737`](https://github.com/OraclousAI/oraclous-backend/issues/737)
* [Interface Contracts §CITE](../flows/interface-contracts.md) — the citation's `permission_ref` is the seam capability 27 fills
