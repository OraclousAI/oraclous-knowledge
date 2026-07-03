---
title: "FE roadmap — the team-of-agents console (v2)"
owner: experience-architect
status: living
grounds-in: capability-surface-inventory.md (§7) + journeys/team-of-agents-console.md (journey spec v2)
---

# FE roadmap — v2 (the team-of-agents console)

**What changed (2026-07-03).** The v1 roadmap below this section migrated the legacy-cloned console
page-by-page (Tools, Connections, Recipes, Nav-IA, Agents) — those epics are **substantially
shipped** (verify residuals per-issue on the board) and their journeys remain valid supporting
surfaces. Meanwhile the backend shipped the **locked product**: two co-equal on-ramps
(DESCRIBE → compiled team · BRING → imported team), one validator, team runs with gates, budgets,
schedules, artifacts, evaluation (inventory §7). None of it has UI. The active roadmap is now
**journey spec v2** (`journeys/team-of-agents-console.md`), built in four phases.

## Active build order (canonical detail: journey spec v2 §9)

| Phase | Increments | Depends on |
| --- | --- | --- |
| **0 — plumbing** | 1 api-client team namespaces (+batch-ingest/memories) · 2 retire dead legacy client | nothing |
| **1 — Runs & Approvals** | 3 run detail v2 (member grid + banners) · 4 run tree · 5 rerun-failed · 6 approvals + gate advance (with interim paused-run discovery) · 7 runs/approvals lists (**← C-5**) | phase 0; real runs seeded via e2e; DS delta tranche 1 (chips/verdict/cost-row) before inc 3 |
| **2 — the team loop** | 8 team review (roster + validator strip) · 9 NL refine rail · 10 readiness checklist + 409 deep-link · 11 pre-flight & GO · 12 **Describe door** (**← C-1**; Import door **parked** with #523, cloud-first) | phase 1 components; DS delta tranche 2 (member-card/stage-rail/op-diff) before inc 8 |
| **3 — standing & substrate** | 13 nav v2 (Teams + Approvals + Members→People) · 14 schedules (org-level now; folds into Team detail when C-1 lands) + home health · 15 artifacts tab + bindings-panel relabel + batch ingest + memories · 16 results/verdict/refresh-delta · 17 "connect your sinks" (unblocked — ADR-041 sink-tool model; folds in #505) | phases 1–2 |

## Backend-gap Contracts — reconciled 2026-07-03; filed JUST-IN-TIME (Reza)

Cloud-first is ratified (ADR-040 Decision 7; #523). Deliver-back is BUILT (#515/#542/#544,
ADR-041) — the old C-6 is withdrawn. Full reconciliation: journey spec v2 §8.
**No backend work before the FE pipeline reaches the consuming increment** (Reza, 2026-07-03):
C-5 files as Phase 1 nears inc 7; C-1 as Phase 2 nears inc 12; C-2's USD portion only if inc 11
wants dollars. Until then these are a tracked plan, not open tickets.

| # | What | Blocks | Owner |
| --- | --- | --- | --- |
| **C-1 (re-scoped)** | On-ramp ergonomics + draft persistence: discoverable/seeded compiler-team, draft save/list/version, re-import merge (compiler already runs via `POST /v1/engine/team-runs`, ADR-047) | Phase 2 inc 12 (Describe door); draft persistence in inc 8 | solution-architect |
| **C-2 (re-scoped)** | USD-surfacing harness (`cost.usd` + `max_usd_total` enforcement — both hang off the same work); optional run-level pre-flight. Schedule pre-flight BUILT (#603) | Phase 2 inc 11 (USD portion; token caps un-blocked) | solution-architect |
| **C-5** | Team-run list endpoint (org-scoped, state-filterable) | Phase 1 inc 7 | solution-architect |

Everything else in phases 0–3 is unblocked today: **15 of 17 increments need no backend work**
(only inc 7 ← C-5 and inc 12 ← C-1; the Import door is parked by decision, not blocked).

## v1 epics (shipped; journeys remain the per-surface reference)

Tools (`#98`) · Connections (`#103`, G1 shipped) · Recipes (`#109`) · Nav-IA (`#115`) ·
Agents & harness (`#121`, G2 shipped as `/api/v1/agent-bindings`). Residual unbuilt increments
from these epics stay valid and can interleave with phase 3 — never ahead of phases 0–2.

## Delivery — one PR per PHASE (Reza, 2026-07-03; supersedes the per-increment baton here)

**One FE agent, one phase in flight, ONE PR per phase** (one commit per increment inside — the
PR-BUNDLING LAW applied to FE). No per-increment review rounds, no craft-nit iterations, no human
CI babysitting before a phase is shippable; the automated FE invariant checks run machine-side.

1. EA readies a **phase**: opens/assigns its increment issues together (each with its live-app
   test recipe) → FE builds the whole phase, opens **one PR**, then idles.
2. Review is **one pass, two questions**: on the spec's track? and **operating, not a mock** —
   driven on the running console against the real gateway (real endpoints, real runs, zero
   fabricated data). experience-architect approves via `johnkennII`; the CTO's pass folds into
   the same gate.
3. Merge → **Reza tests the shipped phase live** → EA readies the next phase.
4. Contract-gated increments inside a phase (7 ← C-5, 12 ← C-1) trigger their just-in-time
   Contract as the phase readies; the Import door stays parked with #523.
