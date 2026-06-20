# ADR-037 — Flow-Level Evaluation, Named Gate Batteries, and Run-Tree Correlation (E4)

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-21 |
| Approved by | Reza (2026-06-21) — CTO accept per §22; security-architect reviewed via the adversarial design pass |
| Supersedes | None |
| Superseded by | None |
| Driving epic | E4 — Evaluation + named gate batteries + run-tree + progress · issue [#385](https://github.com/OraclousAI/oraclous-backend/issues/385); this ADR is the contract issue [#468](https://github.com/OraclousAI/oraclous-backend/issues/468), which **blocks** the four impl issues #469 (`core/evaluate`), #470 (named battery), #471 (run-tree), #472 (progress/O4) |
| Driving artifact | Team-of-Agents — North-Star Lock & Acceptance Test (§6 items 16, O4; §4 CUT list) |
| Builds on | [ADR-031](adr-031-ohm-v1.1-team-manifest.md) (OHM v1.1 — `orchestration.success_criteria`/`termination.convergence`) · [ADR-002](adr-002-ohm-as-canonical-manifest-format.md) (`$ref` fail-closed) · [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (internal/gateway trust) · ADR-006/ADR-012/[ADR-030](adr-030-realize-postgres-rls-backstop.md) (org-scoping + RLS backstop) · KRS `EvalJudge` (#331/#333) |

## Context

The team runtime ships with **no judge, no scorer, and no success-criteria check anywhere**. A run that returns `"SUCCEEDED"` means only *"the loop returned text with no tool calls"* — there is no verdict on whether the work is correct or complete. Three concrete absences follow, and this ADR fixes the contract for all three at once so the four E4 impl issues build against fixed seams with **no remaining architecture choices**.

1. **No flow-level evaluator.** The only judge in the platform is the KRS `EvalJudge` (#331), and reading it confirms a *clean, reusable* seam wrongly assumed RAGAS-coupled: the only retrieval-specific things are the four fixed metric NAMES + their prompts. The reusable core is provider- and rubric-agnostic — the `EvalJudge` Protocol (`complete_json`/`complete_text`, temperature 0, `response_format=json_object`, the `make_judge(settings)` lifespan factory → typed 422 when no key) and the whole `evaluation_service` orchestration posture (per-request semaphore, eval-slots → typed 429, a whole-evaluation `asyncio.timeout` returning PARTIAL results under the gateway deadline, per-dimension fail-soft, `_verdict_fraction` majority-fail, strict JSON parse/clamp/NaN-reject). What is missing is a *generalization*: the verdict is retrieval-fixed (four fields + `is_grounded`, no `pass`/`failures[]`/`recommended_action`), the request is retrieval-shaped, and the judge lives *inside* knowledge-retriever-service.
2. **No named multi-check gate battery.** Lock §6 item 16 forbids hand-waving a real gate as "maps onto C1." The two concrete targets need *different* reduce semantics: the EURail report-editor **10-gate** is a flat AND-floor (10 hard checks, ANY fail ⇒ BLOCKED, gates 9–10 refresh-only); the book **QA Lock / Gate C** is a severity-precedence floor (`integrity > fact > grammar > engagement` — cannot lock while any CRITICAL remains, lower tiers reported-not-blocking). The OHM invocation surface exists but is inert: `orchestration.success_criteria: str` and `termination.convergence: str|None` are prose that **nothing parses** today. The named-fragment home (`OHMManifest.schemas`, resolved fail-closed via `references.py`) is the proven record-once pattern; `OHMRunIf`/`_eval_run_if` already affords the conditional dispatch the refresh-only gates reuse.
3. **No correlated run-tree, no real progress.** A team run fans out into N child harness executions that are causally **orphaned** — the team-run dispatch and the round-table both **discard `result["id"]`**. The only correlation is the single `engine_jobs.harness_execution_id` soft cross-reference (depth 1). `engine_jobs.progress` is hardcoded (`5`/`100`). So there is no observable causal tree to monitor/replay/audit as one unit, and nothing to monitor a standing team against — the O4 "is my team healthy / did last night run / what did it cost" surface does not exist.

This ADR decides the contract for all three **plus the autonomous-vs-HITL re-dispatch policy boundary** the verdict enables. **E4 produces the verdict + the progress signal; the closed-loop re-dispatch mechanism that consumes them is E8 and is out of scope** — only the policy line is fixed here.

## Decision

### Decision 1 — The `core/evaluate` judge contract (one judge, generalized; #469)

**The judge engine is PROMOTED out of KRS-retrieval coupling into a shared `packages/eval` module** (peer to `packages/ohm`) — the retrieval rubric and the new flow rubric become **two rubrics over one engine** (the literal "Extract" lift-tag). Promoted verbatim: the `EvalJudge` Protocol, `OpenAIEvalJudge`, `make_judge(settings)`, and the entire `evaluation_service` orchestration posture (semaphore, eval-slots 429, deadline→partial, per-dimension fail-soft, `_verdict_fraction`, strict parse/clamp/NaN-reject). KRS's existing `/v1/graph/{graph_id}/evaluate` becomes a **thin caller** of the shared engine with the retrieval rubric — no behaviour change, **no second judge anywhere**.

**`core/evaluate` is a first-party `core/*` capability** (the `KnowledgeRetrieverConnector`/`InternalTool` template): a registered INTERNAL tool, **NO credential**, the executor forwards the caller's verified org identity (`X-Principal-*`/`X-Organisation-Id` gated by `X-Internal-Key`, ADR-018). It wraps a NEW internal `POST /internal/v1/evaluate` **on knowledge-retriever-service** (KRS already hosts the lifespan judge, the eval-slots semaphore, and the `get_principal → bind_org_context → use_organisation_context` chain, so the shared engine is consumed with zero new lifecycle).

**The Verdict shape (fully typed):**
```
Verdict {
  score: float                 # 0.0–1.0, 4dp — weighted mean of computed dimension_scores (weights default-uniform; rubric may override)
  pass: bool                   # PASS iff score >= pass_threshold AND no CRITICAL/AND-floor dimension failed. Fail-closed: ambiguous/partial → pass=false
  dimension_scores: { <name:str>: float }   # one per computed dimension; fail-soft nulls EXCLUDED
  failures: [ { dimension: str, severity: "critical"|"major"|"minor", reason: str, score: float|null } ]   # reason is customer-text-free (§3.7/no-leak)
  recommended_action: "accept" | "revise" | "retry" | "escalate_human" | "reject"   # the E8 re-dispatch HINT
  metrics_computed: [str]      # lifted verbatim from _build_result
  warnings: [str]              # skipped dims / caps / deadline-partial / malformed judge output — lifted verbatim
  evaluated: { target_kind: "run"|"stage"|"member_output", target_ref: str, organisation_id: str }
}
```
The KRS path keeps `EvaluationResponse` (back-compat, `overall` aliases `score`); the flow path emits `Verdict`. The engine computes `score`/`dimension_scores`/`metrics_computed`/`warnings` exactly as `_build_result` today; `pass`/`failures[]`/`recommended_action` are the new additive fields it derives from the rubric.

**The Rubric model (rubric-agnostic config the engine runs):**
```
Rubric {
  dimensions: [ { name: str, prompt: str, weight: float=1.0, threshold: float=0.5,
                  severity: "critical"|"major"|"minor"="major",
                  kind: "llm_judge"|"deterministic" } ]   # llm_judge → one complete_json call; deterministic → a coded check, no LLM
  pass_threshold: float = 0.7
  precedence: [str] = []   # optional explicit AND-floor order; default = severity rank (critical first)
}
```

**How `success_criteria` (prose `str`) becomes a Rubric — two sources, decided here so no OHM schema change is forced:**
1. **Prose path (the solo-author 80%):** a non-`battery:` string is fed as one holistic `llm_judge` dimension (*"how well does this output satisfy: &lt;criteria&gt;"*). `convergence: "evaluator>=N"` is sugar for an anonymous one-dimension rubric at `pass_threshold = N`.
2. **Structured path:** a `battery:<name>` reference (Decision 2) resolves to a pre-declared multi-check Rubric. #469 owns *running an arbitrary Rubric*; #470 owns *declaring the battery*.

**`core/evaluate` grades inline-supplied output** (decided to unblock #469 from #471): the request carries the target's text/structured output **inline** (`evaluated.target_kind` + payload). Fetch-by-ref from the org-scoped run-tree is the #471-dependent enhancement, not a #469 blocker. The judge **does not re-execute anything**. **Self-judging bias** (judge model == author model) is **warned, not gated** (the rubric may pin a distinct `eval_judge_model`).

### Decision 2 — The named-gate-battery contract (declaration + invocation + two floor modes; #470)

A battery is declared as a new named-fragment store and invoked from the two existing string fields by reference — **no new field on `OHMOrchestration`/`OHMTermination`, no breaking change to the prose path.**

- **Declaration — `OHMManifest.batteries: dict[str, OHMGateBattery] = {}`** (a sibling of `schemas`, same `$ref`/record-once discipline, additive, team-only). Resolved at load like `references.py` (**fail-closed**: a `battery:<name>` referencing an undeclared battery aborts the load). No OHM v1.x schema bump beyond this additive block + the `battery:` token.
- **Invocation — a leading `battery:<name>` token selects the structured path; any other string stays prose.** `success_criteria: "battery:report-editor-10gate"`; `termination.convergence: "battery:book-qa-lock"`. The prefix is the *only* thing distinguishing a named battery from a free-form judge — backward compatible; the importer-filled prose `success_criteria` is never mis-routed.

```
OHMGateCheck {
  name: str                                   # unique within the battery; the addressable check id
  kind: "evaluator" | "deterministic"         # evaluator → core/evaluate(rubric,target); deterministic → a coded predicate
  rubric: str | None                          # evaluator: the prose criterion #469's judge grades
  check_ref: str | None                       # deterministic: a registered core/check/<id> predicate
  params: dict = {}                           # e.g. {"min_ratio": 0.333} (EURail citation floor)
  severity: "CRITICAL"|"MAJOR"|"MINOR" = "CRITICAL"   # precedence/AND-floor tier; default CRITICAL = blocking
  applies_when: OHMRunIf | None = None        # REUSE OHMRunIf/_eval_run_if — EURail gates 9–10 refresh-only, fail-closed-skip
}
OHMGateBattery { name: str, description: str="", checks: list[OHMGateCheck], floor: "and"|"precedence" = "and" }
OHMCheckVerdict { name, passed: bool, severity, reason: str, score: float|null, skipped: bool }
OHMBatteryVerdict { passed: bool, check_verdicts: [OHMCheckVerdict], failures: [OHMCheckVerdict],
                    blocking_severity: "CRITICAL"|"MAJOR"|"MINOR"|None, recommended_action: "pass"|"block"|"escalate_human" }
```
- **`floor: "and"` (EURail 10-gate):** PASSES iff EVERY *applicable* check passes; ANY fail ⇒ BLOCKED. (`applies_when` skips refresh-only gates.)
- **`floor: "precedence"` (book QA Lock):** PASSES iff NO CRITICAL check fails; MAJOR/MINOR failures are **reported, non-blocking** while every CRITICAL clears. Tier = severity rank, refined within a tier by `checks[]` order — `integrity`/`fact` = CRITICAL, `grammar`/`engagement` = MAJOR/MINOR encodes `integrity > fact > grammar > engagement`.

**The battery-runner is a pure function in `packages/ohm`** (injected-dispatch like `run_team`): it takes the resolved `OHMGateBattery` + the graded output + an injected `core/evaluate` invoker, runs `deterministic` checks in-process (no LLM) and `evaluator` checks via the judge, and returns `OHMBatteryVerdict`. `core/gate-battery` registers as a `CapabilityKindPlugin` alongside `core/evaluate`. **#470 ships the initial `core/check/<id>` deterministic-predicate set** the 10-gate needs (e.g. `core/check/record-count`, `core/check/citation-coverage`, `core/check/no-disputed`, `core/check/schema-valid`) as a registered, extensible builtin table — adding a predicate is a code change to that table, not an architecture decision. **#470 is Blocked-by #469** for its evaluator-kind checks. **Scope line:** a battery *runs and returns a verdict invocable from the field*; the convergence-ENFORCEMENT loop (stop the team when `passed`) is E8, NOT #470.

### Decision 3 — The run-tree correlation contract (`trace_id` + `parent_execution_id`; #471)

**Reshape the existing `engine_jobs.harness_execution_id` seam into a full causal tree by threading TWO server-minted ids — NOT a new tracing scheme.**
- **`trace_id: UUID`** — the ROOT execution id, **constant across every node** of one team run (root + every sub-harness execution + every board task). The *membership* join key: `WHERE trace_id = :root AND organisation_id = :org`. For a standalone job, `trace_id == harness_execution_id` (a degenerate one-node tree).
- **`parent_execution_id: UUID|None`** — the immediate causal parent (NULL ⇔ root). Gives the tree its *shape*.

`trace_id` and the existing `x-request-id` are **two separate ids, never conflated**: `x-request-id` is request-scoped, client-untrusted, `req_<hex>`-shaped → the ephemeral log/span co-rail (threaded by `oraclous_telemetry`, unchanged). `trace_id` is execution-scoped, server-minted UUID, persisted — the durable tree key.

**Mint/thread.** The ENGINE is authoritative: `TeamRunService._drive` mints ONE root = `trace_id`, persists it on `engine_team_runs.root_execution_id` **before** dispatch; each member dispatch passes `parent_execution_id=<root>` + `trace_id=<root>`, and **the returned `result["id"]` is NO LONGER DISCARDED** — `dispatch` returns `{output, status, execution_id}`, recorded onto `engine_team_runs.child_execution_ids` (`role -> [ids]`, a **list** per role so a fan-out role's parallel instances — the EURail 14-way swarm — are not lost). The harness: `if inbound trace_id is None, set trace_id = execution_id` at the mint line, persisting BOTH new columns **atomically with the row create** (a half-written node would orphan itself).

**New nullable columns (additive Reshape — no NOT NULL backfill; old rows read NULL = legacy single node):** `harness_executions`: `parent_execution_id`, `trace_id` (+ index `(organisation_id, trace_id)`). `engine_jobs`: `trace_id` (+ index). `engine_team_runs`: `root_execution_id`, `child_execution_ids JSONB DEFAULT '[]'`. `engine_roundtables`: `root_execution_id` + per-turn `execution_id` (stop discarding `result["id"]`). `ExecuteHarnessRequest`/`HarnessClient.execute` gain the two fields (in the **body**, first-class run-tree data — not a header).

**Root stability across resume:** the root is minted ONCE at the QUEUED→RUNNING claim and persisted; a resume **reads `root_execution_id` and mints only if NULL** — never re-mints, so a resume never splits the tree.

**Org-isolation invariant (security-marked, fail-closed, STRUCTURAL — no new app check):** every tree query is `WHERE trace_id = :t AND organisation_id = :org`; the inbound `parent_execution_id`/`trace_id` are **NEVER trusted to widen scope** — the harness derives org from the principal ONLY and persists the child under that org. Under the ADR-030 RLS FORCE, a forged cross-org `trace_id` yields zero joinable rows. A tree can never span two orgs **by construction**. #471 carries the load-bearing security test (an org-A request carrying org-B's `trace_id` neither links nor leaks, asserted against the org-scoped repo read). A new `GET /v1/team-runs/{id}/tree` (engine, org-scoped) is **read-only observability** — producing/reading the tree NEVER auto-triggers a re-dispatch.

### Decision 4 — The autonomous-vs-HITL re-dispatch POLICY boundary (the only E8 line fixed here)

E4 **produces** the verdict; it builds no re-dispatch mechanism. The `recommended_action` is the hint, and the severity→action default is pinned here:
- a **CRITICAL** failure → `escalate_human` (book QA-Lock CRITICAL is HITL by design);
- `score < pass_threshold` with no CRITICAL → `revise`/`retry` (`OHMBatteryVerdict → "block"`, autonomous re-task permitted);
- `pass = true` → `accept` (`→ "pass"`); a `reject`-class verdict → HITL.

**The line E8 must honour:** a verdict may trigger **AUTONOMOUS** re-dispatch (in E8) only when **(a)** `pass=false`, **(b)** NO failure is `critical`, AND **(c)** `recommended_action ∈ {revise, retry}`. ANY critical failure, OR `recommended_action ∈ {escalate_human, reject}`, OR any manifest-mutating re-plan → a **HITL gate** (§22 posture). **E4 stamps the classification; E4 does NOT act on it** — no #469–#472 PR may call `enqueue_*`/re-enqueue off a tree read or verdict; reviewers MUST reject such wiring. The mechanism lands in E8.

### Decision 5 — The progress-against-objective signal + O4 light status (#472), and the evaluation wall-clock budget

**Replace the hardcoded `engine_jobs.progress` (`5`/`100`) with a goal-attainment signal** `progress: int 0–100`, computed by the engine and readable mid-run by both the orchestration agent (job/tree read) and a human (status surface). The aggregation is **fixed here** so #472 implements with no further decision:
- `progress = round(100 × attainment)`, where `attainment` is, in priority order: (1) the latest **evaluator partial** — `core/evaluate`/battery aggregate fraction — when a `battery:`/`evaluator>=N` `success_criteria`/`convergence` is declared; else (2) **member-completion** — fraction of declared team members whose node reached a terminal `pass` (from the #471 run-tree); and is **floored by** member-completion so it never reports ahead of the work actually done; plus (3) when `success_criteria` names a **count target** (e.g. "≥600 records"), `min(count/target, 1.0)` is blended in as an additional dimension. Fail-closed: an uncomputable signal holds the last value (never jumps to 100).
- **O4 light status surface** — `GET /v1/team-runs/{id}/status` (engine, **request-path org-scoped**), a one-glance `{ healthy: bool, state, progress, last_run_at, last_outcome, cost: {tokens, usd} }`. `cost` is read from the **existing metering**; the read uses `org_scope` (the request-path binding), **NOT** the cross-org maintenance/owner reader. **No full-trace machinery** — the full run-tree (Decision 3) is opt-in, required only for the EURail 14-way swarm; every other standing team uses this light status.

**Evaluation wall-clock budget (closes the InternalTool-timeout interaction):** `core/evaluate` runs as an `InternalTool` under the executor's hard tool timeout (30s); the judge orchestration deadline (`eval_deadline_seconds`, 25s) sits **UNDER** it and returns **partial results** rather than 504-burning. A battery runs its checks within the caller's tool budget, evaluator checks bounded by the eval-slots semaphore; a check that exceeds its per-check deadline **fails fail-soft** with `reason="timeout"` (never a 500/504). Deterministic checks are in-process (sub-ms). The battery's total budget ≤ the tool timeout.

## Alternatives considered

- **A. A second, flow-specific judge.** Rejected — the KRS judge is already rubric-agnostic except metric names; a second judge duplicates the hardest-won posture (client safety + fail-soft/deadline orchestration) and drifts. Promote to `packages/eval`, KRS as a thin caller = exactly one judge.
- **B. Keep `core/evaluate` inside KRS (no shared package).** Rejected as the *home*, accepted for the *endpoint*: the engine moves to `packages/eval` (no retrieval dependency), but the internal endpoint is hosted in KRS (already has the judge + eval-slots + org-context) rather than over-building a new service.
- **C. Add a structured `success_criteria` object to OHM now.** Rejected for E4 — forces an OHM schema bump (E1's surface), breaks the prose-writing 80% and the importer. The `battery:` token rides the existing `str`; the only new surface is the additive `batteries` store.
- **D. One reduce semantics for all batteries.** Rejected — mis-models the book QA Lock (severity-precedence, not flat-AND). `floor: and|precedence` + per-check `severity` is the minimum expressing both targets.
- **E. Reuse `x-request-id` as the tree key.** Rejected — request-scoped, client-untrusted, not a UUID; collapsing the two makes the tree unjoinable across a resume and trusts a client header for a tenancy-adjacent key.
- **F. A second progress field / parallel tracing scheme / per-member verdict store.** Rejected — Reshape the existing `engine_jobs.progress` and `harness_execution_id`; the run-tree carries the per-member verdict.
- **G. Make the re-dispatch mechanism part of E4.** Rejected — it is the §4 CUT (E8 owns the loop). Only the policy line is fixed here.

## Consequences

**Positive.** A flow has a real verdict for the first time (one judge, hardened once, KRS posture preserved). The two real gates (EURail 10-gate; book QA Lock) are runnable as **named** batteries (item 16). A team run becomes one observable causal tree (the orphaned `result["id"]` captured), with org-isolation **structural** (org-from-principal + RLS FORCE). Zero forced OHM schema bump. The autonomous-vs-HITL line is fixed and stamped into the verdict, so E8 and #470 cannot diverge.

**Security conditions the impl issues MUST carry (from the adversarial design review — each is a DoD line, not advisory):**
- **H1 (#471):** build the tree only from engine-owned rows + fetch child detail over the harness **org-scoped** API — never read `harness_executions` the engine doesn't own.
- **H2 (#469):** `evaluated.organisation_id` is **server-stamped from the principal** (ORG001) — never read from the body (no forging a foreign-org verdict).
- **H3 (#472):** the O4 cost/status read uses **request-path `org_scope`**, NOT the cross-org maintenance/owner reader.
- **H4 (#471):** resume reads the root **under `org_scope`** so a foreign `trace_id` reads NULL (unvalidated thread-through cannot widen scope).
- **H5 (#469):** the internal endpoint reuses the KRS gateway-trust auth chain (X-Internal-Key pinned); the verdict `reason`/`failures[].reason` is a **label, not customer text** (§3.7 / no verbatim manifest/output echo).

**Negative.** The judge engine moves to `packages/eval` (re-point KRS `/evaluate`, re-run its eval tests against the moved seam — mechanical but real, its own review). Inline grading (the first cut) trusts the org-scoped orchestration agent to pass the right output; fetch-by-ref is a later #471-dependent enhancement. Three tables gain nullable columns + two services gain two body fields — migrations are online/additive (NULL = legacy single node), and the harness must write `trace_id` **atomically** with the row create (the sharpest #471 edge). Self-judging bias persists when judge model == author model (warned, not gated). A larger eval surface is now spec the four issues hold to — offset by it being fixed HERE, so #469–#472 implement with no further architecture decisions.

## §4 — Explicit scope CUTs (kept honest with the Lock §4 CUT list)

- **Closed-loop re-dispatch = E8.** E4 produces the verdict + progress; the re-task/replace/re-route mechanism + termination/convergence enforcement live in E8. Only the autonomous-vs-HITL policy line (Decision 4) is fixed here. No E4 code path re-enqueues off a tree/verdict read.
- **Full cross-service distributed-trace = opt-in.** The full run-tree is REQUIRED for the EURail 14-way swarm (the #385 acceptance); every other standing team uses the O4 light status (Decision 5). The heavy machinery is not taxed onto a single-owner team.
- **Required adversarial QA round-table = opt-in.** The required thing for item 16 is the *deterministic named battery*; a mandatory multi-evaluator debate is opt-in.
- **HITL SLA/capacity apparatus, cross-org isolation as a new control, A2A recursion, mandatory plan-approval = opt-in (Lock item 15).** E4 must not tax a single-owner team with any of these.

## See also

- Epic #385 · contract issue #468 · impl issues #469 (`core/evaluate`) / #470 (battery) / #471 (run-tree) / #472 (progress/O4)
- ADR-031 (OHM v1.1) · ADR-018 (edge auth) · ADR-030 (RLS backstop) · KRS `EvalJudge` #331/#333
- `oraclous-backend/docs/team-of-agents-capability-design.md` (§5 Phase C, §11) · the North-Star Lock (§6 items 16/O4, §4 CUTs)
