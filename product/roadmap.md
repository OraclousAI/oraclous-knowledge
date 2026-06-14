---
title: "FE migration roadmap — epics, increments, order"
owner: experience-architect
status: living
grounds-in: capability-surface-inventory.md + the per-journey docs in product/journeys/
---

# FE migration roadmap

The legacy-cloned console is migrated to a journey-driven product, **incrementally** — every increment is a
small vertical slice that runs and is testable on the live app (frontend `CLAUDE.md` §3.6). The canonical
design for each epic is its `product/journeys/<epic>.md`; this page is the **order** and the **dependency
map**. Issues are created in `oraclous-frontend` (GitHub), authored by `experience-architect` as the
**johnkennII** identity; backend gaps are Contracts in `oraclous-backend` for `solution-architect`.

## Two backend gaps — file as Contracts NOW (worked in parallel by the backend)
| Gap | What | Blocks | Owner |
| --- | --- | --- | --- |
| **G1** | OAuth-connect bridge: a provider token captured at login → a resolvable broker **tool** credential, via the gateway (no new session) | Connections inc 5 | solution-architect |
| **G2** | Workspace↔harness binding: an ADR + a gateway endpoint to list/attach/detach the agents bound to a workspace | Agents inc 6 | solution-architect |

Filing both now means they can be resolved while the FE works the ~21 unblocked increments.

## Epic order (recommended)

| # | Epic | Increments | Status | Notes |
| --- | --- | --- | --- | --- |
| 0 | **Foundations** | personas (`product/personas/`), this roadmap, the inventory | docs done; personas need Reza/CTO sign-off | informs everything; no FE build |
| 1 | **Tools** | 5 (inc 1 = `#97`, in flight) | started | fully gateway-exposed; no backend dep |
| 2 | **Connections** | 5 (inc 1–4 now; **inc 5 ← G1**) | ready | addresses "stop pasting keys"; inc 1 creates `/app/connections` |
| 3 | **Recipes** | 5 (all now) | ready | addresses the empty Recipes page; no backend dep |
| 4 | **Navigation & IA** | 5 (all now; **inc 2 ← Connections inc 1**) | ready | the structural spine fix; hybrid greenfield-nav + reshape |
| 5 | **Agents & harness** | 6 (inc 1–5 now; **inc 6 ← G2**) | ready | clarity + completeness + the new workspace-binding concept |

**Why this order.** Foundations first (cheap, informs all). Tools is already in flight and fully unblocked.
Connections and Recipes fix the two loudest broken pages with zero backend dependency. Navigation restructures
the spine once Connections exists as a page (inc 2 needs it). Agents & harness is mostly polish on the most
complete surface, with the one genuinely new concept (workspace binding) deferred to its ADR. The two blocked
increments (Connections 5, Agents 6) land when G1/G2 resolve.

## Cross-epic dependencies (do not violate)
- **Nav-IA inc 2** (promote Connections to a nav item) **depends on Connections inc 1** (which creates the
  `/app/connections` page). Build Connections inc 1 before Nav-IA inc 2.
- **Connections inc 5** depends on **G1**. **Agents inc 6** depends on **G2**.
- Within each epic, increments are strictly ordered (each builds on the last) — see the journey doc.

## Per-epic increment index (canonical detail in the journey docs)
- **Tools** (`journeys/tools.md`): 1 detail drawer (`#97`) · 2 register a tool · 3 configure an instance ·
  4 attach a credential · 5 validate/test connection.
- **Connections** (`journeys/connections.md`): 1 first-class page · 2 add any credential type · 3 rename ·
  4 connected-providers panel · 5 **OAuth connect (G1)**.
- **Recipes** (`journeys/recipes.md`): 1 structured detail · 2 start from template · 3 dry-run · 4 save draft ·
  5 run on a workspace.
- **Nav-IA** (`journeys/navigation-ia.md`): 1 grouped spine · 2 promote Connections · 3 Jobs→Runs ·
  4 Ask→Explore · 5 consolidate Admin + retire flat arrays.
- **Agents & harness** (`journeys/agents-harness.md`): 1 separate agents/instances · 2 model picker + key
  readiness · 3 pre-save review · 4 richer runs table · 5 resolve escalated run · 6 **workspace binding (G2)**.

## Issue map (GitHub, created as johnkennII)
Epics (`oraclous-frontend`): Tools **#98** · Connections **#103** · Recipes **#109** · Nav-IA **#115** · Agents & harness **#121**.

| Epic | inc 1 | inc 2 | inc 3 | inc 4 | inc 5 | inc 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Tools | #97 *(in flight)* | #99 | #100 | #101 | #102 | — |
| Connections | #104 | #105 | #106 | #107 | #108 *(blocked G1)* | — |
| Recipes | #110 | #111 | #112 | #113 | #114 | — |
| Nav-IA | #116 | #117 *(← #104)* | #118 | #119 | #120 | — |
| Agents & harness | #122 | #123 | #124 | #125 | #126 | #127 *(blocked G2)* |

Backend Contracts (`oraclous-backend`, for solution-architect): **G1 #339** (OAuth-connect bridge → unblocks #108) · **G2 #340** (workspace↔harness ADR → unblocks #127).

## Serial delivery — one increment at a time (the build ↔ review baton)
**No parallelization.** A single FE agent works one increment at a time; experience-architect (johnkennII) is
the reviewer. The two take turns, **GitHub signals are the baton, and whoever is not acting stays idle.** Full
protocol: `oraclous-frontend/CLAUDE.md` §3.7 (FE side) + the experience-architect persona §5 (reviewer side).

**The pickup signal.** The FE agent builds only an issue **assigned to it (`Jahankohan`) and labelled
`ready`** (CLAUDE.md §0). experience-architect readies an increment by assigning `Jahankohan` + adding
`ready`. The other 24 increments are intentionally **not** `ready` — only one is ever in the agent's queue.

**The turn sequence (strict):**
1. EA **readies one** increment (assign + `ready`) → FE's turn; EA idle.
2. FE builds, **opens one PR**, then **goes idle** — it does NOT pick up another issue.
3. EA **reviews on the running app** → **requests changes** (this is how FE is notified of improvements; baton back to FE, who revises the **same PR** then idles again) **or** **approves via `johnkennII` and merges automatically** — a *confirmed* PR (EA-approved + CI green + mergeable) is merged without asking; there is no merge-confirmation step.
4. **On merge, EA immediately readies the next** increment (assign + `ready`) so the FE never idles waiting. The maintainer tests merged increments live **in parallel** — that is **not** a gate on readying the next. Repeat.

Blocked increments (#108←G1, #127←G2) are never readied until their Contract lands. There is always exactly
one increment in flight; nothing is queued ahead.

## The loop (per increment)
experience-architect (johnkennII) **opens** the issue → **readies** it (assign `Jahankohan` + `ready`) when
its dependency is met → FE agent (`Jahankohan`) builds + opens a PR → experience-architect validates on the
running app + CTO reviews craft → both approve via johnkennII → merge → test live → ready the next. Blocked
increments (#108←G1, #127←G2) stay un-ready until their Contract lands; everything else proceeds in order.
