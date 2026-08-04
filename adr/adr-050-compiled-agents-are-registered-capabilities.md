# ADR-050 — Compiled Agents Are Registered Capabilities; `manifest_ref` Is the Registry Id

## Status

| | |
| --- | --- |
| Status | **Proposed** |
| Date | 2026-08-04 |
| Deciders | Drafted by `solution-architect`; **pending CTO acceptance** |
| Driving issue | [oraclous-backend#695](https://github.com/OraclousAI/oraclous-backend/issues/695) (E10) — the compiler never registers the agents it generates |
| Amends | **ADR-031 §124** — replaces the `org:<org>/research-agent@3` reference form with the registry id, and removes the version suffix |
| Builds on | ADR-002 (resolution semantics) · ADR-031 (OHM v1.1 team manifest) · ADR-032 (capability ceiling) · ADR-047 §45 (the recorded deviation) · ADR-048 (team lifecycles) |

## Context

A compiled team member and an agent built in the console builder are the same object: an `OHMManifest` with `metadata.kind: "agent"`, produced by the same generator (`build_subharness`). They are not treated as the same object.

The console builder files its agent through `POST /api/v1/capabilities` as a `kind: harness` descriptor, takes the returned id, and stores that id as the member's `manifest_ref`. From there the agent lists on the agents page, opens in the builder, and binds to a workspace.

The compiler files nothing. It stamps each member `manifest_ref: "org:compiled/<role>@1"` and ships the generated manifests inline in `engine_team_drafts.sub_harnesses`. In the reporting organisation, `capability_descriptors` held twenty-six rows, all `kind: tool` and none `kind: harness`, while two stored drafts carried four and fourteen inline members between them. A user who compiled a fourteen-agent team reported that none of them appeared on the agents page. The page was correct; nothing had been written for it to read.

ADR-031 §124 already specifies the reference form as the design, and its example member carries `manifest_ref: "org:<org>/research-agent@3"` — organisation-namespaced, versioned, resolved from the registry. ADR-047 §45 records the deviation inside the compiler's own output contract, noting that a team "loads but cannot run" because its `manifest_ref`s resolve to nothing registered. So the gap is a conformance gap against a decision already taken, with two loose ends the original decision did not settle.

The first loose end is that the reference form in ADR-031 is not resolvable by the shipped resolver, and never was. `RegistryClient.get_capability` interpolates its argument directly into a path (`GET /api/v1/capabilities/{capability_id}`); a reference containing a slash produces a different URL rather than a lookup. Implementing the ADR form as written would require a per-organisation name-uniqueness constraint and a version resolver, neither of which exists anywhere in the platform.

The second loose end is that the runtime dispatches from the inline sub-harness when one is present and consults `manifest_ref` only when it is absent. That means the inline dictionary is not merely a workaround: on a run record it is the record of what actually executed. Any move to references has to decide what happens to that record.

## Decision

1. **`manifest_ref` is the registry capability id.** The resolvable form of a member's sub-harness reference is the identifier `GET /api/v1/capabilities/{id}` already accepts. ADR-031 §124's `org:<org>/research-agent@3` example is amended to the id form. The console builder already produces this form; a compiled member and a console-built agent are the same object and therefore carry the same kind of reference. An opaque identifier also carries no namespace, so organisation scoping is enforced by an organisation-scoped registry read rather than by parsing a string — a more robust place for it than a reference format that a caller supplies.

2. **The version suffix is removed, not deferred.** There is no version axis on a registered agent. Editing an agent mutates its descriptor, and every team referencing it observes the change on its next run; that is the reuse semantic, stated plainly rather than hidden behind a resolver. Decision 4 is what makes this safe. If per-team pinning is later wanted, it is a new decision with a use case behind it, and its natural shape is a pinned snapshot on the referencing draft rather than a version string inside the reference.

3. **Registration happens at draft persistence, not on every compile.** A compiler run becomes a stored team draft only when the console explicitly saves it; a compile the user abandons registers nothing. Each agent member of a persisted draft is registered as one `kind: harness` capability in the owning organisation, and the member's `manifest_ref` becomes the returned id. Registration is find-or-refresh, keyed on the descriptor's own manifest id within the owning organisation, so a repeat save or a draft replacement updates the existing row rather than creating a duplicate. Registration is fail-closed: a registry failure fails the draft write, because a half-registered draft is worse than an unsaved one.

4. **A run record keeps a resolved snapshot; a draft keeps only references.** A persisted draft stops carrying inline sub-harnesses for its registered agent members, so there is one source of truth for what an agent is. At team-run creation the engine resolves each member's reference and writes the resolved manifests onto the run record, which is then the record of what executed and keeps an old run replayable after its agents are edited. The dispatch path is unchanged: it still finds a per-role sub-harness, because the snapshot is that sub-harness. Resolution is one step at run creation, not a change to the executor.

5. **The capability ceiling is unaffected.** The harness intersects a member's declared `tools[]` against the resolved manifest on the reference path explicitly, so ADR-032 continues to hold for a registered member. A registered agent whose descriptor is later edited to declare a wider capability set than the referencing member declared still dispatches at the member's narrower ceiling.

## Consequences

- The agents page, the builder, and workspace bindings work for compiled agents without further work, because all three read the registry rows this decision creates.
- A later team can reference an existing registered agent instead of generating a near-duplicate. That reuse is the point of the change and is also its main hazard: editing a shared agent changes the future behaviour of every team pointing at it. Decision 4 bounds the hazard to future runs; past runs are immutable.
- Two follow-ons are opened by this decision and are deliberately not blockers: a reverse index answering "which teams reference this agent" before an edit, and a delete guard for an agent that a stored draft still references.
- Existing drafts carrying inline sub-harnesses and unresolvable `org:compiled/<role>@1` references keep running unchanged, because the dispatch path prefers an inline sub-harness when one is present. No data migration is required.
- ADR-031 carries an "Amended by ADR-050" note against §124 for the reference form and the removed version suffix. ADR-047 §45's recorded deviation is closed by this decision rather than left standing.
- The reference format decision does not touch the compiler's capability-absence gate. That gate normalises member tool bindings, not member references, so the masquerade protection it provides is unchanged in both directions. The imported-MCP tool reference shape resolves through a separate name-slug resolver on a separate field and is likewise unaffected.

## Alternatives considered

- **Teach the resolver ADR-031's `org:<org>/<name>@<version>` form.** Rejected. It requires a per-organisation name-uniqueness constraint and a version resolver that do not exist, it introduces a second reference form beside the one the console builder already produces, and a caller-parsed namespace is a weaker place to enforce organisation scoping than an organisation-scoped read.
- **Register on every compile.** Rejected. A compile is an experiment; two drafts in one organisation would have produced eighteen library entries. A library filled with abandoned experiments is not a library.
- **Register always, with a draft lifecycle on the agent.** Rejected. It reaches the same outcome as Decision 3 at the cost of a second state machine on the capability, duplicating the draft state the team draft store already holds.
- **Keep inline sub-harnesses on the draft alongside the references.** Rejected. Two copies of each agent means editing the registered one silently does not affect the team, which makes the reuse benefit cosmetic while carrying its full cost.
- **Add a version axis so an edit never changes an existing team.** Rejected for now. The run snapshot in Decision 4 already protects history, which is the property a version axis would otherwise be protecting; adding one now buys a second concept and a resolver for no protection that is not already present.

## See also

- `adr/adr-031-ohm-v1.1-team-manifest.md` §124 — the amended reference contract
- `adr/adr-047-harness-compiler-planner.md` §45 — the recorded deviation this closes
- `adr/adr-002-ohm-as-canonical-manifest-format.md` — resolution semantics
- `adr/adr-032-capability-absence-structural-gate.md` — the ceiling that continues to hold
- [oraclous-backend#695](https://github.com/OraclousAI/oraclous-backend/issues/695) — the driving issue, carrying the measured evidence
- [oraclous-backend#694](https://github.com/OraclousAI/oraclous-backend/issues/694) — edits the same seam; ships in the same pull request
