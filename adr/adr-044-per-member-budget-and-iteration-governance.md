---
title: "ADR-044 — User-Configurable Per-Member Budget & Iteration Governance (nested under the team-pooled OHMBudget)"
---

# ADR-044 — User-Configurable Per-Member Budget & Iteration Governance

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-27 |
| Approved by | Pending (Reza / CTO) |
| Supersedes | None |
| Superseded by | None |
| Driving artifact | The #440 book-GO end-to-end run (the from-scratch team-of-agents GO) |
| Builds on | [ADR-031](adr-031-ohm-v1.1-team-manifest.md) (team-pooled `OHMBudget` — one Team Harness = one budget surface) · [ADR-035](adr-035-coordination-control-and-media.md) §1/§5 ("choice is prose, mechanics are coded"; dispatch-time ceiling) · ADR-042 (team-run member isolation / non-abort) · ADR-043 (the conductor + #553 re-route) · [ADR-009](adr-009-metering-at-substrate-billing-as-separable.md) (raw-token metering, pricing separable) |

## Context

The #440 book-GO e2e — a from-scratch team pressed GO with no pre-seeded data — exposed a governance gap between the two budget tiers the platform actually ships. The platform has a real **per-run** enforcement engine and a **per-team** ceiling *schema*, with **nothing in between** and **nothing user-authored per agent**:

1. **Per-run enforcement exists, but is derived from a hardcoded tier — not user-set.** The runtime ceilings are a `PolicyEnvelope` (`harness-runtime-service/.../domain/policy.py:39-52`): `max_iterations`, `max_tool_calls`, `max_wall_time_seconds`, `max_tokens`, plus `gated_bindings` / `tool_ceiling` / `redact_patterns`. The envelope is built from a **named `PolicySet`** drawn from a **hardcoded built-in catalogue** of exactly five tiers (`policy.py:57-101`): `development-default` (200k tokens / 600s / 200 tool-calls), `staging-default` (100k/300s/100), `production-default` (50k/180s/50), `production-strict` (20k/60s/20), `production-federated` (50k/180s/50), with `DEFAULT_POLICY_SET_REF = development-default` (`policy.py:103`). The iteration cap is *derived, never authored*: `max_iterations = min(hard_max_iterations, policy.max_tool_calls + 1)` (`policy.py:212-215`) — a safety backstop bounded by a service hard cap, never a number the user picks per agent. This contradicts the platform principle that **the user brings their own model, budget, and decisions** (configurable, never hardcoded): today a tier is imposed.

2. **The team-pooled budget is in the schema but is DEAD.** `OHMBudget` (`packages/ohm/.../manifest.py:236-247`) is the ADR-031 keystone — `max_tokens_total` / `max_tool_calls_total` / `max_sub_runs` / `max_usd_total` / `ttl_seconds`, explicitly **team-pooled, no per-member budget surface** (ADR-031 Decision keystone + its Alternative-C rejection). A repo-wide grep finds **zero** non-test, non-`manifest.py` references to `max_*_total` / `OHMBudget`: nothing in the harness loop or the engine reads it. The pooled envelope is declared and validated but **enforced nowhere** — the loop's `PolicyEnvelope` and the team `OHMBudget` are two unconnected ceilings, and the *outer* one does not bind at all.

3. **There is no per-member budget surface — only a per-member *capability* ceiling.** `OHMMember` (`manifest.py:122-148`) carries `tools[]` (`manifest.py:134`, "deny-by-default") but **no budget block**. The `tools[]` ceiling, by contrast, already **nests and is enforced**: the engine passes `capability_ceiling=list(member.tools)` per sub-run (`execution-engine-service/.../services/team_run.py:88`) → the harness client puts it in the HTTP body (`.../services/harness_client.py:130`) → HRS `execute(...)` (`harness_execution_service.py:187-199`, `capability_ceiling` at `:194`) → `build_envelope(manifest, policy, external_ceiling=ext_ceiling)` intersects it (`policy.py:209-210`, `ceiling = ceiling & external_ceiling`) → it is enforced fail-closed at the dispatch seam (`tool_use.py:173`). **This is the exact seam a per-member *budget* must ride** — it already threads a per-member cap through the same engine→HRS→envelope→loop path, member-by-member.

4. **USD is estimable but is not a live budget gate.** `billing/rates.py:54-67` prices raw tokens → an estimated USD spend read-time (BYOM estimate; an unpriced model returns `priced=False`/`usd=None`, never a fabricated price — `rates.py:35-42, 62-63`). `OHMBudget.max_usd_total` (`manifest.py:245`) has the data to enforce but **no enforcement site**.

5. **Exhaustion is already best-in-class — but the policy line is not declared.** On every budget breach the loop does **not terminate — it ESCALATES**: `_escalate(...)` (`tool_use.py:138-157`) returns `HarnessStatus.ESCALATED` with a typed `error_type` (`wall_time` `tool_use.py:168/253`, `tool_call_budget` `:216`, `token_budget` `:278`, `iteration_cap` `:316`) and `output=last_text` plus a **resumable `LoopCheckpoint`** for the HITL path. This degrade-to-human-with-resume is strictly richer than the hard-raise that mainstream frameworks default to (see Alternatives). But *which* action a breach takes is hardcoded to escalate; it is not a declared, per-budget choice — and issue **#580** (degrade-not-crash on empty/missing retrieval) is a sibling symptom: a member that should proceed-with-what-it-has currently has no declared **degrade** action to pick.

The #440 book-GO trigger crystallised this: a from-scratch team must let its author **size each agent** (a cheap researcher member should not be allowed to burn the whole team token pool in one runaway loop) **and** keep one aggregate kill-switch over the fan-out. The dual-control consensus across the agent-framework field is explicit: *use BOTH per-agent caps AND a global per-run cap — one misbehaving agent can exhaust the whole budget even if every other agent is well-behaved, so you need both a local limit and an aggregate kill-switch* ([dual per-agent + global control](https://waxell.ai/blog/ai-agent-token-budget-enforcement); [hierarchical budget allocation survey, arXiv](https://arxiv.org/pdf/2509.08157)). Anthropic's multi-agent guidance is the same shape: **subagents run in isolated contexts with their own iteration budgets, preventing unbounded execution**, returning a condensed summary so the orchestrator's context grows slowly ([building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). Token accumulation in fan-out is super-linear — each subagent reply re-enters the orchestrator — which is exactly *why* a pooled cap alone is unsafe (a runaway member starves the pool) and a per-member cap alone is unsafe (`per-member × unbounded fan_out` is unbounded).

This ADR fills the gap that sits precisely **between** the per-run engine and the per-team schema: a **user-configurable, per-member budget**, nested **under** the team-pooled `OHMBudget` as the umbrella ceiling, with the system policy-tier demoted from a hard rule to a **default safety ceiling**, the dead `OHMBudget` finally **wired to enforcement**, and the exhaustion action made a **declared** `escalate | degrade` choice (tying off #580).

## Decision

### 1. A per-member `budget` block on `OHMMember` (the missing layer)

`OHMMember` gains an **optional** `budget` block — a per-member analogue of the per-member `tools[]` ceiling, declarative in the manifest, mirroring the CrewAI per-`Agent` model ([CrewAI Agents docs](https://docs.crewai.com/en/concepts/agents)) made OHM-native:

```yaml
members:
  - role: researcher
    kind: agent
    manifest_ref: "org:<org>/research-agent@3"
    tools: [ web.search, web.fetch ]      # existing capability ceiling (ADR-032), unchanged
    budget:                                # NEW — optional per-member resource cap
      max_iterations:   12                 # plan-act-observe loops for THIS member
      max_tool_calls:   30
      max_tokens:       150_000
      max_wall_seconds: 300
      max_usd:          1.50               # optional; honoured only for a priced model
      on_exhaustion:    escalate           # escalate (default) | degrade
```

Every field is optional; an absent `budget` block means the member inherits (decision 4 — back-compat). The block carries **only** resource ceilings and the exhaustion action — never a capability (capability is `tools[]`); a `budget` can only *tighten* what a member may consume, never widen what it may *do*.

**Schema home:** the block is `OHMMemberBudget` in `packages/ohm/.../manifest.py`, beside `OHMMember`/`OHMBudget`/`OHMTermination`, with `extra="ignore"` and all-optional fields (the house pattern). `ohm-lint` validates non-negative integers and `on_exhaustion ∈ {escalate, degrade}`.

### 2. Enforcement resolves `member-cap → team-cap → system safety-ceiling`, tighter-of always wins

The per-member budget rides the **already-shipped per-member ceiling seam** (Context §3) — **no new enforcement surface in the loop**. The engine resolves the effective per-member envelope as the **tighter-of** three layers, in this order, for *each* dimension independently:

```
effective_cap(dim) = min(
    member.budget.<dim>            if declared,        # the user's per-agent request
    team.budget.<dim_total> share  if pooled-bound,    # the umbrella ceiling (decision 3)
    policy_tier.<dim>              (the DEFAULT)        # the system safety ceiling (decision 5)
)
```

- The per-member values thread engine→HRS exactly as `capability_ceiling` does today: a `member_budget` param on `make_harness_dispatch` (`team_run.py:59-69`) → the harness-client body (`harness_client.py:130` sibling) → HRS `execute(..., member_budget=…)` (`harness_execution_service.py:187-199`, beside `capability_ceiling` at `:194`).
- HRS folds them into the `PolicyEnvelope` at exactly one place — `build_envelope` (`policy.py:185-224`) gains a `member_budget` arg and applies the **same `min()`-intersection** the derived iteration cap already uses (`policy.py:212-215`) and the `external_ceiling` set-intersection uses (`policy.py:209-210`). `max_iterations` becomes `min(hard_max_iterations, member.max_iterations or (policy.max_tool_calls + 1))`; `max_tokens` / `max_tool_calls` / `max_wall_time_seconds` become `min(policy.<dim>, member.budget.<dim>)` when the member declares one.
- **The enforcement sites do not change.** The existing breach checks fire unchanged on the now-tighter envelope: wall-time (`tool_use.py:168/253`), tool-call budget (`:216`), token budget (`:278`), iteration cap (`:316`). A per-member cap is enforced by making the envelope smaller, not by adding a code path.

A member value can therefore **only narrow** — `min()` guarantees a member's request is clamped by the team ceiling and the system default, never the reverse. This is the fail-closed, least-privilege posture ADR-035 §1 names ("the controller cannot grant itself more"): a per-member *budget*, like a per-member *ceiling*, can only tighten the governed envelope.

### 3. The team-pooled `OHMBudget` becomes a live, enforced kill-switch (wire the dead schema)

`OHMBudget.max_*_total` (`manifest.py:242-246`) is promoted from dead schema to the **aggregate draw-down ceiling** over the whole fan-out — the dual-control "global kill-switch". Enforcement is **engine-side**, at the point the engine already accumulates per-member cost:

- The team-run dispatch already surfaces each member's raw token cost via `on_cost(total_tokens)` (`team_run.py:76-77`, called per sub-run) and each child execution id via `on_child` (`team_run.py:75`). The engine maintains a **pooled running total** (`tokens`, `tool_calls`, `sub_runs`, `usd`, `started_at`) per team run, drawn down **atomically** as each member settles (the ADR-031 Consequences "D3 atomic draw-down" the keystone flagged).
- Before dispatching the next member (or the next `fan_out` instance), the engine checks the pooled total against `OHMBudget.max_*_total` / `max_sub_runs` / `ttl_seconds`; a breach **halts further dispatch** and settles the team run via the conductor's non-abort path (ADR-042/043) — it does not silently overspend.
- `max_usd_total` is enforced with the shipped pricing: `rates.price(model_binding, in, out)` (`rates.py:54`) converts each member's tokens to USD and draws down the pooled `usd`. **Unpriced-model honesty is preserved** — a model absent from `RATES` returns `priced=False` (`rates.py:62-63`); an unpriced member cannot be USD-gated, so the engine **falls back to the token ceiling** for that member and never fabricates a price (ADR-009 intact: the substrate still records raw tokens only; USD is a read-time estimate, not platform billing).

This makes the keystone real rather than aspirational: **one Team Harness = one enforced pooled ceiling**, and a `fan_out` of N sub-runs draws down **one** pooled total, so `per-member-cap × unbounded max_parallel` is still bounded by `max_*_total`. The per-member caps (decision 1) nest *under* this — they do **not** replace it (resolving ADR-031 Alternative-C cleanly: per-member is a floor on safety, the pool stays the only enforceable aggregate ceiling).

### 4. Back-compat — no per-member budget ⇒ inherit (zero migration)

The change is **additive and inheriting**, the same posture ADR-031 took for the team blocks:

- A member with **no `budget` block** inherits: its effective envelope is `min(team-pool share, system default tier)` exactly as decision 2 computes with the member layer absent. Every shipped v1.0 and v1.1 manifest runs **unchanged**.
- A team with **no `OHMBudget`** has no pooled kill-switch bound; per-member caps (if any) still apply, falling back to the system default tier. (A team with neither is exactly today's behaviour — the hardcoded tier.)
- A single-agent (non-team) harness has **one implicit member** whose budget is its own manifest; `member_budget` is `None`, `build_envelope` behaves precisely as today (`policy.py:212-215` unchanged path). The single-agent spine is not touched.

### 5. The system policy tier becomes a DEFAULT safety ceiling, not a hard rule

The hardcoded `POLICY_SETS` catalogue (`policy.py:57-101`) stops being the *imposed* ceiling and becomes the **outermost default** in the decision-2 `min()`. The user's per-member (and per-team) values are the *request*; the org's resolved policy tier is the *ceiling*. The resolution rule replaces "hardcoded tier wins" with **"tighter-of(user request, team pool, system tier) wins"** — the org-scoped, bring-your-own-budget model no mainstream framework offers (every surveyed framework is author-set with only an implicit framework default, never a user value clamped by an enforced org ceiling). The tier still **binds as the safety floor**: a user can only tighten below it, never widen above it (least-privilege, fail-closed). A deployment may still *force* a tier (the existing `_force_policy_set` governance floor, `harness_execution_service.py:212`) — a forced tier is the hard ceiling the user's value is clamped under.

### 6. Exhaustion is a declared `escalate | degrade` choice (ties off #580)

`on_exhaustion` makes the breach action a **per-budget declared choice**, never prose-picked (it is a coded mechanic per ADR-035 §1 — the controller cannot choose to ignore a budget, only the author/manifest declares the *action*):

- **`escalate` (default)** — the shipped behaviour: `_escalate(...)` (`tool_use.py:138-157`) → `HarnessStatus.ESCALATED` + typed `error_type` + resumable `LoopCheckpoint`. The team conductor (ADR-043) routes it to HITL / re-plan. Unchanged.
- **`degrade`** — return the member's **best-effort `last_text`** as a `SUCCEEDED`-with-warning result rather than escalating: the loop already carries `output=last_text` on the escalation result (`tool_use.py:148-149`), so degrade returns that text with a `budget_degraded` warning instead of pausing the run. This is the LangChain `early_stopping_method="generate"` analogue ([early_stopping_method ref](https://reference.langchain.com/python/langchain-classic/agents/agent/AgentExecutor/early_stopping_method)) and the direct fix for **#580**: a member that runs out (or finds nothing) **proceeds with what it has** rather than hard-failing and cascade-blocking the team.
- **Never a silent `terminate`.** There is deliberately no "kill the member with no output" option — a budget breach either escalates (default) or degrades to best-effort; it never drops work on the floor. This keeps Oraclous's exhaustion model strictly richer than every framework's hard-raise (OpenAI `MaxTurnsExceeded`, LangGraph `GraphRecursionError`).

The **pooled** `OHMBudget` breach (decision 3) is always a hard team-level halt (the kill-switch), independent of any member's `on_exhaustion` — `on_exhaustion` governs only the *member-local* breach.

## Alternatives considered

### A. Per-member budgets that sum to the team total (no pooled enforcement)

Give each member its own budget and let the team total be their sum, dropping the pooled `OHMBudget` enforcement. **Rejected** — this is ADR-031's already-rejected Alternative C, and #440 proves why: a `fan_out` over a runtime-resolved list can spawn N members each individually under-budget while the aggregate is unbounded (`per-member × max_parallel` with a dynamic `over`), so "sum of per-member" is unenforceable at the moment of a dynamic fan-out. The pooled `max_*_total` is the only ceiling both meaningful and enforceable for a team. This ADR keeps the pool as the umbrella **and** adds per-member caps *under* it — the dual-control answer, not the sum answer.

### B. Keep the hardcoded policy tier as the hard rule; no user-set per-member budget

Leave `POLICY_SETS` as the imposed ceiling and never expose a user budget. **Rejected** — it directly contradicts the platform principle that the user brings their own budget (configurable, never hardcoded). It also leaves the #440 author unable to size a cheap researcher away from an expensive synthesiser; every agent gets the same tier regardless of its job. The tier is the right *safety floor* (decision 5) but the wrong *only* control.

### C. A per-member iteration/turn cap only (the mainstream-framework shape)

Adopt only a per-agent iteration cap (CrewAI `max_iter` 20, LangChain `max_iterations` 15, OpenAI `max_turns` 10, LangGraph `recursion_limit` 25) and nothing else. **Rejected as insufficient** — every one of those frameworks explicitly admits an iteration/RPM cap **does not bound token cost**: a single long-context call can cost 50× a short one, so an agent stays under its iteration cap while burning the budget ([CrewAI per-role budget overruns](https://dev.to/awxglobal/preventing-crewai-budget-overruns-hard-limits-per-agent-role-3njp)). An iteration cap is a *loop-breaker*, not a *spend* control. Oraclous already has the token/USD data (`rates.py`, raw metering); a budget that is iteration-only would throw that away. We adopt the iteration cap **as one dimension among token/tool-call/wall-time/USD**, not as the whole budget.

### D. A prose-configurable budget the orchestration agent reasons over

Let the Orchestration Agent (ADR-035) decide per-member budgets dynamically in prose. **Rejected** — ADR-035 §1 lists budgets explicitly as a *coded, non-controller-configurable* mechanic ("the controller cannot grant itself more"). A prose-set budget collapses the "choice is prose, mechanics are coded" invariant: a wrong prose choice could grant a runaway member more pool. The author/manifest declares budgets; the controller may only choose *who acts*, bounded by those coded caps. (Dynamic surplus/deficit reallocation — the "traded-commodity" advanced shape in the [hierarchical allocation survey](https://arxiv.org/pdf/2509.08157) — is a possible *later* engine feature, but it must remain a coded draw-down against the pool, never a prose grant.)

### E. Hard-terminate on exhaustion (the OpenAI/LangGraph default)

Make a budget breach raise and kill the member with no output. **Rejected** — it is strictly worse than the shipped `_escalate` (resumable, carries `last_text`) and it directly causes the #580 cascade-failure: a member that hard-errors on empty data blocks the whole team. `escalate` (resume) and `degrade` (best-effort) cover the real cases; silent terminate drops work and is never offered.

## Consequences

### Positive

- **The middle tier finally exists.** A team author can size each agent (a cheap researcher capped tight, an expensive synthesiser given headroom) while one pooled kill-switch bounds the whole fan-out — the dual-control best practice, made structural. The #440 from-scratch-team case becomes governable per-agent.
- **The dead `OHMBudget` becomes load-bearing.** `max_*_total` / `max_sub_runs` / `ttl_seconds` / `max_usd_total` go from validated-but-ignored to an enforced aggregate ceiling, realising the ADR-031 keystone ("one Team Harness = one governed run") rather than asserting it.
- **Zero new enforcement surface in the loop.** Per-member budgets ride the *existing* per-member `tools[]` seam (engine→HRS→`build_envelope`→loop); the breach checks fire unchanged on a tighter envelope. Reshape, not rebuild — small PRs, low regression risk on the shipped single-agent spine.
- **Bring-your-own-budget, org-clamped.** The user value is the request; the org tier is the enforced ceiling; `min()` makes a user value only ever tighten. No mainstream framework offers this — it is the Oraclous edge (org-scoped, least-privilege, fail-closed).
- **USD becomes a first-class budget** (not just an estimate), with unpriced-model honesty preserved — a differentiator that fits BYOM, gated off the already-shipped `rates.price`.
- **#580 closes on the policy line.** A member can declare `on_exhaustion: degrade` to proceed-with-what-it-has instead of cascade-failing on empty data, and escalate-not-terminate stays the default.

### Negative

- **Pooled draw-down adds engine-side concurrency.** The pooled total must be decremented atomically across concurrent `fan_out` sub-runs and race-safely with the conductor's CAS settle (a cancelled/timed-out branch settling concurrently must not corrupt the pool) — the D3 concern ADR-031 flagged, now load-bearing. This is real concurrency work in the engine.
- **Three resolution layers raise the "why did my agent stop?" surface.** A member can now be capped by its own budget, the team pool, *or* the system tier; the escalation/warning message must name **which** layer bound it (the typed `error_type` plus the resolved-from layer), or debugging a stop is opaque.
- **USD enforcement inherits estimate drift.** `max_usd` gates on `rates.py` list prices that drift and may not match a BYOM user's tier; a member can over/under-spend the *real* dollars relative to the gate. The token cap remains the precise control; USD is the convenient-but-approximate one (and is skipped, not faked, for unpriced models).
- **One more optional block to author.** `OHMMember.budget` grows the manifest surface; the importer (ADR-034) and `ohm-lint` must handle it. Mitigated by full inheritance (decision 4) — hand-authoring a budget is opt-in, the absent case is unchanged.

## Implementation notes

- **Schema:** `OHMMemberBudget` in `packages/ohm/.../manifest.py` (beside `OHMBudget` at `manifest.py:236`, `OHMMember` at `:122`); add optional `budget: OHMMemberBudget | None = None` to `OHMMember`; `ohm-lint` validates non-negative ints + `on_exhaustion` enum.
- **Resolution (`min()`-intersection):** extend `build_envelope` (`policy.py:185-224`) with a `member_budget` arg applied via `min()` exactly as the derived iteration cap (`policy.py:212-215`) and `external_ceiling` (`policy.py:209-210`) already do. The breach sites in `tool_use.py` (`:168/253`, `:216`, `:278`, `:316`) are **unchanged**.
- **Plumbing (mirror the `capability_ceiling` path):** `make_harness_dispatch` (`team_run.py:59`) gains a per-member `member_budget`; thread it through the harness client body (`harness_client.py:108-130`) and HRS `execute(...)` (`harness_execution_service.py:187-199`, beside `capability_ceiling` `:194`).
- **Pooled enforcement (engine-side):** accumulate `on_cost`/`on_child` (`team_run.py:75-77`) into a per-team-run pooled total; check against `OHMBudget.max_*_total`/`max_sub_runs`/`ttl_seconds` before each dispatch; USD via `rates.price` (`rates.py:54`) with `priced=False` → fall back to the token cap. Halt-on-breach settles via the conductor non-abort path (ADR-042/043).
- **Exhaustion action:** `on_exhaustion` selects between the shipped `_escalate` (`tool_use.py:138`) and a new `degrade` return that surfaces `last_text` (already on the escalation result, `:148-149`) as `SUCCEEDED`-with-`budget_degraded`-warning. Wire `degrade` to satisfy #580.
- **Out of scope (later, gated):** dynamic surplus/deficit reallocation across members ("traded-commodity"); a policy *service* replacing the hardcoded `POLICY_SETS` catalogue (this ADR demotes the catalogue to a default but does not move it out of code); per-member USD reconciliation against real provider invoices.
- **ADR-042 / ADR-043 are referenced by number from the #440 e2e and #580 (member isolation / non-abort; the conductor + #553 re-route); their files are not yet written in `oraclous-knowledge/adr/` (highest present is ADR-039). The pooled-breach halt and the degrade path land on whatever non-abort settle path those ADRs ratify — confirm their final numbers/seams when authored before merging this ADR's references.**

## References

- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the team-pooled `OHMBudget` keystone (one Team Harness = one budget surface) this ADR wires to enforcement and nests per-member caps under; its Alternative-C rejection (no per-member-that-sums) this ADR honours by nesting, not summing
- [ADR-035 — Coordination Control & Media](adr-035-coordination-control-and-media.md) — §1 budgets are a coded, non-controller-configurable mechanic ("the controller cannot grant itself more"); §5 the dispatch-time per-member ceiling whose engine→HRS→envelope seam the per-member budget reuses
- ADR-042 — team-run member isolation / non-abort (referenced from #440 + #580; file pending — confirm number)
- ADR-043 — the conductor + #553 recalibration / re-route (the non-abort settle path a pooled breach lands on; file pending — confirm number)
- [ADR-009 — Metering at Substrate, Billing as Separable](adr-009-metering-at-substrate-billing-as-separable.md) — raw-token metering / read-time USD estimate the `max_usd` gate builds on without becoming platform billing
- Grounding (read, by path): `harness-runtime-service/.../domain/policy.py:39-52,57-101,103,185-224,209-215` (`PolicySet`/`PolicyEnvelope`, hardcoded tiers, derived iteration cap, `build_envelope` intersection); `.../domain/loop/tool_use.py:138-157,168,216,253,278,316` (`_escalate` + the breach sites); `packages/ohm/.../manifest.py:122-148,236-247` (`OHMMember.tools` at `:134`, `OHMBudget`, no per-member budget); `.../domain/billing/rates.py:35-42,54-67` (`price` + unpriced honesty); `execution-engine-service/.../services/team_run.py:59-99` (per-member dispatch, `capability_ceiling=list(member.tools)` `:88`, `on_cost`/`on_child` `:75-77`) + `.../services/harness_client.py:108-147` (HTTP body) + `harness-runtime-service/.../services/harness_execution_service.py:187-199,212,225-235` (`execute` signature, `_force_policy_set`, ceiling plumbing)
- Frameworks: [CrewAI Agents](https://docs.crewai.com/en/concepts/agents) · [CrewAI per-role budgets](https://dev.to/awxglobal/preventing-crewai-budget-overruns-hard-limits-per-agent-role-3njp) · [LangChain max_iterations](https://reference.langchain.com/python/langchain-classic/agents/agent/AgentExecutor/max_iterations) / [early_stopping_method](https://reference.langchain.com/python/langchain-classic/agents/agent/AgentExecutor/early_stopping_method) · [LangGraph recursion_limit](https://docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT) · [AutoGen max_consecutive_auto_reply](https://microsoft.github.io/autogen/0.2/docs/reference/agentchat/conversable_agent/) · [OpenAI Agents SDK max_turns](https://openai.github.io/openai-agents-python/running_agents/) · [Temporal activity timeouts](https://temporal.io/blog/activity-timeouts) · [Anthropic — building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [Dual per-agent + global control](https://waxell.ai/blog/ai-agent-token-budget-enforcement) · [Hierarchical budget allocation survey](https://arxiv.org/pdf/2509.08157)
- Parent issue: oraclous-backend **#440** (the book-GO e2e trigger) · sibling **#580** (degrade-not-crash on empty/missing retrieval)
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-27 | Initial draft (Proposed). Decides user-configurable per-member budgets (`OHMMember.budget`: `max_iterations`/`max_tool_calls`/`max_tokens`/`max_wall_seconds`/`max_usd`/`on_exhaustion`) nested under the team-pooled `OHMBudget`; enforcement resolves member-cap → team-cap → system-tier as tighter-of(`min()`), riding the existing per-member ceiling seam with no new loop surface; wires the dead `OHMBudget` to engine-side pooled draw-down (the global kill-switch, USD via `rates.price` with unpriced fallback); demotes the hardcoded `POLICY_SETS` tier from hard rule to default safety ceiling; makes exhaustion a declared `escalate (default) | degrade` choice tying off #580; back-compat by inheritance (no budget ⇒ inherit, single-agent path untouched). Pending Reza/CTO. |
