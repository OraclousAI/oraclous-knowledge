# Team-of-Agents — North-Star Lock & Acceptance Test

> **Status:** LOCKED (the requirement, not the implementation) · **Authority basis:** the zero-headache sufficiency-lock review (run `wf_bb701ec2-9e2`, 3 per-use-case stress-tests → convergence synthesis → adversarial verify + completeness critic, corrections applied) on top of the team-of-agents architecture audit (`wf_693afa65-500`) and the R7 reconciliation. · **Enforced by:** the `use-case-guardian` persona/agent — every ADR, design change, and PR is checked against §6 below.
>
> This is the **stable anchor** that the three north-star use cases can never silently drift away from again. It sits above `team-of-agents-capability-design.md` (the capability spec) and `team-of-agents-use-case-playbooks.md` (the walkthroughs): where this file and either of those diverge, **this file wins** and the other is updated.

---

## 0. The one requirement

> **Bring the team you already have, press GO, and it runs — no re-authoring, no "but first you must…", no extra requirements.**

The three north-star use cases are the **acceptance test**, not examples. They all *already exist* as Claude Code agent setups; the product must adopt them, not make the user rebuild them.

| Use case | What the user brings today |
|---|---|
| **EURail assessment** | one `eurail-report` SKILL.md orchestrator + 23 module prompts + a Python merge spine + a 909-record ledger + seeded-refresh mode + a report-editor 10-gate + docify + agent-pack + a KGB backfill |
| **bitcoin-gpt / doefin-gpt** | 17 `.claude/agents` across 4 standing teams + ~30 skills + 25 stateful Python data loaders + a 21-module analysis library + a half-built harness + 2 MCP servers + a graphify world-model graph |
| **book studio** | 30 `.claude/agents` + 7 coordinator skills + 6 team charters + the `bible/` (git-versioned markdown canon) + 7 structural author gates + scheduled cloud-routine marketing |

## 1. Why every prior iteration failed

Each prior round (the original architecture, the R7 plan, and even the first cut of `team-of-agents-capability-design.md`) treated the hard part as a **footnote**: *"the prompts port almost verbatim," "register it as a tool," "the bible becomes the blackboard."* Every one of those phrases hides days-to-weeks of the user's real, working engineering. **All three use cases abandon at the same walls** — and they are not in the runtime that runs a team; they are in **getting the team you already have into the product, and getting its results back out in the form you keep them.** The lock below makes those walls first-class requirements.

---

## 2. The six headache-elimination requirements (R1–R6)

Each is now a **mandatory, first-class requirement**, not an aside. The *binding cases* column is corrected per the adversarial pass — a requirement is real if it blocks **at least one** case; it is not claimed universal where it isn't.

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

**With R1–R6 + the capability-absence gate + O1–O8, the design is NECESSARY and SUFFICIENT for all three. As originally written (without them) it is INSUFFICIENT — it fails every case on step one.** Coverage confirmed: EURail (skill-import, seeded-refresh, web battery, merge/10-gate, docify+pack, vertical-compose-by-reference); bitcoin (agents-importer, loader+library adoption, graph-adopt, standing mode, cost tiers, served surface); book (43-artifact importer, capability-absence + blocking-gate-node, file-native bible + Hierarchy-of-Truth, single-tenant GO, schedule+notification import, deliver-back-as-files, DAG-from-showrunner).

---

## 6. THE NORTH-STAR ACCEPTANCE TEST (the guardian's enforceable contract)

Falsifiable "press-GO" assertions. **Each item is enforced by the case(s) that exercise it; no case may regress an item it exercises. Items a case doesn't exercise are not vacuously asserted against it.** Any PR/ADR/design change that regresses a bound item **fails the guardian gate.**

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
| O1–O8 | The operational requirements in §3 each pass their acceptance check | per §3 |

---

## 7. Design deltas (fold into `team-of-agents-capability-design.md`)

**Phase A:** **A-NEW-1** the Importer (R1) as the top-priority platform capability (frontmatter→member mapping: `model`→tier, `tools`→capability ceiling, `skills`→inlined sub-harness refs, body→subgoal/role; skill-orchestrator + charter adapters). **A-NEW-2** capability-absence in the OHM v1.1 schema (the `tools` line is an *authoritative ceiling*, not advisory). **A-NEW-3** Hierarchy-of-Truth/precedence as an importer-populated manifest field (graph-as-truth becomes a *mode*).
**Phase B:** **B-NEW-1** import-driven DAG assembly (R4) — demote B2/B4 to opt-in. **B-NEW-2** adopt the `## Handoff` convention as B5's envelope source.
**Phase C:** **C-NEW-1** dual substrate (file-native + graph-adopt) — C4 never forces a second graph. **C-NEW-2** library-as-tool-group + merge/VERIFY + the **named 10-gate evaluator battery** (not "maps onto C1"). **C-NEW-3** C5 becomes a real seeded-refresh cross-run lifecycle.
**Phase D:** **D-NEW-1** single-tenant local GO (governance opt-in) — demote D2/D4-SLA/D5-cross-org to opt-in, keep the capability-absence gate + blocking-gate-node + write-scope isolation. **D-NEW-2** standing-team lifecycle. **D-NEW-3** model-tier cost defaults + O2 pre-flight/cap. **D-NEW-4** batteries-included registry (R3). **D-NEW-5** deliver-back modes (R5). **D-NEW-6..** the operational O1/O3–O8 (secrets, partial-failure contract, status surface, edit-running-team, local↔cloud parity, delivery-sink auth, import dry-run).
**Playbooks:** delete every "port almost verbatim" / "register as a tool" / "the bible becomes the blackboard" line — replace with pointers to the importer + adoption primitives + dual-substrate.

---

## 8. ADRs to open (the lock's binding decisions)

1. **ADR — Adoption-First: import `.claude/agents`/skills/charters/skill-orchestrator → Team Harness without re-authoring** (R1+R4). **The keystone — highest priority.**
2. **ADR — Capability-Absence as a Structural Gate** (the gate primitive + the blocking-gate-node) — tool-omission is a hard ceiling no path can escalate.
3. **ADR — Tool & Data Adoption Primitives** (R2) — script-as-scheduled-ingestion + library-as-tool-group + MCP/connector adoption, first-class alongside registry connectors.
4. **ADR — Dual Coordination Substrate + Hierarchy-of-Truth Adoption** (R5) — **amends ADR-027 (:Memory) and ADR-022 (ingestion recipes)**: file-native and graph-adopt are peers; user precedence is adopted, not imposed.
5. **ADR — Three Lifecycles: Bounded Run / Standing Team / Seeded Refresh** (R6) — recurring-budget accounting defined.
6. **ADR — Single-Tenant Local GO; Governance Opt-In** (R6a) — the heaviest amendment: **subordinates ADR-006/008/012/030** (org-everywhere, operator separation, RLS) to a trivial-local-identity default in solo mode; governance invariants remain mandatory in served/multi-tenant mode.
7. **ADR — Batteries-Included Registry + Operational Contract** (R3 + O1–O8) — pre-registered web battery/connectors/scheduler/sink + secrets, cost pre-flight/cap, partial-failure contract, status surface, edit-loop, local↔cloud parity, delivery-sink, dry-run.
8. **Status/retirement note on `ADR-005 L77`** — track sequential/parallel/conditional; record retired-vs-deferred original primitives.

These ADRs + the Importer + the 16-item acceptance test are **the lock**. The implementation track is **"R7: the product loop closes"** = team runtime (design Phase A–D, corrected) + the compiler harness (original R7) + batteries + **the adoption/import front door** — one release, sequenced as epics that each move at least one acceptance item from red to green.
