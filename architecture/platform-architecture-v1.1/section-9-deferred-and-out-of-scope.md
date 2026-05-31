---
confluence_id: "65988"
title: "Section 9 — Deferred and Out-of-Scope"
---

# Section 9 — Deferred and Out-of-Scope

This section names what Oraclous v1 deliberately does **not** include, what is genuinely deferred to later versions with clear criteria for when it becomes in-scope, and what is permanently out of scope.

The purpose is to **prevent scope creep during implementation**. Without an explicit scope line, every implementation decision risks expanding into adjacent territory. Engineers face requests, see plausible extensions, and accept work that wasn't part of the v1 plan. Each addition seems small; the cumulative effect is delivery delay and architectural drift.

This section is the rejection criterion. When a feature is proposed during implementation, the test is: _is it in the in-scope list from Sections 1-8, or is it on the deferred or out-of-scope list here?_ If the latter, the answer is "not now" — with the deferral or rejection rationale already documented.

The section divides into three parts:

* **Deferred to v2** — features the platform should have eventually, with reasoning for why they wait
* **Deferred indefinitely** — features that may or may not happen, depending on customer demand and ecosystem evolution
* **Out of scope permanently** — features the platform explicitly will not build, regardless of demand

Each entry includes the rationale, so future maintainers and contributors understand the choice rather than just inheriting the restriction.

---

## Deferred to v2

These are features the platform should have, but does not need at v1. They are explicitly named so engineering doesn't accidentally implement them piecemeal.

### Multi-modal modalities beyond text-and-structured

**Status:** Documented in Section 3's multi-modal substrate commitments as "additive, not yet implemented."

**What v1 supports:** Text, documents (PDFs, DOCX), structured data (CSV, JSON, relational), code, temporal data (bitemporal records).

**What v2 adds:** Images (perceptual embeddings + OCR), audio (transcription + acoustic embeddings), video (frame-based perceptual + transcription), design files (Figma, Sketch, CAD), 3D and spatial data.

**Why deferred:** Each modality requires its own ingestion pipeline, its own index type, and its own retrieval shape. They are independent of each other. Building them in v1 would multiply the substrate work by 5+ without adding fundamental capability — the architecture already supports them, the implementation does not yet.

**When in-scope:** When a customer has a concrete use case that requires one of these modalities and is willing to be the design partner. The architecture's commitment is that adding a modality is substrate-internal — Section 3 already names this — so adding one when needed does not require architectural revision.

### Outbound harness export to non-OHM runtimes (full compatibility)

**Status:** Documented in Section 7 as "best-effort" with explicit compatibility reports.

**What v1 supports:** Full export to OHM (documentation form), best-effort export to Claude Code (with compatibility report on lossy elements), MCP server exposure of individual tools and harnesses.

**What v2 adds:** Higher-fidelity exporters for specific external runtimes (LangGraph, custom enterprise agent frameworks), with named compatibility tiers and explicit transformation guarantees.

**Why deferred:** The set of external runtimes worth supporting is unclear at v1. Customer demand will reveal which ones matter. Building five outbound exporters speculatively is wasted work; building two on-demand is informed work.

**When in-scope:** When a customer or ecosystem partner needs a specific outbound integration and is willing to validate the exporter against their target runtime.

### Self-modifying harness implementation (advanced)

**Status:** Documented in Section 5 (Flow 6 — Learn) and Section 6 (Governance) as bounded by permission gates.

**What v1 supports:** Consciousness-driven proposals for harness mutations, routed through the harness review system with mandatory HITL approval. Agents can propose; humans approve.

**What v2 adds:** Higher-trust patterns — bounded auto-acceptance of low-risk mutations (e.g., adding a tool reference within an existing capability allocation), self-modification scopes that bypass HITL for specific declared transition types, gradual trust accumulation that loosens HITL over time as an agent's proposals prove sound.

**Why deferred:** v1's bounded learning model is the safe default. Loosening it requires real-world data on how good agents' proposals actually are. Without that data, auto-acceptance is reckless.

**When in-scope:** When v1 has shipped, real harnesses have run, and the proposal-acceptance ratio reveals patterns that justify safer-than-HITL automation for specific cases.

### Codex agent definition adapter

**Status:** Mentioned in Section 7, deferred per customer feedback.

**What v1 supports:** Claude Code [SKILL.md](http://SKILL.md) adapter, MCP tool adapter, OpenAPI adapter, OHM-to-Markdown documentation adapter.

**What v2 adds:** Codex agent definition adapter (inbound + outbound) once the Codex format stabilises.

**Why deferred:** Codex's format is still evolving. Building an adapter against a moving target wastes work. Once stable, the adapter is a contained piece of work.

**When in-scope:** When Codex publishes a stable agent definition format and customer demand surfaces.

### Workspace-level shared task boards (cross-harness)

**Status:** Documented in Section 4 OHM as "out of OHM v1."

**What v1 supports:** Per-harness task boards. Each harness owns its operational state.

**What v2 adds:** Workspace-level boards that cut across harnesses — _"all open tasks for the marketing workspace, regardless of which harness created them"_.

**Why deferred:** Cross-harness boards require explicit query semantics, presentation logic, and ReBAC interactions that are complex. Per-harness boards are sufficient for v1's primary use cases. Cross-harness aggregation can be built later as a read-side feature without changing the substrate.

**When in-scope:** When customer workflows demand cross-harness visibility and the per-harness model proves insufficient.

### Consciousness drift detection (advanced)

**Status:** Section 6.5 Threat 6.2 documents this as Phase 3 (advanced) mitigation.

**What v1 supports:** Direct consciousness corruption detection (Threat 6.1) — provenance, permission gates, manual audit.

**What v2 adds:** Statistical baselines for agent behaviour, automated detection of consciousness drift patterns, periodic consciousness audits with anomaly reports.

**Why deferred:** Drift detection requires baselines. Baselines require historical data. v1 establishes the audit infrastructure; v2 builds the analytics on top of it.

**When in-scope:** When the platform has sufficient operational history to establish meaningful behavioural baselines (typically 6+ months of production use per workspace).

### Federation laundering audit reports (specialised)

**Status:** Section 6.5 Threat 9.2 documents this as Phase 3 mitigation.

**What v1 supports:** Provenance on every federated traversal. Manual audit possible.

**What v2 adds:** Specialised audit reports that detect federation patterns suggestive of data laundering (high-volume cross-workspace reads followed by writes to less-restricted workspaces).

**Why deferred:** Detection requires pattern analytics over substantial provenance volume. v1 captures the data; v2 analyses it.

**When in-scope:** When federation use is widespread enough that pattern detection has signal to work with.

### Higher-order portability (cross-platform harness migration tools)

**Status:** Implied by Section 7's portability story but not explicitly committed to v1.

**What v1 supports:** OHM as canonical format. Adapters per external runtime. Manual export and import.

**What v2 adds:** Migration tools that automate moving a workspace's entire harness set from one platform to another, with compatibility analysis and warnings about what doesn't translate cleanly.

**Why deferred:** No customer has asked for full workspace migration at v1. The capability exists implicitly (adapters can be chained) but the tooling and UX are work that should wait for real demand.

**When in-scope:** When a customer needs to evacuate a workspace from another platform or take their workspace elsewhere.

### Additional LLM provider integrations beyond v1 set

**Status:** Documented in Section 2's LLM Provider definition.

**What v1 supports:** Anthropic native, OpenAI-compatible (covers OpenAI, OpenRouter, Azure OpenAI, LM Studio, Ollama, vLLM, Together, Anyscale, Groq, and other compatible endpoints), AWS Bedrock native.

**What v2 adds:** Google Gemini native API, Cohere, Mistral La Plateforme native, and other vendor-native APIs as customer demand surfaces.

**Why deferred:** v1's three protocol shapes cover the overwhelming majority of customer needs. Adding native integrations for additional vendors is a contained code change to the LLM client factory; it doesn't require architectural revision. Each addition is evaluated against customer demand and the vendor's API stability.

**When in-scope:** When a specific customer needs a non-v1 provider and the vendor's API is stable enough to integrate against.

### Specific billing pricing model

**Status:** Architecture exposes the metering surface in v1; pricing model is product strategy.

**What v1 supports:** Substrate-level metering of tokens, invocations, storage, and execution time. Per-organisation and per-workspace metering data. Usage reporting APIs in both deployment modes. Billing Service infrastructure deployed in cloud mode.

**What v2 adds:** The specific pricing model the Billing Service implements (per-workstation monthly, per-token consumption, hybrid tiered pricing, etc.). The pricing model is a product decision, not an architecture decision.

**Why deferred:** Pricing strategy depends on customer research, competitive positioning, and operational cost data that doesn't exist yet. The architecture's job is to make billing _possible_; product strategy decides how billing _works_.

**When in-scope:** When cloud-hosted deployment is ready to onboard paying customers. The metering surface is ready in v1; the pricing logic is built when the pricing model is decided.

### Advanced billing features for self-hosted customers

**Status:** Self-hosted billing is the customer's concern; v1 exposes metering but not chargeback tooling.

**What v1 supports:** Usage metrics exposed via API, queryable by self-hosted customers for their own internal chargeback or analytics. Cost allocation by workspace and by member.

**What v2 might add:** Pre-built chargeback report templates, internal invoicing tooling for self-hosted customers, integration with common enterprise expense systems.

**Why deferred:** Self-hosted customers vary widely in how they handle internal chargeback. Building one solution would fit some and frustrate others. Better to expose the data and let customers build what fits their organisation.

**When in-scope:** If demand from self-hosted customers surfaces for specific chargeback tooling.

---

## Deferred indefinitely

These are features that may or may not happen. They are not on the v2 roadmap. They are documented here so engineers don't spend time on them without explicit decision.

### Visual workflow editor (drag-and-drop harness construction)

**What it would be:** A graphical interface where operators construct harnesses by dragging nodes (actors), connecting them with edges (orchestration), and configuring each node visually.

**Why indefinitely deferred:** The platform's core thesis is **prose-defined orchestration**. A visual editor reintroduces the workflow-style framework opinion the architecture deliberately avoids. The compiler harness already does the work of generating harnesses from natural language; if customers need visual editing, they can edit the compiled OHM in a text editor with structured assistance.

**When it might happen:** If overwhelming customer demand shows visual editing is genuinely needed for adoption. This would be a significant architectural revision (the compiler's role would change, the manifest format might need adjustment). Until that signal is unambiguous, not building.

### Real-time collaborative harness editing

**What it would be:** Multiple operators editing the same harness manifest simultaneously, with conflict resolution, presence indicators, change-attribution.

**Why indefinitely deferred:** OHM is small enough that single-author editing (with version control via the substrate's versioning) is sufficient. Real-time collaboration adds substantial implementation complexity for marginal benefit. Git-style branching and merging via the platform's versioning is the recommended pattern.

**When it might happen:** If real-world usage shows persistent multi-editor conflicts that versioning can't address gracefully. Unlikely.

### LangChain or framework-style compatibility layers

**What it would be:** Adapters that make Oraclous look like LangChain or another popular agent framework, so applications written against those frameworks could run on Oraclous's substrate.

**Why indefinitely deferred:** Section 7's portability story is OHM as canonical, with adapters per format. Adopting another framework's interface as a first-class compatibility layer would compromise OHM's role as the canonical hub. The "Oraclous as MCP server" pattern (Section 7) is the right level of compatibility — protocol-level, not framework-level.

**When it might happen:** Not at the platform level. Customers who need framework compatibility can write their own adapters; the platform won't ship them.

### Built-in fine-tuning pipeline beyond the FTOps application

**What it would be:** Native platform support for model fine-tuning workflows — training data preparation, training runs, model registry, deployment.

**Why indefinitely deferred:** FTOps is **an application** built on Oraclous (one of several possible — alongside digital twin, customer support, code audit). Building fine-tuning into the platform layer would conflate one application with the substrate. The right pattern is: ship FTOps as a reference application built on the platform's primitives.

**When it might happen:** When FTOps as an application matures and customers ask for primitives that could legitimately be platform-level (specialised model serving infrastructure, distributed training coordination). Even then, the bar is high — most fine-tuning needs are application-level, not platform-level.

### Native multi-language SDKs beyond Python and TypeScript

**What it would be:** First-party SDKs in Go, Rust, Java, Ruby, etc.

**Why indefinitely deferred:** The platform exposes REST APIs, MCP, and OHM as standard formats. Any language with HTTP and YAML support can integrate. SDKs are convenience layers; the architecture doesn't require them. Building five SDKs that all wrap the same API is engineering effort better spent on the API itself.

**When it might happen:** If a specific language ecosystem becomes a major customer segment and the lack of a native SDK is a real friction point. Customer-driven, not platform-driven.

---

## Out of scope permanently

These are things Oraclous explicitly will not build, by architectural commitment. They are documented here so the answer to _"could the platform do X?"_ is unambiguous when X is one of these.

### Agent autonomy beyond bounded learning

**What it would be:** Agents that can rewrite their own role, expand their own capability allocation, grant themselves new scopes, or modify their consciousness permissions without HITL.

**Why permanently out of scope:** This contradicts Section 6's governance model and Section 6.5's security principles. Bounded learning (with HITL on consequential mutations) is the platform's safety floor. Removing the floor isn't an enhancement; it's removing the floor.

The most permissive setting in v1 is "agent may propose harness changes, routed through review." There is no setting that removes the review. There is no path to one. Customers who want unbounded autonomy can grant the equivalent in their own systems; the platform refuses.

### Hidden behaviour or platform magic

**What it would be:** Features that the platform performs on behalf of customers without their knowledge or ability to inspect — silent updates, undocumented retries, hidden state, opaque decision logic.

**Why permanently out of scope:** This contradicts the recursion principle from Section 3 and the sovereignty principle threaded through the entire document. Everything the platform does is either:

* Visible code in an open-source repository, or
* A customer-owned harness or capability the customer controls

There is no third category. "Platform does X automatically" is not a feature; it's a bug to be exposed and made explicit.

### Capability content moderation by the platform

**What it would be:** Platform-level filtering of capability outputs based on the platform vendor's content policies — refusing to execute certain kinds of tools, blocking outputs the platform vendor deems inappropriate, etc.

**Why permanently out of scope:** Oraclous is self-hosted and customer-owned. The customer's policies govern their workspace, not Oraclous-the-company's policies. The platform provides the mechanism for customers to define content moderation (via output redaction, HITL gates, custom skills); it does not impose moderation.

This includes refusing to facilitate categories of work (e.g., the platform will not refuse to ingest particular kinds of documents or refuse to execute particular kinds of capabilities). The substrate is neutral; customer policies are not.

### Centralised credential storage by the platform vendor

**What it would be:** Customers' OAuth tokens, API keys, and secrets stored in infrastructure operated by Oraclous-the-company in a way that grants Oraclous-the-company access.

**Why permanently out of scope:** Founding principle #3 (data ownership). Customer credentials live in the customer's `credential-broker-service` instance — even in cloud-hosted deployments, the broker operates with per-organisation encryption keys that Oraclous-the-company cannot directly decrypt. There is no shared credential pool, no platform-vendor-accessible secret store. The cloud-hosted deployment mode does not weaken this; it shifts who operates the deployment, not who has access to the data within it.

### Cross-customer data sharing or aggregation

**What it would be:** The platform learning across customers — _"customers like you often configure their compiler this way"_, or aggregated analytics across customer organisations.

**Why permanently out of scope:** Data sovereignty is absolute, in both deployment modes. In self-hosted mode, this is trivially enforced (the platform vendor has no infrastructure to aggregate from). In cloud-hosted mode, this is enforced by the organisation-isolation guarantees of Section 6.5 Threat 10.1 — Oraclous-the-company has no code path that can read data across organisation boundaries. The platform vendor has no access to customer data, no ability to aggregate across customers, no telemetry that reveals customer workflows. The platform improves through customer feedback and community contributions, not through customer-data mining.

### Agent legal personhood claims or representations

**What it would be:** Treating agents as entities with rights, responsibilities, or legal standing equivalent to humans. Marketing or documentation that suggests agents are "intelligent" or "thinking" in the sense humans are.

**Why permanently out of scope:** Agents are software that uses LLMs as a resource (Section 2). They have identities for governance purposes, scopes for access control purposes, and consciousness for operational memory purposes. They are not minds; they are not parties; they have no rights.

The platform's framing must remain honest. "Second mind" (the platform vision) is a metaphor for organisational augmentation — humans and agents working together — not a claim that agents are minds. Marketing or documentation that crosses this line is corrected.

---

## How to use this section

When implementation reaches a decision point about whether to build a feature, the test is:

1. **Is it explicitly in scope per Sections 1-8?** If yes, build it.
2. **Is it on the "deferred to v2" list?** If yes, defer with the documented criteria for when it becomes in-scope.
3. **Is it on the "deferred indefinitely" list?** If yes, document the request as customer feedback for future consideration; do not build.
4. **Is it on the "out of scope permanently" list?** If yes, decline and reference the reasoning here.
5. **Is it in none of these categories?** Then the document is silent on it. Decision-makers should ask: _should this be in v1?_ If yes, add it to Sections 1-8 (the architecture grows). If no, add it here (the boundary clarifies). Silence in the document is a signal that the question was not anticipated, not that the answer is yes.

The discipline of using this list is what prevents scope creep. Architecture documents that lack explicit scope boundaries tend to become wishlists; this section is the boundary.

---

## Final note: the architecture's living nature

This document is v1.0 of Oraclous's architecture. It is the contract between architecture and engineering at the point of locked. But it is not immutable.

As implementation proceeds, real-world feedback will surface mistakes, opportunities, and learnings that the document didn't anticipate. The right response is **document revision**, not silent deviation. Each material learning should produce either:

* A document update that revises the affected sections, or
* An ADR (Architecture Decision Record) that supersedes a specific decision in the document with explicit reasoning

The document's authority comes from being the single source of truth for architectural decisions, not from being unchanging. Versions matter: v1.0 is the starting commitment; v1.1, v1.2, v2.0 represent considered evolution.

What does NOT happen is _implicit_ deviation — code that contradicts the document without explicit reasoning. The discipline of "implementation conforms to document, or document changes first" is what keeps the architecture coherent over time. It is the same discipline Section 6 applies to governance: the rules win until they are deliberately changed; they cannot be silently bypassed.

The platform that emerges from this architecture will be one of the most ambitious open-source AI infrastructure projects ever attempted. Its success depends on the engineering work — but more deeply, on maintaining the architectural integrity through that work. This document is the spine; sections 1-9 are its vertebrae; revisions are its growth. Everything depends on keeping it honest.

---

_End of v1.1 — Sections 1 through 9 complete, with BYOM, cloud-hosted mode, billing, and organisation tenancy added. Architecture locked. Implementation may now begin against this document._
