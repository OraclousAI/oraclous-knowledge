# knowledge-graph-service

**Layer:** 1 (Substrate) · **Port:** 8003 · **Status:** Renamed from `knowledge-graph-builder` in Phase 3; ingest-only after retriever extraction

## Purpose

`knowledge-graph-service` is the substrate's write side. It owns ingestion, schema management, analytics, and ReBAC graph maintenance.

## Responsibilities

- Multi-modal ingestion: text, documents, structured data, code, temporal data
- ReBAC graph maintenance
- Schema management
- Multi-tenant component wrappers for write paths
- Analytics: community detection, centrality
- Provenance writes (universal sink)
- Background job orchestration for long-running ingestion pipelines

## Migrations

**Organisation backfill (A1 cutover, ORA-24):** a one-time, idempotent migration scoping pre-A1 deployment's substrate data to an organisation. See [Runbook — Organisation Backfill Migration (ORA-24)](../operations/runbook-organisation-backfill-migration-ora-24.md).
