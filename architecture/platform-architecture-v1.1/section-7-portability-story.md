---
confluence_id: "753728"
title: "Section 7 — Portability Story"
---

# Section 7 — Portability Story

**Related structured artifact:** this section is the architectural narrative for portability — what OHM _does_, how adapters relate to it, how MCP integrates with the Capability Registry. The format itself — fields, canonical serialisation, reference resolution, versioning, typed errors — lives in [OHM v1.0 Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501).

The decision that OHM is the canonical hub for all portability operations is recorded in [ADR-002 — OHM as Canonical Manifest Format](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058). When this section says "adapters route through OHM," the spec defines what they have to produce; ADR-002 records why.

This section defines how Oraclous interoperates with the broader agentic ecosystem. The platform's open-source thesis depends on portability being real: customers must be able to bring their existing agentic work _into_ Oraclous, and take Oraclous-defined work _out_ to other runtimes when their needs change.

The thesis is straightforward: **Oraclous publishes a manifest format (OHM) and a reference runtime, but does not lock customers into either.** A customer who outgrows the reference runtime should be able to export their harnesses and run them elsewhere with minimal friction. A customer arriving from Claude Code, Codex, or any other agentic environment should be able to bring their existing agents and skills with them.

Portability is also the platform's defence against lock-in concerns. Enterprise buyers asking _"what happens if we leave?"_ must have a credible answer that isn't _"you don't."_

## The two directions of portability

Portability has two directions, and they have different design implications:

**Inbound portability** — bringing external artifacts into Oraclous. A Claude Code [SKILL.md](http://SKILL.md) becomes an OHM skill. An MCP server's tools become OHM tools. A Codex agent definition becomes an OHM agent. This is the more common direction, because customers usually arrive at Oraclous with existing work.

**Outbound portability** — taking Oraclous artifacts out to other environments. An OHM harness becomes consumable by a Claude Code workspace. An OHM tool becomes exposed via MCP for any MCP client. An OHM agent becomes runnable in a Codex environment. This is rarer but architecturally critical: without it, Oraclous is a closed substrate dressed as an open one.

Both directions go through **adapters** — capabilities that translate between OHM and external formats. The platform ships a small set of adapters by default; customers can write their own; adapters live in the Capability Registry like any other capability.

---

## OHM as the canonical hub

Every portability operation routes through OHM. This is a deliberate architectural choice — and it matters enough to be explicit:

The platform does _not_ support direct format-to-format translation. A Claude Code skill cannot be translated directly to a Codex agent without first becoming an OHM artifact. This is because:

* Without a canonical hub, every adapter pair requires its own translation logic. Two formats: one adapter. Five formats: ten adapter pairs. Twenty formats: 190 adapter pairs. The cost scales quadratically.
* The canonical hub lets the platform reason about portability as a single concern (does this map cleanly to OHM?) rather than per-format.
* Provenance, versioning, and ReBAC are all OHM-shaped. Adapters that bypass OHM also bypass these guarantees.

So: **all inbound translations produce OHM. All outbound translations start from OHM.** The Capability Registry stores OHM. Adapters are tools that read or write the source/target format on one side and OHM on the other.

This shape is what makes the platform genuinely portable rather than merely interoperable. The difference matters.

---

## Oraclous as an MCP server

Oraclous exposes itself as an MCP server through the Application Gateway. Any MCP-compatible client (Claude Desktop, Cursor, Continue, custom integrations) can connect and consume the workspace's capabilities.

### What's exposed via MCP

The MCP server surface is determined by ReBAC. A connected MCP client authenticates with an integration key (or member credentials), and the server exposes only the capabilities that the authenticated actor has access to in the connected workspace.

The default MCP surface includes:

* **Capabilities exposed as MCP tools** — every OHM tool in the workspace that the actor can invoke becomes an MCP tool. Input/output schemas translate directly (OHM uses JSON Schema, MCP uses JSON Schema).
* **Harnesses exposed as MCP tools** — committed harnesses with the appropriate publishing settings appear as callable tools. Invoking the MCP tool triggers a harness execution; the result is the harness's output.
* **Knowledge graphs exposed as MCP resources** — workspace knowledge graphs are accessible as MCP resources for clients that want direct read access.
* **Task boards exposed as MCP resources** — task board state is readable; some actions (claim a task, complete a task, hand off) are exposed as tools.

### What's NOT exposed via MCP

The MCP server deliberately does not expose:

* **The Substrate's internals** — direct database access, raw ReBAC edits, identity management
* **The full Registry** — only the capabilities accessible to the connected actor, not the workspace inventory
* **Other workspaces' capabilities** — even with elevated ReBAC, the MCP server presents one workspace per connection
* **Platform-update mechanisms** — these are workspace-internal

This selectivity is the MCP server's safety property. External clients see what the platform's governance allows; nothing more.

### Connection authentication

MCP clients authenticate one of three ways:

* **Integration keys** — workspace-scoped, role-bound keys generated by workspace admins. Best for service-to-service integrations.
* **Member credentials** — a member's own credentials authorise their MCP client. The MCP server exposes capabilities scoped to the member's permissions.
* **Agent credentials** — an agent's identity can authenticate an MCP client, with the agent's own capability allocation defining what's exposed. This is useful for AI clients (Claude Desktop, Cursor) acting on a member's behalf.

Each connection establishes the same execution context model the Runtime uses internally: an authenticated actor, a scope, a workspace. Provenance for MCP-initiated actions is identical to provenance for internally-initiated actions.

---

## Oraclous as an MCP client

The other half: Oraclous can consume external MCP servers, bringing their tools into the Capability Registry as native OHM tools.

### How external MCP servers become OHM tools

A workspace admin registers an external MCP server by providing:

* The server's URL (for HTTP/SSE) or invocation command (for stdio)
* Authentication credentials
* The workspace this server's tools should appear in
* An optional scoping filter (only import tools matching a pattern)

The platform then:

1. Connects to the MCP server and enumerates its tools
2. Translates each tool's MCP schema to an OHM tool descriptor
3. Wraps the MCP invocation in an `implementation.type: mcp` handler
4. Registers each translated tool in the Capability Registry with a content hash and a stable id
5. Records the MCP server's metadata (where it came from, when it was synced)

From that point on, the imported tools are first-class OHM capabilities. Agents can be allocated them. Harnesses can route through them. They appear in compiler surveys. The MCP origin is preserved in provenance — every invocation records that the tool came from the external server — but otherwise the tools behave identically to native ones.

### Why this matters

This is what makes Oraclous a _consumer_ of the agentic ecosystem rather than an isolated platform. The growing universe of MCP servers — for databases, code repositories, design tools, infrastructure platforms, productivity apps — all become available to Oraclous workspaces with no per-server engineering work. The platform inherits the ecosystem's momentum.

It also flips the conventional lock-in story. Most platforms ask _"can we lock customers in by being the only place their tools work?"_ Oraclous's answer is the opposite: _"we work with all of your tools, so leaving us doesn't mean abandoning your tooling."_ This is the architectural anti-lock-in commitment, made concrete.

---

## Inbound adapters: external → OHM

The platform ships with adapters for the most common external formats. Each adapter is itself a capability — registered in the Registry, invokable by other harnesses, customisable by the workspace.

### Claude Code [SKILL.md](http://SKILL.md) adapter

Translates Claude Code skill files into OHM skills.

**Source format:** Markdown files with YAML frontmatter, typically located at `~/.claude/skills/<skill-name>/SKILL.md`.

**Translation logic:**

* The YAML frontmatter's `name` becomes the OHM skill's `metadata.name`
* The frontmatter's `description` becomes both `metadata.description` and `spec.description_for_compiler`
* The Markdown body becomes `spec.instructions`
* Any referenced files in the skill directory (auxiliary docs, example data) are attached as supplementary content
* The skill's resource budget and trigger conditions are mapped where possible; gaps are flagged in conversion notes

**Lossy elements:**

* Claude Code's per-skill model selection (if present) becomes a hint rather than a hard constraint, since OHM agents reference workspace-level LLM config
* Claude Code's filesystem-rooted resource references must be re-anchored to the workspace's substrate

The adapter produces an OHM document that round-trips: the [SKILL.md](http://SKILL.md) → OHM → [SKILL.md](http://SKILL.md) path preserves semantics, though not necessarily byte-for-byte identity.

### MCP tool adapter

Translates MCP tool definitions into OHM tools. Covered in detail in the previous subsection. The adapter is the most-used inbound adapter because MCP is the broadest external format.

### OpenAPI / REST adapter

Translates OpenAPI 3.x specifications into OHM tools, one tool per operation.

**Source format:** an OpenAPI document (YAML or JSON).

**Translation logic:**

* Each operation (`GET /users/{id}`, `POST /messages`, etc.) becomes a separate OHM tool
* Path parameters, query parameters, and request body schemas combine into the tool's input schema
* Response schemas become the output schema
* Authentication declared in the OpenAPI security schemes becomes credential requirements
* The operation's `summary` and `description` become the tool's compiler-facing description

**Why this matters:** vast amounts of enterprise functionality lives behind OpenAPI-documented REST APIs. This adapter is how those APIs become workspace capabilities without per-API engineering.

### Codex agent definition adapter

Translates Codex agent definitions into OHM agents.

**Source format:** Codex's agent specification (the exact shape depends on Codex's published format at adapter implementation time).

**Translation logic:**

* The Codex agent's role/system prompt becomes the OHM agent's `spec.role`
* The Codex agent's tool list maps to capability allocation (with each Codex tool translated via the MCP adapter if it's MCP-shaped, or via custom translation otherwise)
* The Codex agent's model config becomes the OHM agent's `spec.llm_config`

**Lossy elements:**

* Codex agents may have execution patterns (planning loops, reflection cycles) that map to OHM differently. The translation produces an OHM agent that's _closest_ to the original behaviour; exact replication is not guaranteed.

### Custom adapters

Customers can write their own adapters. The adapter contract is minimal: a capability that accepts a source-format input and emits OHM. Adapters can be tools (one-shot translation), skills (provide guidance for an agent that does the translation), or full sub-harnesses (for complex multi-step conversions).

Custom adapters are how the platform stays open-ended. Enterprise customers with proprietary agent formats can build adapters once and bring their entire agent inventory into Oraclous without per-agent migration work.

---

## Outbound adapters: OHM → external

The reverse direction: exporting OHM artifacts for use in other runtimes.

### OHM → Claude Code [SKILL.md](http://SKILL.md)

The inverse of the inbound Claude Code adapter. Takes an OHM skill and produces a [SKILL.md](http://SKILL.md).

**Translation logic:**

* `metadata.name` → frontmatter `name`
* `spec.description_for_compiler` → frontmatter `description`
* `spec.instructions` → Markdown body
* Capability requirements are flagged as comments in the [SKILL.md](http://SKILL.md), since Claude Code resolves capabilities differently

**Lossy elements:**

* Versioning is dropped (Claude Code doesn't have a versioning model for skills)
* ReBAC scopes are dropped (Claude Code is single-user)
* Cross-skill capability references become external references the user must resolve

### OHM tool → MCP exposure

OHM tools can be exposed via the Oraclous MCP server (covered earlier) or exported as standalone MCP server definitions. The standalone export produces a small MCP server definition (a JSON file plus any wrapper code) that an external user can run independently to expose the tool.

**Use case:** a customer builds a powerful tool in Oraclous, then wants to make it available to their Claude Code environment without keeping the tool in Oraclous. They export the tool to a standalone MCP server and discontinue the Oraclous dependency.

### OHM harness → execution recipe

This is the most complex outbound direction. An OHM harness contains orchestration, actors, schedules, policies — much of which has no direct equivalent in simpler runtimes.

The platform offers two outbound modes for harnesses:

**Full export** — emits a recipe document (Markdown with embedded structured blocks) that describes the harness in human-readable form. This is for documentation, audit, and migration planning. It is not directly executable by other runtimes.

**Compatible export** — for each major external runtime (Claude Code workspaces, Codex projects, LangGraph applications), the platform offers a best-effort translator that produces a runnable approximation. The translator is honest about what gets lost: a harness with HITL gates exported to a single-user environment loses the HITL gates (or converts them to inline pauses). A harness with cross-workspace traversal exported to a single-workspace environment loses traversal.

**Lossy elements are explicit.** The exporter generates a "compatibility report" alongside the exported artifact, listing exactly what was dropped or transformed. Customers know exactly what they're getting.

The honest framing: **harnesses are most portable as concepts, less so as runnable artifacts.** A harness defined in Oraclous can be _understood_ in any environment, but only fully _executed_ by an OHM-capable runtime. This is acceptable because customers leaving Oraclous typically want migration support, not transparent runtime substitution.

---

## The bidirectional case: working across Oraclous and Claude Code

A useful concrete example, because this is the most realistic interop scenario:

A developer works in Claude Code on their laptop, using their team's set of [SKILL.md](http://SKILL.md) files for code review, PR drafting, and architecture analysis. Their team's workspace in Oraclous has the same skills — synced via the bidirectional adapter — and other team members can invoke them through Oraclous's UI or task boards.

The interop flow:

**Initial sync.** The developer (or workspace admin) configures the Claude Code skills directory as an inbound source. The adapter syncs [SKILL.md](http://SKILL.md) files into the workspace as OHM skills. From the team's perspective, the skills are available to any team member, in any Oraclous harness.

**Authoring in Claude Code.** The developer creates a new [SKILL.md](http://SKILL.md) locally. On next sync (manual or scheduled), the adapter detects the new skill and registers it as an OHM skill in the workspace, with the developer recorded as the author. Other team members can immediately use it.

**Authoring in Oraclous.** Another team member creates a new OHM skill through Oraclous's UI. The outbound adapter (configured to write back to the Claude Code skills directory) emits a [SKILL.md](http://SKILL.md) the developer sees on their next Claude Code session. The two-way flow is symmetric.

**Conflict resolution.** When the same skill is edited in both places between syncs, the adapter flags the conflict. Resolution is interactive — the workspace admin sees the two versions, picks one or merges, and the merged result becomes the canonical version (with provenance recording the merge).

**Authority preservation.** The OHM version is canonical for the workspace. The [SKILL.md](http://SKILL.md) is a synchronised copy. When in doubt, the OHM version wins; the [SKILL.md](http://SKILL.md) is regenerated from it. This is the architectural commitment: OHM is canonical, external formats are projections.

The same pattern works for other bidirectional sources: MCP servers (more limited — usually inbound-only), Git repositories of agent definitions (full bidirectional with the repository as source of truth or as projection, configurable), team knowledge bases.

---

## Default adapters shipped with the platform

The platform ships these adapters in the default capability inventory for new workspaces:

* **MCP tool adapter** (inbound + outbound) — for connecting to and exposing MCP servers
* **Claude Code** [**SKILL.md**](http://SKILL.md) **adapter** (inbound + outbound) — bidirectional
* **OpenAPI adapter** (inbound only) — for importing REST APIs as tools
* **OHM-to-Markdown documentation adapter** (outbound only) — produces human-readable docs from any OHM artifact

These cover the common cases. Customers writing custom adapters for other formats add them as capability packs (the OHM `capability_pack` kind), which can be shared across workspaces or published to the community.

---

## What portability does NOT cover

Honest constraints, named explicitly:

**Knowledge graph data.** Knowledge graphs are workspace-internal. Portability for graph data is a separate concern handled through standard export formats (Neo4j dumps, RDF, JSON-LD) — not through OHM. OHM references graphs but does not contain them.

**Member directory and ReBAC graph.** These are platform-internal. Migrating users and permissions between Oraclous workspaces, or between Oraclous and another platform, is an operational concern, not a manifest concern.

**Provenance history.** Provenance is queryable via APIs but is not designed to be portable. A harness exported to another runtime starts with empty provenance there. The Oraclous-side provenance for past executions remains in the Substrate.

**Credentials.** Credentials never leave the credential broker. A harness exported to another runtime gets capability references that the destination runtime must resolve with its own credentials. The platform does not export secrets in any form.

**Per-actor consciousness records.** Consciousness is per-agent and substrate-anchored. Exporting an agent to another runtime exports its OHM definition but not its accumulated consciousness. The destination agent starts fresh.

Each of these constraints is intentional. Portability is about manifests and capabilities — the things that _define_ work. Data, identity, secrets, and accumulated learning are workspace-internal concerns with their own migration paths.

---

## The portability principle, restated

Every architectural decision in this section serves one principle:

> **Oraclous publishes a format and a runtime, not a destination.** Customers can arrive with their existing work and leave with the work they've built. The platform's value is the substrate it provides, not the data it captures.

This is the open-source thesis made operational. A customer evaluating Oraclous can verify the portability story themselves — by checking that adapters exist, by inspecting OHM as a documented format, by testing the export flow. The platform's commitment is verifiable, not aspirational.

This is also the lock-in defence: a customer asking _"what happens if we want to leave?"_ can be shown the export tooling, the adapter inventory, and the OHM specification. The honest answer to lock-in is portability, demonstrated.
