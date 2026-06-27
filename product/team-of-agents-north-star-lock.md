# Team-of-Agents — North-Star Lock & Acceptance Test

> **Status:** LOCKED (the requirement, not the implementation) · **Authority basis:** the zero-headache sufficiency-lock review (run `wf_bb701ec2-9e2`, 3 per-use-case stress-tests → convergence synthesis → adversarial verify + completeness critic, corrections applied) on top of the team-of-agents architecture audit (`wf_693afa65-500`) and the R7 reconciliation. · **Enforced by:** the `use-case-guardian` persona/agent — every ADR, design change, and PR is checked against §6 below.
>
> This is the **stable anchor** that the platform's **two co-equal on-ramps** — DESCRIBE→team (the compiler, cloud-first) and BRING→team (import, local) — can never silently drift away from again. The three north-star use cases are the IMPORT on-ramp's acceptance test (and its import-fidelity demo); the compiler on-ramp is exercised by its own acceptance (§6 C1–C2). It sits above `team-of-agents-capability-design.md` (the capability spec) and `team-of-agents-use-case-playbooks.md` (the walkthroughs): where this file and either of those diverge, **this file wins** and the other is updated.

---

## 0. The one requirement — two first-class on-ramps to the same GO

> **Get a team that runs — either by DESCRIBING the objective in English (Oraclous builds the team) or by BRINGING the team you already have (Oraclous adopts it) — then press GO and it runs. Either way: no re-authoring, no "but first you must…", no extra requirements.**

The product has **two co-equal on-ramps** to the one outcome (a runnable, validated Team Harness you press GO on). Neither is the "main" one; both are first-class and each is separately tested:

| On-ramp | The user starts with | The primitive | Where it's locked |
|---|---|---|---|
| **DESCRIBE → team** (the compiler / planner) | a prose objective and **nothing to import** — no `.claude/agents` dir | **cloud-first**: Oraclous *synthesizes* the team from the objective (plan → survey capabilities → draft the OHM manifest → validate), then refine in NL | §2 R0 (Compile); §6 items C1–C2; ADR-047 |
| **BRING → team** (the importer / adoption) | an existing Claude Code agent setup that **already works** | **local**: Oraclous *adopts* it as-is — imports the agents/skills/charters/orchestrator → OHM, with zero re-authoring | §2 R1–R6; §6 items 1–16; ADR-034/045 + the R2–R6 ADRs |

**The use cases are the acceptance test for the IMPORT on-ramp — and they earn that role precisely because they already exist.** The three north-star use cases all *already exist* as working Claude Code agent setups (table below); for the BRING on-ramp they are **a real acceptance test, not examples** — the product must adopt them as-is, never make the user rebuild them, and they double as the proof of **import-fidelity** (what came out runs the same as what went in). They are **not the whole north-star**: the DESCRIBE on-ramp serves the user who has nothing to import, and it is exercised by its **own** acceptance (§6 C1–C2, anchored on the EURail-as-prose equivalence oracle), not by these three import artifacts. Import rigor is undiminished; the compiler is added beside it.

| Use case (the IMPORT-on-ramp acceptance test) | What the user brings today |
|---|---|
| **EURail assessment** | one `eurail-report` SKILL.md orchestrator + 23 module prompts + a Python merge spine + a 909-record ledger + seeded-refresh mode + a report-editor 10-gate + docify + agent-pack + a KGB backfill |
| **bitcoin-gpt / doefin-gpt** | 17 `.claude/agents` across 4 standing teams + ~30 skills + 25 stateful Python data loaders + a 21-module analysis library + a half-built harness + 2 MCP servers + a graphify world-model graph |
| **book studio** | 30 `.claude/agents` + 7 coordinator skills + 6 team charters + the `bible/` (git-versioned markdown canon) + 7 structural author gates + scheduled cloud-routine marketing |

## 1. Why every prior iteration failed

Each prior round (the original architecture, the R7 plan, and even the first cut of `team-of-agents-capability-design.md`) treated the hard part as a **footnote**: *"the prompts port almost verbatim," "register it as a tool," "the bible becomes the blackboard."* Every one of those phrases hides days-to-weeks of the user's real, working engineering. **All three use cases abandon at the same walls** — and they are not in the runtime that runs a team; they are in **getting the team you already have into the product, and getting its results back out in the form you keep them.** The lock below makes those walls first-class requirements.

---

## 2. The on-ramp requirements — R0 (COMPILE) + R1–R6 (IMPORT)

Two co-equal on-ramp requirement sets. **R0 (COMPILE)** is the DESCRIBE→team on-ramp (the cloud-first primitive); **R1–R6** are the IMPORT→team on-ramp's headache-elimination requirements (the local primitive). Each requirement is **mandatory and first-class**, not an aside. The *binding cases* column is corrected per the adversarial pass — an IMPORT requirement is real if it blocks **at least one** of the three import use cases; it is not claimed universal where it isn't. R0 binds the **from-scratch / no-existing-team** user (the case the three import artifacts do *not* exercise) and is anchored on ADR-047.

### R0 — COMPILE, don't make-them-author *(binds: the from-scratch / no-existing-team user; equivalence-anchored on EURail)*
A first-class **prose on-ramp** turns an English objective into a runnable team **with nothing to import** — co-equal with R1's importer, not a footnote. The user states an `objective` (plus optional `inputs` / `constraints` / `success_criteria`) and Oraclous *synthesizes* the team. Six first-class properties (ADR-047):

- **(a) The goal→manifest contract.** Prose objective → a single schema-valid OHM v1.1 `kind:team` manifest (populated `members[]` / `orchestration` / `task_board` / `budget` / `governance`) **plus** the per-role `sub_harnesses` — without which a team loads but cannot run. **Zero manual OHM authoring**, exactly as R1 promises for import.
- **(b) Capability-survey as the structural source.** A capability-surveyor surveys the **live registry + the seed capability inventory** to produce the **typed catalog** the drafter may draw `members[].tools` from — and **only** from. The survey is not prompt-shrinking convenience; under capability-absence it is the *allowed set*.
- **(c) ONE validator, shared with the importer's dry-run.** The drafted manifest passes the **exact same** `assemble_team()` / `ImportReport` / `would_block` / `render_report()` dry-run the importer uses (R1/O8) — schema-validates, acyclic runnable DAG, every `tools[]` resolves, capability-absence holds. **One validator, two on-ramps** — the prose front door cannot drift from the import front door, and there is no second validator.
- **(d) Capability-absence holds at COMPILE time.** Each drafted `member.tools` is the immutable hard ceiling (the §2 capability-absence gate, R0's twin of R1's import ceiling). A sub-goal needing an unsurveyed capability **fails closed with a gap report** — a blocking flag → `GO: BLOCKED` — **never a hallucinated tool** (the field's #1 failure mode, structurally impossible here).
- **(e) NL refine as a typed structural delta.** "add a fact-checker" / "make research parallel" / "the editor is human" is parsed into a typed patch (`add_member` / `set_fan_out` / `change_kind` / `add_depends_on`) over the *existing* manifest, re-run through the **same** validator, preserving every untouched member/edge byte-identical — never a blank re-draft.
- **(f) An eval-set for a non-deterministic generator.** NL→team is non-deterministic, so it ships an eval stack: deterministic plan guardrails (the shared validator) → the **EURail-ledger equivalence oracle** (the same objective *in prose* reproduces the 909-record ledger about as well as the *imported* EURail team, passing the 10-gate) → a reference-objective LLM-judge (split plan-adequacy / run-outcome, sample-N, K-of-N ship-bar).
> *Honesty note:* R0 is exercised by the **from-scratch user**, the case the three import artifacts do **not** cover — which is exactly why the compiler needs its own acceptance (§6 C1–C2) and its own equivalence oracle, rather than riding on the import use cases. The compiler is **itself a Team Harness** (planner / capability-surveyor / manifest-drafter / reviewer) on the shipped runtime, reachable through the gateway today — no new platform code, no new gateway routing.

### R1 — IMPORT, don't re-author *(binds: all three)*
A first-class **one-command importer** ingests an existing `.claude/agents/*.md` directory (frontmatter `name/description/model/tools/skills` + body), `.claude/skills/*` coordinators, `teams/<n>/charter.md`, **and** a single skill-as-orchestrator (EURail's shape) → runnable Role-Agent sub-harnesses + the Team Harness, **with zero manual OHM authoring.** Skills referenced in frontmatter are auto-resolved and inlined. "Port almost verbatim" is a tool the product runs, never hand-work. *This is the top-priority deliverable; if step one fails, nothing else matters.*

### R2 — ADOPT the tool/data layer *(binds: bitcoin-gpt strongly, EURail partially; not book)*
Three adoption primitives, all first-class:
- **(a) Script-as-scheduled-ingestion** — "run this CLI loader on a schedule, land output in the org store," preserving its own caching/backfill/rate-limits (bitcoin's 25 loaders; EURail's KGB backfill).
- **(b) Library-as-tool-group** — mount a local Python package's N functions as callable tools (`bitcoin_gpt.analysis.*`; EURail's merge spine as a *verifiable function*, not "concat-dedupe").
- **(c) MCP/connector adoption** — already-MCP sources (fred, mempool, graphify) import directly.
> *Honesty note:* the book case needs only **(c)**. Do not present (a)/(b) as universal.

### R3 — BATTERIES-INCLUDED defaults *(split coverage — see note)*
The platform ships, **pre-registered and credential-ready**: a **web-research battery** (search + fetch + read), **common SaaS connectors**, a **scheduler**, and a **notification/delivery sink**.
> *Honesty note:* the **web-research battery is an EURail blocker (one case)** — 14 live-web researchers are inert without it. The **scheduler + notification sink are universal** (EURail delivery, bitcoin crons, book 06:00 + PushNotification). Bind them separately.

### R4 — IMPORT-DRIVEN ASSEMBLY *(binds: all three)*
The importer **derives the inter-member/inter-team DAG from the source** — the skill-orchestrator's subagent-spawn graph (EURail), the `## Handoff` convention + `cron.yaml` (bitcoin), the showrunner routing + charters + 7-gate sequence + living-TOC loop (book). `depends_on`, conditional dispatch, and schedules are **generated from import**; the user may edit, but never starts from a blank manifest.

### R5 — SUBSTRATE FIDELITY *(binds: all three, opposite needs)*
The design's "blackboard = Neo4j" assumption is **wrong for two of three**. Make two substrates first-class and let the source decide:
- **(i) File-native** — git-versioned markdown read/written **in place**, with `CONTRADICTS` layered over it as a *derived, disposable index* (book: `bible/`, `rules/`, `drafts/`).
- **(ii) Graph-adopt** — use the user's **existing** graphify graph as the blackboard; never force a second graph (bitcoin's world-model).
- **Hierarchy-of-Truth adoption** — precedence/provenance is a manifest field populated from the source (book: `rules > bible > TOC > drafts`, graph derived-and-disposable). The product **adopts** the user's truth model; it never inverts it to graph-as-truth.
- **Deliver-back in source format** — files into the user's git tree (book chapters/`production/`), docify + agent-pack (EURail), and/or a served surface (bitcoin) — whichever the source used.

### R6 — TURNKEY GO *(split coverage — see note)*
- **(a) Single-tenant local GO** — credentials/tenancy default to a **trivial local identity**; org/ReBAC/BYOM/gateway are **opt-in, not preconditions** *(binds: all three; the book hardest)*.
- **(b) Three first-class lifecycles** — **bounded run**, **standing/recurring team** (long-lived, scheduled, non-terminating, recurring-budget accounting) *(bitcoin; book marketing)*, and **seeded-refresh** (cross-run: re-verify a prior ledger, emit a what-changed delta — EURail's `--refresh-from`) *(EURail)*.
- **(c) Cost-sane defaults** — per-member model-tier with a cheaper default for routine scheduled scans, **surfaced before GO** *(bitcoin hardest; applies to any multi-member/standing fleet)*.

### The CAPABILITY-ABSENCE GATE primitive *(binds: book primarily; any imported team)*
A member's imported `tools:` set is its **hard capability ceiling**, enforced at dispatch: **no orchestrator, A2A, or coordinator path may grant a capability the source file didn't declare.** Tool-omission stays **structural, not policy** — this is the realization of the book's 7 author gates (`tools: Read,Grep,Glob,Write` ⇒ the agent literally cannot publish/upload/spend).
> *Correction (adversary #6):* this is distinct from, and additional to, **HITL-as-a-blocking-gate-node** — the *step* where the human advances the work (gates A–G). Capability-absence prevents bad sends; the blocking-gate-node models "pause here until the author approves." **The book needs both.** Keep the blocking-gate-node non-opt-in for the book; only the HITL **SLA/capacity** apparatus is cut to opt-in.

> *Correction (adversary #7) — "bring your harness" resolves honestly:* the user brings agent **definitions**; **the platform is the runtime.** A user's partially-built harness (bitcoin's AgentSpec parser, tool-group YAML, Postgres schema, Modal target) is *not* reused as a runtime — the importer lifts the *definitions*, the platform supplies execution. State this plainly so "bring my harness" never implies runtime reuse.

---

## 3. Operational requirements (O1–O8) — "living with it once it's running"

The completeness critic's gaps. The lock above gets the team **in**; these are what stop the user abandoning in week one/two. Each is a requirement with a one-line acceptance check.

| # | Requirement | Abandon-force | Acceptance check |
|---|---|---|---|
| **O1** | **Secret onboarding** — "paste your keys once, scoped and reused" (Anthropic/OpenAI, FRED, loader tokens, mempool, graphify) | P0 (day one) | First scheduled run consumes user secrets with **no per-tool auth prompt wall** |
| **O2** | **Cost pre-flight + hard cap** — projected recurring bill **before** GO + a spend cap that **pauses** (not silently overruns) | P0 | Pressing GO on a standing fleet shows "~$X/day at this cadence" and a cap that halts the fleet |
| **O3** | **Partial-failure delivery contract** — defined "researcher 9/14 timed out / FRED down" behavior; partial result with holes **flagged**, never silently worse | P0 | A half-failed run delivers a labeled partial + a list of what it skipped |
| **O4** | **Light status surface** — "is my team healthy / did last night run / what did it cost" (the thing the solo author actually opens) | P1 | A standing team exposes a one-glance status without the cut full-trace machinery |
| **O5** | **Edit-a-running-team** — change a member prompt / add a member; next run picks it up; **re-import-merge vs. clobber** is defined; in-platform edits survive an upstream re-import | P1 | Editing member 12 and re-importing the upstream dir does not silently lose either change |
| **O6** | **Local↔cloud parity** — a team validated in single-tenant local GO behaves the same when promoted to served/multi-tenant (same batteries, scheduler semantics, substrate) | P1 | Promotion changes governance only, not behavior |
| **O7** | **Delivery-sink auth + idempotency** — outputs land *where*, with *whose* creds, overwriting/appending *how* (git branch/commit/PR; webhook/email target); a refresh produces a clean delta, not a clobbered tree | P2 | A recurring refresh writes a clean diff into the target with explicit creds/semantics |
| **O8** | **Import dry-run** — "show what you parsed, the DAG, which tools resolved vs. failed, what a dry pass would do" **before** the first cost-incurring/side-effecting run | P2 | A 30-agent import yields a validation report before any live run |

---

## 4. CUT — gold-plating, made opt-in (not default)

None of the three needs these on the minimal path; keep them as **opt-in**, never a tax:

- **B4 A2A invoke-harness / recursive agent-calls-agent** — opt-in (EURail unused; book one delegation a coordinator covers; bitcoin no-direct-coupling).
- **B2 dynamic runtime coordinator** — the **generated DAG (R4)** replaces it on the minimal path (incl. static conditional edges); dynamic coordination is opt-in.
- **D4 HITL SLA/capacity apparatus** — opt-in. **(Keep the capability-absence gate AND the blocking-gate-node — book needs both; cut only the SLA/queue/time-to-resolution machinery.)**
- **D5 cross-org / confused-deputy / covert-channel isolation** — opt-in (serving-time only). **Keep the within-run write-scope isolation half** (book needs it).
- **D2 partial-failure compensation / idempotency quarantine** — opt-in for side-effecting serving (not the read-mostly cases). *(Distinct from O3, which is the user-facing delivery contract and is required.)*
- **C2 full cross-service distributed-trace correlation** — keep for the 14-way swarm (EURail); for the rest, **O4's light status surface** suffices.
- **Mandatory propose-then-human-approve Planner gate** — opt-in (experienced conductors import-and-run; plan-approval is a setting).
- **Adversarial QA round-table as a *required* stage** — opt-in medium (bitcoin's curator AND-floor and EURail's report-editor are single-evaluator).
- **Team budget pooling + per-member ReBAC envelope** *(book)* — opt-in for single-tenant; required in served/multi-tenant mode.

---

## 5. Sufficiency verdict

**Sufficiency is judged per on-ramp.** For the **IMPORT** on-ramp: **with R1–R6 + the capability-absence gate + O1–O8, the design is NECESSARY and SUFFICIENT for all three import use cases. As originally written (without them) it is INSUFFICIENT — it fails every case on step one.** Coverage confirmed: EURail (skill-import, seeded-refresh, web battery, merge/10-gate, docify+pack, vertical-compose-by-reference); bitcoin (agents-importer, loader+library adoption, graph-adopt, standing mode, cost tiers, served surface); book (43-artifact importer, capability-absence + blocking-gate-node, file-native bible + Hierarchy-of-Truth, single-tenant GO, schedule+notification import, deliver-back-as-files, DAG-from-showrunner).

For the **COMPILE** on-ramp: **with R0 (the goal→manifest contract + capability-survey + the SHARED dry-run validator + compile-time capability-absence + NL-delta refine + the eval-set, ADR-047), the from-scratch / no-existing-team user is SUFFICIENTLY served — the case none of the three import artifacts exercise.** Without R0 that user has **no path** (an English objective and nothing to import dead-ends). The two on-ramps converge on one validator and one runtime, so the import sufficiency above carries forward to a *compiled* team unchanged once it passes the shared dry-run.

---

## 6. THE NORTH-STAR ACCEPTANCE TEST (the guardian's enforceable contract)

Falsifiable "press-GO" assertions across **both on-ramps**. Items 1–16 + O1–O8 are the **IMPORT** on-ramp's contract (bound by the three import use cases); items **C1–C2** are the **COMPILE** on-ramp's contract (bound by the from-scratch / no-existing-team user, equivalence-anchored on EURail). **Each item is enforced by the case(s) that exercise it; no case may regress an item it exercises. Items a case doesn't exercise are not vacuously asserted against it.** Any PR/ADR/design change that regresses a bound item — on either on-ramp — **fails the guardian gate.**

| # | Assertion | Binds |
|---|---|---|
| 1 | An existing `.claude/agents/` dir (or a single skill-orchestrator) imports to a runnable Team Harness with **zero manual OHM authoring** (17/30/23-artifact teams included) | all |
| 2 | Skills/coordinators referenced in frontmatter (`skills:`) are auto-resolved and inlined; no skill is re-authored by hand | all |
| 3 | The inter-member/inter-team DAG (`depends_on`, conditional dispatch, schedules) is **derived from the source** (showrunner / `## Handoff` / `cron.yaml` / skill-spawn graph); the user edits, never hand-wires from blank | all |
| 4 | A member imported with `tools: Read,Grep,Glob,Write` has **no** send/publish/upload/spend capability at runtime, and **no orchestrator/A2A/coordinator path can grant one** | book + any imported team |
| 4b | A human gate (A–G) is a **blocking DAG node**: the run pauses until the author advances it; agents cannot cross it | book |
| 5 | An imported **live-web** researcher performs search+fetch+read immediately, no connector to build first | EURail (any live-web researcher) |
| 6 | An existing stateful Python loader (CLI, cached, backfilled) runs **on a schedule into the org store as-is** — not rewritten as a REST connector | bitcoin; EURail backfill |
| 7 | A local Python package (`bitcoin_gpt.analysis.*`, the EURail merge spine) mounts as a callable tool group; imported agents **compute, not just narrate** | bitcoin; EURail |
| 8 | The user's existing substrate is reused **in place** — git-markdown stays file-native (book); an existing graphify graph is adopted as the blackboard (bitcoin); **no forced migration to a second graph** | book; bitcoin |
| 9 | The product honors the user's precedence (book: `rules > bible > TOC > drafts`, graph derived-and-disposable); it never inverts canonical truth to graph-as-truth | book |
| 10 | Team outputs land in the **source format** — editable `.md`/`production/` in the user's git tree (book), docify+agent-pack (EURail), served surface (bitcoin) | all (form varies) |
| 11 | A solo author presses GO with **zero org/ReBAC/BYOM/gateway setup**; multi-tenant governance is opt-in | all |
| 12 | A scheduled, long-lived, **non-terminating** team runs on crons sharing live state, with recurring-budget accounting — not modeled as re-spawned one-shots | bitcoin; book marketing |
| 13 | GO in **refresh mode** re-verifies a prior run's ledger against a seed and emits a what-changed delta (reproduces EURail's 909-merged) | EURail |
| 14 | Pressing GO on **any multi-member/standing fleet** surfaces model-tier economics + a projected recurring cost **up front**, and applies a cheaper default for routine scheduled scans | bitcoin hardest; any standing fleet |
| 15 | HITL-SLA, cross-org isolation, A2A recursion, mandatory plan-approval, and full trace correlation are **all opt-in** — a single-owner autonomous team is never taxed by machinery it doesn't use | all |
| 16 | A deterministic multi-check quality gate (EURail's report-editor 10-gate; the book QA Lock) runs as a **named evaluator battery**, not "maps onto C1" hand-wave | EURail; book |
| **C1** | A **prose objective with no existing `.claude/agents` dir** compiles to a **runnable, validated Team Harness** (schema-valid OHM v1.1 + `sub_harnesses`) that passes the **SAME** `assemble_team()`/`ImportReport` dry-run as the importer (item 1's validator), and runs through the gateway — **zero manual OHM authoring**, exactly as import | compiler (from-scratch user) |
| **C2** | At compile time **capability-absence holds**: the drafter draws `members[].tools` **only** from the surveyor's catalog; a sub-goal needing an unsurveyed capability yields a **fail-closed gap report (`GO: BLOCKED`), never a hallucinated tool** — and a NL refine (`add_member`/`set_fan_out`/`change_kind`) re-validates through the same gate, preserving the rest. Equivalence-anchored: EURail's objective *in prose* reproduces the 909-record ledger about as well as the *imported* EURail team (the 10-gate oracle) | compiler (from-scratch user); EURail-as-prose equivalence |
| O1–O8 | The operational requirements in §3 each pass their acceptance check | per §3 |

---

## 7. Design deltas (fold into `team-of-agents-capability-design.md`)

**Phase A — TWO co-equal on-ramps:** **A-NEW-0** the Harness Compiler / Planner (R0, ADR-047) as a co-equal top-priority platform capability beside the Importer — the **prose** front door (planner / capability-surveyor / manifest-drafter / reviewer, itself a Team Harness; prose→OHM v1.1 team + `sub_harnesses`; the surveyor's catalog is the sole source for `members[].tools`; NL-refine as a typed delta; compile-and-run default / approval opt-in). **A-NEW-1** the Importer (R1) as the co-equal top-priority **import** front door (frontmatter→member mapping: `model`→tier, `tools`→capability ceiling, `skills`→inlined sub-harness refs, body→subgoal/role; skill-orchestrator + charter adapters). **Both front doors share one validator** (`assemble_team()`/`ImportReport` — the Importer's assembler *extended* with a prose-in path, never duplicated). **A-NEW-2** capability-absence in the OHM v1.1 schema (the `tools` line is an *authoritative ceiling*, not advisory) — enforced for **both** import and compile output. **A-NEW-3** Hierarchy-of-Truth/precedence as an importer-populated manifest field (graph-as-truth becomes a *mode*).
**Phase B:** **B-NEW-1** import-driven DAG assembly (R4) — demote B2/B4 to opt-in. **B-NEW-2** adopt the `## Handoff` convention as B5's envelope source.
**Phase C:** **C-NEW-1** dual substrate (file-native + graph-adopt) — C4 never forces a second graph. **C-NEW-2** library-as-tool-group + merge/VERIFY + the **named 10-gate evaluator battery** (not "maps onto C1"). **C-NEW-3** C5 becomes a real seeded-refresh cross-run lifecycle.
**Phase D:** **D-NEW-1** single-tenant local GO (governance opt-in) — demote D2/D4-SLA/D5-cross-org to opt-in, keep the capability-absence gate + blocking-gate-node + write-scope isolation. **D-NEW-2** standing-team lifecycle. **D-NEW-3** model-tier cost defaults + O2 pre-flight/cap. **D-NEW-4** batteries-included registry (R3). **D-NEW-5** deliver-back modes (R5). **D-NEW-6..** the operational O1/O3–O8 (secrets, partial-failure contract, status surface, edit-running-team, local↔cloud parity, delivery-sink auth, import dry-run).
**Playbooks:** delete every "port almost verbatim" / "register as a tool" / "the bible becomes the blackboard" line — replace with pointers to the importer + adoption primitives + dual-substrate.

---

## 8. ADRs to open (the lock's binding decisions)

The lock binds **both on-ramps**. ADR #0 below is the COMPILE on-ramp (R0); ADRs #1–#8 are the IMPORT on-ramp (R1–R6) + cross-cutting gates. Both converge on the *same* `assemble_team()`/`ImportReport` dry-run validator — one validator, two on-ramps.

0. **ADR-047 — Harness Compiler / Planner: the prose on-ramp** (R0) — **co-equal keystone with #1.** An English objective compiles to a runnable OHM v1.1 Team Harness (planner / capability-surveyor / manifest-drafter / reviewer, itself a Team Harness), passing the **SAME** dry-run validator as the importer, capability-absence-bounded at compile time, NL-refine as a typed structural delta; compile-and-run by default with plan-approval opt-in (per §4); the three-layer eval-set incl. the EURail-as-prose equivalence oracle. *(Status: Proposed 2026-06-27; epic #391 / E10.)*
1. **ADR — Adoption-First: import `.claude/agents`/skills/charters/skill-orchestrator → Team Harness without re-authoring** (R1+R4). **The keystone for the IMPORT on-ramp — highest import priority.** (ADR-034/045.)
2. **ADR — Capability-Absence as a Structural Gate** (the gate primitive + the blocking-gate-node) — tool-omission is a hard ceiling no path can escalate. **Binds both on-ramps** — enforced at import *and* at compile time (#0).
3. **ADR — Tool & Data Adoption Primitives** (R2) — script-as-scheduled-ingestion + library-as-tool-group + MCP/connector adoption, first-class alongside registry connectors.
4. **ADR — Dual Coordination Substrate + Hierarchy-of-Truth Adoption** (R5) — **amends ADR-027 (:Memory) and ADR-022 (ingestion recipes)**: file-native and graph-adopt are peers; user precedence is adopted, not imposed.
5. **ADR — Three Lifecycles: Bounded Run / Standing Team / Seeded Refresh** (R6) — recurring-budget accounting defined.
6. **ADR — Single-Tenant Local GO; Governance Opt-In** (R6a) — the heaviest amendment: **subordinates ADR-006/008/012/030** (org-everywhere, operator separation, RLS) to a trivial-local-identity default in solo mode; governance invariants remain mandatory in served/multi-tenant mode. **Both on-ramps' compiled/imported teams run under this default.**
7. **ADR — Batteries-Included Registry + Operational Contract** (R3 + O1–O8) — pre-registered web battery/connectors/scheduler/sink + secrets, cost pre-flight/cap, partial-failure contract, status surface, edit-loop, local↔cloud parity, delivery-sink, dry-run. **The compiler's capability-survey (#0) plans against this same registry + the seed capability inventory.**
8. **Status/retirement note on `ADR-005 L77`** — track sequential/parallel/conditional; record retired-vs-deferred original primitives. **ADR-047 also fills the un-ratified ADR-005 P1 (upfront planning / decomposition) pillar.**

These ADRs + **both front doors (the Importer AND the Harness Compiler)** + the acceptance test (16 import items + O1–O8 **and** the compiler items C1–C2) are **the lock**. The implementation track is **"R7: the product loop closes"** = team runtime (design Phase A–D, corrected) + **the compiler harness (R0 / ADR-047 / E10) and the adoption/import front door (R1 / E2) as co-equal on-ramps** + batteries — one release, sequenced as epics that each move at least one acceptance item (on either on-ramp) from red to green.
