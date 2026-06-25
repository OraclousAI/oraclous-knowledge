# ADR-041 — Artifacts Live on Oraclous; Storage Sinks are Pluggable Connected Tools; the Graph is the Universal Index

## Status

| | |
| --- | --- |
| Status | **Accepted** |
| Date | 2026-06-25 |
| Deciders | Drafted by the CTO (johnkennII) at Reza's direction, capturing Reza's architecture; **accepted by Reza (CTO) — 2026-06-25** (on the johnkennII CTO review, PR oraclous-knowledge#78). johnkennII reviewed the PR; it does not accept the decision. |
| Driving epic | [#387](https://github.com/OraclousAI/oraclous-backend/issues/387) (E6) — the use-case proofs (book deliver, DoefinGPT served-surface [#543](https://github.com/OraclousAI/oraclous-backend/issues/543)) lean on this |
| Builds on | ADR-040 (cloud-first / graph-primary substrate) · ADR-038 (tool/data adoption primitives) · ADR-039 (batteries-included registry — the sink capabilities) · ADR-034 (adoption-first import) · the importer file→graph mapping ([#509](https://github.com/OraclousAI/oraclous-backend/issues/509)) |
| Extends | **ADR-040** — generalizes graph-primary from *knowledge/inputs* to *artifacts/outputs*: a team's outputs are first-class graph citizens, and deliver-back is one pluggable sink, not the default |
| Realizes | E6 item 10 / O7 (clarifies deliver-back as a pluggable sink, not the default) + the artifact-home and graph-index invariants |

## Context

E6's deliver-back (item 10 / O7, [#515](https://github.com/OraclousAI/oraclous-backend/issues/515)) shipped a **github-sink** that writes a team's outputs to an external git tree as a clean-delta PR. Planning the E6 use-case proofs (book, DoefinGPT / bitcoin-gpt) surfaced a foundational question the design had left implicit: **where do an agent team's artifacts (its outputs / work products) live, and how do the agents retain visibility into them?**

The implicit reading — *deliver-back = export the team's output to the user's external source (git)* — is wrong as a default:

- It treats Oraclous as a **passthrough**. The platform's reason to exist is to be the **home** of the agents' work.
- For an **Oraclous-native** use case (bitcoin-gpt — its world model is a graphify graph on the platform) there is **no external source to export to**; the artifacts should **live on the platform** and be served from it.
- Some creators *do* want their artifacts **also** stored externally (git, Notion, Google Doc, an external relational DB) — a deliberate, per-team choice, not a default.
- When artifacts go external, the agents must **not lose visibility** into their own work — the graph is the agents' single window into everything.

The book is **not** the special case: its author may *choose* to also store chapters in a git tree, but by default its artifacts live on Oraclous too.

## Decision

1. **Artifacts live on Oraclous by default.** A team's outputs are first-class Oraclous citizens, written into the platform's graph (the agents' native home). The platform is the home of the agents' work, **not a passthrough**. This holds for every use case (book + DoefinGPT) by default.

2. **Storage destinations are pluggable, connected TOOLS, chosen at team / harness CREATION time.** Where *else* — beyond Oraclous-native — a team's artifacts are stored is the creator's decision, expressed as the **sink capabilities / connectors / MCPs the team OHM binds**. This is the Claude Code model: the agent writes through whichever tools it is connected to. The **github-sink ([#546](https://github.com/OraclousAI/oraclous-backend/issues/546)) is ONE such sink tool**; the Oraclous-native graph store is another; Notion / Google Doc / an external relational DB are further connectors, or MCP-imported tools ([#541](https://github.com/OraclousAI/oraclous-backend/issues/541)). "Store at Oraclous" = bind the graph-native sink; "store at X" = bind X's connector. **Deliver-back is not a distinct feature — it is "the team has a sink tool bound."**

3. **The graph is the always-on UNIVERSAL INDEX — the visibility invariant, not a selectable destination.** Regardless of which sink(s) a team binds, **every artifact is indexed in the graph** so the agents (and other teams) retain full visibility into their work, wherever the bytes physically live. The graph is **not** one storage option a creator can opt out of; it is the constant index that keeps the agents' world coherent across all sinks. An external sink stores the bytes externally **and** the graph indexes them (a retrievable handle + metadata); an Oraclous-native sink stores the bytes and the index together. **A sink path that writes externally without graph-indexing is NON-CONFORMANT** — it makes the agents blind to their own published work.

4. **Sink selection lives in the manifest / creation layer; graph-indexing is a sink-path invariant.** The team OHM declares its bound sinks (the creation-time "where to store" choice); the sink-execution path MUST satisfy Decision 3 for every artifact, regardless of destination.

## Consequences

- **The github-sink ([#515](https://github.com/OraclousAI/oraclous-backend/issues/515) / [#546](https://github.com/OraclousAI/oraclous-backend/issues/546)) is correctly ONE pluggable sink**, not the default or special "deliver-back." Its conformance to the graph-index invariant (Decision 3) **must be verified**: if it writes to github without the artifacts landing in the graph, that is a gap to close — the agents would be blind to their delivered work. (Open verification item against the running deliver-back path.)
- **DoefinGPT ([#543](https://github.com/OraclousAI/oraclous-backend/issues/543)):** artifacts live on Oraclous (graph) and are **served from the platform** — *not* a github deliver, unless the creator binds a github sink (then: write + graph-index).
- **Book:** artifacts live on Oraclous by default; the author may bind a github sink to *also* store in their git tree (a demo choice) — with the github content **indexed back into the graph**.
- **MCP-enablement ([#541](https://github.com/OraclousAI/oraclous-backend/issues/541)) gains importance** — it is the path by which arbitrary external sinks (Notion, etc.) become connectable as tools.
- A creation-time **"connect your sinks"** step (binding sink capabilities) is a first-class manifest / harness concern, mirroring connecting MCPs in Claude Code.
