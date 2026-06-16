# ADR-029 — Workspace↔Harness Binding (a curation edge in the capability registry, not a manifest field)

## Status

| | |
| --- | --- |
| Status | Accepted |
| Date | 2026-06-16 |
| Deciders | solution-architect (drafted), Reza (directed "drive G2 now"; accepted the drafted shape with both defaults) |
| Driving epic | Agents & harness (`oraclous-frontend` [#121](https://github.com/OraclousAI/oraclous-frontend/issues/121)) · increment 6 [#127](https://github.com/OraclousAI/oraclous-frontend/issues/127) · Contract G2 [`oraclous-backend#340`](https://github.com/OraclousAI/oraclous-backend/issues/340) |
| Builds on | [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) (OHM as the canonical, portable manifest), [ADR-006](adr-006-organisation-as-outermost-tenancy-unit.md) (organisation as the outermost tenancy unit), [ADR-018](adr-018-edge-authentication-trusted-gateway.md) (trusted gateway), [ADR-019](adr-019-r6-gateway-datastore-and-integration-key-authz-floor.md) (org-scoping authz floor; cross-org ReBAC deferred) |

## Context

Agents (OHM **harnesses**, stored as `kind:harness` capabilities in the capability registry) and
workspaces (knowledge **graphs**) are today two independent surfaces. An OHM manifest's only tenancy
anchor is `owner_organization_id` (OHM spec, the ReBAC anchor); it has **no workspace field**, and
`GET /api/v1/graphs` and `GET /api/v1/capabilities` are separate listings with no relation between them.

The consequence is a product gap, not just a missing endpoint: every agent lives in one flat,
org-wide list with no relationship to the workspaces it actually operates on. The Agents & harness
journey, increment 6 (FE #127), needs the inverse — open a workspace and see/manage *its* agents, and
on an agent see *which workspaces it serves*. This is a genuinely **new concept**, so it needs a
decision before any FE or endpoint work.

The Contract (G2, `oraclous-backend#340`) framed the open question as **where the relation lives**:

1. **A manifest label** — a `workspace_id`/`graph_ids` field on the OHM manifest.
2. **A capability-registry edge** — a join relation between the harness capability and the graph.
3. **A knowledge-graph-side association** — a node/edge stored in the tenant graph (Neo4j).

…plus the direction/cardinality, the ReBAC/org-scoping implications, and the gateway endpoints.

### Why not a manifest label, and why not graph-side

- **Manifest label — rejected.** An OHM manifest is the *canonical, portable definition* of an agent
  (ADR-002): it must be reusable and exportable independent of any one deployment. Embedding a
  `workspace_id` welds the definition to a specific graph, breaks portability, and forces a manifest
  re-version on every attach/detach (a binding change is not a definition change). A single field also
  cannot express the real cardinality (an agent may serve several workspaces; a workspace has several
  agents). Binding is an **association**, not part of the agent's identity.
- **Graph-side (Neo4j) — rejected.** The graph substrate holds the *tenant's knowledge content*.
  Storing a control-plane relation (which platform harness is curated to a graph) inside tenant data
  mixes planes, splits ownership of harness metadata away from the registry that owns it, and makes the
  org-scoping/authz story inconsistent (the binding must scope exactly like harnesses and graphs do).

## Decision

**The workspace↔harness binding is a many-to-many curation edge owned by the capability registry — not
an OHM manifest field and not a graph-substrate association.**

1. **Storage — a registry join relation.** Add `harness_graph_binding` to the capability-registry
   datastore:

   | column | notes |
   | --- | --- |
   | `harness_capability_id` | FK → the `kind:harness` capability |
   | `graph_id` | the knowledge graph (workspace) |
   | `organisation_id` | the shared owning org (denormalised for the same-org check + scoping) |
   | `created_at`, `created_by` | provenance (the acting principal) |

   **Unique** on `(harness_capability_id, graph_id)` (so attach is idempotent and there is at most one
   edge per pair). The OHM manifest, the graph, and harness execution are **untouched**.

2. **It is a curation/visibility association — NOT an authorization grant and NOT an execution route.**
   Binding an agent to a workspace changes *neither* what data the agent can read *nor* where it runs.
   The agent's data access is already governed by its tools/connectors under org-scoping; the binding
   only answers "which agents are *for* this workspace" for discovery and management. This is a hard
   invariant: the binding must **never** become a backdoor data-access path. (If execution-scoping — an
   agent running *against* a bound graph — is ever wanted, that is a separate decision built on this
   edge, explicitly out of scope here.)

3. **Org-scoping floor.** A binding is permitted **only when the harness and the graph share the same
   `owner_organization_id`**. A cross-org attach is rejected. This matches the as-built authz posture
   (org-scoping only; cross-org ReBAC deferred — ADR-019). The `organisation_id` column is the seam: if
   cross-org grants ever land (R6/R8 ReBAC), the same-org check relaxes to a ReBAC check without
   re-architecting the edge.

4. **Cardinality + lifecycle.** Many-to-many. Deleting either the harness or the graph
   **cascade-deletes** its binding rows — no dangling edges. Attach is idempotent; detach of a
   non-existent edge is a no-op-success-shaped 404 (see endpoints).

5. **Authorization to manage** mirrors capability management: an org principal with write access to the
   org's capabilities may attach/detach; read/list follows existing capability visibility. (In practice,
   per the FE persona model, owner/standalone manage; members get the read view.)

6. **Gateway endpoints** — the FE talks only to the gateway (FE invariant §1.1); these are added to the
   gateway OpenAPI under the incremental-contract rule (ADR-015). The binding data lives in and is served
   by the **capability registry**; the gateway routes the `/agents` sub-paths of `graphs/` to the
   registry (path-based routing), keeping the rest of `/api/v1/graphs/*` on the knowledge-graph service.

   | Method + path | Purpose | Returns |
   | --- | --- | --- |
   | `GET /api/v1/graphs/{graph_id}/agents` | the harnesses bound to a workspace | list of `{harness_id, name, kind, summary}` (enough to render without a second fetch) |
   | `POST /api/v1/graphs/{graph_id}/agents` `{harness_id}` | attach | `201` created · `200` if already bound (idempotent) · `409` if not same-org · `404` if either object is absent/not visible to the caller's org |
   | `DELETE /api/v1/graphs/{graph_id}/agents/{harness_id}` | detach | `204` · `404` if not bound |
   | `GET /api/v1/capabilities/{harness_id}/graphs` | the workspaces a harness serves (for agent detail) | list of `{graph_id, name}` |

   Naming note: the route says `graphs`/`capabilities` (the real objects); the FE labels them
   "workspace"/"agent" (the user-facing terms) — consistent with the existing nav (Workspaces → graphs).

## Consequences

- **FE #127 unblocks.** It consumes these four endpoints verbatim — list a workspace's agents, attach an
  existing agent, detach, and show an agent's workspaces — with no locally-invented shape (§1.1). The
  "build one in-context" affordance is just the existing agent-builder followed by an attach.
- **Backend work** is one capability-registry migration (`harness_graph_binding`) + the four
  gateway-exposed endpoints + the same-org guard + cascade-on-delete. **No change** to the OHM manifest,
  the graph substrate, or harness execution.
- **Non-breaking.** Existing agents and graphs gain an empty binding set; nothing changes until an edge
  is created. No data migration.
- **Authz stays consistent** with today (org-scoping floor); the `organisation_id` seam carries the edge
  forward to cross-org ReBAC if/when it lands, without a redesign.
- **Plane separation preserved** — control-plane association stays in the registry; tenant knowledge
  content stays in the graph; the portable agent definition (OHM) stays portable.
- **Recorded as a Contract.** The endpoint shapes go into `oraclous-knowledge/flows/interface-contracts.md`;
  paired implementing issues (the backend endpoints; the FE #127 build) link this ADR. The Contract is
  not Done until the gateway exposes the endpoints and the shared shape is enforced.
- **Open for the deciders:** (a) the reverse-lookup path — `/api/v1/capabilities/{harness_id}/graphs`
  vs. a `?graph_id=`/`?harness_id=` query form — is an ergonomics call, defaulted to the nested form
  here; (b) whether members get the read view or no view of a workspace's agents (defaulted to read,
  mirroring capability visibility).
