# Runbook — Organisation Backfill Migration (ORA-24)

**What this is:** The one-time migration that scopes an existing (pre-A1) deployment's substrate data to an organisation. Adds and backfills `organisation_id` across Postgres, Neo4j and Redis.

## When to run

**Do not run in production yet.** Production run is gated on A2 (ORA-17) and A3 (ORA-18) landing. Rehearse on a staging clone only.

## Preconditions

- A1 substrate schema is present
- You have connections to each store: Postgres, Neo4j, Redis
- The Redis client is created with `decode_responses=True`
- You have taken a backup / snapshot of each store

## What it does

| Store | Action | Seed |
| --- | --- | --- |
| Postgres | Add `organisation_id uuid`, backfill rows, set NOT NULL, apply RLS policy | `SEED_ORGANISATION_ID` (`00000000-0000-0000-0000-000000000001`) |
| Neo4j | Set `organisation_id` on every org-scoped-label node and relationship | same seed (string form) |
| Redis | Cold-start flush: delete legacy un-scoped `qcache:{graph_id}:{sha256}` entries | n/a (cache repopulates) |

## Procedure

```python
import psycopg
from oraclous_substrate.migrations import org_backfill

# Postgres
with psycopg.connect(POSTGRES_DSN) as conn:
    org_backfill.backfill_postgres(conn)
    conn.commit()

# Neo4j
from neo4j import GraphDatabase
driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
org_backfill.backfill_neo4j(driver)

# Redis
import redis
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
org_backfill.migrate_redis_cache(client)
```

## Verification

After forward migration, run:

```sql
SELECT count(*) FROM public."knowledge_graphs" WHERE organisation_id IS NULL;
-- must return 0 for every tenant table
```

```cypher
MATCH (n:`__Entity__`) WHERE n.organisation_id IS NULL RETURN count(n);
// must return 0 for every org-scoped label
```

## Rollback

```python
with psycopg.connect(POSTGRES_DSN) as conn:
    org_backfill.rollback_postgres(conn)
    conn.commit()

org_backfill.rollback_neo4j(driver)
```

**Redis has no rollback.** The cache flush is a cold start — the cache repopulates correctly on the next read.

## Related

- ORA-24 — the story
- ADR-006 — Organisation as Outermost Tenancy Unit
- [knowledge-graph-service](../services-reference/knowledge-graph-service.md)
