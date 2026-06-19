# Oraclous — Team-of-Agents Use-Case Playbooks

> **Companion to** `team-of-agents-capability-design.md`. Assumes the design's Phase A–D capabilities are built (the "hypothetically ready product"). Each playbook is a concrete, step-by-step demonstration; every step cites the design capability it uses (e.g. **[B1]** = the orchestrator primitives). The three cases — EURail assessment, bitcoin-gpt/doefin-gpt market intelligence, and the book studio — were chosen because each *independently* exercises every pillar, which is the validation that the capability set is complete.
>
> **Common shape.** On the ready product, every team is **one Team Harness (OHM v1.1) = one governed run** [A1]: one budget envelope, one provenance/run-tree, one tenancy boundary. You author (or have the Planner emit) the manifest, the Coordinator dispatches members via the orchestrator primitives, members coordinate through the chosen media, the Evaluator gates quality, the closed loop refines, and the output is served. The difference between the three cases is *topology, media mix, cadence, and who consumes the result*.

---

## Playbook 1 — The EURail Assessment (a one-shot research → graph → served-agent flow)

**Objective.** Produce a cited, board-grade AI-adoption assessment of Eurail, persist the evidence as a knowledge graph, and stand up an inference agent the Eurail team can query — all as one governed, multi-tenant run.

**The team (one Team Harness, fan-out/fan-in pipeline).** This is the `14 research → 3 analysis → 4 synthesis → 2 QA` topology, expressed as members with dependency edges [A1/A2]:

| Member (role) | kind | sub-goal | depends_on | medium |
|---|---|---|---|---|
| `researcher` (fan-out ×14) | agent | gather cited evidence for one research module | — | parallel + **blackboard** |
| `analyst` (×3) | agent | turn merged evidence into the maturity scorecard / federation / market reads | researcher (barrier) | structured hand-off |
| `synthesizer` (×4) | agent | write the diagnosis / roadmap / partnership / appendix sections | analyst | structured hand-off |
| `qa` (×2) | agent | adversarially verify claims + resolve conflicts | synthesizer | **round-table** |

### Step by step

1. **State the objective.** Submit the objective + inputs (subject = Eurail, the module list, the success criteria: *"every claim cites a source; ≥600 evidence records; conflicts resolved"*) to the Planner. The Planner (Harness Compiler) surveys the substrate and **emits the Team Harness** above [A1/A2], or you author it directly. *(Optional Gate: review/approve the plan.)*
2. **Fan out the 14 researchers** [B1 `orchestrate.parallel`]. The Coordinator [B2] reads `orchestration.style` and dispatches 14 `researcher` sub-harnesses **concurrently**, each in its own context window, each over one module (one item of `fan_out.over: $.modules`). Each researcher calls the **`web.search` + `web.fetch` tools** — the one capability that must be added for this case (see §"what's new" below) — plus `graph_ingest`/`knowledge_retriever` for any existing org knowledge. Each emits a typed `evidence_batch` [B5] to the **blackboard** [C4] (team-scope `:Finding` nodes), so researchers see each other's findings and avoid duplication; `CONTRADICTS` edges flag disagreements.
3. **Barrier + merge** [B1 fan-in barrier + B3 reducer]. The parallel stage blocks until all 14 complete (or the termination rule fires [D1]); the reducer dedupes the 14 evidence batches into one merged ledger.
4. **Run the 3 analysts** [B1 `orchestrate.sequential`]. Each consumes the merged ledger via a structured hand-off [B5] and produces a scored analysis module.
5. **Run the 4 synthesizers**, same pattern — each writes one document section, citing only blackboard-backed evidence.
6. **Adversarial QA round-table** [round-table medium]. The 2 `qa` members deliberate over the synthesis — one refutes weak claims, one checks conflict resolution — turn by turn over a shared (now *structured*) transcript.
7. **Evaluate** [C1]. The Evaluator scores the run against `success_criteria` (citation coverage, evidence count, unresolved `CONTRADICTS` = 0). **Below threshold → closed loop** [C5]: re-task the specific researcher whose module is thin, or send conflicts back to a redo — *not* a blind re-run.
8. **Monitor throughout** [C2/C3]. The whole thing is one **run-tree** — root Team Harness + 14+3+4+2 child executions + board tasks — with a live progress signal (% modules done, evidence count vs target) and the **team budget envelope** enforced [D3] so 14 parallel researchers can't blow the aggregate cost.
9. **Deliver to the graph.** The merged, QA-passed ledger is ingested via `graph_ingest` into an org-scoped Neo4j graph (recipe maps each evidence record → `:Claim`/`:Entity` nodes) — *this already works today*.
10. **Serve the inference agent** [serving path, exists]. Publish a **long-lived inference Team Harness** wired to `knowledge_retriever`/`federated_search` over that graph; mint a **gateway integration key** scoped to the Eurail org and bound to that agent. The Eurail team queries their assessment through the gateway, fully org-isolated.

**What's reused (today):** graph ingest, KRS retrieval, published-agent + integration-key serving, provenance, BYOM. **What's new (this design):** the parallel orchestrator + barrier [B1], structured hand-off [B5], the evaluator + closed loop [C1/C5], the run-tree [C2]. **The one extra tool:** a `web.search`/`web.fetch` connector [registry connector, the gap flagged in the feasibility review] so researchers can do live web research.

> **Why a team, not one agent:** the 14 researchers must run **in parallel, each in an isolated context**, to produce *diverse, independent* evidence at scale — exactly what head-switching (one context, many roles) cannot do. This is the orchestrator-worker pattern, with a touch of round-table at the QA stage.

---

## Playbook 2 — bitcoin-gpt / doefin-gpt (continuous, multi-team market intelligence)

**Objective.** *Not* a one-shot report and *not* a single model — a **standing collection of agent teams** that continuously interpret the Bitcoin ecosystem (regimes, players, causality), maintain a shared world-model graph, and serve an interpretive surface ("what is the market trying to do?"). The project already defines **16 agents across 4 distinct teams**; this is the canonical "lots of agents / separate teams each for a different purpose" case.

**Four Team Harnesses (one per purpose, sharing one blackboard).** Each team is its *own* Team Harness [A1] — separate budgets, schedules, and ReBAC scopes — but all read/write the **shared world-model graph** [C4 blackboard] so the teams compose without coupling:

| Team Harness | members (role-agents) | purpose | cadence |
|---|---|---|---|
| **Market-Dynamics Research** | `research-lead`, `analyst`, `engineer` (+ `macro-strategist`, `quant-research-lead`, `intelligence-publisher`) | model BTC as a causal system; regimes, lead-lag, features | scheduled (daily/weekly) + on-demand |
| **Business Pillar** | `strategist`, `osint-analyst`, `product-analyst`, `market-analyst` | model the BTC *industry* (players, funding, regulators, ICPs) | scheduled (weekly) + on-demand |
| **Instrument / Market Design** | `instrument-architect`, `market-mechanism-designer`, `market-sizing-analyst`, `unit-economics-modeler`, `gtm-competitive-strategist` | derive tradeable payoffs + venue mechanisms (the Doefin bridge) | on-demand (triggered by research output) |
| **Research Radar & Curation** | `research-scout`, `research-curator` | keep the backlog high-signal; scout generates, curator adversarially scores | scheduled (continuous) |

### Step by step

1. **Connect the data sources once** [B4 connectors + credential broker]. Register each data layer as a **tool** resolved by the credential broker: `web.fetch`/REST connectors for **Binance** (spot + futures), **Coin Metrics**, **Blockchain.com**, **mempool.space**, **FRED** (API key), **alternative.me** (Fear & Greed), **Bitnodes**; the existing `postgresql`/`mysql` connectors for any local store; **MCP import** for anything that speaks it. Paid sources (Glassnode/CoinGlass) become tools only if/when procured — the manifest references a tool that may not exist yet, fail-closed. Credentials are encrypted per-org (ADR-020); no key is baked in.
2. **Stand up the shared world-model graph** [C4 + KGS]. One org-scoped Neo4j graph is the **blackboard**: ingestion recipes map on-chain/market/macro records and player/entity profiles → typed nodes; this is the persistent substrate every team reads and extends. (KGS ingest + recipes exist today.)
3. **Author the four Team Harnesses** [A1/A2] — each maps the project's existing `.claude/agents/*.md` system prompts onto Role-Agent sub-harnesses (the prompts port almost verbatim), with the project's `## Handoff` convention becoming **structured hand-off envelopes** [B5] and dependency edges.
4. **Run Market-Dynamics on a schedule** [engine schedules, exist]. A cron-fired run: `analyst` members **fan out** [B1] over data layers (one per on-chain / market / derivatives / macro source), write findings to the blackboard [C4]; `research-lead` runs the causal/lead-lag analysis over the merged evidence; `intelligence-publisher` emits a report. Budget-bounded per run [D3].
5. **Run Research Radar continuously** [B1 + C1]. `research-scout` generates candidate questions across its 5 lenses (fan-out); `research-curator` **is the Evaluator** [C1] — it adversarially scores candidates against an AND-floor rubric and promotes only those that clear the bar, writing the backlog. This is the project's existing "scout generates, curator arbitrates" pattern realized as fan-out → judge.
6. **Trigger Instrument Design on demand** [B4 A2A + conditional]. When the research team's output crosses a threshold (a regime/measure worth trading), a **conditional** orchestrator [B1] dispatches the Instrument Design team; `instrument-architect` → `market-mechanism-designer` → `unit-economics-modeler` run as a pipeline [B5], delegating sub-questions via A2A invoke [B4].
7. **Cross-team coordination via the blackboard, not direct coupling** [C4]. The project's principle — "integration happens at the conductor level, not via agent-to-agent coupling" — maps exactly onto the blackboard: the Business team reads macro context the Market team wrote; the Instrument team reads both. No team calls another's internals; they share graph state. `CONTRADICTS` edges + arbitration [D5] resolve cross-team disagreements.
8. **Monitor & evaluate each team independently** [C1/C2/C3]. Each Team Harness is its own run-tree with its own budget and progress signal; the curator (radar) and a flow-level Evaluator gate quality. Drift over time is caught by re-evaluating standing findings.
9. **Refine the world model** [C5 closed loop]. When the Evaluator flags a stale or contradicted finding, the loop re-tasks the relevant analyst (re-fetch the data layer, re-run the analysis) — the world model stays current without a human re-running everything.
10. **Serve the interpretive surface** [serving path]. A long-lived inference Team Harness (the "ask what the market is doing" surface) is published and exposed via gateway integration keys — to you, to the Doefin product, or to external consumers — each scoped by ReBAC. The same graph powers the Doefin instrument-design bridge.

**Why this needs the full design (not just Playbook 1's):** it is **many standing teams** with *different objectives, data, expertise, and cadence*, coordinating through a **shared blackboard** [C4], running on **schedules** with **independent budgets** [D3], and **continuously refined** [C5] — it exercises P1–P5 *and* the missing middle (cross-team budget, blackboard consistency, conflict arbitration) far more than a one-shot report does.

**Reused today:** KGS graph + recipes, KRS retrieval, schedules, connectors framework, credential broker, serving. **New (this design):** the four Team Harnesses [A1], parallel/conditional orchestration [B1], A2A delegation [B4], the blackboard team-scope memory [C4], per-team evaluator + closed loop [C1/C5], per-team budget envelopes [D3]. **Extra tools:** the market/macro REST connectors (small, credential-broker-backed).

---

## Playbook 3 — The Book Studio (six teams, human gates, living refinement)

**Objective.** Produce, fact-check, quality-gate, and market a serious non-fiction book through **six distinct teams** with **seven human gates** — the user's "research team / writing team / marketing team," realized as the project's six teams (Insight, Research, Editorial, Quality, Production, Growth). This is the richest case: it stresses **HITL-as-team-member**, **evaluation-as-gate**, the **blackboard**, and the **closed-loop refinement** hardest.

**Six Team Harnesses sharing one knowledge substrate.** Each team is a Team Harness [A1]; the **`bible/` is the blackboard** [C4] (canonical claims/concepts/sources/people-stories — the single source of truth every team reads); the project's **seven author gates** are **HITL members** [D4] with a structural "no-send-tool" guarantee:

| Team Harness | members | objective | gate after |
|---|---|---|---|
| **① Insight & Calibration** | `book-calibrate` (coordinator) + `calib-audience`/`demand`/`competitive`/`reader-voice`/`channel` | positioning: who's it for, what's the white-space | **Gate A** (approve TOC restructure) |
| **② Research & Knowledge** | `research-scout`, `bible-keeper`, `toc-cartographer` | evidence → canonical `bible/`; conflict = stop | (feeds editorial) |
| **③ Writing & Editorial** | `chapter-architect`, `narrative-drafter`, `developmental-editor`, `line-editor` | outline → prose toward the emotional `target_state` | **Gate B** (dev-edit decision) |
| **④ Quality & Integrity** | `prose-lint`, `fact-checker`, `book-integrity`, `engagement-reviewer` | the **Evaluator team**: integrity > fact > grammar > engagement | **Gate C** (Lock) |
| **⑤ Production** | `book-formatter`, `cover-generator`, `kdp-launch-prep`, … | locked manuscript → KDP-ready artifacts | **Gate D/E** (manuscript / upload) |
| **⑥ Marketing & Growth** | `book-market` (coordinator) + `repurpose-*`, `pr-*`, `ad-strategist`, … | repurpose + PR + ARC, **draft-only** | **Gate F/G** (publish / ad-spend) |

### Step by step

1. **Author the six Team Harnesses** [A1] from the project's existing `teams/` + `.claude/agents` definitions — each agent prompt becomes a Role-Agent sub-harness; each team's coordinator skill (`book-calibrate`, `book-market`, the `book-studio` showrunner) becomes a **Coordinator/orchestration agent** [B2].
2. **The `bible/` becomes the blackboard** [C4]. Instead of file-based handoffs, the canonical knowledge lives as team-scope graph memory: `bible-keeper` writes `:Claim`/`:Concept`/`:Source` nodes; every other team reads them by traversal; `book-integrity` runs its **`CONTRADICTS` detection** over the graph (the project already uses graphify for exactly this). The **Hierarchy of Truth** (`rules/` > `bible/` > `TOC` > `drafts/`) becomes node provenance + governance precedence.
3. **Calibrate (Team ①)** [B1 fan-out + B3 synthesis]. The coordinator fans out 5 `calib-*` members in parallel, then synthesizes a Narrative-Positioning brief + a restructure *proposal* (never edits the TOC directly).
4. **Gate A — HITL member** [D4]. The author is a *first-class member* of the run, not a side-channel: the run **blocks** at the gate with an SLA, surfaces the proposal, and resumes on the author's approve/revise decision. The "agents can't edit the TOC; proposals only" rule is the **within-run isolation** guarantee [D5] — the structural no-write boundary.
5. **Research (Team ②)** [structured hand-off + blackboard]. `research-scout` gathers evidence (delegating hard questions via **A2A** [B4] to a `deep-research` sub-harness), `bible-keeper` canonicalizes into the blackboard; **on a detected conflict it stops and escalates** — the project's "conflict = stop, don't write" is exactly **fail-closed arbitration** [D5].
6. **Write (Team ③)** [B1 sequential pipeline]. `chapter-architect` → `narrative-drafter` → `developmental-editor` run as a pipeline, each consuming the prior's typed output [B5], drafting toward the `target_state`, citing only blackboard facts. The dev-editor emits a *memo*, never a silent rewrite.
7. **Gate B — HITL** [D4]: author decides revise / re-outline / restructure.
8. **Quality (Team ④) is the Evaluator** [C1]. This team **is** the flow-level evaluator made concrete: `fact-checker` verifies every claim against `bible/sources` then web (labels needs-source/disputed/prediction), `book-integrity` adjudicates contradictions across the whole manuscript (per-save, via the graph), `engagement-reviewer` scores emotional-state attainment, `prose-lint` checks voice. Their verdicts are **structured** [C1].
9. **Gate C — Lock = an evaluator-gated barrier** [C1 + D1]. The chapter **cannot lock** while any `CRITICAL` (integrity) or `needs-source/disputed/unlabeled-prediction` (fact) remains. This is precisely *convergence criteria* [D1] enforced by the Evaluator — "good enough" is defined, not mechanical.
10. **The Living TOC is the closed loop** [C5]. A trigger (calibration finding, research result, a graph "god-node", or a dev-editor rec) → a restructure *proposal* → Gate A → `toc-cartographer` applies it → touched chapters bump `calibration_version`. This is **monitor → evaluate → re-plan → re-dispatch** realized as the manuscript's structural refinement, bounded by the "emotional arc must still hold" guardrail.
11. **Production (Team ⑤)** runs only after **Gate D** (full-manuscript integrity sweep passes) — a team whose dispatch is *conditional* [B1] on the Evaluator's full-book verdict. **Gate E**: the author holds KDP credentials; production agents have **no upload tool** (structural [D5]).
12. **Marketing (Team ⑥) runs as scheduled team runs** [engine schedules + D4]. `repurpose-writer` fires daily (06:00 cloud routine), `pr-*` weekly — each re-reads `marketing/profile.md`, writes **only** to a drafts queue, ends with a notification. **Gate F/G**: nothing publishes and no ad spends until the author moves a file / authorizes budget. The "generators have no send/publish/spend tools" rule is the **structural gate** [D4/D5] — the same fail-closed serving boundary the gateway enforces for external access.

**Why six teams, not one pipeline:** the teams have **different success metrics** (audience-fit / truth / emotional-impact / consistency / discoverability / reach), **different skills**, **non-overlapping write scopes**, **different gates**, and **different cadence** (calibration on-demand, research parallel-across-chapters, QA in-parallel-with-writing, production conditional on Gate D, marketing as standing routines). One team cannot hold all six objectives — which is exactly why the design makes each a separate Team Harness sharing one blackboard.

**Reused today:** schedules (marketing routines), HITL task board (gates), graph + graphify (bible/integrity), KRS, serving. **New (this design):** the six Team Harnesses [A1], coordinators per team [B2], the bible-as-blackboard [C4], the QA-team-as-evaluator with gated convergence [C1/D1], the living-TOC closed loop [C5], **HITL-as-first-class-member** [D4] (the seven gates), and within-run write-scope isolation [D5].

---

## Cross-case summary — what each case proves

| Capability | EURail | bitcoin-gpt | book studio |
|---|---|---|---|
| **A1 OHM v1.1 team manifest** | 1 pipeline team | 4 standing teams | 6 gated teams |
| **B1 parallel/sequential/conditional + barrier** | 14-way fan-out + barrier | per-team fan-out + conditional trigger | calibration fan-out; production conditional on Gate D |
| **B2 orchestration agent** | pipeline coordinator | per-team coordinators | `book-studio` showrunner + per-team |
| **B3 aggregation/merge** | merge 14 evidence batches | merge data-layer findings | synthesize calibration |
| **B4 A2A invoke** | — | instrument-design delegation | scout → deep-research |
| **B5 structured hand-off** | research→analysis→synthesis | `## Handoff` envelopes | architect→drafter→editor |
| **C1 evaluator** | citation/conflict gate | research-curator (radar) | the whole QA team (Gate C) |
| **C2 run-tree / C3 progress** | one tree, module progress | per-team trees | per-team trees, chapter status |
| **C4 blackboard** | shared `:Finding` nodes | shared world-model graph | the `bible/` |
| **C5 closed loop** | re-task thin module | refresh stale world-model | the living TOC |
| **D1 termination/convergence** | evidence-count + conflicts=0 | per-run budget/convergence | Lock = no CRITICAL |
| **D3 team budget envelope** | bound 14 parallel runs | per-team budgets | per-team budgets |
| **D4 HITL-as-member** | optional plan gate | conductor on-demand | **seven author gates** |
| **D5 isolation + arbitration** | org-scoped serving | cross-team `CONTRADICTS` | write-scope + "conflict=stop" |
| **serving (exists)** | Eurail team integration key | interpretive surface + Doefin | KDP/marketing draft queues |

All three cases are *currently* run as local Claude Code skill pipelines with file-based handoffs, single-tenant, no governance/budget/audit/serving. Re-expressing them as Team Harnesses on the ready product is what converts each from a **one-off local run** into a **governed, multi-tenant, durable, observable, refinable product** — which is the entire point of the team-of-agents capability.
