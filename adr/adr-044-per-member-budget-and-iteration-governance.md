---
title: "ADR-044 — Three-Layer Team Budget Governance (per-agent safety cap · per-run team pool · per-period accrual) — RE-BASELINED to correct the original per-member-budget-surface over-reach (= ADR-031's rejected Alternative C)"
---

# ADR-044 — Three-Layer Team Budget Governance

> **This revision CORRECTS the original ADR-044 over-reach.** The first draft of this ADR designed a
> **per-member BUDGET SURFACE** — a six-field `OHMMemberBudget` block (`max_iterations` / `max_tool_calls`
> / `max_tokens` / `max_wall_seconds` / `max_usd` / `on_exhaustion`) hung off `OHMMember`, "nested under"
> the team pool. That is exactly **ADR-031's explicitly-rejected Alternative C** ("per-member budgets that
> sum to the team total") and it breaks ADR-031's keystone — **one Team Harness = one budget surface**. A
> per-member *budget* is a second governed ceiling; the keystone permits only one. #576 (PRs #582 / #583 /
> #584, **merged to `main`**) correctly shipped the **opposite** thing: a per-agent **SAFETY CAP** — a
> sub-ceiling clamped `<=` the team pool, with docstrings that cite this very ADR-031 conflict. This
> re-baseline replaces the over-reach with the real, founder-confirmed model: **three user-configurable
> budget *layers*, none of them a competing per-member budget surface.** L1 = the per-agent safety cap
> (**SHIPPED on `main`**, #576); L2 = the per-run team pool (the one budget surface, ADR-031 keystone); L3 =
> the per-period accrual window. The original draft also wrongly claimed it tied off **#580** by making
> exhaustion a declared `escalate | degrade` choice — it does not; `on_exhaustion` is **deferred** to a
> follow-up (decision 4).

## Status

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-27 |
| Approved by | Reza Jahankohan |
| Supersedes | None (re-baselines the original ADR-044 draft in place) |
| Superseded by | None |
| Driving artifact | The #440 book-GO end-to-end run (the from-scratch team-of-agents GO) + Reza's 2026-06-27 budget-model confirmation |
| Builds on | [ADR-031](adr-031-ohm-v1.1-team-manifest.md) (team-pooled `OHMBudget` — **one Team Harness = one budget surface**; the keystone this re-baseline now respects) · [ADR-043](adr-043-conductor-imported-teams-and-consciousness.md) (the within-run conductor — the loop a per-agent cap bounds) · [ADR-048](adr-048-three-team-lifecycles.md) / **#585** (the standing-team lifecycle + run-level pooled enforcement this ADR's L2/L3 hand off to) · [ADR-035](adr-035-coordination-control-and-media.md) §1 ("choice is prose, mechanics/budgets are coded") · [ADR-009](adr-009-metering-at-substrate-billing-as-separable.md) (raw-token metering; USD is a read-time estimate, not platform billing) |

## Context

The #440 book-GO e2e — a from-scratch team pressed GO with no pre-seeded data — exposed a budget-governance
gap, and the original ADR-044 mis-corrected it. The right model, confirmed by Reza on 2026-06-27, is
**three user-configurable layers, none hardcoded** — and crucially the per-agent layer is a *safety cap*,
not a *budget surface*.

**Why the original over-reached.** ADR-031 fixed a keystone invariant: a Team Harness has **exactly one
budget surface** — the team-pooled `OHMBudget`, on `main` today as `max_tokens_total` / `max_tool_calls_total`
+ the rest of the pooled-total block (`packages/ohm/src/oraclous_ohm/manifest.py:287-291`) — and ADR-031
Alternative C ("per-member budgets that sum to the team total") was **rejected** precisely because a `fan_out`
over a runtime-resolved list can spawn N members each individually under-budget while the aggregate is
unbounded, so a sum-of-per-member budget is unenforceable at the moment of a dynamic fan-out. The original
ADR-044's six-field `OHMMemberBudget` block *is* that rejected per-member budget surface under a different
name. We discard it.

**What #576 actually shipped (the real L1) — SHIPPED on `main`.** #576 did **not** add a per-member budget;
it added a per-agent **safety sub-ceiling** and wired it correctly under the keystone. **State of record:
#576 (PRs #582 / #583 / #584) is MERGED to `main`** (merge commit `b1d50d57`), so all of the L1 symbols and
their line citations below resolve on the deployed `main` codebase:

- `OHMMember.max_tokens` / `OHMMember.max_tool_calls` (`manifest.py:155-156`, `int | None`, `ge=1`) — a
  member's own ceiling.
- `OHMBudget.max_tokens_per_member` / `OHMBudget.max_tool_calls_per_member` (`manifest.py:295-296`) — a
  **team-wide default** sub-ceiling, with the inline comment (`manifest.py:292-294`) stating: *"team-wide
  per-member SAFETY-CAP defaults. NOT a per-member budget surface (ADR-031's rejected Alternative C) — they
  are per-member sub-ceilings, each clamped `<=` the pooled total above, never a replacement for it."*
- `resolve_member_caps(member, budget)` (`manifest.py:299-327`) — precedence is the member's own value > the
  team-wide `max_*_per_member` default > `None` (keep the policy tier); and when a `budget` is present the
  resolved cap is **clamped `<=` the team-pooled `max_*_total`** (`manifest.py:323-326`,
  `max_tokens = min(max_tokens, budget.max_tokens_total)`), so *no single member can be granted more than the
  whole team's pool.* Its docstring is explicit that the pool's **aggregate** enforcement across members / a
  dynamic fan-out is **separate engine-side work — ADR-031 design D3 — that this function neither adds nor
  changes** (`manifest.py:310-313`).

So L1 is **designed, built, and shipped on `main`**, and it is a safety cap, not a budget. What remains is to
(a) ratify the three-layer model so the picture is whole, (b) point L2 (the per-run pooled aggregate) at its
enforcement issue **#585** without duplicating it, and (c) point L3 (the per-period recurring window) at
**ADR-048 / E8** without duplicating it.

**The dual-control rationale stands.** The agent-framework field is unambiguous: use **both** a per-agent
cap **and** an aggregate per-run cap — one misbehaving agent can exhaust the whole budget even if every
other agent is well-behaved, so you need both a local limit and an aggregate kill-switch
([dual per-agent + global control](https://waxell.ai/blog/ai-agent-token-budget-enforcement);
[hierarchical budget allocation survey, arXiv](https://arxiv.org/pdf/2509.08157)). Anthropic's multi-agent
guidance is the same shape — subagents run in isolated contexts with their own iteration budgets, preventing
unbounded execution ([building effective agents](https://www.anthropic.com/engineering/building-effective-agents)).
The fix is to make the per-agent thing a **cap under** the pool (L1), keep the pool the **one** enforced
budget surface (L2), and add a **recurring window** for standing teams (L3) — not to mint a second
per-member budget surface.

**The user owns the budget.** All three layers are **user-set, none hardcoded**. The system policy tiers
(the hardcoded `POLICY_SETS` catalogue in `harness-runtime-service/.../domain/policy.py`) are only a
**DEFAULT safety ceiling** — default-OFF / overridable — never a hard cap the user cannot raise.

## Decision

**Adopt a three-layer team budget model. Every layer is user-configurable; none is hardcoded. The per-agent
layer (L1) is a SAFETY CAP, not a budget surface; the per-run team pool (L2) is the single budget surface
(ADR-031 keystone); the per-period window (L3) bounds the recurring accrual a standing team incurs across
runs. This ADR ratifies the model and L1's shipped shape; it references — and does not duplicate — L2's
enforcement (#585) and L3's realization (ADR-048 / E8).**

### L1 — Per-agent cap (a SAFETY SUB-CEILING, clamped `<=` the team pool) — SHIPPED on `main` (#576)

**Decision.** Each member has a token / tool-call ceiling so no single agent runs away. It is a safety
sub-ceiling — **not** a per-member budget surface — and is clamped `<=` the team pool, so it respects the
ADR-031 keystone (it can only *tighten*, never escape, the one budget surface).

**Why.** The dual-control "local limit": a cheap researcher member must not be allowed to burn the whole team
pool in one runaway plan-act-observe loop. A pure pooled cap alone is unsafe because a single runaway member
starves the pool before any other member runs.

**User-config surface.** The user sets either a member's own `OHMMember.max_tokens` / `max_tool_calls` or a
team-wide default `OHMBudget.max_tokens_per_member` / `max_tool_calls_per_member` (`manifest.py:155-156` and
`:295-296`); the member's own value overrides the team-wide default.

**Shipped vs to-build.** **SHIPPED on `main` — #576 (PRs #582 / #583 / #584, merge commit `b1d50d57`).** The
per-member safety-cap schema (`max_*_per_member`) and `resolve_member_caps` are on the deployed `main`
codebase. No further design or build work for L1.

**Code seam.** `resolve_member_caps(member, budget)` (`packages/ohm/.../manifest.py:299-327`) resolves the
effective cap with precedence *member-own > team-wide default > policy tier* and applies the
`min(cap, budget.max_*_total)` clamp at `manifest.py:323-326`. The resolved cap rides the per-member dispatch
seam (engine → HRS → `build_envelope` → loop) the capability ceiling already uses.

### L2 — Per-team budget, PER RUN (the team pool — THE one budget surface) — enforcement = #585

**Decision.** The team pool is **the** budget surface (the ADR-031 keystone). For a single team run the
engine keeps a **running tally** of draw-down across the whole fan-out and **HALTS dispatch before the team
total is exceeded** — closing the unbounded-fan-out / "10,000 copies" hole that a per-agent cap alone
(`per-agent × unbounded max_parallel`) cannot.

**Why.** A `fan_out` over a runtime-resolved list can spawn N sub-runs each individually within its L1 cap
while the aggregate is unbounded; the **only** ceiling that is both meaningful and enforceable for a team is
the pooled `max_*_total`. This is the dual-control "aggregate kill-switch", and it is why ADR-031 rejected
the sum-of-per-member shape: the pool is the one enforceable aggregate.

**User-config surface.** `OHMBudget.max_tokens_total` / `max_tool_calls_total` / `max_sub_runs` /
`max_usd_total` / `ttl_seconds` — all user-set on the Team Harness. **The L2 pooled schema is on `main`
today** (`packages/ohm/src/oraclous_ohm/manifest.py:287-291`; `max_tokens_total` / `max_tool_calls_total` at
`:287-288`).

**Shipped vs to-build.** **L2 schema is SHIPPED on `main`; engine-side aggregate enforcement is TO-BUILD —
issue #585.** Today the pool is declared and validated on `main` but not yet drawn-down/halted-on in the
engine (the ADR-031 design D3 "atomic draw-down across concurrent fan-out sub-runs"). **#585 owns this
enforcement; this ADR references it and does not duplicate the design.** USD draw-down uses the shipped
read-time pricing with unpriced-model honesty (a model absent from the rate table is token-gated, never
USD-gated, and never fabricates a price — ADR-009 intact).

**Code seam.** The clamp target already exists: `resolve_member_caps` clamps each L1 cap to
`budget.max_*_total` (`manifest.py:323-326`). The aggregate tally + halt is the **#585** engine work,
settling a breach via the conductor's non-abort path (ADR-043).

### L3 — Per-team budget, PER PERIOD (daily / weekly / monthly accrual window) — realized in E8 (ADR-048)

**Decision.** Spend **accrues across runs within a window and RESETS at the window boundary**; a
standing / recurring team cannot exceed its **daily (or weekly, or monthly) allowance**. The window and the
amount are **both user-configurable** — the user picks the *period* (`daily | weekly | monthly`) **and** the
*amount* (e.g. `$X` or `N` tokens per period).

**Why.** The L2 per-run pool resets every run, so it can never see what a standing team burns over a *sequence*
of scheduled runs. A standing team on a cron needs a ceiling on its *recurring accrual* — the cadence-level
cost a single run's pool is blind to (ADR-048 frames this exact non-overlap: "a pool resets every run; the
fleet's daily burn does not").

**User-config surface.** A schedule-level recurring cap on the standing team: the user sets the **period**
(daily / weekly / monthly) and the **allowance** for that period; the lifecycle accrues against it across
fires and pauses the standing team when the window's allowance is hit, resetting at the boundary. (The
concrete field names land in ADR-048 / E8; this ADR fixes only that the window is user-chosen and the period
is one of daily / weekly / monthly.)

**Shipped vs to-build.** **TO-BUILD — realized in E8, the standing-team lifecycle, under [ADR-048](adr-048-three-team-lifecycles.md)**,
built **on top of** the L2 per-run tally (#585). **This ADR references ADR-048 / E8 and does not duplicate the
lifecycle design.**

**Code seam.** The standing-team lifecycle + schedule-level recurring cap + cost pre-flight in
`execution-engine-service/.../services/schedule_service.py` / `team_run_service.py` (ADR-048 decisions 2 + 4).
ADR-048 explicitly draws the boundary: the run-level pool is owned here-and-#585, the schedule-level recurring
cap is new in ADR-048 — they are deliberately non-overlapping.

### The ADR-031 reconciliation (crisp)

- **L1 is a SAFETY CAP, not a budget surface.** A per-agent cap can only *tighten* what a member may consume;
  it is clamped `<=` the team pool (`manifest.py:323-326`) and can never escape it. It is the analogue of the
  per-member capability ceiling (ADR-032) — a sub-ceiling, not a second governed budget.
- **L2 — the team pool — is THE one budget surface.** Exactly one enforced aggregate ceiling per Team Harness,
  as ADR-031's keystone mandates. L1 nests *under* it; L3 is a *window* over a *sequence* of it. There is
  **no** per-member budget that sums to or escapes the pool.
- **Therefore this no longer contradicts ADR-031.** The discarded over-reach (a per-member budget surface) was
  ADR-031 Alternative C; the shipped-and-ratified model is the dual-control answer ADR-031 invited — one
  pool, per-agent *caps* under it, a periodic *window* over it.

### What ties off where (reference, don't duplicate)

| Layer | Owner | State |
| --- | --- | --- |
| L1 per-agent safety cap | **#576** (`resolve_member_caps`, `manifest.py:299-327`) | **SHIPPED on `main`** (PRs #582 / #583 / #584, merge `b1d50d57`) |
| L2 per-run team-pool enforcement | **#585** | **Schema on `main`; engine-side aggregate tally + halt TO BUILD** (ADR-031 design D3) |
| L3 per-period accrual window | **[ADR-048](adr-048-three-team-lifecycles.md) / E8** | **To build** (standing-team lifecycle, schedule-level recurring cap on the L2 tally) |

### Boundary note — this ADR NARROWS #585 to run-level-only; per-member is re-homed to #576

ADR-048's current text (its `Builds on` line and §1 boundary) phrases **#585** as owning "**per-member AND
run-level pooled** budget enforcement." **This re-baseline narrows that:** the **per-member** layer is L1, a
shipped *safety cap* owned by **#576** (on `main`), and **#585 owns the run-level pooled aggregate
enforcement ONLY**. The two are different things — L1 is a per-agent sub-ceiling resolved in
`resolve_member_caps`; #585 is the engine-side pooled draw-down — and conflating them in #585 mis-states the
work. **ADR-048's "per-member and" phrasing needs the matching trim** (to "run-level pooled") so the two
Proposed ADRs agree on what #585 contains; accept this pair together, or apply that ADR-048 edit at
acceptance. The *substance* (run-level pool owned by #585, per-period cap new in ADR-048) is unchanged and
already consistent with ADR-048's decision text.

### Deferred — `on_exhaustion` (escalate \| degrade) is NOT in this ADR

**The original ADR-044 wrongly claimed it tied off #580** by making the exhaustion action a declared
`escalate | degrade` choice on a per-member budget block. **It does not, and this re-baseline corrects the
record:** there is no `OHMMemberBudget`, so there is no `on_exhaustion` field. **Today the behaviour is
hardcoded-escalate** (the loop's `_escalate` path returns `ESCALATED` with a typed `error_type` and a
resumable checkpoint). **Whether a limit should `escalate` (default) or `degrade` (proceed with best-effort
`last_text`) is DEFERRED to a follow-up issue** and is **not** ratified here. **#580 (degrade-not-crash on
empty / missing retrieval) is NOT tied off by this ADR** — it remains open and is the natural home (with a
sibling exhaustion-policy issue) for that decision.

## Alternatives considered

### A. A per-member budget surface nested under the team pool (the original ADR-044 over-reach)

Hang a six-field `OHMMemberBudget` block off `OHMMember`, "nested under" the pool. **Rejected — this is
ADR-031's already-rejected Alternative C.** A per-member *budget* is a second governed ceiling; ADR-031's
keystone permits exactly one (the team pool). #440 proves the enforceability failure: a dynamic `fan_out`
spawns N members each under their own budget while the aggregate is unbounded, so a per-member budget is
unenforceable at the fan-out moment. The correct shape — which #576 shipped on `main` — is a per-agent
**safety cap** clamped `<=` the pool (L1), not a per-member budget. This re-baseline discards the over-reach.

### B. Per-agent caps only (no pooled aggregate enforcement)

Ship only the L1 per-agent cap and call budgeting done. **Rejected as insufficient** — `per-agent ×
unbounded max_parallel` is unbounded, so an L1-only model still has the "10,000 copies" hole. The pooled
aggregate (L2 / #585) is the only ceiling that bounds a dynamic fan-out; L1 and L2 are dual-control, both
required.

### C. A pooled per-run cap only (no per-agent cap, no period window)

Enforce only the team pool. **Rejected** — one runaway member starves the whole pool before any other member
runs (the dual-control "local limit" gap), and a standing team on a cron has no ceiling on its *recurring*
accrual (the pool resets every run and never sees the cadence burn). All three layers are needed.

### D. A hardcoded policy tier as the hard ceiling (no user budget)

Leave the `POLICY_SETS` catalogue as the imposed ceiling and never expose a user budget. **Rejected** — it
contradicts the platform principle that the **user owns the budget** (configurable, never hardcoded). The
tier is the right *default safety ceiling* (default-OFF / overridable), never the *only* control and never a
cap the user cannot raise.

### E. A prose-configurable budget the orchestration agent reasons over

Let the orchestration agent set per-member/per-team budgets dynamically in prose. **Rejected** — ADR-035 §1
lists budgets as a *coded, non-controller-configurable* mechanic ("the controller cannot grant itself more").
A prose-set budget collapses the "choice is prose, mechanics are coded" invariant — a wrong prose choice could
grant a runaway member more pool. The author / manifest declares the numbers; the controller may only choose
*who acts*, bounded by those coded caps.

## Consequences

### Positive

- **The keystone is respected, not broken.** L1 is a safety cap clamped under the pool; the pool stays the
  single budget surface. This ADR no longer contradicts ADR-031.
- **The model is whole and founder-confirmed.** Three user-set layers — per-agent cap (L1), per-run pool
  (L2, #585), per-period window (L3, ADR-048/E8) — with the user owning every one and the system tier
  demoted to a default safety ceiling.
- **L1 is shipped on `main`.** `resolve_member_caps` (`manifest.py:299-327`) ships the per-agent cap with the
  pool-clamp on the deployed `main` codebase (#576); the safety control is live, no further L1 work.
- **Clean hand-off, no duplication.** L2's enforcement is #585's; L3's realization is ADR-048's. This ADR
  references both and duplicates neither — the boundary ADR-048 already draws (run-level pool vs schedule-level
  recurring cap) is honoured, and the per-member-vs-run-level cut is stated explicitly (#585 = run-level only).
- **The record is corrected.** #580 is explicitly NOT tied off; `on_exhaustion` is deferred — no false claim
  of a closed loop.

### Negative

- **L2 still owes real concurrency work.** The pooled tally must be drawn down atomically across concurrent
  `fan_out` sub-runs and race-safely with the conductor's settle (ADR-031 design D3). That is #585's burden,
  unbuilt today (the schema is on `main`; the enforcement is not).
- **Three layers raise the "why did my agent stop?" surface.** A stop can come from the L1 cap, the L2 pool,
  or the L3 window; the escalation / warning must name **which** layer bound it or debugging is opaque.
- **Exhaustion policy is unresolved.** Until the deferred `escalate | degrade` decision lands, exhaustion is
  hardcoded-escalate; #580's degrade-on-empty case stays open.
- **A paired ADR-048 edit is owed.** ADR-048's "per-member and run-level pooled" #585 phrasing must be trimmed
  to "run-level pooled" to match this re-baseline's cut; accept the two together.

## Implementation notes

- **L1 — SHIPPED on `main` (#576).** `OHMMember.max_tokens` / `max_tool_calls` (`manifest.py:155-156`),
  `OHMBudget.max_tokens_per_member` / `max_tool_calls_per_member` (`manifest.py:295-296`),
  `resolve_member_caps` with the `min(cap, max_*_total)` clamp (`manifest.py:299-327`, clamp at `:323-326`).
  Built by #576 (PRs #582 / #583 / #584, merge `b1d50d57`). No further design or build work.
- **L2 — #585.** Schema on `main` (`OHMBudget` pooled totals, `manifest.py:287-291`). Engine-side TO BUILD:
  accumulate per-member raw token / tool-call / sub-run / USD cost into a per-team-run pooled tally; check
  against `OHMBudget.max_*_total` / `max_sub_runs` / `ttl_seconds` / `max_usd_total` before each dispatch;
  halt-on-breach settles via the conductor non-abort path (ADR-043). USD via the shipped read-time pricing
  with unpriced-model fallback to the token ceiling (ADR-009 intact). #585 owns **run-level pooled enforcement
  only** — do not duplicate the design here, and do not fold per-member (L1/#576) into it.
- **L3 — ADR-048 / E8.** Schedule-level recurring cap with a user-chosen period (daily / weekly / monthly) and
  allowance, accruing across fires on top of the L2 tally and pausing the standing team at the window boundary;
  cadence-aware cost pre-flight. Owned by **ADR-048** (standing-team lifecycle) — do not duplicate.
- **Deferred — `on_exhaustion`.** The `escalate | degrade` policy line is a follow-up issue (the natural home
  for #580's degrade-on-empty case), not this ADR. Today's behaviour is hardcoded-escalate.
- **System tier is a DEFAULT, not a hard cap.** The hardcoded `POLICY_SETS` catalogue
  (`harness-runtime-service/.../domain/policy.py`) is the outermost default safety ceiling — default-OFF /
  overridable — under all three user layers; a forced-tier governance floor (the existing `_force_policy_set`)
  remains the one ceiling a user cannot raise above.

## References

- [ADR-031 — OHM v1.1 Team Manifest](adr-031-ohm-v1.1-team-manifest.md) — the keystone (one Team Harness =
  one budget surface) this re-baseline respects; its **Alternative C** (per-member-that-sums) is the over-reach
  the original ADR-044 committed and this revision discards; its design **D3** (atomic pooled draw-down) is L2 / #585
- [ADR-048 — Three Team Lifecycles](adr-048-three-team-lifecycles.md) / **#585** — L3 (the per-period recurring
  window on the standing-team lifecycle) is realized in E8; ADR-048 owns the run-level-pool vs schedule-level-cap
  boundary this ADR's L2/L3 hand off to. **Paired edit owed:** ADR-048's "#585 owns per-member AND run-level
  pooled" phrasing should be trimmed to "run-level pooled" to match this ADR's cut (per-member = L1 / #576)
- [ADR-043 — Conductor for Cyclic Imported Teams](adr-043-conductor-imported-teams-and-consciousness.md) — the
  within-run conductor a per-agent cap (L1) bounds and the non-abort settle path an L2 breach lands on
- [ADR-035 — Coordination Control & Media](adr-035-coordination-control-and-media.md) — §1 budgets are a coded,
  non-controller-configurable mechanic ("the controller cannot grant itself more")
- [ADR-009 — Metering at Substrate, Billing as Separable](adr-009-metering-at-substrate-billing-as-separable.md)
  — raw-token metering / read-time USD estimate the L2 USD draw-down builds on without becoming platform billing
- Grounding (read by path, on `main` — the deployed codebase): `packages/ohm/src/oraclous_ohm/manifest.py`
  — `OHMMember.max_tokens` / `max_tool_calls` (`:155-156`); `OHMBudget` (`:281`) pooled totals
  `max_tokens_total` / `max_tool_calls_total` (`:287-288`, full pooled block `:287-291`) **and** the
  per-member safety-cap defaults `max_*_per_member` (`:295-296`) with the ADR-031-citing comment (`:292-294`);
  `resolve_member_caps` (`:299-327`, member-own > team-default > policy-tier precedence; pool clamp `:323-326`)
- Frameworks: [Anthropic — building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
  · [Dual per-agent + global control](https://waxell.ai/blog/ai-agent-token-budget-enforcement)
  · [Hierarchical budget allocation survey](https://arxiv.org/pdf/2509.08157)
- Parent issue: oraclous-backend **#440** (the book-GO e2e trigger) · L1 **#576** (SHIPPED on `main`) · L2
  run-level enforcement **#585** · L3 **ADR-048 / E8** · exhaustion policy / **#580** (deferred — NOT tied off
  by this ADR)
- [ADR index](index.md)

## Revision history

| Date | Change |
| --- | --- |
| 2026-06-27 | **RE-BASELINE (Proposed).** Discards the original ADR-044 over-reach (a per-member `OHMMemberBudget` budget surface = ADR-031's rejected Alternative C, breaking the one-budget-surface keystone). Replaces it with the founder-confirmed **three-layer model**: **L1** per-agent **SAFETY CAP** clamped `<=` the team pool — **SHIPPED on `main`** (#576, PRs #582 / #583 / #584, merge `b1d50d57`; `resolve_member_caps`, `manifest.py:299-327`); **L2** per-run **team pool** = the one budget surface (ADR-031 keystone), schema on `main` (`manifest.py:287-291`), running-tally + halt-before-exceeded enforcement **#585** (run-level only), referenced not duplicated; **L3** per-period (daily/weekly/monthly, user-chosen period + amount) **accrual window** that resets at the boundary — realized in **E8 / ADR-048**, referenced not duplicated. All three user-set; the system policy tier is a default-OFF / overridable safety ceiling, never a hard cap. **Corrects the record: `on_exhaustion` (escalate \| degrade) is DEFERRED to a follow-up (today hardcoded-escalate); #580 is NOT tied off; and #585 is narrowed to run-level-only (paired ADR-048 phrasing trim owed).** Pending Reza. |
| 2026-06-27 (superseded) | *Original draft (now replaced above).* Decided a user-configurable per-member `OHMMemberBudget` block nested under the team pool, with `on_exhaustion` claiming to tie off #580. Over-reached into ADR-031's rejected Alternative C; re-baselined. |
