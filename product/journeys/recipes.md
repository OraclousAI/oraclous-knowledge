---
title: "Journey — Recipes: from an inert JSON viewer to an author-run ingestion surface"
owner: experience-architect
status: signed
signed-by: experience-architect
surface: Recipes (apps/console/src/pages/RecipesPage.tsx)
grounds-in: capability-surface-inventory.md §2 (knowledge-graph recipes + ingest)
legacy-divergence: the legacy app had no recipe authoring; the real backend (ADR-022) models template → dry-run → save-draft → run-on-graph. We expose that lifecycle; a naive "add a recipe" CRUD form is the WRONG model.
backend-gaps: none (every capability is gateway-exposed today)
---

# Journey — Recipes

**Persona.** The knowledge / data steward who turns raw sources into the graph via concern-driven recipes
(ADR-022) — they want to author, preview before any write, and run on a workspace, not edit raw JSON.

**Today (the problem).** `RecipesPage` is a browse-only library; selecting a recipe dumps raw
`JSON.stringify` into a `<pre>`. The api-client exposes only `list()`/`get()` and types the document as an
opaque `Record`. The backend serves the entire ADR-022 lifecycle through the gateway — templates, dry-run,
save, and `recipe_id` on `/graphs/{id}/ingest` — and the FE exposes none of it (inventory §2). No backend
dependency.

## Design constraints
Mint = a live job-running pulse or promoted dot only; "Save draft", "Dry run", "Run on workspace" are
standard buttons. Detail opens in a focus-trapped drawer with a real "View raw document" toggle (not a div).
A run reuses the existing GraphDetailPage ingestion-job poll (`GET /graphs/{id}/jobs/{id}`). Sentence case,
no emoji, AA floor; compose from existing drawer/card/field/select/tabs/callout + catalog.css tiles.

## Increments (small, vertical, each testable on the app)

| # | Increment | Gateway capability | Test on the app |
| --- | --- | --- | --- |
| 1 | **Structured recipe detail** (not raw JSON) in a drawer; keep a "View raw" toggle | `GET /api/v1/recipes/{id}` (existing) | click a tile → drawer with concern/status, what it produces (entities/relationships), expected source; raw toggle works |
| 2 | **Start from a template** (built-in author-ready templates) | `GET /api/v1/recipes/templates` (new client method) | "Author a recipe" → template picker → pick → seeded "draft (unsaved)" rendered structured |
| 3 | **Dry-run preview** (no writes) | `POST /api/v1/recipes/dry-run` (new) | sample + source-type → "Run a dry run" → projected node labels + counts + relationships + ontology-violation callout; Explorer counts unchanged |
| 4 | **Save a draft** | `POST /api/v1/recipes` (new) | "Save draft" → toast → new tile with "draft" chip appears; reopen shows structured detail |
| 5 | **Run a recipe on a workspace** | `recipe_id` on `POST /api/v1/graphs/{id}/ingest|upload` + jobs poll | pick a workspace + source → job streams pending→running(mint)→completed; Explorer shows projected nodes |

## Increment 1 — build brief (the first issue)

**Goal.** Replace the raw-JSON detail with a structured, focus-trapped detail drawer that explains what a
recipe does and produces — keeping a raw-document escape hatch.

**Scope (in).** A drawer opened from a tile click rendering format-0.2 sections: header (concern + status,
sourceType, version), "What this recipe does", "What it produces" (entity/domain labels + relationship
types), and the expected source shape. Type the recipe document in `packages/api-client/src/recipes.ts`
beyond the opaque `Record` (typed `RecipeDocument` from the real format-0.2 fields, with unknown-passthrough
for forward-compat). A real `<button>` "View raw document" disclosure reveals the existing JSON. Graceful
empty states; close via button + Esc returning focus to the tile.

**Scope (out).** No authoring/templates/dry-run/save/run (increments 2–5); no edit; no new tokens; list tiles
stay as-is.

**How to test on the app.** `pnpm -r build && VITE_API_BASE_URL=<gateway> pnpm --filter @oraclous/console dev`,
open `/app/recipes`, click a tile → drawer with readable prose (not a JSON blob); toggle "View raw" on/off;
keyboard Tab→tile, Enter opens, focus into drawer, Esc returns focus; axe-core AA clean. No regression: list +
loading/empty/error states still render.
