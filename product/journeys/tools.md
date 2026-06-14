---
title: "Journey — Tools: from a flat catalogue to configurable, usable tools"
owner: experience-architect
status: signed
signed-by: experience-architect
surface: Tools (apps/console/src/pages/ToolsPage.tsx + new detail/config surfaces)
grounds-in: capability-surface-inventory.md §1 (capability-registry tools/instances)
legacy-divergence: the legacy app had a flat tool list; the real backend models register → instance → configure-credentials → validate → execute. We expose that lifecycle, which the legacy clone never did.
---

# Journey — Tools

**Persona.** An org admin / builder who wants to actually *use* a tool: see what it does, what it needs,
set it up with their credentials, confirm it works, and add new tools.

**Today (the problem).** [ToolsPage.tsx](../../oraclous-frontend/apps/console/src/pages/ToolsPage.tsx) is a
browse-only catalogue: tiles are inert (`cursor: 'default'`), the only write action is admin MCP-import.
The backend already supports the full lifecycle through the gateway (inventory §1) — it's a frontend
exposure gap, no backend work needed.

**Why Tools is the first journey.** Every capability it needs is gateway-exposed **today** (no backend
dependency, no Contract), so each increment is immediately testable on the running app.

## Design constraints (design system)
- Mint `#10D88A` only for live signal (e.g. a healthy/connected dot) — never a button fill.
- No emoji; Lucide icons only. Sentence case; second-person bare imperative ("Configure this tool", not "Let's…").
- Banned words apply to UI copy (incl. "journey" in product copy). Numerals as digits. WCAG AA from the start.
- Compose from existing design-system components (drawer/sheet, card, button, field, status-pill) — no new tokens; any gap is a `reground-ds` delta.

## Increments (small, vertical, each testable on the app)

Each is one GitHub issue → one PR → run-on-app test. Ordered so the app is usable after every step.

| # | Increment | Gateway capability | Test on the app |
| --- | --- | --- | --- |
| **1** | **Tool detail view** — clicking a tool tile opens a detail panel (drawer) showing its description, category, capabilities, **credential requirements**, and docs link | renders from the existing `GET /api/v1/tools` list data (no new endpoint) | Open Tools, click a tile → a detail drawer opens with the tool's info incl. what credentials it needs; Esc/close works; keyboard-reachable |
| 2 | **Register a tool** — an "Add a tool" action (admin) that registers a tool descriptor | `POST /api/v1/tools` | Add a tool → it appears in the catalogue (pending/active per policy) |
| 3 | **Configure a tool instance** — from the detail, "Set up this tool" creates a configured instance | `POST /api/v1/instances` | Set up a tool → an instance is created and shown |
| 4 | **Attach a credential to the instance** — pick/enter the credential the instance needs | `POST /api/v1/instances/{id}/configure-credentials` (+ `POST /credentials`) | Attach a key → the instance shows "credential configured" |
| 5 | **Validate / test connection** — "Test connection" runs validate + health | `GET /api/v1/instances/{id}/{validate-execution,health}` | Click "Test connection" → a healthy (mint) or error state with the reason |

(OAuth auto-connect for credential attachment is a later cross-journey increment, gated on backend gap **G1** — see inventory.)

## Increment 1 — build brief (the first issue)

**Goal.** Make the inert Tools tiles interactive: click a tile → a detail drawer with the tool's full
information, including the credential requirements that are already in the data but never shown. This is
the smallest slice that makes the page *do something* and sets up every later increment.

**Scope (in).**
- A detail **drawer/sheet** (reuse the design-system sheet/drawer) opened from a tile click.
- Renders from the tool object already in the `useTools()` list (name, category, description, documentationUrl, capabilities, `credentialRequirements`) — **no new api-client method, no new gateway call.**
- Sections: header (name + category chip), description, **"What this tool can do"** (capabilities), **"What it needs to run"** (credential requirements — type + provider, read-only for now), and a safe docs link (reuse `safeDocUrl`).
- Empty/graceful states if a field is absent; close via button + Esc; focus trap; the tile is now a real `<button>` (remove `cursor: 'default'`).

**Scope (out).** No register/configure/credential writes yet (increments 2–5). No new tokens. No nav change.

**Acceptance / how to test on the app.**
1. `pnpm -r build && VITE_API_BASE_URL=<live gateway> pnpm --filter @oraclous/console dev`, open `/app/tools`.
2. Click any tool tile → a drawer opens showing the tool's description, capabilities, **what credentials it needs**, and a docs link (if any).
3. Keyboard: Tab reaches the tile, Enter opens it, focus moves into the drawer, Esc closes and returns focus to the tile. axe-core AA clean.
4. The catalogue still loads, the MCP-import/approve/reject admin flow still works (no regression).

**Design system check.** Mint only on any live/health signal (none here yet); no emoji; sentence case;
compose from existing components; AA contrast.
