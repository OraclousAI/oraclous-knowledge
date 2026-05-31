---
source_page_id: 688383
title: "Contributing to Documentation"
---

# Contributing to Documentation

How to add to, edit, or restructure the Oraclous knowledge base. Written for both humans (Reza, future hires) and the docs-writer agent.

## Who maintains what

* **The docs-writer agent** — keeps service references, configuration references, and operational artifacts in sync with merged code. Lower-stakes edits without architectural implications.
* **Engineers (human)** — write ADRs, update architecture pages when an ADR is accepted, update service references for material API or behavioural changes.
* **Reza (tech lead)** — owns architecture pages, ADR approval, structural decisions about the knowledge base itself.
* **Future security and compliance owners** — own the corresponding hubs.

## When to add a page

* You're capturing a decision that should not be relitigated → write an ADR (under 02. ADRs)
* You're documenting a new service → create a service reference under 04. Services Reference
* You're documenting a new operational artifact → create under 05. Operations
* You're capturing a runtime convention or pattern → add to the relevant hub under 03. Engineering or 07. Frontend
* You're defining a new term → add to the Glossary

When in doubt, the right home is more often "extend an existing page" than "create a new one."

## When to update an existing page

* The architecture has changed and an ADR has been accepted that supersedes a prior decision
* A service has shipped a new feature or changed a behaviour
* An operational lesson has been learned that belongs in the Troubleshooting Playbook
* A configuration setting has been added, removed, or renamed

## How to update an architecture page

Architecture pages (under 01. Architecture) are LOCKED at versions. Material changes:

1. Draft the proposed change in a side document
2. Write an ADR that captures the decision and rationale
3. On ADR acceptance, bump the architecture document to a new version (e.g. v1.1 → v1.2)
4. Update the affected section page(s) with the new content
5. Add an entry to Architecture Revision History (under 01. Architecture)
6. Add an entry to the Change Log (under 08. Meta)
7. Update the Glossary if any term meanings shifted

Architecture pages with the LOCKED status macro are not edited in place without going through this process.

## How to write an ADR

Use the ADR template under 02. ADRs. The ADR captures:

* **Title** — `ADR-NNN — short noun-phrase decision`
* **Date** — when accepted
* **Status** — Proposed, Accepted, Superseded by ADR-XXX, Deprecated
* **Context** — what we were trying to decide and why
* **Decision** — what we chose, stated as a commitment
* **Consequences** — what becomes true, what becomes hard, what we've accepted
* **Alternatives considered** — and why they were not chosen

Accepted ADRs are immutable. Superseded ADRs are not deleted.

## Code blocks and diagrams

* **Code blocks** — fenced; language tag where syntax highlighting helps
* **YAML samples in OHM-specific contexts** — use full OHM kind/version preamble; partial OHM is misleading
* **Diagrams** — prefer Mermaid for inline diagrams; PNG only when Mermaid can't express what's needed

## Reviews

* **ADRs** — require explicit acceptance by Reza (tech lead) before status changes from Proposed to Accepted
* **Architecture pages** — same as ADRs since they reflect ADR-driven decisions
* **Service references** — backend implementer reviews for accuracy; PR approval is sufficient
* **Operational pages** — operations owner reviews; minor edits don't require formal review
* **Compliance pages** — security/compliance owner reviews; legal review for customer-facing claims

## What to avoid

* Restating content from another page; link to it instead
* Marketing voice
* Speculation about future plans without a clear "deferred" or "speculative" marker
* Embedding business secrets that don't belong in documentation
* Long internal debates preserved as part of a page (decisions belong in ADRs; debates belong in your head or in a meeting log)

## When to ask Reza first

* Adding a new top-level hub (currently 01–08)
* Material structural changes
* Renaming a hub or top-level page
* Deprecating a substantive page
* Customer-facing commitments

## Related references

* **Documentation Conventions** — writing style, page anatomy, status conventions
* **02. ADRs hub** — ADR template
* **Glossary** — defined terms
* **Change Log** — material structural changes
