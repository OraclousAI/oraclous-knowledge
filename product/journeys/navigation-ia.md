---
title: "Journey — Navigation & information-architecture restructure"
owner: experience-architect
status: signed
signed-by: experience-architect
surface: nav spine (apps/console/src/nav/index.ts + components/shell/Sidebar.tsx)
grounds-in: capability-surface-inventory.md (the real user-visible object model)
legacy-divergence: the current nav is the legacy graph-RAG product's flat skeleton (Dashboard/Workspaces/Agents/Jobs/Tools/Recipes/Ask/Developer/Members/Billing); this restructures it into the real object model. Hybrid: greenfield the spine, reshape into it, keep all components and pages.
backend-gaps: none
---

# Journey — Navigation & IA restructure

**Why.** The nav is the wrong product's skeleton: a flat undifferentiated list, legacy labels ("Jobs" = runs,
"Ask" = the old second-mind), Connections hidden in Settings, no grouping by what people do. This is the
deeper structural fix the whole effort exists for — done incrementally so the app stays navigable at every
step.

**Proposed new structure (grouped, persona-aware):**
- **Home** — Dashboard
- **Build** — Agents · Tools · Recipes
- **Operate** — Runs (was Jobs) · Workspaces · Connections (promoted out of Settings) · Explore (was Ask)
- **Admin** — Members · Billing · Developer · Settings (owner-gated as today)

A single data-driven grouped definition drives both the desktop sidebar and the mobile drawer; pages route
in unchanged. One source of truth filtered per persona (owner/member/standalone), replacing the three flat
arrays.

## Design constraints
Structure + labels only. Lucide icons already exported; reuse the existing `.shell-sidebar__section-label`
`<h3>` for group headers (non-interactive, not tab stops). Mint stays live-signal-only — do **not** repaint
nav selection mint; keep `aria-current="page"`. Relabels avoid the banned-word list ("Runs" not "Jobs",
"Explore" not "Ask"). AA: every item a real button/link, predictable keyboard order, mobile drawer keeps its
focus trap.

## Increments (small, vertical, each testable on the app)

| # | Increment | Test on the app | Depends |
| --- | --- | --- | --- |
| 1 | **Grouped nav spine** (NavGroup data model + grouped sidebar; same labels/routes) | every item under group headers reaches the same page; group headers not tab stops; mobile drawer focus trap holds | none |
| 2 | **Promote Connections** to a first-class Operate item (`/app/connections`) | Operate shows Connections → the connections manager; Settings shows a "moved" link | inc 1 + **Connections epic inc 1** |
| 3 | Relabel **Jobs → Runs**, keep route, redirect `/app/jobs` | Operate shows Runs → same runs list (heading "Runs"); `/app/jobs` redirects | inc 1 |
| 4 | Relabel **Ask → Explore**, move into Operate, redirect `/app/my-space` | Explore in Operate (no orphan "Personal"); `/app/my-space` redirects | inc 1 |
| 5 | Consolidate **Admin** group + persona hygiene; retire the flat legacy arrays (single grouped source of truth) | owner/member/standalone trees correct; all old routes redirect; `activeNavId` resolves every route | 2,3,4 |

## Increment 1 — build brief (the first issue)

**Goal.** Greenfield the nav data model into ordered groups and render a grouped sidebar — **keeping every
existing label and route** so nothing moves yet; only the structure groups.

**Scope (in).** Introduce a `NavGroup` shape (section header + ordered `NavItem[]`) in `nav/index.ts`;
re-express `NAV_BY_PERSONA` as ordered groups (Home / Build / Operate / Personal / Admin) keeping current
labels+routes (Jobs stays "Jobs"→`/app/jobs`, Ask stays "Ask"→`/app/my-space`). Update `Sidebar.tsx` to
render groups using the existing `.shell-sidebar__section-label` header; keep `.shell-nav-item` + `activeNavId`
unchanged. Preserve the three persona variants, the Workspaces-shortcut section, and the spend strip.

**Scope (out).** No relabels (inc 3/4), no re-homing Connections (inc 2), no route changes/redirects, no
collapsible groups.

**How to test on the app.** Sign in: the sidebar shows the same items under group headers; click every item →
same page as before; active item keeps `aria-current`; Tab moves in group order, headers skipped; mobile
drawer renders grouped + focus-trap holds. No regression across owner/member/standalone; Workspaces shortcut +
spend strip still render; axe-core AA clean.

> **Cross-epic note:** inc 2 (promote Connections) depends on the **Connections epic** having created the
> `/app/connections` page (its increment 1). Sequence Connections inc 1 before Nav-IA inc 2.
