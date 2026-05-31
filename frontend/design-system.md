---
source_page_id: 852071
title: "Design System"
---

# Design System

The visual and interaction language of the Oraclous frontend. This page defines tokens, conventions, and patterns that hold across every screen.

## Status

Placeholder — design system formalises as the v1 UI lands

The seed comes from the legacy `Jahankohan/oraclous-app` repo; the formal design system grows from there.

## Design principles

* **Dark-first, dark-only** — the platform operates in a dark visual register. Light mode is not supported for v1.
* **Quiet by default** — colour is used for meaning, not decoration. Most of the surface is neutral; accent colour signals status, action, or attention.
* **Information density without claustrophobia** — the platform shows a lot (graphs, task boards, manifests, provenance). The design system trades raw density for legibility through spacing scale and typographic rhythm.
* **Distinctive, not eccentric** — Syne for display, DM Mono for code; these set the voice. Avoid additional display fonts.
* **Provenance and metadata are first-class** — every primary surface has a way to see _why_ something is the way it is (who authored it, when, with what permissions)

## Token categories

* **Colour** — base palette (neutrals 0–950), accent (one primary, one secondary), semantic (success, warning, danger, info)
* **Typography** — Syne for headings/display, DM Mono for code/identifiers, system sans for body
* **Spacing** — 4 px base, multiples through 64 px; component-level spacing uses tokens, not arbitrary values
* **Radius** — small (4 px), medium (8 px), large (12 px); fully-rounded reserved for avatars and pill controls
* **Elevation** — flat-first; elevation reserved for floating UI (popovers, dialogs, toasts); no decorative shadows
* **Motion** — durations are short (120 ms / 200 ms / 320 ms); easing is `ease-out` by default; reduce-motion respected
* **Iconography** — lucide-react only, stroke width 1.5 px standard, 1.75 px in dense UI

## Component conventions (visual)

* Buttons have three sizes (sm / md / lg) and four variants (primary, secondary, ghost, danger)
* Forms use a consistent label-above-field pattern; inline errors below the field; never error-toasts for validation
* Tables prefer monospaced numerals; right-aligned numbers; left-aligned text
* Empty states always include: an icon, a one-line explanation, a primary action
* Loading states use shimmer skeletons for known shapes; spinners only for indeterminate operations

## Voice and copy

* **Plain, direct** — short sentences; second person; no marketing voice
* **Honest** — "this didn't work because X" not "oops, something went wrong"
* **No emoji in UI copy** — emoji belongs in customer-authored content, not platform chrome

## What this page will cover

* **Token reference** — the canonical token list with values and CSS variable names
* **Component gallery** — visual reference for every shadcn-derived component as customised
* **Patterns** — common compositions (form layout, list-detail, board view, graph view, modal stack)
* **Accessibility** — colour contrast, focus indicators, keyboard navigation, screen-reader text
* **Iconography** — approved lucide set; how to request additions
* **Imagery** — when to use illustrations, when not to; placeholder treatment for empty graphs
* **Brand boundary** — what is Oraclous-the-platform UI vs Oraclous-the-company marketing (different visual systems)

## Tokens as code

Tokens live in `tailwind.config.ts` as the source of truth. The Tailwind theme is the source; CSS variables and component code consume the tokens. No raw hex values in component code.

## Related references

* **Frontend Stack Reference** — technology choices including Tailwind and shadcn
* **Component Conventions** — code-level component patterns (this page covers the visual side)
* **State and Data Patterns** — how data flows through components
