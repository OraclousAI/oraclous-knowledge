# Architecture Revision History

**Document status:** Active · **Current architecture version:** v1.1

This page is the chronological audit trail for the Platform Architecture document and its structured artifacts.

## 5. Revision history

### 31 May 2026 — Threat Catalogue T6-M5 accepted

Codifies the structural constraint that makes ADR-009's "metering events are operator-readable metadata" safe across implementation drift. Usage-event `dimensions` bounded: key length (64), value length (256), cardinality (16), no whitespace/control-character keys. Catalogue version 1.0 → 1.1.

Approved by: tech-lead (Reza Jahankohan)

### 29 May 2026 — ADR-012 accepted

ADR-012 refines ADR-006 with the substrate tenancy-enforcement seam (`oraclous_substrate.access`) and two RLS backstop preconditions: the `NOSUPERUSER/NOBYPASSRLS` application role, and the transaction-local org-GUC lifetime.

Approved by: tech-lead (Reza Jahankohan)

### 28 May 2026 — Coordination layer: work-breakdown hierarchy, migration source maps, cross-cutting agreement protocol

New: `10. Engineering Flows` hub; Cross-cutting agreement protocol; Interface Contracts. 09. Releases → v3 with Section 7 (migration source maps). R0.5 → v3.

Approved by: tech-lead (Reza Jahankohan)

### 27 May 2026 — Platform Architecture v1.1 locked

Architecture v1.1 locked as the foundation document for the project restart. Founding ADRs 1–11 drafted in parallel.
