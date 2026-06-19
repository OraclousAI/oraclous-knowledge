---
title: "R7 (re-planned) — The Product Loop Closes: Team-of-Agents Runtime + Compiler"
---

# R7 (re-planned) — The Product Loop Closes

> **Status:** Planned → Briefed (pending tech-lead sign-off) · **Re-plans** the orphaned original [R7 — Compiler harness and seed manifests](r7-phase-7-compiler-harness-and-seed-manifests.md), which was marked "superseded by R3.5" but **never rebuilt** — the R3.5 pivot re-planned R4/R5/R6 and jumped to security ("R7-SEC" = the re-planned R8 security pass), skipping the compiler entirely. This release restores it, **plus** the team-of-agents runtime the compiler always presumed but that was never separately scoped.
>
> **Authority:** `product/team-of-agents-north-star-lock.md` (THE LOCK) governs scope and acceptance. Capability detail: `oraclous-backend/docs/team-of-agents-capability-design.md`. Walkthroughs: `…/team-of-agents-use-case-playbooks.md`. Enforced by the `use-case-guardian` persona.
>
> **Release-ID note (for tech-lead):** "R7-SEC" already occupies the R7 label for the security track. This product-loop release needs a non-colliding ID (R7-PL, R9, or similar) — flagged as an open naming decision; content is ID-independent.

| Field | Value |
| --- | --- |
| Owner | tech-lead |
| Briefer | solution-architect (with product-planner + the use-case-guardian) |
| Dependencies | R3.5 (services real) ✅ · re-planned R4 (harness-runtime) ✅ · R5 (execution-engine) ✅ · R6 (gateway) ✅ |
| Supersedes | original R7 (compiler-only) — content folded in as Epic E10 |

---

## 1. Goal

After this release, a user **brings the team they already have** (an existing `.claude/agents` directory, skills, charters, or a single skill-orchestrator) **or describes an objective in plain English**, **presses GO**, and it runs — *with no re-authoring, no "but first you must…", no extra requirements.* The product loop closes on **both on-ramps**: **import** an existing team, or **compile** one from a prose objective and refine it in natural language. Every prior iteration failed because the hard parts (import, tool/data adoption, substrate fidelity, deliver-back, turnkey GO) were treated as footnotes; this release makes them first-class, measured by the locked North-Star Acceptance Test against three real use cases.

## 2. Scope

**In scope** (the ten epics, §4): the OHM v1.1 team contract; the adoption-first **importer**; the team **runtime** (orchestrators + barrier + hand-off + aggregator + HITL gate-node); **evaluation** + named gate batteries + run-tree; **tool/data adoption** + batteries-included registry; **dual substrate** + Hierarchy-of-Truth + deliver-back; **single-tenant local GO** + governance opt-in; **lifecycles** (bounded/standing/seeded-refresh) + cost governance; the **operational contract** (O1–O8); the **compiler harness** (describe→team) + seed defaults.

**Out of scope** (opt-in or later, per the lock §4 CUT list): A2A recursion, cross-org/confused-deputy isolation, HITL SLA/capacity apparatus, mandatory plan-approval, full distributed-trace correlation, team budget-pooling for single-tenant — all **opt-in**, never on the minimal path. Security hardening stays in the R7-SEC track.

## 3. Acceptance criteria (release-level)

**The release is done when all 16 items of the North-Star Acceptance Test + O1–O8 (lock §6/§3) are green for all three use cases**, verified by the `use-case-guardian` with run evidence and signed off by Reza per the §22 human gate. Each epic below is a *deliverable* whose acceptance criterion is the lock acceptance item(s) it turns green. "PR merged / CI green" is **not** done; **the real use case running with no headache is done.**

## 4. Epics (E1–E10)

Each epic's first issue is its `[adr]`; code issues are TDD `[tests]`→`[impl]` pairs bundled per the PR-bundling law. "Acc." = lock acceptance items moved red→green.

| Epic | Goal | ADR(s) | Acc. | Deps |
|---|---|---|---|---|
| **E1 — OHM v1.1 Team Manifest + contract** | the schema + data model that lets a team *exist* | Team-Manifest · Capability-Absence · Hierarchy-of-Truth · ADR-005-L77 status | 1,2,3,4,4b,9 (expressibility) | — |
| **E2 — The Importer (Adoption-First) + DAG-from-source + dry-run** | bring `.claude/agents`/skills/charters/skill-orchestrator → runnable team, zero re-authoring | Adoption-First (R1+R4) | 1,2,3,O8 | E1 |
| **E3 — Team runtime** | orchestrators (seq/par/cond) + true fan-in barrier + structured hand-off + aggregator + HITL blocking-gate-node | Coordination-control & media | 4(enforced),4b | E1 |
| **E4 — Evaluation + named gate batteries + run-tree + progress** | quality gates + the watched signal | Flow-level-evaluation | 16,O4 | E3 |
| **E5 — Tool & data adoption + batteries-included registry** | loaders-as-ingestion, library-as-tools, web battery, scheduler, sink, secrets | Tool-&-Data-Adoption (R2) · Batteries+Operational (R3,O1) | 5,6,7,O1 | E1 |
| **E6 — Dual substrate + Hierarchy-of-Truth + deliver-back** | file-native OR graph-adopt; honor the user's truth; return outputs in source format | Dual-Substrate (amends ADR-027/022) | 8,9,10,O7 | E1 |
| **E7 — Single-tenant local GO + governance opt-in** | press GO with zero org/ReBAC/BYOM/gateway; demote the tax to opt-in | Single-Tenant-GO (amends ADR-006/008/012/030) | 11,15,O6 | E1 |
| **E8 — Lifecycles + cost + closed loop** | standing/recurring teams, seeded-refresh, cost pre-flight/cap, re-dispatch, convergence | Three-Lifecycles | 12,13,14,O2 | E3,E4 |
| **E9 — Operational contract** | partial-failure delivery, edit-a-running-team, status, parity, delivery-sink | (folded into E5's Operational ADR) | O3,O5; O4/O6/O7 final | E3,E7 |
| **E10 — Compiler harness (describe→team) + seed defaults + eval-set** | the NL front door (original R7) + its test harness | Compiler-Harness/Planner | the prose on-ramp (complements 1) | E1,E2,E3 |

**Issue lists per epic** are in the appendix (§9); they match the reviewed chat print, plus the **compiler eval-set** issue added to E10 (§7).

## 5. Milestones (M1–M4) — each is a real use case pressing GO

A milestone is reached when its epics are code-done **and** the real use case runs end-to-end with its bound acceptance items green and Reza signs off.

| Milestone | "Presses GO" | Required epics | Why this use case |
|---|---|---|---|
| **M1 — Book** *(primary test bed)* | import 30 agents → write a chapter → gates hold → files land in git | E1+E2+E3+E6+E7 | most **complete working system**; self-contained, file-native, no web/data deps; stresses the hardest trust feature (structural gates) |
| **M2 — EURail** *(objective validator)* | refresh-mode run → reproduce the shipped **909-record ledger** + pass the 10-gate | + E4+E5(web)+E8(refresh) | the only one with a **known-good output to diff against** — objective pass/fail |
| **M3 — bitcoin-gpt** *(stress test)* | standing teams on crons over an adopted graphify graph, cost-bounded | + E5(loaders+library)+E6(graph-adopt)+E8(standing+cost) | **highest coverage**; least complete, so validated **last** |
| **M4 — Describe→Team** | press GO from a prose objective; compiler builds + you refine in NL | + E10 (+E9 hardening) | the second on-ramp; validated by the §7 methodology |

## 6. The working process (how an implementation is finalized)

```
THE LOCK  (16-item acceptance test — the north star)
  └─ ADRs        decide the contract        (solution-architect → CTO accepts)
      └─ EPIC    a coarse capability slice
          └─ ISSUE   one work unit = [tests] PR then [impl] PR (TDD, ADR-010)
              └─ PR      CI-green + non-author review + use-case-guardian check → CTO merges
          └─ [epic code-done when its issues merged]
  └─ MILESTONE   a use case presses GO
      └─ ACCEPTANCE RUN: bring the REAL use case → press GO → verify bound acceptance
                          items (guardian, with run evidence) → Reza GO sign-off (§22)
      └─ [milestone done when the real project runs with no headache]
```

**Two test levels.** *Level 1 (per PR):* unit + integration via testcontainers, CI gates, the guardian's per-PR check that no bound acceptance item regressed and no new "but first you must…" was introduced. *Level 2 (per milestone):* the **acceptance run** — the real use case (the actual `book/.claude/agents/` dir, EURail's real objective, bitcoin's real loaders) is run on the platform and checked against the milestone's bound acceptance items; Reza presses GO and confirms. This is the structural fix to the repeated failure: **a milestone's definition of done is the real use case running, not CI green.**

## 7. Test & validation methodology

**Per-issue:** TDD two-PR (ADR-010), every test mapped to a `pytest` marker, CI `quality`/`tests`/`integration`/`security` gates.

**Per-milestone acceptance run:** documented in §6; the use-case test beds are **book (primary)**, **EURail (objective-diff validator vs the 909-record ledger)**, **bitcoin-gpt (final stress test)**.

**Compiler (E10) — three-layer eval** (because NL→team is non-deterministic generation, not exact-match):
1. **Deterministic plan guardrails** (every generation, exact pass/fail): the emitted manifest schema-validates as OHM v1.1, every member's tools resolve, the DAG is acyclic/runnable, capability-absence holds, a missing capability fails closed with a gap report — i.e. the compiler's output passes the **same dry-run validation as the importer's output (E2)**.
2. **The same end-result acceptance test as the oracle** (the key): give the compiler a use case's objective **in prose**, run the generated team, and check the output against that case's **acceptance items** — identical gate to the import path. The **equivalence test**: the compiler, given EURail's objective in prose, builds a team whose output reproduces the shipped 909-record ledger about as well as the imported team does. Import and compile converge on one gate: *run it — does it achieve the objective?*
3. **A reference objective eval-set + LLM-judge** (quality, the ship-bar): ~15–30 prose objectives, each with a runnable acceptance check + a rubric the flow-level evaluator (C1) scores on plan adequacy (sub-goal coverage, right roles, no missing capability) and on run outcome. **Ship-bar = passes K-of-N reference objectives** ("useful for early adopters," not "perfect for all prose" — the original R7 risk note), and the compiler, being a harness, is iterated without architecture change.

Plus: **refine-loop tests** (apply a known NL edit — "add a fact-checker", "make research parallel", "the editor is human" — assert the *structural delta* in the manifest) and **adversarial tests** (underspecified → asks/defaults not hallucinate; missing capability → fail-closed; gate-smuggling → capability-absence holds).

## 8. ADRs implemented (the lock's 8)

1. Adoption-First importer (R1+R4) — **keystone** · 2. Capability-Absence as a structural gate (+ blocking-gate-node) · 3. Tool & Data Adoption primitives (R2) · 4. Dual coordination substrate + Hierarchy-of-Truth (amends ADR-027/022) · 5. Three lifecycles (R6) · 6. Single-tenant local GO; governance opt-in (amends ADR-006/008/012/030 — **Reza-blessed**) · 7. Batteries-included registry + operational contract (R3 + O1–O8) · 8. ADR-005 L77 status/retirement note.

## Migration source map (build-on seams, not greenfield-by-default)

| Deliverable | Build on (existing seam) | Verdict |
| --- | --- | --- |
| E3 orchestrators/barrier | `execution-engine roundtable_service.drive` (sequential skeleton) + `job_service` | Reshape |
| E3 HITL gate-node | `task_service.py` + HITL claim/complete/approve | Reshape |
| E4 evaluator | KRS `EvalJudge` (#331), generalized to rubrics | Extract |
| E4 run-tree | `engine_jobs.harness_execution_id` link | Reshape |
| E6 graph-adopt / file-native | KGS + KRS + ADR-022 recipes + `memory_client.py` | Reshape |
| E5 connectors/MCP | capability-registry connector/executor framework | Reshape |
| E1/E2 OHM + import | `harness-runtime domain/ohm/manifest.py` | Reshape/Greenfield |
| E10 compiler | original R7 design (Flow-1 Compile) | Greenfield |

## Risks

| Risk | Likelihood | Mitigation |
| --- | --- | --- |
| The importer is the keystone — if it slips, every milestone slips | High | E2 is sequenced first after E1; M1 (book) is the thinnest vertical to prove it fast |
| Single-tenant-GO amendment (ADR #6) weakens tenancy invariants | Medium | Governance is opt-in for solo mode only; **mandatory and unchanged in served/multi-tenant mode**; security-architect co-reviews |
| Compiler produces low-quality teams for novel objectives | High | Ship-bar is K-of-N reference objectives ("useful for early adopters"); compiler is a harness, iterated without architecture change |
| Scope sprawl re-introduces the "extra requirement" failure | Medium | The use-case-guardian BLOCKs any PR that adds a "but first you must…" or regresses a bound acceptance item |

## Dependencies

**Upstream:** R3.5 + re-planned R4/R5/R6 (all ✅). The team-of-agents **runtime gap** (audit `wf_693afa65-500`) is the substance of E1–E4. **Downstream:** served-mode hardening composes with R7-SEC; the compiler is a SOC-2 material input.

## Status / Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 2026-06-19 | Page created — re-plans the orphaned original R7 as the product-loop release; consolidates the epic/milestone/process/test plan that was previously only in session | coordinator (product-planner) | Stop the execution plan living only in chat; provide the canonical input to GitHub issue creation |

---

## 9. Appendix — issue lists per epic

*(As reviewed; each code issue = a `[tests]`→`[impl]` pair. The full per-issue scope is in the session print and will be mirrored into each GitHub issue at creation.)*

- **E1:** `[adr]` OHM v1.1 + 3 gate/precedence ADRs · OHM v1.1 schema · team data model + DAG/topo-resolver · capability-absence enforcement · precedence/Hierarchy-of-Truth field.
- **E2:** `[adr]` Adoption-First · `.claude/agents` parser→Role-Agents · skill resolver/inliner + charter adapter · skill-orchestrator adapter · DAG-from-source · import dry-run (O8).
- **E3:** `[adr]` Coordination-control · the three orchestrators + fan-in barrier · structured hand-off envelope · aggregation/merge reducer · HITL blocking-gate-node · orchestration agent (opt-in).
- **E4:** `[adr]` Flow-evaluation · `core/evaluate` · named multi-check gate battery (10-gate / QA Lock) · run-tree correlation · progress signal + light status.
- **E5:** `[adr]` Tool/data adoption + batteries · script-as-scheduled-ingestion · library-as-tool-group · web-research battery · common connectors + scheduler + sink · secret onboarding (O1).
- **E6:** `[adr]` Dual substrate · file-native blackboard · graph-adopt · Hierarchy-of-Truth enforcement · deliver-back modes + delivery-sink auth (O7).
- **E7:** `[adr]` Single-tenant GO · trivial local identity + opt-in governance · the opt-in demotions · local↔cloud parity (O6).
- **E8:** `[adr]` Three lifecycles · standing/recurring lifecycle · seeded-refresh · cost pre-flight + cap (O2) + model-tier defaults · closed-loop re-dispatch + termination.
- **E9:** partial-failure delivery contract (O3) · edit-a-running-team (O5) · status/parity hardening (O4/O6).
- **E10:** `[adr]` Compiler/planner · the compiler as a Team Harness · NL review/edit refine loop · seed defaults (inventory/policy/catalog/bootstrap) · **compiler eval-set** (reference objectives + judge rubric + the EURail-ledger equivalence test).
