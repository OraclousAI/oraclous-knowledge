# ADR-002 — OHM as Canonical Manifest Format

| Field | Value |
| --- | --- |
| Status | Accepted |
| Date | 27 May 2026 |
| Approved by | tech-lead (Reza Jahankohan) |
| Driving artifacts | Section 4 · OHM v1.0 Standalone Specification |

## Decision

The Oraclous Harness Manifest (OHM) is the canonical, sole format for describing a harness. The specification is owned by Oraclous and versioned independently.

OHM is a single YAML 1.2 document containing exactly `ohm_version`, `metadata`, `capabilities`, `models`, `prompts`, `governance`, `runtime`, and (when signed) `signatures`. Every reference resolves at harness load time, atomically, with partial loads forbidden.
