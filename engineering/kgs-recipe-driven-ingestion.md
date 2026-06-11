# KGS recipe-driven (instruction-driven) ingestion

_Capability brief. Tracking: [#257](https://github.com/OraclousAI/oraclous-backend/issues/257) (epic) → #258 Slice A (EURail structured) · #259 Slice B (free-text hard schema) · #260 Slice C (agent + authoring)._

## Why this exists

The knowledge-graph-service ingests two ways today, both lossy for curated knowledge:

- **Free text** → the LLM extractor runs with an **open schema** (`entity_extractor.py:71` → `GraphSchema(node_types=())`), so it *discovers* entities/relationships ad-hoc and **drops all curated structure** — typed entities, provenance, confidence, and especially **conflicts**. (Probed live on the EURail corpus: 600 evidence claims + 24 conflicts collapse to generic `Company`/`Regulation` nodes — **no `Evidence`/`Source`/`Conflict` node, no `CONTRADICTS` edge**.)
- **Structured (CSV/JSON)** → an `ingest_schemas.py:20` `recipe_id` projects rows, but recipes are **structured-only**, and the "ontology" is **labels-only** (`ontology_schemas.py:11` `allowed_labels: list[str]` + a mode) applied as a *post-extraction filter* (`domain/ontology.py:41`).

The legacy `knowledge-graph-builder` (branch `develop`) had a real **instruction-driven extraction** system that **was not carried over** (a hollow port — recipes exist for structured data only, the ontology concept is unused for extraction, and `EntityExtractor` accepts a `schema` it is never given). This issue **restores that capability and makes it materially better**, because the legacy itself is prompt-only + free-text-only and would not fully solve our actual use cases (the EURail evidence/conflicts graph, and an "onboarder" agent that reasons over confidence + conflicts).

This is filed as a **hollowness-remediation** of the KGS recipe/ontology surface (per the §22 not-a-stub DoD): the recipe + ontology types exist as scaffolding but never drive extraction.

---

## The legacy mechanism (the blueprint — for reference, not the target)

Path: `legacy-reference/old-backend/knowledge-graph-builder/app`.

1. **`GraphInstructions`** — per-graph, versioned, stored on the Neo4j Graph node (`schemas/graph_schemas.py:378-421`): `EntityTypeDefinition`(name, description, examples, properties) + `RelationshipTypeDefinition`(name, source_type, target_type, properties) + extraction density + focus areas + ignore patterns + a custom suffix.
2. **`IngestionOverrides`** — per-job, merged onto the graph instructions at ingest time (`graph_schemas.py:424-443`): one-time focus, density override, extra entity types, schema-evolution hint, temporal context (`valid_from`/`valid_to`/`source_date`), ingest mode (full/incremental/upsert).
3. **`effective_instructions`** — the *resolved* (graph + overrides) instructions captured as JSON on the `IngestionJob` at job start, as provenance (`alembic/.../add_effective_instructions_to_jobs.py`; `services/background_jobs.py:504-542`).
4. **Compilation → extraction** (`services/instructions_service.py:174-260`, `services/pipeline_service.py:738-775`): the resolved instructions are compiled to **(a)** a prompt prefix (`to_prompt`: domain context, entity types with descriptions/examples, relationship types, density, focus, ignore) and **(b)** a **plain-text** schema block (`build_schema_block` → literally `"Node types: A, B, C\nRelationship types: …"`). Both are baked into the extraction `prompt_template` and passed to `LLMEntityRelationExtractor`. **The extractor itself runs open-schema — the "schema" is only text in the prompt.**
5. **Post-extraction ontology enforcement** (`pipeline_service.py:1176-1260`): `WARN` (count only) / `STRICT` (drop off-ontology nodes + their non-structural edges) / `COERCE` (fuzzy-remap close labels at threshold 0.7, drop the rest).
6. **Temporal-contradiction detection** (`pipeline_service.py:1306-1398`): a narrow inline check for overlapping `valid_time` on existing relationships before write.

---

## Where the legacy falls short — and how we beat it

| # | Legacy shortcoming | What we do instead |
|---|---|---|
| 1 | **Soft schema** — the ontology is *plain text in the prompt*; the LLM may ignore it; conformance is only repaired *after* the fact by dropping data. | **Hard + soft + enforce (three layers).** Feed a real `neo4j_graphrag` `GraphSchema` (node_types + relationship_types + **patterns**) into `extract_for_chunk` — the extractor already accepts it (`entity_extractor.py:61,90`) and the library raises `SchemaValidationError` on violations. Keep the prompt prefix (domain/density/focus/examples) as soft steering, and keep post-enforcement (WARN/STRICT/COERCE) as a final backstop. |
| 2 | **Free-text only** — semi-structured data (JSONL/CSV) is forced through lossy LLM extraction. The legacy could *not* have preserved the EURail evidence/conflicts either. | **Multi-modal under one recipe.** (a) free-text → LLM + hard schema; (b) **deterministic structured/semi-structured mapping** (CSV/JSON/JSONL field → typed node/edge + properties, **no LLM, zero loss**); (c) hybrid (map structured fields deterministically, LLM-extract free-text fields under the same schema). EURail's JSONL goes through (b) → exact `Evidence`/`Source`/`Conflict` nodes. **This beats the legacy.** |
| 3 | **Pipeline parameter** — not reusable, not shareable, not agent-addressable. | **First-class, versioned, org-scoped Recipe** (extends the existing recipe store + the FE "Recipes" page) **plus an agent capability** — a registry tool so an agent (the onboarder/ingestion agent) can pick a recipe + pass per-job overrides and drive ingestion. The legacy had no agent path. |
| 4 | **Provenance is instructions-only** — no per-node lineage. | **Provenance-first.** Every extracted/mapped node + edge carries source lineage (source doc/chunk id, record id, source URL, confidence, dimensions, evidence-id when the recipe maps them); the job stores the **effective recipe** (version + resolved `GraphSchema`) + an **extraction/enforcement report** (counts, violations, coercions). |
| 5 | **Conflicts/evidence not first-class** (only a narrow temporal check). | **First-class evidence + conflict modeling.** The recipe schema declares provenance-bearing node types (`Evidence{confidence,dimensions}`, `Source{url,date}`) and **meta-relationships** (`CONTRADICTS`, `SUPPORTS`, `RESOLVED_BY`). Critically, the mapping mode supports **edge records** (a `conflicts.jsonl` row links two `evidence_ids` → an edge), not just node records. Ship a reusable **"evidence-and-conflicts" recipe template**. |
| 6 | Schema authored entirely by hand. | **Three authoring paths**: hand-authored, **LLM-assisted synthesis from a sample** (`neo4j_graphrag` ships `SchemaFromTextExtractor`), and a **recipe-template library** — so onboarding a new domain is fast. |
| 7 | Merge keyed on chunk id only (re-ingest duplicates curated records). | **Recipe-defined node identity keys** (e.g. `Evidence` keyed by `evidence-id`) → deterministic `MERGE`, so re-ingesting corrected evidence **updates** rather than duplicates. |
| 8 | No preview. | **Recipe dry-run** — validate a recipe against a sample and preview the nodes/edges + violations **before** a full ingest. |

---

## Target design

A unified, versioned, org-scoped **Ingestion Recipe** = the carrier of the ontology **and** the extraction/mapping config. One recipe drives all modes.

**Recipe shape (extends today's thin recipe/ontology):**
- `schema`: `entity_types[]` (name, description, examples, properties, **identity_key**) + `relationship_types[]` (name, source_type, target_type, properties) — replaces the labels-only `allowed_labels`.
- `extraction`: `density`, `focus[]`, `ignore[]`, domain, custom suffix (free-text mode steering).
- `mapping`: for structured/semi-structured — per-record-type field→node/edge maps, incl. **edge records** keyed by foreign ids (conflicts linking evidence).
- `enforcement_mode`: open / warn / strict / coerce.
- `provenance`: which fields become source/confidence/dimension/evidence-id properties.

**Resolution + compilation (domain layer, ORAA-4 §21):**
- `RecipeResolver`: graph-default recipe ⊕ per-job overrides → `ResolvedRecipe` (mirrors the legacy resolver, but org-scoped + Postgres-backed).
- `RecipeCompiler`: `ResolvedRecipe` → **(a)** a populated `neo4j_graphrag.GraphSchema` (the hard schema), **(b)** a prompt prefix (soft steering), **(c)** a deterministic mapping plan (structured mode).

**Wiring:**
- **Free-text**: `make_extractor(settings, schema=resolved.to_graphschema())` → `extract_for_chunk(schema, prompt_prefix, chunk)` (both slots exist today). Then post-enforcement (warn/strict/coerce) as a backstop; emit the enforcement report.
- **Structured/semi-structured**: extend `_ingest_structured` (today CSV/JSON) to consume the recipe's mapping plan over CSV/JSON/**JSONL**, writing typed nodes/edges with provenance properties and `MERGE` on identity keys.
- **Provenance/job**: persist `effective_recipe` + the extraction/enforcement report on the ingestion job (the legacy's `effective_instructions`, generalized).

**Agent-addressable:** a capability-registry tool (e.g. `core/graph-ingest@1.0.0`) that an agent calls with `{graph_id, source, recipe_ref, overrides}` — so the onboarder/ingestion agent drives ingestion; plus the ingest API accepts `recipe_id` + `overrides` for **free-text too** (today `recipe_id` is structured-only).

---

## Build on these (new-backend surfaces — refs)

- `entity_extractor.py:56-90` — `EntityExtractor(__init__ schema: GraphSchema | None)`, defaults open at `:71`; `extract_for_chunk(self._schema, "", chunk)` at `:90` (**the `schema` and prompt slots are already there — just never populated**).
- `neo4j_graphrag.experimental.components.schema` — `GraphSchema`, `SchemaBuilder`, `RelationshipType`, `SchemaValidationError`, `SchemaFromTextExtractor` (native hard-schema + LLM schema synthesis).
- `schema/ontology_schemas.py:11` `OntologyRequest.allowed_labels` + `domain/ontology.py:22` `Ontology` — extend labels-only → typed entity/relationship definitions.
- `domain/job.py:36` `IngestionPayload.recipe_id`, `schema/ingest_schemas.py:20` (structured-only) — extend to free-text + add `overrides`.
- `schema/recipe_schemas.py` (`StoreRecipeRequest`/`RecipeSummary`) + the recipe store/repository — extend the recipe format.
- `tasks/ingest_tasks.py` `_ingest_async` / `_ingest_structured`, `services/ingestion_service.py:45-67` — the wiring sites.

---

## EURail / onboarder acceptance (the proof)

1. Author an **"evidence-and-conflicts" recipe**: `Evidence{evidence-id (key), claim, confidence, label, dimensions[]}`, `Source{url (key), name, publication_date}`, `Conflict{conflict-id (key), topic, resolution, synthesis_note}`; relationships `Evidence-[:FROM_SOURCE]->Source`, `Conflict-[:CONTRADICTS]->Evidence` (edge records via `evidence_ids`), `Conflict-[:RESOLVED_BY]->...`.
2. Ingest `v2/05-evidence.jsonl` (600) + `v2/05-conflicts.jsonl` (24) in **structured mode** → a graph with typed Evidence/Source/Conflict nodes carrying confidence/dimensions/provenance and `CONTRADICTS`/`RESOLVED_BY` edges — **deterministic, lossless** (vs the current open-schema flattening).
3. Query proves it: *"HIGH-confidence Evidence on `regulatory-exposure`"*, *"the 24 Conflicts + their resolutions"*, *"Evidence contradicted by another source"*.
4. **Onboarder agent** (harness OHM = interview prompt + `knowledge-retriever` (and/or a graph-query) tool + an OpenRouter model): interviews the user, retrieves the relevant HIGH-confidence evidence per dimension + the live conflicts/resolutions, and emits a structured tailored brief. The "custom look" is the FE rendering that structured output.

---

## Work breakdown (slices — sliceable into sub-issues)

1. **Recipe + ontology model/API** — extend the recipe format + ontology (typed entity/relationship defs, mapping, enforcement, provenance, identity keys); versioned, org-scoped, Postgres-backed; CRUD + dry-run.
2. **Resolver + compiler** (domain) — `ResolvedRecipe` → `GraphSchema` + prompt prefix + mapping plan.
3. **Free-text hard-schema wiring** — feed the compiled `GraphSchema` + prompt to `EntityExtractor`; post-enforcement (warn/strict/coerce) + report.
4. **Structured/semi-structured mapping mode** — recipe-driven field→node/edge mapping over CSV/JSON/JSONL, incl. edge records + `MERGE` on identity keys + provenance properties.
5. **Provenance + job record** — `effective_recipe` + extraction/enforcement report; per-node/edge source lineage.
6. **Schema authoring aids** — `SchemaFromTextExtractor`-backed "synthesize a recipe from a sample" + a template library (incl. the evidence-and-conflicts template).
7. **Agent capability + ingest API** — `core/graph-ingest` registry tool; ingest API accepts `recipe_id` + `overrides` for free-text.
8. **EURail acceptance + tests** — ingest the EURail corpus via the recipe; the queries above; the §22 DoD (real substrate, org-scoped, not-hollow, Reza sign-off).

## DoD / notes
- ORAA-4 §21 layering throughout; org-scoped (no cross-org recipe/graph access); §22 not-a-stub (the recipe must actually drive extraction, proven by the EURail acceptance, not just stored).
- Ties directly to oraclous-frontend "Recipes" page (recipe authoring/selection) and the onboarder-agent concept.
- Legacy is the *blueprint for the resolver/compiler ergonomics*, not the implementation — we use the library's native hard schema, add the structured/semi-structured mode, provenance lineage, identity-key merge, agent addressability, and the evidence/conflict primitives the legacy lacked.
