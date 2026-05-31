---
confluence_id: "557174"
title: "Change Log"
---

# Change Log

A running record of material changes to the Oraclous knowledge base. This page captures _what changed and why_ across the documentation as a whole; individual pages also retain their own Confluence-managed version history.

## What goes here

* Architecture version locks (e.g. v1.1 LOCKED on 27 May 2026)
* New ADRs accepted
* Major restructuring of hubs or sections
* New top-level pages or sections
* Material refactoring that changes how to find information
* Deprecation of pages or sections

## What does not go here

* Per-page typo fixes, formatting tweaks
* Routine edits the docs-writer agent makes as services ship
* Minor link updates
* Confluence-internal version increments

For routine edits, Confluence's per-page version history is the record. This page captures only changes that affect _how the knowledge base is structured or what it commits to_.

## Format

Entries are in reverse chronological order. Each entry has:

* Date
* What changed (one or two lines)
* Who initiated it
* Pages affected (links)
* Rationale or reference (ADR if relevant)

## Recent changes

### 27 May 2026 — Initial knowledge base structure

The Oraclous Platform space was created with eight top-level hubs (01. Architecture through 08. Meta) and substantive content for:

* Architecture v1.1 (all 10 sections plus parent page)
* 11 founding ADRs (ADR-001 through ADR-011)
* Engineering hub with Test Strategy, Agent Team Roster, and process pages
* Services Reference hub with per-service reference pages
* Operations hub with Deployment Topology and structured placeholders for the rest
* Compliance hub with structured placeholders
* Frontend hub with stack reference, design system, conventions
* Meta hub with this change log, glossary, and conventions

Initiated by Reza Jahankohan as part of the Oraclous V1 restart. Source documents: Architecture v1.1 draft, founding ADRs, agent team design.

### Architecture v1.1 LOCKED — 27 May 2026

Architecture v1.1 is the locked baseline. Material changes require an ADR. Pages under 01. Architecture carry the LOCKED status. Migration phases derived from this baseline are documented in Section 8 of the architecture.

## How to add an entry

When making a material change:

1. Make the change to the affected page(s)
2. Add an entry here in reverse chronological order
3. Reference any ADR that drove the change
4. Where the change affects external commitments (compliance posture, customer-facing claims), call this out explicitly

## Related references

* **Documentation Conventions** — what qualifies as a material change
* **02. ADRs** — decisions that drive change-log entries
* **Architecture Revision History (under 01. Architecture)** — the architecture-specific revision record
