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
| **2 — the team loop** | 8 team review (roster + validator strip) · 9 NL refine rail · 10 readiness checklist + 409 deep-link · 11 pre-flight & GO · 12 on-ramp doors (**← C-1**) | phase 1 components; DS delta tranche 2 (member-card/stage-rail/op-diff) before inc 8 |
| **3 — standing & substrate** | 13 nav v2 (Teams + Approvals + Members→People) · 14 schedules (org-level now; folds into Team detail when C-1 lands) + home health · 15 artifacts tab + bindings-panel relabel + batch ingest + memories · 16 results/verdict/refresh-delta · 17 delivery sink (**← C-6**) | phases 1–2 |

## Backend-gap Contracts (file NOW; worked in parallel)

| # | What | Blocks | Owner |
| --- | --- | --- | --- |
| **C-1** | On-ramp assembly + team persistence via the gateway (compile-from-prose, import-bundle → ImportReport, draft save/list/version) | Phase 2 inc 12 (the doors); draft persistence in inc 8 | solution-architect |
| **C-2** | USD pricing + run-level cost pre-flight (`cost.usd`, `max_usd_total` enforcement) | Phase 2 inc 11 (USD portion; token caps un-blocked) | solution-architect |
| **C-5** | Team-run list endpoint (org-scoped, state-filterable) | Phase 1 inc 7 | solution-architect |
| **C-6** | Delivery sink write-back (git/webhook/pack targets, creds, overwrite/append semantics — lock O7/R5) | Phase 3 inc 17 | solution-architect |

Everything else in phases 0–3 is unblocked today: 14 of 17 increments need no backend work.

## v1 epics (shipped; journeys remain the per-surface reference)

Tools (`#98`) · Connections (`#103`, G1 shipped) · Recipes (`#109`) · Nav-IA (`#115`) ·
Agents & harness (`#121`, G2 shipped as `/api/v1/agent-bindings`). Residual unbuilt increments
from these epics stay valid and can interleave with phase 3 — never ahead of phases 0–2.

## Serial delivery — one increment at a time (unchanged)

**No parallelization.** One FE agent, one increment, one PR; experience-architect (johnkennII)
reviews on the running app; the CTO reviews craft; GitHub signals are the baton and whoever is
not acting stays idle. Full protocol: `oraclous-frontend/CLAUDE.md` §3.7 + the
experience-architect persona §5.

1. EA **readies one** increment (assign `Jahankohan` + `ready`) → FE's turn; EA idle.
2. FE builds, **opens one PR**, then idles — never picks up a second issue.
3. EA reviews **on the running app** → request changes (baton back) or approve via `johnkennII`
   and merge (CI green + mergeable merges without asking).
4. On merge, EA immediately readies the next. Contract-blocked increments (7 ← C-5, 12 ← C-1,
   17 ← C-6) are never readied until their Contract lands.
