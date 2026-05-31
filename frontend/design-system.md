# Design System

**Status:** Placeholder — design system formalises as the v1 UI lands

## Design principles

- **Dark-first, dark-only** — light mode is not supported for v1
- **Quiet by default** — colour is used for meaning, not decoration
- **Information density without claustrophobia** — readable through spacing scale and typographic rhythm
- **Distinctive, not eccentric** — Syne for display, DM Mono for code
- **Provenance and metadata are first-class** — every primary surface has a way to see _why_

## Token categories

- **Colour** — base palette (neutrals 0–950), accent (one primary, one secondary), semantic (success, warning, danger, info)
- **Typography** — Syne for headings/display, DM Mono for code/identifiers, system sans for body
- **Spacing** — 4 px base, multiples through 64 px
- **Motion** — durations are short (120 ms / 200 ms / 320 ms); `ease-out` by default; reduce-motion respected
