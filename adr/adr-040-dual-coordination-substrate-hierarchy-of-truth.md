# ADR-040 — Dual Coordination Substrate + Hierarchy-of-Truth Adoption

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-24 |
| Deciders | solution-architect (drafted at Reza's direction — the coordinator-session rule relaxed for this ADR); **accepted by Reza (CTO) — 2026-06-24**, on the johnkennII CTO + use-case-guardian PR review (PR oraclous-knowledge#75) |
| Driving epic | [#387](https://github.com/OraclousAI/oraclous-backend/issues/387) (E6) · ADR issue [#511](https://github.com/OraclousAI/oraclous-backend/issues/511) |
| Builds on | ADR-031 (OHM v1.1 team manifest — the `precedence` field) · ADR-035 (coordination control & media — the `blackboard` medium) · ADR-034 (adoption-first import) · ADR-032 (capability-absence) |
| Amends | **ADR-027** (agent-memory store — scope hardcoding + `CONTRADICTS` canonicity) · **ADR-022** (recipe-primitive ingestion — recipe target) |
| Realizes | North-Star Lock R5 (substrate fidelity); §6 acceptance items 8, 9, 10; O7; §7 A-NEW-3 |

## Context

The team coordination design assumes the **blackboard is the Neo4j `:Memory` graph** — baked into `team-of-agents-capability-design.md` §C4, the ADR-027 `team` scope, and the ADR-035 `blackboard` medium (realized on "team-scope graph memory"). The North-Star Lock's adversarial review (R5) found that assumption is **wrong for two of the three north-star use cases**, and that it silently **inverts the user's own truth model**. Three concrete gaps exist today:

1. **No file-native substrate.** The book studio keeps its canon as a **git-versioned markdown tree** (`bible/`, `rules/`, `drafts/`, `production/`). The current design would force that canon into a graph and hand results back out of a graph — destroying the very artifact the author keeps and edits. There is no path to read/write the markdown **in place** with `CONTRADICTS` layered over it as a *derived, disposable* index.

2. **No graph-adopt path.** bitcoin-gpt already maintains its own **graphify world-model graph**. The platform today would stand up a *second* graph (a fresh KGS `:Memory` graph), forcing a migration and a duplicate world-model. There is no way to point the blackboard at the user's **existing** graph.

3. **The user's truth model is not honored, and the derived index is treated as canonical.** Precedence/provenance (book: `rules > bible > TOC > drafts`, graph derived-and-disposable) is expressible (ADR-031 `OHMPrecedence`) but **not enforced** at runtime. Worse, the ADR-027 write path **hardcodes `scope:"agent"`** (`memory_client.py:135,160`) and is flag-gated OFF — the `team` scope ADR-027 defined is *never written* — and the `CONTRADICTS` resolution **invalidates the older node** (`new_wins`, `memory_repository.record_contradiction`), i.e. a *derived* contradiction index mutates the user's canonical truth.

R5 requires two first-class substrates (**the source decides**), an **adopted** truth model, and **deliver-back in the source format**. This ADR decides those; the E6 child issues (#512 file-native, #513 graph-adopt, #514 hierarchy-of-truth, #515 deliver-back/O7) implement against it.

## Decision

1. **Two coordination substrates are PEERS; the source decides — never imposed.** The `blackboard` medium (ADR-035) is realized by exactly one of two substrates, selected by the importer (ADR-034) from the user's source:
   - **(i) File-native** — git-versioned markdown read and written **in place** (book: `bible/`, `rules/`, `drafts/`, `production/`). **No migration into a store.** A `CONTRADICTS` contradiction index is layered **over** the files as a **derived, disposable** index — recomputed from the files, never the source of truth; deleting it loses nothing canonical.
   - **(ii) Graph-adopt** — the user's **existing** graph is the team-scope blackboard. Members write/read `:Finding`/`:Memory`/world-model nodes against *that* graph; Oraclous **never** stands up a second graph (bitcoin's shared world-model).

2. **Hierarchy-of-Truth is ADOPTED, not imposed.** The OHM v1.1 `precedence` field (ADR-031 `OHMPrecedence{order, graph}`, `manifest.py:249`) is populated by the importer from the source and **enforced** at runtime: on a `CONTRADICTS`/conflict, the higher-precedence source wins (book: `rules > bible > TOC > drafts`); the derived graph index is **not** canonical. `precedence.graph` defaults to **`derived`** (disposable index); **`authoritative` (graph-as-truth) is an explicit opt-in mode, never the default** (lock §7 A-NEW-3). The runtime never inverts canonical truth to graph-as-truth.

3. **The derived index is disposable (amends ADR-027 §1).** When `precedence.graph: derived` (the default), `CONTRADICTS` edges are recorded as **flags** but **do not invalidate** the older memory — `valid_to` stays NULL and precedence (not recency) decides which source wins; nothing canonical is destroyed and the index is rebuildable from source. The legacy `new_wins` invalidation applies **only** under the explicit `authoritative` mode. `record_contradiction` gains a resolution-mode parameter; `derived` is the default.

4. **The team blackboard write path carries scope (amends ADR-027 §1).** The fire-and-forget write path stops hardcoding `scope:"agent"` (`memory_client.py:135,160`): it carries the run's scope, so a **team** run writes **`team`-scope** nodes (the scope ADR-027 defined but never wrote). An automatic **team-scope read each turn** gives concurrent members visibility of each other's in-flight state. ADR-027's zero-risk shape is preserved unchanged — fire-and-forget, fail-soft, short-timeout, flag-gated (`HARNESS_MEMORY_WRITES`), no coupling of run latency/success to the store. For graph-adopt, the write target is the **adopted** graph, not a fresh KGS graph.

5. **Recipes target the selected substrate (amends ADR-022 §3).** An ingestion recipe no longer always projects into a new unified KGS graph. Its **target becomes a choice** mirroring the substrate: a file-native team's recipe produces the **derived file-tree index** (contradictions / cross-references that index the markdown without becoming canonical); a graph-adopt team's recipe writes into the **adopted graph** (the user's existing graph), never a mandatory second graph. The recipe contract gains a `target` discriminator: `file_tree_index` | `{graph, graph_id}`.

6. **Deliver-back lands in the source format — the generic O7 sink contract (decided here; idempotent-refresh hardened in E9).** Team outputs land in the format the user used: editable `.md`/`production/` written into the user's **git tree** (book) with defined branch/commit/PR semantics and **idempotency keys** (a recurring refresh writes a **clean delta**, not a clobbered tree); a **served surface** (bitcoin). The generic delivery-sink contract — *whose* creds, overwrite-vs-append, the idempotency key — is decided here; the docify/agent-pack form (EURail) and the idempotent-refresh hardening reuse this sink under E5/E8/E9.

## Boundaries (out of scope — opt-in per Lock §4 CUT, or owned elsewhere)

- **D2** partial-failure compensation / idempotency quarantine for side-effecting serving — opt-in (distinct from O7's delivery-sink idempotency, which is in scope).
- **D5** cross-org / confused-deputy / covert-channel isolation — opt-in (serving-time); the *within-run write-scope isolation* half rides with E3/E7.
- Team budget **pooling** + per-member ReBAC envelope (single-tenant) — E7/E8.
- The run-tree / evaluator wiring (E4), the schedule/loader/connector adoption that *feeds* a substrate (E5), and the seeded-refresh lifecycle that *drives* O7 delivery (E8). This ADR decides the **substrates + truth model + sink contract**, not the lifecycles or evaluators on top.

## Alternatives considered

- **Keep `blackboard = graph` only (status quo).** Rejected — wrong for the book (forces the git-markdown canon into a graph and destroys the author's in-place artifact) and bitcoin (forces a second graph beside the existing world-model). This is the exact gap R5 names.
- **Migrate file-native sources into a graph and serve from the graph.** Rejected — inverts the user's canonical truth to graph-as-truth (violates item 9 / A-NEW-3) and breaks the author's edit loop. The file tree must stay canonical.
- **Keep `CONTRADICTS` always canonical (`new_wins`, status quo).** Rejected — that treats a *derived* index as truth and lets recency silently overwrite a higher-precedence source. Precedence must decide; the index must be disposable.
- **Add a brand-new `substrate:` selector field to the OHM schema.** Rejected — the choice already rides on the importer-populated `precedence` (ADR-031) plus the `orchestration.medium` `blackboard` entry (ADR-035); adding a third field is schema sprawl. **Reuse, don't add.**
- **Stand up a unified Oraclous graph and import the user's graph into it.** Rejected — same "forced second graph / duplicate world-model" failure mode item 8 forbids; adopt the user's graph in place.

## Consequences

- The **importer (ADR-034)** detects the substrate from the source and populates `precedence` + the substrate selection; nothing downstream chooses the substrate.
- The **orchestrator/runtime** enforces precedence on conflict and never writes graph-as-truth unless `authoritative`.
- Code seams reshaped: `memory_client.py` (scope param), `memory_service.py` read side (team-scope read each turn), `memory_repository.record_contradiction` (derived resolution mode), the recipe target discriminator, and the delivery-sink capabilities (git-tree + served-surface) on the capability-registry connector framework.
- **Test invariant:** the two substrates pass the same dry-run validation, and **deleting the derived index must lose nothing canonical** (file-native) / **no second graph is created** (graph-adopt).
- **ADR-035 status note:** the `blackboard` medium is now realized by **two peer substrates** (file-native | graph-adopt) instead of the single graph-resident assumption; the rest of the media taxonomy is unchanged.
- ADR-027 and ADR-022 carry an "Amended by ADR-040" note for the scope / `CONTRADICTS`-canonicity and recipe-target changes respectively.

## References

- North-Star Lock — R5 (substrate fidelity), §6 items 8/9/10, O7, §7 A-NEW-3: `oraclous-knowledge/product/team-of-agents-north-star-lock.md`
- Capability design — §C4 (blackboard), §6 (media guide), §9 (build-on seams): `oraclous-backend/docs/team-of-agents-capability-design.md`
- Amends: `oraclous-knowledge/adr/adr-027-agent-memory-ebbinghaus-store.md`, `oraclous-knowledge/adr/adr-022-recipe-primitive-unified-graph-ingestion.md`
- Builds on: `adr-031-ohm-v1.1-team-manifest.md`, `adr-035-coordination-control-and-media.md`, `adr-034-adoption-first-import.md`
