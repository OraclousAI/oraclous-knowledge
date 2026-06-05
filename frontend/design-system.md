---
confluence_id: "852071"
title: "Design System"
---

# Design System

The visual and interaction language of the Oraclous frontend.

## Source of truth — the brand v1.0 handoff (decided, high-fidelity)

The design system is **already decided and high-fidelity.** It lives, read-only, in the legacy FE app:

```
legacy-reference/old-frontend/design_handoff_oraclous_v1/
```

Per its `README.md` the handoff is **final** ("colours, typography, spacing, motion, and copy are decided; recreate pixel-by-pixel; do not improvise — if something is genuinely missing, ask before inventing"). FE-first work **must respect it.** Contents:

| Path | What |
|---|---|
| `01-design-tokens/colors_and_type.css` (also root `colors_and_type.css`) | The canonical token set — colour, type, spacing, motion, the `.brand-prompt`/`.is-blink` utilities |
| `02-brand-assets/` | `oraclous-chevron.svg`, `oraclous-cursor.svg`, `oraclous-mark.svg`, `oraclous-wordmark.png`, `oraclous-lockup.png`, `oraclous-symbol.png` |
| `03-brand-book/brand_book_v0.html` | The brand book |
| `04-redesigned-screens/`, `06-design-system-previews/` | High-fidelity screen + component references (HTML prototypes, not code to copy) |
| `05-ui-kits/{marketing,product}` | UI kits |

> **This page corrects earlier drafts.** Prior versions of this page said "dark-first, dark-only" and named **Syne / DM Mono** — both are **superseded** by the handoff (see corrections below). When this page and the handoff diverge, **the handoff wins.**

## The six non-negotiables (brand regressions if broken)

1. **Mint `#10D88A` is LIVE-SIGNAL only** — active source nodes, the streaming cursor, "agent online" dots, the active graph edge. Never a button fill, hover, brand-mark colour, or decoration.
2. **No emoji anywhere** in platform chrome — use `lucide-react`. (Emoji is allowed only in customer-authored content.)
3. **Banned-word list** — strip from every string: *revolutionize, unleash, supercharge, AI-powered, game-changing, seamlessly, leverage (verb), robust, cutting-edge, innovative, empower, intuitive, ecosystem, journey (for users)*.
4. **The symbol never appears alone** — `>|` (chevron + cursor) is always in lockup with the `ORACLOUS` wordmark, **or** functioning as the in-product live cursor. Never a bare chevron on a favicon / OG image / splash.
5. **Cursor blink is `1.06s steps(1, end)`** — discrete on/off (terminal duty cycle), not a fade. The `.is-blink` utility encodes it.
6. **The chat-prompt indicator is the brand chevron + brand cursor** — shipped as `<BrandPrompt>` (`src/components/brand/BrandPrompt.tsx`), rendered in every composer / "ask the graph" input. Forbidden substitutes: keyboard `>`, typographic `›` (U+203A), letter `I`, em-dash, or a Lucide `chevron-right`.

## Tokens (from `colors_and_type.css` — authoritative)

* **Typography** — `--font-sans: 'Sora'` (300–800; display + product), `--font-mono: 'JetBrains Mono'` (400–600; code/identifiers), with `'Inter'` as the **dense fallback only** (`--t-dense`/`--t-tiny`). Sora holds at 13.5px for dense product UI (Reza checkpoint). **(Corrects the old "Syne / DM Mono".)**
* **Surface / theme** — **light is the default surface** (`--paper #F4F4F2`, `--ink #0B1220`); **dark is a supported variant** via `:root[data-surface="dark"]` / `.surface-dark` (tokens flip). **(Corrects the old "dark-first, dark-only / light not supported".)**
* **Colour** — core (`--ink`, `--paper`, `--paper-soft`, `--rule`, `--mute`), the single `--accent` mint (live-signal-only), semantic (`--success #2E8B57` — deliberately *not* mint, `--warning`, danger), and OKLCH equivalents.
* **ReBAC permission states** (a key product differentiator — visualised in the grant editor, graph, audit): `--perm-granted` (mint), `--perm-inherited` (cool blue #6BA0E8), `--perm-denied` (iron red #C8412C), `--perm-expired` (amber-brown #B5862A), each with a `-bg` tint.
* **Spacing / radius / elevation / motion** — per the handoff: spacing scale, small/medium/large radius (fully-rounded for avatars/pills only), flat-first elevation, short motion (reduce-motion respected).
* **Iconography** — `lucide-react` only.

## Target stack & integration approach

The handoff files are **HTML design references, not production code.** Recreate them **inside the existing legacy FE codebase** (`oraclous-visual-flow` — React + TypeScript + Vite + Tailwind + shadcn/ui), keeping its routing, API client (`src/lib/api.ts`), React Query usage, lazy loading, and folder layout. **Only the visual + content layer changes.** Tokens are the source of truth — port `colors_and_type.css` into the Tailwind theme (`tailwind.config.ts`); no raw hex in component code.

> FE-first targets the **real application gateway** (port 8006) and the R3.5 capabilities behind it (auth/orgs, credentials, knowledge-graph, retrieval, capability-registry **sync** execution). Agent-orchestration/streaming UIs wait for R4/R5.

## Design principles (aligned to the handoff)

* **Quiet by default** — colour carries meaning, not decoration; the mint signal is rationed (non-negotiable #1).
* **Information density without claustrophobia** — graphs, boards, manifests, provenance shown legibly via the spacing scale + Sora's dense sizing.
* **Distinctive, not eccentric** — Sora (display/product) + JetBrains Mono (code) set the voice; no additional display fonts.
* **Provenance and metadata are first-class** — every primary surface can show *why* (author, time, permissions).

## Voice and copy

* Plain, direct, second person; no marketing voice; honest errors ("this didn't work because X").
* No emoji in platform chrome; obey the banned-word list (non-negotiable #3).

## Related references

* **Legacy handoff** — `legacy-reference/old-frontend/design_handoff_oraclous_v1/` (the decided source of truth)
* **Frontend Stack Reference** — Tailwind + shadcn choices
* **Component Conventions** — code-level component patterns (this page covers the visual side)
* **State and Data Patterns** — how data flows through components
