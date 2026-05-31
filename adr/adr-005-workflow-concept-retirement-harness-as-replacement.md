# ADR-005 — Workflow Concept Retirement; Harness as Replacement

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |

## Context

The v0 system carried two parallel concepts: _agents_ and _workflows_. This created persistent costs: two governance evaluations, two audit streams, two budget surfaces.

## Decision

The platform has one first-class actor concept: the **harness**. The v0 "workflow" concept is retired. Every executable thing is a harness described by an OHM document.

There is no workflow service, workflow database, or workflow type in the substrate.
