---
source_page_id: 884820
title: "Documentation Conventions"
---

# Documentation Conventions

How we write, organise, and maintain documentation across the Oraclous knowledge base. This page is the canonical reference for the docs-writer agent and for any human writing into the space.

## What documentation is for

* **Capturing decisions** — so they aren't relitigated; ADRs are the primary form
* **Onboarding** — so new contributors (human or agent) can become productive quickly
* **Operating** — so on-call engineers can resolve incidents at 3am without reverse-engineering
* **Compliance** — so auditors can verify our claims with documented evidence
* **Customer trust** — so prospects and active customers can understand what we promise

Documentation is _not_ for: marketing copy, internal politics, idle speculation, dated meeting minutes.

## Section structure

The space has eight numbered hubs at the top level:

1. **01. Architecture** — what the platform is and how it's structured
2. **02. ADRs** — decisions that shaped the architecture
3. **03. Engineering** — how the platform is built
4. **04. Services Reference** — per-service references
5. **05. Operations** — how the platform is deployed and operated
6. **06. Compliance** — formal compliance posture
7. **07. Frontend** — UI stack and conventions
8. **08. Meta** — documentation about the documentation

Numbered prefixes preserve ordering in the Confluence sidebar. New top-level hubs require an explicit decision.

## Writing principles

* **Prose, not bullets, by default** — bullets where the content is genuinely a list; otherwise sentences
* **Short paragraphs** — three to six sentences is the sweet spot
* **No marketing voice** — describe what is true, with its limitations and trade-offs; no "powerful," "robust," or "leveraging"
* **Concrete over abstract** — examples beat principles when both are possible
* **Cross-reference, don't duplicate** — link to the source-of-truth page rather than restating
* **Date what changes** — when a page is materially updated, include a version note in the page or its commit message
* **British English** — "behaviour," "organisation," "favour"; consistent across the space

## Page anatomy

Each substantive page should have:

* **A descriptive title** — verbose is fine; "Cross-Workspace Federation Under ReBAC" beats "Federation"
* **A one-paragraph opener** — what this page is and isn't, and who it's for
* **A status block where relevant** — placeholder, draft, locked, deprecated
* **Headings with semantic meaning** — not "Section A," "Section B"
* **A Related References block at the bottom** — outbound links to the pages this one depends on or relates to

## Status conventions

Pages declare status using the Confluence status macro:

* `placeholder` — structure fixed; content not yet substantive
* `draft` — content present, not yet reviewed
* `current` — reviewed, in force
* `locked` — content has been declared LOCKED at a known version (e.g. Architecture v1.1)
* `deprecated` — superseded; kept for historical reference; the superseding page is linked

## ADR conventions

ADRs follow a structured template (defined under 02. ADRs hub). Once accepted, ADRs are immutable — they record what we decided at a point in time. Superseded ADRs are not deleted; a new ADR supersedes them by reference.

## Diagrams

* **Diagrams as text where possible** — Mermaid or PlantUML embedded so diffs work
* **Diagrams must have a textual description** — accessibility and future-proofing; if the diagram doesn't render, the description must still convey the meaning
* **Visual diagrams stored as PNG plus source** — never as PNG alone

## Linking conventions

* Internal Confluence links use Confluence's smart links
* External links spell out the URL in plain prose context the first time, then bare-link subsequently
* GitHub links pin to specific commits, not branches, for anything that needs to be reproducible
* Page IDs are preserved in URLs — short titles can change without breaking links

## The docs-writer agent

The docs-writer agent maintains substantive content as the platform evolves. It reads merged code and updates the corresponding documentation pages. Human review remains the final authority on what is published.

## Related references

* **02. ADRs hub** — ADR template and conventions
* **Glossary** — defined terms used across the documentation
* **Change Log** — how knowledge-base changes are tracked
* **Contributing to Documentation** — how to make additions and edits
