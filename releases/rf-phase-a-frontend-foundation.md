---
confluence_id: "4620289"
title: "RF Phase A — Frontend Foundation"
---

# RF Phase A — Frontend Foundation

| Release ID | RF (Frontend track) — **Phase A** |
| --- | --- |
| Status | In progress |
| Window | Parallel track from R0.5 onward; this is the front-loaded foundation slice |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| Briefer | [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) (with [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) for package/storage-primitive decisions) |
| Dependencies | None for the foundation itself (gateway-independent). Live features depend on R6 (Application Gateway). |

## Goal

Stand up `oraclous-frontend` as a working **pnpm-workspace monorepo** whose **console app shell** builds, lints, type-checks, and renders the ported Oraclous **design system and layouts** against mocked/empty data — with the **api-client present as a typed contract shell** (including the ORA-56 gateway error envelope) and **zero live backend dependency** — so feature work can begin the moment the Application Gateway lands at R6. The foundation proves the repo's invariants are CI-enforceable before any feature consumes them. This is a **clone-and-refactor** of the legacy frontend (`legacy-reference/old-frontend`), which is the behavioural spec.

## Scope

### In scope (Phase A)

* pnpm-workspace monorepo scaffold (`packages/*` + `apps/*` + `tests/*`), strict TS base, tooling — per `oraclous-frontend/CLAUDE.md` §6
* CI that mechanically enforces the FE invariants (api-client boundary, no-token-in-storage, WCAG AA via axe-core, bundle budget, no `dangerouslySetInnerHTML`) — the machine floor replacing the absent FE review agents
* `packages/design-system` — tokens extracted from legacy `src/index.css` + the 48 shadcn/ui primitives
* Layout port — the newer `DashLayout`/`Sidebar`/`TopBar` chrome on design-system tokens
* `packages/api-client` — typed **contract shell** (structure + mock seam + the ORA-56 error-envelope types); no live calls, not generated
* `apps/console` — app shell (routing, ProtectedRoute, tenant gate) rendering on mocked data, with a **non-localStorage** token store

### Out of scope (deferred)

* All live backend-bound feature pages (Dashboard, Workspaces, Agents, the `@xyflow/react` Explorer, recharts dashboards, landing animations) — render as `PlaceholderView` for now; need the live gateway (R6)
* OpenAPI-**generated** api-client — R6, gated on the gateway publishing its spec
* Live auth/OAuth round-trips — gateway-bound
* `packages/widget-sdk`, `apps/portal`, `apps/widget-host`, `packages/analytics` bodies — scaffold-only here
* FE test agents (test-author / test-review / code-reviewer) and the full 7-state gate — reintroduced at **RF Phase B**

## Deliverables

- [ ] **Monorepo scaffold** — pnpm workspaces, strict TS base, tooling, empty package/app skeletons; `pnpm -r build` green ([ORA-82](https://oraclous.atlassian.net/browse/ORA-82))
- [ ] **CI invariant gates** — api-client-boundary, no-token-in-storage, axe-core AA, bundle budget, no-`dangerouslySetInnerHTML` ([ORA-83](https://oraclous.atlassian.net/browse/ORA-83))
- [ ] **e2e/release workflow stubs + CODEOWNERS + .env.example** (gateway-only base URL) ([ORA-84](https://oraclous.atlassian.net/browse/ORA-84))
- [ ] **design-system tokens** extracted from `src/index.css`, AA-verified ([ORA-85](https://oraclous.atlassian.net/browse/ORA-85))
- [ ] **shadcn/ui primitives** token-bound; `cn` → `ui-utils` ([ORA-86](https://oraclous.atlassian.net/browse/ORA-86))
- [ ] **Layout port** — DashLayout/Sidebar/TopBar on DS tokens, AA ([ORA-87](https://oraclous.atlassian.net/browse/ORA-87))
- [ ] **api-client contract shell** — typed structure + mock seam + ORA-56 envelope; no live calls/codegen ([ORA-88](https://oraclous.atlassian.net/browse/ORA-88))
- [ ] **console app shell** — routing + ProtectedRoute + non-localStorage tokens; renders on mocked data; axe AA clean ([ORA-89](https://oraclous.atlassian.net/browse/ORA-89))

## Migration source map

Per [09. Releases](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164160) Section 7. Authored 31 May 2026 by [product-planner](https://oraclous.atlassian.net/wiki/spaces/OP/pages/884840) from a read of the legacy frontend (`legacy-reference/old-frontend`) and the new repo's `CLAUDE.md`. Migration default: **clone-and-refactor**; the legacy app is the behavioural spec.

| Foundation concern | Legacy source | Target in new repo | Verdict |
| --- | --- | --- | --- |
| Monorepo structure | legacy single-app root | pnpm workspaces `packages/*`+`apps/*`+`tests/*` | Greenfield (legacy informs settings only) |
| Package manager | `bun.lockb` + `package-lock.json` + `pnpm-lock.yaml` (ambiguous) | **pnpm only**, `packageManager` pinned | Decision: pnpm (per repo [CLAUDE.md](http://CLAUDE.md) §6) |
| TS config | loose `tsconfig.app.json` | strict `tsconfig.base.json` | Reshape |
| CI / invariant gates | none meaningful | `ci.yml` w/ boundary + token + axe + bundle gates | Greenfield |
| Design tokens | `src/index.css` (paper/ink/mint, Sora+JetBrains, scales, ReBAC perm colours) | `packages/design-system` token layer + Tailwind preset | Extract |
| shadcn primitives | `src/components/ui/` (48 + `use-toast`) | `packages/design-system`; `cn` → `packages/ui-utils` | Lift |
| Layout / chrome | `src/dash/shell/{DashLayout,Sidebar,TopBar}.tsx` (+ `dash/context,nav,icons`) | `apps/console` shell on DS tokens | Reshape |
| Older layout shell | `src/components/layout/*` | not ported (feature/deferred) | Drop/defer |
| Routing skeleton | `src/App.tsx` (lazy, Suspense, ProtectedRoute, TenantGate) | `apps/console` route skeleton; unimplemented → PlaceholderView | Reshape |
| api-client (shape) | `src/lib/api.ts` domain types | `packages/api-client` typed contract shell (no live calls, not generated) | Reshape (heavy) |
| api-client (transport/errors) | `api.ts` raw fetch, `{detail}` errors | gateway-only seam + **ORA-56 error-envelope types** | Reshape (invariant fix) |
| Token storage | `src/lib/auth.ts` localStorage tokens | platform storage primitive, **not** localStorage (§3.5) | Reshape (invariant fix) |
| Auth base URL | separate `VITE_AUTH_BASE_URL` | collapsed to single `VITE_API_BASE_URL` → gateway (§3.1) | Reshape (invariant fix) |

## Decomposition plan (executed 31 May 2026)

Two epics — the `[impl-infra]` scaffold (coordinator session, devops-implementer) and the frontend foundation (FE repo session, frontend-implementer). **FE asymmetry:** no test agents until RF Phase B; flow is **READY → IMPLEMENTATION → CODE REVIEW (human) → DONE**; CI gates (Epic A1) enforce the invariants in agents' place; human tech-lead signs all `[impl]` PRs.

| Epic | Owner / session | Stories |
| --- | --- | --- |
| [ORA-80](https://oraclous.atlassian.net/browse/ORA-80) Epic A1 — Repo scaffold & CI | devops-implementer · `[impl-infra]` · coordinator session | [ORA-82](https://oraclous.atlassian.net/browse/ORA-82) A1-S1 monorepo scaffold (Greenfield) · [ORA-83](https://oraclous.atlassian.net/browse/ORA-83) A1-S2 CI invariant gates (Greenfield) · [ORA-84](https://oraclous.atlassian.net/browse/ORA-84) A1-S3 e2e/release stubs + CODEOWNERS (Greenfield) |
| [ORA-81](https://oraclous.atlassian.net/browse/ORA-81) Epic A2 — Frontend Foundation | frontend-implementer · `[impl]` · FE repo session | [ORA-85](https://oraclous.atlassian.net/browse/ORA-85) A2-S1 design-system tokens (Extract) · [ORA-86](https://oraclous.atlassian.net/browse/ORA-86) A2-S2 shadcn primitives (Lift) · [ORA-87](https://oraclous.atlassian.net/browse/ORA-87) A2-S3 layout port (Reshape) · [ORA-88](https://oraclous.atlassian.net/browse/ORA-88) A2-S4 api-client contract shell (Reshape; Relates ORA-56) · [ORA-89](https://oraclous.atlassian.net/browse/ORA-89) A2-S5 console app shell (Reshape) |

### Sequencing

* **Epic A1 first** (A1-S1 → A1-S2 → A1-S3). **A1-S1 (**[**ORA-82**](https://oraclous.atlassian.net/browse/ORA-82)**) is Ready now.** Nothing in A2 starts until the scaffold + CI gates are live (so A2 PRs are enforced from the first commit).
* **Epic A2:** A2-S1 → A2-S2 (sequential) ∥ A2-S4 (parallel, shares no code with the DS); A2-S3 needs S1+S2; A2-S5 integrates S2+S3+S4.

## Architecture references

* `oraclous-frontend/CLAUDE.md` — the repo contract: target tree (§6), the eight invariants (§3), FE asymmetry (§1), stack (§7), clone-and-refactor default (§11)
* [Interface Contracts §3](https://oraclous.atlassian.net/wiki/spaces/OP/pages/1277953) — the ORA-56 gateway error envelope the api-client shell embeds

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| Package-manager drift (legacy bun vs target pnpm) | Low | A1-S1 pins `packageManager: pnpm@x` and keeps only `pnpm-lock.yaml`; bun/npm configs not carried forward. | devops-implementer |
| api-client invents cross-repo shapes with no live gateway | Medium | Shell only; embed ORA-56 + already-canonical shapes; everything else a `// Contract: ORA-xxx` TODO. | frontend-implementer |
| Token-storage primitive (§3.5) not yet concrete for A2-S5 | Medium | Confirm/define the sanctioned primitive at A2-S5 grooming (solution-architect); carve a sub-task if needed. | solution-architect |
| Design-system tokens fail WCAG AA contrast | Low | A2-S1 verifies contrast (body ≥4.5:1, UI/large ≥3:1) before primitives bind. | frontend-implementer |

## Dependencies

**Upstream:** none for the foundation (gateway-independent). **Downstream:** the live console (feature pages, generated api-client, real auth) and later RF phases depend on **R6** (Application Gateway). ORA-55 (api-client parses the error envelope, deferred-to-frontend) re-grooms once this foundation lands.

## Sprint references

RF Phase A transitioned **Proposed → Briefed → In progress** on 31 May 2026 (product-planner took the gate and created this page on the tech-lead's authorisation). Two epics ([ORA-80](https://oraclous.atlassian.net/browse/ORA-80), [ORA-81](https://oraclous.atlassian.net/browse/ORA-81)) + 8 stories ([ORA-82](https://oraclous.atlassian.net/browse/ORA-82)–[ORA-89](https://oraclous.atlassian.net/browse/ORA-89)) created with lift-tags + named legacy sources + `Blocks` links. The first wave (A1-S1 [ORA-82](https://oraclous.atlassian.net/browse/ORA-82) → devops-implementer) is **Ready**; the rest are Backlog.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 31 May 2026 | Page created; RF Phase A scoped to the Frontend Foundation; migration source map + decomposition (epics [ORA-80](https://oraclous.atlassian.net/browse/ORA-80)/[ORA-81](https://oraclous.atlassian.net/browse/ORA-81), stories [ORA-82](https://oraclous.atlassian.net/browse/ORA-82)–[ORA-89](https://oraclous.atlassian.net/browse/ORA-89)) recorded; pnpm decision; first wave to Ready. Status Proposed → Briefed → In progress. | product-planner (coordinator; solution-architect on package/storage decisions) | Stand up the Frontend track foundation (clone-and-refactor) on tech-lead authorisation, in parallel with R2 |
