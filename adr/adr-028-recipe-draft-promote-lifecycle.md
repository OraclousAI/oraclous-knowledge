# ADR-028 — Recipe Draft → Promote Lifecycle (a stored recipe is a draft until promoted)

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-14 |
| Deciders | experience-architect (drafted, building the backend), Reza (directed: "build a real draft lifecycle" rather than accept promote-on-save) |
| Driving epic | Recipes (oraclous-frontend [#109](https://github.com/OraclousAI/oraclous-frontend/issues/109)) · increment 4 [#113](https://github.com/OraclousAI/oraclous-frontend/issues/113) · backend impl in `oraclous-backend` |
| Builds on | [ADR-022](adr-022-recipe-primitive-unified-graph-ingestion.md) (the recipe primitive + versioned recipe library) |

## Context

The Recipes UI authors a recipe from a template, dry-runs it, and **saves** it. The store endpoint
(`POST /api/v1/recipes`) previously **promoted on save**: `recipe_repository.store` hardcoded
`status="promoted"` and bumped the version — there was **no draft state**. So a recipe went live the
instant it was saved, with no authoring/review stage, and the "save a **draft**" journey could not be
honoured (the FE correctly refused to fake a "draft" chip and surfaced the mismatch).

Two facts shaped the decision:

1. The `recipes` row already has a `status` column (default `"draft"`) and an index keyed on
   `(organisation_id, source_type, shape_signature, status)` — the original schema *intended* a
   status-aware lifecycle that the code never used.
2. **Nothing filtered recipes by status.** Ingestion (`tasks/ingest_tasks.py`,
   `routes/ingest_routes.py`) loads a recipe by id with `get_latest` and runs it — so the moment
   drafts exist, an unreviewed draft could be used in a real graph run unless ingestion is guarded.

## Decision

A stored recipe is a **draft** until explicitly **promoted**. Only a promoted recipe is runnable.

1. **`store` saves a draft.** `recipe_repository.store` sets `status="draft"` (column + the embedded
   `recipe_json["status"]`) and returns `{id, version, status: "draft"}`. Versioning is unchanged
   (each store is a new `(id, version)` row).
2. **`promote` is a separate, in-place transition.** `POST /api/v1/recipes/{id}/promote` flips the
   latest version `draft → promoted` **in place — no new version** — so the promoted recipe keeps its
   `id+version` (the immutable identity a graph run pins to). It updates both the `status` column and
   `recipe_json["status"]`. **Idempotent** (re-promoting is a no-op success); 404 on an unknown id.
3. **Drafts are not runnable — ingestion is guarded.** Both ingest paths (the sync `ingest-sql` route
   and the async structured-ingest task) reject a non-promoted recipe: a stored recipe whose
   `status != "promoted"` returns **409 Conflict** ("promote it before ingesting") / fails the task.
   This makes the run-time invariant explicit: **a graph run always pins to a reviewed, promoted,
   immutable recipe version.**

**Promote is an explicit step, not part of FE CRUD for now** — the Recipes "save draft" increment
stops at draft; who promotes (a human action or an agent step) is a later increment. Built-in
templates are in-memory and returned by `GET /recipes/templates` as-is; authoring from a template and
saving goes through `store`, so it lands as a draft like any other.

## Consequences

- **Non-breaking for existing data.** Every recipe stored before this change is already `"promoted"`,
  so existing runs are unaffected; only newly-saved drafts must be promoted before they can run.
- The FE "Save draft" → draft tile is now honest (the tile renders the real `draft` status).
- A draft can be authored + dry-run-previewed freely (dry-run does no writes and isn't gated), then
  promoted when ready.
- **Version semantics:** promote does not bump the version (status is orthogonal to versioning); a new
  authoring pass that re-stores creates a new draft version, which is promoted on its own.
- A future "unpromote"/retire or a draft→review→promote approval gate can extend this lifecycle
  without re-architecting it (the status column already carries the state).
