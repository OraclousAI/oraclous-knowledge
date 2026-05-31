---
confluence_id: "425993"
title: "Section 4 — Manifest Format Specification"
---

# Section 4 — Manifest Format Specification

**Related structured artifact:** the implementation-ready specification of OHM v1.0 now lives as a standalone sibling page: [OHM v1.0 — Standalone Specification](https://oraclous.atlassian.net/wiki/spaces/OP/pages/393501).

This section is the _architectural narrative_ for OHM — why it exists, what shape it takes, what its zones mean, and how adapters relate to it. The standalone spec is the _implementation contract_ — field-by-field schema, canonical serialisation rules, reference resolution semantics, versioning commitments, and typed error categories.

When the two disagree, the standalone spec is authoritative for the format itself; this section is authoritative for the architectural rationale. The decision to make OHM the canonical manifest format is recorded in [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058).

This section defines **OHM** — the Oraclous Harness Manifest format. It is the platform's portable contract: the serialised form of every harness, capability, and composable artifact. It is also the format used for adapters to and from external runtimes (Claude Code, Codex, MCP).

## Format choice and rationale

OHM is **YAML with embedded Markdown blocks**.

* **YAML** for the structured zone (actors, capabilities, scopes, schedules, policies, version references). YAML's anchors and references handle capability reuse cleanly, and every YAML parser handles it natively.
* **Markdown blocks for prose** (role descriptions, orchestration rules, hand-off conditions, escalation criteria). Markdown is the natural format for LLM-consumed prose; it lives inside YAML block scalars without escaping pain.
* **File extension:** `.ohm.yaml` (or `.ohm.yml`). A standard `.yaml` extension is also valid — the format is recognised by content, not extension.

This choice is final for v1. Adapters can translate OHM to and from other formats (JSON, Markdown frontmatter, custom DSLs) but the canonical internal representation is OHM.

## Versioning model

Every composable artifact in Oraclous — tools, skills, agents, harnesses, the compiler, consciousness skills — has both a **content hash** and an optional **semver tag**.

* **Content hash** (always present, automatic, immutable) — a `sha256:...` digest of the artifact's canonical serialisation. Used by provenance, by the runtime when resolving exact dependencies, and by the substrate for storage deduplication.
* **Semver tag** (optional, human-assigned, mutable) — a label like `1.2.3` or `compiler-default@2.0` that humans use to refer to versions. Multiple semver tags can point to the same hash.

The manifest references dependencies by **either** hash (for reproducibility) **or** semver tag (for human readability). The substrate resolves either to the same artifact. Best practice in user-authored manifests: tags. Best practice in machine-authored or audit-anchored manifests: hashes.

---

## The OHM document structure

Every OHM document has the same top-level shape:

```yaml
ohm: 1                          # Format version
kind: harness                   # harness | tool | skill | agent | capability_pack
id: <stable-identifier>         # Stable id within the workspace
version:
  hash: sha256:abc123...        # Automatic content hash
  tags: ["1.2.0", "stable"]     # Optional human-readable tags

workspace: <workspace-id>       # Scoping workspace

metadata:
  name: <human-readable-name>
  description: <one-line>
  authors: [...]
  created_at: <iso8601>
  updated_at: <iso8601>

# Kind-specific body follows
spec:
  ...
```

The `ohm: 1` declaration is the format version. Future major versions of OHM will increment this; runtimes can refuse to load incompatible versions safely.

The `kind` field determines the shape of `spec`. We define each kind below.

---

## Kind: `tool`

A tool is a deterministic capability with structured input and output.

```yaml
ohm: 1
kind: tool
id: google-drive-reader
version:
  hash: sha256:...
  tags: ["2.1.0"]

workspace: workspace-tech

metadata:
  name: Google Drive Reader
  description: Read files from Google Drive with OAuth-scoped access.

spec:
  implementation:
    type: internal           # internal | mcp | http | external_adapter
    handler: google_drive_reader.GoogleDriveReader
  
  input_schema:
    type: object
    required: [file_id]
    properties:
      file_id:
        type: string
        description: Google Drive file ID
      extract_content:
        type: boolean
        default: true
  
  output_schema:
    type: object
    properties:
      content: { type: string }
      metadata: { type: object }
  
  credential_requirements:
    - type: oauth_token
      provider: google
      scopes: [drive.readonly]
  
  description_for_compiler: |
    # When to use this tool
    
    Use Google Drive Reader when you need to fetch the contents of a 
    specific file from Google Drive. Best for documents, spreadsheets, 
    and plain text. Not suitable for folder listings &mdash; use the folder 
    capability instead.
    
    # Limitations
    
    - Returns at most 10MB of content per call
    - Binary formats are converted to text where possible
    - Permissions must be granted by the file owner via OAuth
```

Key elements:

* `implementation.type` — `internal` for tools that live in Oraclous's tool library, `mcp` for MCP-served tools, `http` for direct HTTP endpoints, `external_adapter` for tools wrapped via an adapter capability.
* `description_for_compiler` — the Markdown prose block the compiler reads when planning. This is the LLM-facing documentation. It is **not** the same as `metadata.description` (which is for humans browsing the registry).
* `credential_requirements` — declarative; resolved by the Substrate's credential broker at runtime.

---

## Kind: `skill`

A skill is a prose-defined behavioural module an actor loads to handle a class of task. Skills do not execute — they _instruct_.

```yaml
ohm: 1
kind: skill
id: cold-outreach-drafter
version:
  hash: sha256:...
  tags: ["1.0.0"]

workspace: workspace-marketing

metadata:
  name: Cold Outreach Drafter
  description: Draft cold outreach messages tuned to specific ICPs.

spec:
  loaded_when: |
    The actor needs to draft a cold outreach message &mdash; email, LinkedIn DM, 
    or other direct outreach to a person who hasn't engaged with us before.
  
  capability_requirements:
    - id: company-research-tool
      version_tag: stable
    - id: writing-style-guide
      kind: skill
      version_tag: stable
  
  instructions: |
    # Cold Outreach Drafting
    
    When drafting a cold outreach message:
    
    1. **Research first.** Use the company-research-tool to understand the 
       recipient's recent activities, role, and current priorities.
    
    2. **Match register to ICP.** Founders get founder language. 
       Enterprise buyers get enterprise language. Tone follows audience.
    
    3. **One ask per message.** Never combine more than one ask. If you 
       need two things, draft two messages or escalate.
    
    4. **Personalise the first line.** No generic openers. The first line 
       must reference something specific to the recipient.
    
    5. **Soft close.** End with a low-friction next step ("Open to a 
       15-minute call next week?") not a hard ask.
    
    # Tone constraints
    
    - No exclamation marks
    - No emojis unless the recipient uses them in public channels
    - Subject lines under 50 characters
    - Body under 120 words
    
    # When to escalate to a human
    
    - If the recipient is a current or former customer
    - If the message touches contractual or legal matters
    - If you're uncertain about cultural register
  
  description_for_compiler: |
    Load this skill when planning any outreach to non-engaged prospects. 
    Pairs well with the company-research-tool. Do not use for re-engagement 
    of existing customers &mdash; use the customer-followup skill instead.
```

Key elements:

* `loaded_when` — prose condition the runtime evaluates (via the agent) to decide if this skill applies. Like Claude Code's SKILL.md `description` field.
* `capability_requirements` — capabilities this skill expects to use. Declarative — the runtime ensures these are allocated to the agent before the skill is loaded.
* `instructions` — the actual behavioural content. Pure Markdown. The agent reads this when the skill is loaded.
* `description_for_compiler` — concise summary the compiler uses when planning.

---

## Kind: `agent`

An agent is a non-human actor with identity, role, capability allocation, and optionally a sub-harness.

```yaml
ohm: 1
kind: agent
id: outreach-drafter-agent
version:
  hash: sha256:...
  tags: ["1.0.0"]

workspace: workspace-marketing

metadata:
  name: Outreach Drafter
  description: Drafts cold outreach across channels.

spec:
  role: |
    # Role
    
    You are the Outreach Drafter for the Marketing workspace. You draft 
    cold outreach messages to prospects identified by the Lead Researcher. 
    You hand off finished drafts to the Brand Reviewer (human) for approval 
    before they are sent.
    
    # Responsibilities
    
    - Draft outreach across email, LinkedIn, and other channels
    - Match register and tone to the prospect's ICP
    - Flag drafts that need human judgment
    - Update the consciousness record with patterns you notice
    
    # What you do NOT do
    
    - You never send messages directly
    - You never make commitments on behalf of the company
    - You never draft for existing customers (escalate instead)
  
  llm_config:
    # Three-level resolution: agent &rarr; workspace &rarr; organisation
    # When provider_ref is set to a specific provider, it overrides the
    # inherited default. When omitted or set to "inherit", the workspace's
    # default applies, which itself inherits from the organisation.
    provider_ref: workspace-default     # Or: anthropic | openai | openrouter | azure-openai | aws-bedrock | self-hosted
    model_constraint: "claude-sonnet or equivalent"
    # Optional: pin a specific model for reproducibility
    # model: claude-sonnet-4-5-20250929
  
  capabilities:
    - id: cold-outreach-drafter
      kind: skill
      version_tag: stable
    - id: company-research-tool
      kind: tool
      version_tag: stable
    - id: writing-style-guide
      kind: skill
      version_tag: stable
  
  scope:
    workspaces: [workspace-marketing]
    delegated_from: ~                   # Set when agent acts on member's behalf
  
  consciousness:
    enabled: true
    pattern: skill_per_agent            # skill_per_agent | team_agent | workspace_agent
    skill_ref:
      id: default-consciousness-skill
      version_tag: stable
    permissions:
      can_record_observations: true
      can_suggest_tools: true           # Escalates to human for approval
      can_auto_create_tools: false
      can_propose_harness_changes: true # Routed through harness-review system
  
  sub_harness: null                     # No nested harness for this agent
```

Key elements:

* `role` — the prose system prompt for the agent, in the structured/prose hybrid the runtime understands.
* `llm_config` — references the workspace's LLM config service rather than embedding model details directly. This makes the agent portable across providers.
* `capabilities` — the explicit allocation. The runtime will refuse to dispatch any capability not in this list.
* `scope` — where the agent can act. `delegated_from` is the member identity the agent borrows for actions requiring elevated access.
* `consciousness` — declarative. Pattern selection (per-agent skill vs team agent vs workspace agent), permissions, and the skill that defines the consciousness behaviour.
* `sub_harness` — for recursive agents, a reference to a nested harness. Most agents have `null` here.

---

## Kind: `harness`

The central kind. A harness orchestrates multiple actors to accomplish a goal.

```yaml
ohm: 1
kind: harness
id: outreach-pipeline
version:
  hash: sha256:...
  tags: ["1.0.0", "production"]

workspace: workspace-marketing

metadata:
  name: Cold Outreach Pipeline
  description: End-to-end outreach from lead identification to sent message.
  authors: ["[email protected]"]

spec:
  goal: |
    Identify high-fit prospects from our ICP, draft personalised outreach 
    across email and LinkedIn, get human approval for sensitive cases, 
    and track responses through to first meeting booked.
  
  actors:
    - id: lead-researcher
      kind: agent
      ref:
        id: lead-researcher-agent
        version_tag: stable
    
    - id: drafter
      kind: agent
      ref:
        id: outreach-drafter-agent
        version_tag: stable
    
    - id: brand-reviewer
      kind: human_role
      role: brand_lead
      fallback: 
        role: marketing_director
    
    - id: sender
      kind: agent
      ref:
        id: outreach-sender-agent
        version_tag: stable
  
  task_board:
    columns:
      - id: backlog
        name: Backlog
      - id: researching
        name: Researching
      - id: drafting
        name: Drafting
      - id: in_review
        name: In Review
      - id: ready_to_send
        name: Ready to Send
      - id: sent
        name: Sent
      - id: blocked
        name: Blocked
    
    default_assignee: lead-researcher
    
    definition_of_done: |
      A task is done when:
      - An outreach message has been sent through the appropriate channel
      - The prospect's record in the CRM has been updated with the send
      - A follow-up task has been created if a response is expected
  
  orchestration: |
    # How work flows through this harness
    
    1. **Backlog &rarr; Researching**: When a new prospect appears in the 
       backlog, the lead-researcher picks it up, conducts research, 
       and either advances it to drafting or rejects it back to 
       backlog with a reason.
    
    2. **Researching &rarr; Drafting**: The drafter receives the researched 
       prospect and produces a draft message.
    
    3. **Drafting &rarr; In Review**: All drafts go to the brand-reviewer 
       for human approval. The drafter does not skip review except 
       for prospects matching the "safe to send" criteria (see below).
    
    4. **In Review &rarr; Ready to Send**: Reviewer approves. Or sends back 
       to drafting with feedback.
    
    5. **Ready to Send &rarr; Sent**: The sender executes the actual send.
    
    # Safe-to-send criteria
    
    Drafts may skip In Review and go directly to Ready to Send if all 
    of these are true:
    - The prospect is in the "warm intro" category (we have a mutual 
      connection)
    - The message length is under 80 words
    - No commitments or pricing are mentioned
    
    # Conflict resolution
    
    If the drafter and reviewer disagree on register or message direction 
    more than twice, open a round-table including the marketing-director.
    
    # Escalation
    
    Escalate to marketing-director when:
    - A prospect is a former customer (consciousness should flag this)
    - The drafter is uncertain about cultural register
    - The reviewer rejects three drafts in a row
  
  triggers:
    - type: schedule
      cron: "0 9 * * MON-FRI"           # Weekday mornings
      action: check_backlog
    - type: webhook
      endpoint: /webhooks/new-prospect
      action: enqueue_to_backlog
    - type: manual
      allowed_actors: [marketing_director, brand_lead]
  
  policies:
    budget:
      max_llm_tokens_per_run: 50000
      max_tool_invocations_per_run: 30
      max_concurrent_runs: 5
    
    hitl:
      required_at:
        - transition: drafting -> in_review
          assignee: brand-reviewer
          notification_channels: [task_board, email]
          escalation_after_hours: 24
          escalation_channel: 
            type: pagerduty
            severity: low
    
    output_redaction:
      patterns:
        - type: pii
          action: flag
        - type: pricing
          action: block
  
  cross_workspace:
    federation_default: true
    allowed_traversals:
      - to: workspace-product
        purpose: "Read product positioning for outreach context"
        scope_required: [product.read]
  
  consciousness:
    team_record: workspace-marketing-consciousness
```

Key elements:

* `goal` — the prose goal. This is the operator's original intent, preserved through compilation. Used by the compiler when proposing updates, and by humans when reviewing the harness.
* `actors` — the roster. Each actor has an `id` (local to this harness), a `kind` (agent, human_role, tool, harness), and a `ref` (resolves to a registered capability). Human roles include fallback resolution.
* `task_board` — declared inline. Columns, default assignee, and definition of done. The substrate creates an instance of this board when the harness is committed.
* `orchestration` — the prose orchestration spec. This is the largest prose block in a typical harness.
* `triggers` — declarative. Multiple triggers can fire the same harness.
* `policies` — coded constraints. Budget caps, HITL gates, output redaction. The runtime enforces these regardless of what the prose says.
* `cross_workspace` — federation traversal rules. Declarative.
* `consciousness` — team-level consciousness sharing, if enabled.

---

## Kind: `capability_pack`

A capability pack is a versioned bundle of capabilities. Used for distributing related tools and skills together, and for adapters from external runtimes.

```yaml
ohm: 1
kind: capability_pack
id: claude-code-skills-importer
version:
  hash: sha256:...
  tags: ["1.0.0"]

workspace: workspace-tech

metadata:
  name: Claude Code Skills Importer
  description: Imports Claude Code SKILL.md files as Oraclous skills.

spec:
  pack_kind: adapter
  
  source:
    type: claude_code
    path: ~/.claude/skills/
  
  conversion:
    skill_mapper: claude-code-skill-adapter@1.0.0
  
  contents:
    - kind: skill
      source_ref: code-review-skill
      target_id: code-review
      target_version_tag: "1.0.0"
    - kind: skill
      source_ref: pr-summary-skill
      target_id: pr-summary
      target_version_tag: "1.0.0"
```

Capability packs are how the platform makes external runtimes portable. A pack declares: _here is a bundle of capabilities, here is where they come from, here is the adapter that converts them to OHM._ The adapter is itself a capability, recursively.

---

## The two zones, made concrete

Looking across the examples above, the **structured zone** is everything that lives directly in YAML fields:

* `kind`, `id`, `version`, `workspace`, `metadata`
* `actors[].id`, `actors[].kind`, `actors[].ref`
* `capabilities[]`, `scope`, `consciousness.permissions`
* `task_board.columns`, `triggers[]`, `policies`
* `cross_workspace.allowed_traversals`

The **prose zone** is everything inside Markdown block scalars (the `|`-prefixed YAML strings):

* `metadata.description` (when long)
* `description_for_compiler`
* `instructions` (skill body)
* `role` (agent body)
* `goal`, `orchestration`, `task_board.definition_of_done`

The runtime enforces the structured zone. The model interprets the prose zone. **A prose instruction that contradicts a structured policy never overrides the policy.** If the orchestration prose says "skip review for high-priority prospects" but the `policies.hitl.required_at` declares review is mandatory, the runtime enforces review regardless of what the prose says.

This is the architectural guarantee that makes prose orchestration safe.

---

## Bootstrap manifests

When a new workspace is created, the Substrate seeds it with a set of starter OHM documents. **These become workspace-owned artifacts from the moment of creation.** The platform never modifies them after creation; updates flow as proposals the customer can accept or ignore.

The seed set for v1 includes:

* A **default compiler harness** — the harness that turns goals into manifests
* A **default consciousness skill** — the prose contract for what consciousness records and when
* A **default capability inventory** — only the tools and skills required for the workspace to function
* A **default task board** for the workspace itself (separate from per-harness boards)
* A **default policy template** — sensible defaults for budgets and HITL

Each of these is a separate OHM document, committed as-is. Customers can read, fork, edit, replace them — using the same OHM format and the same APIs as any other harness.

### How platform updates reach a workspace

Oraclous maintains a separate **reference catalog** of latest defaults, outside customer workspaces. When the platform publishes a new version of any default, each workspace receives a notification with a diff. Customers can:

* Accept the new default (overwrites their current version, with a rollback option)
* Selectively merge changes
* Ignore the update entirely
* Install a `platform-update-watcher` harness that auto-accepts non-breaking updates on their behalf

This preserves Oraclous's sovereignty principle end to end. **Nothing in the workspace is owned by the platform; everything is owned by the customer.** Updates are offered, never imposed.

---

## Adapter contract for external formats

OHM is canonical. External formats (Claude Code SKILL.md, Codex agent definitions, MCP tool schemas, others) are translated via **adapters**.

An adapter is itself a capability (usually a tool or capability_pack) that:

* Reads a source format
* Emits OHM
* Or in the reverse direction: reads OHM and emits the target format

The adapter contract is minimal:

```yaml
# Pseudo-schema for adapter capabilities
adapter:
  source_format: claude_code_skill
  target_format: ohm_skill
  input_schema: { ... }    # What the source format looks like
  output_schema: { ... }   # OHM kind: skill
  conversion_rules: |
    Description of what gets mapped where, what's lossy, what's preserved.
```

The platform ships adapters for the major external formats. Customers can write their own. Adapters live in the Capability Registry like any other capability.
