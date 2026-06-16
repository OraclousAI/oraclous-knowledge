# ADR-029 — Workspace↔Harness Binding (a curation edge in the capability registry, not a manifest field)

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-16 (rev2 2026-06-17) |
| Deciders | solution-architect (drafted), Reza (directed "drive G2 now"; accepted the drafted shape, then accepted the rev2 pre-build corrections) |
| Driving epic | Agents & harness (`oraclous-frontend` [#121](https://github.com/OraclousAI/oraclous-frontend/issues/121)) · increment 6 [#127](https://github.com/OraclousAI/oraclous-frontend/issues/127) · Contract G2 [`oraclous-backend#340`](https://github.com/OraclousAI/oraclous-backend/issues/340) |
| Builds on | [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) (OHM as the canonical, portable manifest), [ADR-006](adr-006-organisation-as-outermost-tenancy-unit.md) (organisation as the outermost tenancy unit), [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (trusted gateway; services trust forwarded identity + `X-Internal-Key`), [ADR-019](adr-019-r6-gateway-datastore-and-integration-key-authz-floor.md) (org-scoping authz floor; cross-org ReBAC deferred) |

> **Revision log.** **rev2 (2026-06-17)** — a pre-build audit of this design against the real backend code found three gaps in rev1 and corrected them *before* implementation: (1) **routing** — the gateway's static leading-prefix route table cannot route `/api/v1/graphs/{id}/agents` to the registry (it matches the `/api/v1/graphs → knowledge-graph-service` entry); the endpoints are re-homed under a new **`/api/v1/agent-bindings`** registry prefix. (2) **graph-org verification** — the registry cannot read a graph's `owner_organization_id` (KGS exposes none), so the same-org guard now verifies the graph via a KGS internal **membership** call. (3) **cross-service cascade** — graph-delete cannot cascade across services; the graph side is now **tolerate-and-lazily-ignore**, not a hard cascade. Org semantics were also pinned (shared `PLATFORM_ORG` agents are bindable; not-visible → 404). rev1's Decision §3/§4/§6 are superseded by the text below.

## Context

Agents (OHM **harnesses**, stored as `kind:harness` capabilities in the capability registry) and
workspaces (knowledge **graphs**) are today two independent surfaces. An OHM manifest's only tenancy
anchor is `owner_organization_id`; it has **no workspace field**, and `GET /api/v1/graphs` and
`GET /api/v1/capabilities` are separate listings with no relation between them. The result is a product
gap: every agent lives in one flat, org-wide list with no relationship to the workspaces it operates on.
The Agents & harness journey, increment 6 (FE #127), needs the inverse — open a workspace and see/manage
*its* agents, and on an agent see *which workspaces it serves*.

The Contract (G2, `oraclous-backend#340`) framed the open question as **where the relation lives** —
manifest label, capability-registry edge, or graph-side association — plus direction/cardinality, the
ReBAC/org-scoping implications, and the gateway endpoints. rev1 chose the registry edge (below) and was
accepted; **rev2** then corrected three implementation-blocking gaps found by auditing the design against
the actual gateway router, the capability-registry structure, and the knowledge-graph-service surfaces.

### Why not a manifest label, and why not graph-side (unchanged from rev1)

- **Manifest label — rejected.** An OHM manifest is the *canonical, portable definition* of an agent
  (ADR-002); welding a `workspace_id` into it breaks portability, forces a manifest re-version on every
  attach/detach, and can't express the real cardinality. Binding is an **association**, not identity.
- **Graph-side (Neo4j) — rejected.** The graph substrate holds *tenant knowledge content*; a control-plane
  relation does not belong there, and it would split ownership away from the registry that owns harnesses.

## Decision

**The workspace↔harness binding is a many-to-many curation edge owned by the capability registry — not
an OHM manifest field and not a graph-substrate association.**

1. **Storage — a registry join relation.** Add `harness_graph_binding` to the capability-registry
   datastore (a new Alembic migration in that service's own lineage):

   | column | notes |
   | --- | --- |
   | `harness_capability_id` | **FK → `capability_descriptors.id` `ON DELETE CASCADE`** (same-service table — see §4) |
   | `graph_id` | a **plain UUID, no cross-service FK** (graphs live in knowledge-graph-service — see §4) |
   | `organisation_id` | the caller's org, stamped from the principal (never from the body) |
   | `created_by` | the acting principal's user id (add explicitly — the base mixin only gives `created_at`/`updated_at`) |
   | `created_at` | from the base mixin |

   **`UNIQUE(harness_capability_id, graph_id)`** so attach is idempotent (the repository maps the
   `IntegrityError` to an already-bound success — see §6). Index `(graph_id, organisation_id)` for the
   reverse lookup. The OHM manifest, the graph, and harness execution are **untouched**.

2. **It is a curation/visibility association — NOT an authorization grant and NOT an execution route.**
   Binding an agent to a workspace changes *neither* what data the agent can read *nor* where it runs;
   it only answers "which agents are *for* this workspace" for discovery/management. **Hard invariant:**
   the binding must never become a backdoor data-access path. (This invariant is also what makes the
   lazy-ignore cascade in §4 safe.)

3. **Org-scoping — "visible to the caller's org", verified on both sides (rev2).** A binding is permitted
   only when **both** the harness and the graph are resolvable within the caller's org:
   - **Harness:** resolved via the registry's existing org-scoped lookup, which admits the caller's org
     **or** the shared `PLATFORM_ORG`. So a **shared/platform agent CAN be bound to a tenant workspace**
     (the common case) — "same-org" means *visible to the caller*, not strict owner-equality.
   - **Graph:** the registry has no graph table and KGS exposes no `owner_organization_id`, so the registry
     **verifies membership via KGS**: on attach it calls `GET /internal/v1/graphs` forwarding the caller's
     verified principal + org (`X-Principal-*` / `X-Organisation-Id`, gated by `X-Internal-Key` — the
     established ADR-018 forward-and-trust idiom, as the graph-ingest connector already does) and confirms
     `graph_id` is in the returned set. KGS scopes that listing to the forwarded org and never leaks other
     tenants' graphs.
   - The binding row stamps `organisation_id = caller org`. An object **not visible** to the caller (either
     side) → **404** (the registry's established cross-org-as-not-found mask). There is no `409` for a
     same-org *violation* — under the visibility model a mismatch is simply a 404; `409` is not used by
     these endpoints (idempotent re-attach is `200`, not a conflict). *(This refines rev1, which wrongly
     documented a `409` "not same-org".)*

4. **Cardinality + lifecycle — asymmetric cascade (rev2).** Many-to-many.
   - **Harness delete → hard cascade.** `harness_capability_id` is an FK to the registry's own
     `capability_descriptors`, so `ON DELETE CASCADE` removes the binding rows in-service.
   - **Graph delete → tolerate-and-lazily-ignore.** Graphs are deleted in knowledge-graph-service, which
     emits no event/hook to the registry (one-way HTTP; separate Alembic lineages; ORAA-4 §3.1 forbids a
     cross-service FK). A hard cascade is therefore impossible. Instead: `graph_id` is a plain UUID with no
     FK, and **read paths skip any `graph_id` that no longer resolves** (the reverse-lookup and the
     agents-for-a-graph listing filter to live graphs). A dangling row is invisible and harmless — the
     binding is curation-only (§2), so a stale edge can never leak data or grant access. An eager reaper or
     a KGS→registry "graph-deleted" notification (gated by `X-Internal-Key`) is a **deferred follow-up**,
     not required for this slice. *(This corrects rev1's "deleting either side cascade-deletes its rows".)*

5. **Authorization to manage** mirrors capability management: an org principal with write access may
   attach/detach; read/list follows existing capability visibility (members get the read view).

6. **Gateway endpoints — under a new `/api/v1/agent-bindings` registry prefix (rev2).** The FE talks only
   to the gateway (§1.1). Because the gateway route table is **static leading-prefix match**, the endpoints
   live under a single new prefix routed to the capability registry — **add one route-table entry
   `("/api/v1/agent-bindings", "CAPABILITY_REGISTRY_URL")`** (a one-line gateway change in `route_table.py`,
   built as part of #340). This keeps `/api/v1/graphs/*` wholly on knowledge-graph-service.

   | Method + path | Purpose | Returns |
   | --- | --- | --- |
   | `GET /api/v1/agent-bindings?graph_id={id}` | agents bound to a workspace | `[{harness_id, name, kind, summary}]` (live graphs only) |
   | `GET /api/v1/agent-bindings?harness_id={id}` | workspaces a harness serves | `[{graph_id, name}]` (live graphs only) |
   | `POST /api/v1/agent-bindings` `{harness_id, graph_id}` | attach | `201` created · `200` if already bound (idempotent) · `404` if either object is absent/not visible to the caller's org |
   | `DELETE /api/v1/agent-bindings?harness_id={id}&graph_id={id}` | detach | `204` · `404` if not bound |

   Errors follow the registry's existing pattern (`{"detail": …}`, curated/no-leak — never echo ids or an
   upstream body); the gateway normalises status → the canonical `oraclous_errors` envelope on egress
   (`404 → NOT_FOUND`). Naming: routes use the real objects; the FE labels them "workspace"/"agent".

## Consequences

- **FE #127 unblocks** against `/api/v1/agent-bindings` (the rev2 paths) — list a workspace's agents,
  attach an existing agent, detach, and show an agent's workspaces — with no locally-invented shape (§1.1).
  "Build one in-context" is the existing agent-builder followed by an attach.
- **Backend work (#340):** one capability-registry migration (`harness_graph_binding` with the harness FK
  cascade + unique constraint + `created_by`), the binding repository/service/routes (mirroring the
  capability-descriptor stack), the **KGS membership check** on attach (a small internal KGS client reusing
  `KNOWLEDGE_GRAPH_URL` + the internal key), and the **one-line gateway route-table entry**. No change to the
  OHM manifest, the graph substrate, or harness execution.
- **Non-breaking.** Existing agents and graphs gain an empty binding set; no data migration.
- **Authz stays consistent** with today (org-scoping floor; shared `PLATFORM_ORG` agents bindable); the
  `organisation_id` column is the seam for future cross-org ReBAC.
- **Plane separation preserved** — the association lives in the registry; tenant content stays in the graph;
  the portable OHM definition stays portable.
- **Recorded as a Contract.** The endpoint shapes are in `flows/interface-contracts.md` §G2; this ADR + the
  backend implementing issue (#340) + FE #127 link it. The Contract is not Done until the gateway exposes
  the endpoints and the shape is enforced.
- **Deferred follow-ups:** an eager dangling-binding reaper or a KGS→registry graph-deleted notification
  (only if product needs eager cleanup — lazy-ignore is correct + safe meanwhile).
