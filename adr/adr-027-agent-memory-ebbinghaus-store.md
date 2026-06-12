# ADR-027 — Agent Memory: a Complete Ebbinghaus Store with a Fail-Soft Harness Write Path and Tool-Based Recall

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-12 |
| Deciders | solution-architect (drafted); Reza directed the capability ("more complete than the legacy intended") and **delegated the integration decision with one constraint: zero risk to what is already implemented** |
| Driving epic | [#312](https://github.com/OraclousAI/oraclous-backend/issues/312) · issue [#332](https://github.com/OraclousAI/oraclous-backend/issues/332) |
| Builds on | ADR-018 (internal-key trust) · the R4 harness-runtime (consciousness/provenance) · the #310 first-party-tool pattern |
| Re-architects | legacy `knowledge-graph-builder/app/services/memory_service.py` (+ `endpoints/memories.py`, the MemoryRetriever) |

## Context

Agents need memory that persists **across sessions** and behaves like memory: recent and important things surface; unused things fade. The legacy designed exactly this — episodic/semantic/procedural `:Memory` nodes with an **Ebbinghaus forgetting curve** (`I(t) = base · e^(−λ·days_since_access) + access_boost`, per-type λ, rank-based soft forgetting), contradiction detection, supersede versioning, a token-budgeted "## Relevant Memory" context block — but shipped it one-sided and partially fake: **nothing in the backend ever wrote a memory**, the vector index never received an embedding (recall was fulltext-only), and "similarity consolidation" was hash dedup.

The current platform adds one constraint and one neighbor: Reza's **zero-risk** constraint (existing runs/flows must be unaffected), and the **R4 consciousness/provenance layer**, which records *run-level* state but is not a decaying, cross-session, retrievable store — complementary, not overlapping.

## Decision

1. **The store lives in the knowledge-graph-service** — it owns Neo4j, org+graph scoping, fulltext indexes, and the embedder. A new §21 vertical (`routes → services → domain → repositories`): `:Memory(:Episodic|:Semantic|:Procedural)` nodes stamped org+graph by the injected-scope writer; five scopes (session/user/agent/team/organization); content-hash dedup; **bitemporal supersede** updates (`SUPERSEDES` + `valid_to`); contradiction detection for semantic facts (same subject+predicate, different object → `CONTRADICTS`, old invalidated); soft delete by default.

2. **The decay math ports verbatim as pure domain functions** (per-type λ: episodic 0.05 / procedural 0.01 / semantic 0.005; `access_boost = min(0.3, 0.05·ln(1+access_count))`; source-derived base importance), recomputed **lazily on access** (no decay cron). Forgetting is rank-based — memories sink, they are not auto-deleted.

3. **Build what the legacy faked.** Real embeddings from day one (the existing 512-dim embedder; fail-soft to fulltext-only when no key) → **hybrid recall** = fulltext + org-scoped brute-force cosine + importance + recency (the established KRS-pattern, no label-wide vector index per the #305 finding). Consolidation is **true similarity-based** (embedding clusters, not hash dedup), run as a periodic per-graph job reusing the #305 beat/sweep pattern, under the per-graph Redis lock.

4. **The write path is the harness-runtime — fail-soft, flag-gated.** The R4 harness gains a **post-run hook** that writes an episodic memory of the run outcome (and procedural memories from explicit human feedback) to KGS over the internal-key API. The zero-risk shape: **fire-and-forget with a short timeout — a memory write can never fail, block, or slow a run**; flag `HARNESS_MEMORY_WRITES` defaults **off in code** and is enabled in `deploy/.env` (the platform's inert-default/deploy-opt-in convention). No change to run semantics, metering, or provenance.

5. **Recall is opt-in via a first-party tool, not a prompt change.** A capability-registry tool `core/recall-memory` (mirroring `find_similar`) hits the KGS memory search/context endpoints; agents add it through their OHM toolset. The default prompt assembly is **untouched** — an agent without the tool behaves byte-identically to today, which is what makes this zero-risk. (Automatic "## Relevant Memory" prompt injection in the harness is a possible later layer, behind its own default-off flag.)

6. **Boundary with R4 consciousness/provenance:** provenance remains the authoritative *record of what happened*; memory is the *decaying, retrievable distillation* agents recall from. The harness writes to both; neither reads the other's store.

## Alternatives considered

* **Memory inside the harness-runtime.** Rejected — the harness owns runs, not durable org+graph-scoped Neo4j data; KGS already has the substrate (scoping, embedder, fulltext, locks).
* **Automatic prompt injection as the default recall path.** Rejected for v1 — it changes every agent's prompt assembly (precisely the risk Reza excluded). The tool gives the capability with per-agent consent.
* **Extend the consciousness layer into a memory store.** Rejected — different semantics (append-only run record vs decaying ranked recall); coupling them risks the R4 layer.
* **Synchronous in-run memory writes.** Rejected — couples run latency/success to KGS availability; fire-and-forget fail-soft is strictly safer.

## Consequences

* KGS gains the memory vertical (+ fulltext/scope/hash indexes); harness-runtime gains a fail-soft post-run writer; capability-registry gains `core/recall-memory`.
* Existing runs are **provably unaffected**: hook off → no calls; hook on + KGS down → runs still complete (a mandatory failure-mode test).
* Memory volume is bounded by dedup + consolidation + rank-based forgetting; hard deletes remain explicit.
* The legacy's one-sidedness is fixed: writes (harness), real embeddings (recall), and consumers (the tool) all exist from day one.

## See also

* ADR-018 (internal-key trust) · the R4 harness-runtime layer · #310 (`find_similar` tool pattern) · #305 (org-scoped embedding posture, beat/sweep pattern)
* Legacy: `memory_service.py`, `endpoints/memories.py`, `retriever_factory.py` (MemoryRetriever)
* Issues [#332](https://github.com/OraclousAI/oraclous-backend/issues/332) · [#312](https://github.com/OraclousAI/oraclous-backend/issues/312)
