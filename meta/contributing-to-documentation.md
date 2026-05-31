# Contributing to Documentation

How to add to, edit, or restructure the Oraclous knowledge base.

## When to add a page

- Capturing a decision that should not be relitigated → write an ADR (under `adr/`)
- Documenting a new service → create a service reference under `services-reference/`
- Documenting a new operational artifact → create under `operations/`
- Defining a new term → add to the Glossary

## How to update an architecture page

Architecture pages are LOCKED at versions. Material changes:

1. Draft the proposed change in a side document
2. Write an ADR that captures the decision and rationale
3. On ADR acceptance, bump the architecture document version
4. Update the affected section page(s)
5. Add an entry to Architecture Revision History
6. Add an entry to the Change Log
7. Update the Glossary if any term meanings shifted

## How to write an ADR

Use the ADR template under `adr/`. The ADR captures: Title, Date, Status, Context, Decision, Consequences, Alternatives considered.

Accepted ADRs are immutable. Superseded ADRs are not deleted.
