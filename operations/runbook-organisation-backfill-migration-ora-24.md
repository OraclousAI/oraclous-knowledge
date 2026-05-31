---
confluence_id: "2260996"
title: "Runbook — Organisation Backfill Migration (ORA-24)"
---

**What this is.** The one-time migration that scopes an existing (pre-A1) deployment's substrate data to an organisation. It adds and backfills `organisation_id` across Postgres, Neo4j and Redis, seeding the well-known single organisation so a single-tenant deployment keeps behaving exactly as before. Shipped in ORA-24; code lives in `oraclous_substrate.migrations.org_backfill`.

## When to run

**Do not run in production yet.** Authoring and the staging-clone rehearsal are unblocked now. The **production run is gated on A2 (ORA-17) and A3 (ORA-18)** landing — run it in production only once full Epic A is deployed. Until then, rehearse on a staging clone only.

Run this once per existing deployment, at the A1 cutover, _before_ any organisation-scoped writes begin. A fresh (greenfield) deployment never needs it — its tables are created already organisation-scoped by `oraclous_substrate.schema.*.apply`.

## Preconditions

* A1 substrate schema is present on the target (the org-scoped schema + seed organisation from ORA-16).
* You have a connection to each store: a Postgres connection, a Neo4j driver, and a Redis client.
* **The Redis client is created with** `decode_responses=True` (string keys). `migrate_redis_cache` splits keys as strings; a bytes-mode client will not work.
* You have taken a backup / snapshot of each store (this is a schema + data migration).

## What it does

| Store | Action | Seed |
| --- | --- | --- |
| Postgres | Add `organisation_id uuid` to every tenant table, backfill un-scoped rows, set NOT NULL, then apply the forced-RLS + org-isolation policy shape. | `SEED_ORGANISATION_ID` (`00000000-0000-0000-0000-000000000001`) |
| Neo4j | Set `organisation_id` on every org-scoped-label node and `IN_COMMUNITY` relationship that lacks one; (re-)create the org-scoped indexes. | same seed (string form) |
| Redis | Cold-start flush: delete legacy un-organisation-scoped `qcache:{graph_id}:{sha256}` entries so nothing stale is read across the new key prefix. | n/a (cache repopulates) |

## Procedure

The Postgres and Neo4j entry points operate on the connection/driver you pass and **do not commit** — you own the transaction. Every entry point is idempotent: re-running is a safe no-op.

### 1. Rehearse on a staging clone first

- [ ] Restore a recent production snapshot into a staging environment.
- [ ] Run the full procedure below against staging.
- [ ] Run the verification step; confirm zero un-scoped primitives.
- [ ] Run the rollback, confirm it reverts cleanly, then re-run the forward migration (idempotency check).

### 2. Postgres

```python
import psycopg
from oraclous_substrate.migrations import org_backfill

with psycopg.connect(POSTGRES_DSN) as conn:
    org_backfill.backfill_postgres(conn)   # seeds SEED_ORGANISATION_ID by default
    conn.commit()
```

**Large-table lock window.** `backfill_postgres` runs `ADD COLUMN` + a full-table `UPDATE` + `SET NOT NULL` + `apply()` in the single transaction you commit. On a large tenant table this holds an exclusive lock for the duration. For large production tables, set a `lock_timeout` and/or run the backfill in batches in a maintenance window; rehearse the timing on the staging clone first.

### 3. Neo4j

```python
from neo4j import GraphDatabase
from oraclous_substrate.migrations import org_backfill

driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
org_backfill.backfill_neo4j(driver)
```

### 4. Redis (cold-start flush)

```python
import redis
from oraclous_substrate.migrations import org_backfill

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)  # decode_responses is required
org_backfill.migrate_redis_cache(client)
```

## Verification

After the forward migration, confirm **no primitive is left unscoped** (the T1 control — a primitive a query can reach without an organisation is a cross-org read).

**Postgres** — for each tenant table, this must return `0`:

```sql
SELECT count(*) FROM public."knowledge_graphs" WHERE organisation_id IS NULL;
-- repeat for ingestion_jobs, connectors, blob_cas
```

**Neo4j** — for each org-scoped label, this must return `0`:

```cypher
MATCH (n:`__Entity__`) WHERE n.organisation_id IS NULL RETURN count(n);
// repeat for __Community__, __Contradiction__, Chunk, and the IN_COMMUNITY relationship
```

**Redis** — no legacy un-scoped cache key remains:

```shell
redis-cli --scan --pattern 'qcache:*'   # surviving keys should all be 4-segment org-scoped keys
```

**Static gate** — the 0b organisation-scoping analysis (`tools.lint.check_org_scoping`) must pass over the migration source. This is enforced in CI by `tests/lint/test_org_backfill_static_analysis.py`.

## Rollback

Each store has a tested rollback. Rollback removes the organisation scoping and **preserves the data** (Postgres rows are kept; only the column/policy/RLS are removed). Like the forward migration, the Postgres/Neo4j rollbacks operate on your connection/driver and do not commit.

```python
from oraclous_substrate.migrations import org_backfill

# Postgres: drops the RLS policy, disables/unforces RLS, drops the organisation_id column (rows preserved)
with psycopg.connect(POSTGRES_DSN) as conn:
    org_backfill.rollback_postgres(conn)
    conn.commit()

# Neo4j: removes the organisation_id property from the org-scoped nodes + relationships
org_backfill.rollback_neo4j(driver)
```

**Redis has no rollback.** The cache flush is a cold start — there is nothing to revert. The cache repopulates under the new organisation-scoped keys (`qcache:{organisation_id}:{graph_id}:{digest}`) on the next read. The first reads after migration are cache misses by design.

## Redis cache strategy (why flush, not backfill)

The legacy cache key `qcache:{graph_id}:{sha256}` carries only the query _hash_, so the A1 organisation-then-graph key (which hashes the query _text_) cannot be recomputed from an existing entry — the legacy entries cannot be backfilled in place. The migration therefore takes the cold-start route: it removes the legacy un-scoped entries so nothing stale can be read across the new prefix, and the cache repopulates correctly. The flush is scoped to the `qcache:` namespace — non-cache keys and already-organisation-scoped keys are left untouched (it is **not** a blanket `FLUSHDB`).

## Related

* [ORA-24](https://oraclous.atlassian.net/browse/ORA-24) — the story; impl PR #19, tests PR #16.
* [ADR-006 — Organisation as Outermost Tenancy Unit](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393403) (the reason every primitive must be organisation-scoped; threat T1).
* [knowledge-graph-service](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753832) — the substrate write side this data belongs to.
* Code: `packages/substrate/src/oraclous_substrate/migrations/org_backfill.py`; schema declarations in `oraclous_substrate.schema.{postgres,neo4j}` and `oraclous_substrate.cache_keys`.

_Authored by docs-writer for ORA-43 (2026-05-29), from merged PRs #16 (tests) and #19 (impl). Operator-facing; the production run remains gated on A2/ORA-17 + A3/ORA-18._
