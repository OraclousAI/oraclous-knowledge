# ADR-024 — Graph Versioning & Rollback: Deferred Pending a Write-Path Soft-Invalidation Prerequisite

## Status

| | |
| --- | --- |
| Status | Proposed → **Deferred** |
| Date | 2026-06-12 |
| Deciders | solution-architect (drafted), Reza (signed off the deferral) |
| Driving epic | [#294](https://github.com/OraclousAI/oraclous-backend/issues/294) — Legacy-restorations · issue [#304](https://github.com/OraclousAI/oraclous-backend/issues/304) |
| Relates to | [ADR-022](adr-022-recipe-primitive-unified-graph-ingestion.md) (ingestion / write path) · PR #323 (bitemporal edge fields) · the [#312](https://github.com/OraclousAI/oraclous-backend/issues/312) deferred backlog |

## Context

The legacy supported graph **versioning** — zero-copy snapshots (a `GraphVersion` *pointer* node anchoring a `captured_at` moment), **soft invalidation** (`transaction_time` + `invalidated_at` on every node/edge), and **partial rollback** (revert a subset by `SET`/`REMOVE invalidated_at`, cascading to dangling relationships) — via `versioning_service.py` / `snapshot_service.py` / `rollback_service.py`, behind `/graphs/{id}/versions` + `/graphs/{id}/rollback` endpoints.

It is tempting to assume the R3.5 substrate already supports this, because the **bitemporal fields exist**: the multi-tenant writer stamps `transaction_time` + `invalidated_at` on every node/edge, and #323 added `valid_from`/`valid_to`/`event_time` (edge temporal *facts*) plus `ingestion_jobs` timestamp columns. **It does not.** The audit (#304 grounding) established the blocking fact:

* The ingest write-path **hard-deletes on re-ingest** — `graph_write_repository._delete_document()` runs a `DETACH DELETE` over the matching nodes. `invalidated_at` is **never set** on delete; prior graph **state is destroyed**, not invalidated.
* #323's additions timestamp *facts on live edges* and *the ingest job*, not prior graph **state**. Neither preserves history.

So no snapshot can be reconstructed and no rollback target survives. Versioning/rollback is **not buildable over the current substrate** without first changing the write semantics — and that change is on the ingest spine, where the T1 injected-scope + idempotency invariants live.

## Decision

**Defer #304.** Versioning/rollback requires a write-path prerequisite (below) that touches ingest idempotency + multi-tenant scoping and must be retested carefully. With **no current consumer** (the frontend does not use versioning), taking that ingest risk now is not justified. The decision and its prerequisite are recorded here so the question is not re-litigated and so the gating work is explicit when a consumer arrives. #294 Slice 3 therefore ships **#303 only**.

### The unblock path (when a consumer needs it)

1. **Write-path soft-invalidation (the gating task).** Replace the `DETACH DELETE` in `_delete_document()` with `SET n.invalidated_at = datetime()`; on re-ingest, `MERGE` edges and set `valid_to` on superseded ones rather than overwriting; make every read filter live state — `transaction_time <= $t AND (invalidated_at IS NULL OR invalidated_at > $t)`. **Retest idempotency + cross-org isolation** — this is the real risk, not the snapshot API.
2. **Then the versioning surface, per the legacy design.** Zero-copy `GraphVersion` pointer nodes anchoring `captured_at`; rollback via `SET`/`REMOVE invalidated_at` with a relationship cascade; the `/graphs/{id}/versions` + `/graphs/{id}/rollback` endpoints (sync small / async-with-job large).

## Alternatives considered

* **A. Build full versioning now.** Rejected — high-effort write-path surgery + real ingest risk for a feature nothing consumes yet.
* **B. Snapshot-metadata only, without the write-path change.** Rejected — a `GraphVersion` pointer is useless when the underlying history is hard-deleted; it would record a checkpoint you cannot restore to (false capability).
* **C. Soft-delete foundation only (the write-path change, defer the API).** Considered — it has standalone value (history preservation, time-travel queries) and is the principled first step. Deferred *with* the rest because it still carries the ingest-spine risk and no consumer needs even time-travel today; it is folded into step 1 of the unblock path for when one does.

## Consequences

* #294 Slice 3 ships **#303 (community detection)** only; **#304 stays in the deferred backlog** alongside #312 (federation / RAGAS / agent-memory).
* When versioning is needed, **this ADR is the entry point** and the **write-path soft-invalidation change is the gating task** — not the snapshot/rollback API, which is straightforward once history is preserved.
* No code changes result from this ADR.

## See also

* [ADR-022](adr-022-recipe-primitive-unified-graph-ingestion.md) — ingestion / the write path this depends on
* PR #323 — bitemporal `valid_from`/`valid_to`/`event_time` edge fields (facts on live edges, not state history)
* Legacy source: `legacy-reference/old-backend/knowledge-graph-builder/app/services/{versioning_service.py, snapshot_service.py, rollback_service.py}`
* Issues [#304](https://github.com/OraclousAI/oraclous-backend/issues/304) · [#294](https://github.com/OraclousAI/oraclous-backend/issues/294) · [#312](https://github.com/OraclousAI/oraclous-backend/issues/312)
