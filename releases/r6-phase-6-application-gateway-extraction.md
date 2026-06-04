---
confluence_id: "196877"
title: "R6 — Phase 6: Application Gateway extraction"
---

# R6 — Phase 6: Application Gateway extraction

> **SUPERSEDED by [R3.5 — Make every service real](r3.5-make-every-service-real.md) (2026-06-04).** The application gateway is now step (6) of the R3.5 per-service sequence, built last after services (1)–(5) are real and Reza-accepted. This standalone phase is discarded; content below is retained for reference only.

| Release ID | R6 |
| --- | --- |
| Status | <custom data-type="status" data-id="id-0">Planned</custom> |
| --- | --- |
| Window | Weeks 25-28 |
| --- | --- |
| Owner | [tech-lead](https://oraclous.atlassian.net/wiki/spaces/OP/pages/983101) |
| --- | --- |
| Briefer | [solution-architect](https://oraclous.atlassian.net/wiki/spaces/OP/pages/164068) |
| --- | --- |
| Dependencies | R0–R5 (gateway sits in front of every layer; everything beneath must be in target shape first) |
| --- | --- |

## Goal

Lift the platform's public-facing surface — chat APIs, published agents, integration keys, embeddable widgets, the new MCP server, the new MCP client integrations, webhook receivers, task board UIs — into a new `application-gateway-service`. Consolidate the scattered external surface area into one place with one consistent security model. Until the gateway exists in target shape, the platform's portability story cannot be demonstrated end to end.

## Scope

### In scope

* `application-gateway-service` deployed as its own service with its own deployment unit
* Chat APIs migrated: the chat persistence layer (Postgres with RLS) lives in the gateway; the execution backing is delegated to the harness runtime
* Published agents and integration keys migrated from `knowledge-graph-builder` (now `knowledge-graph-service`) to the gateway
* New MCP server implementation: exposes the workspace's capabilities to MCP-compatible clients (Claude Desktop, Cursor, Continue); selective surface determined by ReBAC; three authentication modes (integration keys, member credentials, agent credentials)
* New MCP client integrations: external MCP servers can be registered and their tools imported into the capability registry as first-class OHM tools (uses the inbound adapter from R2)
* Webhook receivers for external triggers (Git pushes, calendar events, third-party integrations)
* Task board UI APIs exposed
* Embeddable widget surface for putting Oraclous-powered agents into customer applications

### Out of scope

* Compiler harness (R7) — the gateway hosts it but the harness itself is R7
* Billing Service (deferred to future release; pricing model is product strategy and the metering surface from R0.5 is the contract billing later consumes)
* Outbound exporters for harnesses to specific external runtimes beyond best-effort (Claude Code skills round-trip and OHM-to-Markdown are in scope; LangGraph, Codex exporters are out)

## Deliverables

- [ ] **application-gateway-service deployed** — verified by the new service running with its own deployment unit; all gateway-shaped concerns migrated; ports and APIs documented
- [ ] **Chat APIs migrated** — verified by chat traffic routing through the gateway; chat persistence with RLS works as before; the runtime is called for execution; no breaking changes for current customer integrations
- [ ] **Published agents and integration keys migrated** — verified by every existing published agent continuing to serve traffic; integration keys remain valid; rate limits and CORS scoping preserved
- [ ] **MCP server live** — verified by an MCP-compatible client connecting, authenticating with an integration key, enumerating the workspace's capabilities, and invoking one; provenance captures the MCP-initiated action
- [ ] **MCP client integration live** — verified by registering an external MCP server, its tools appearing in the capability registry as OHM tools, an agent being allocated one, and the runtime invoking it successfully
- [ ] **Webhook receivers live** — verified by at least three webhook source types working (Git push, calendar event, generic HTTP); each receiver triggers the correct harness via the execution engine
- [ ] **Task board UI APIs exposed** — verified by a member loading a task board view from the gateway; assignment, claim, hand-off, escalation, status transitions all work through the API
- [ ] **Embeddable widget surface working** — verified by a sample widget embedded in an external host application invoking a published agent through the gateway; CORS, rate limits, integration key enforcement all working

## Architecture references

* [Section 8 — Phase 6](https://oraclous.atlassian.net/wiki/spaces/OP/pages/688329)
* [Section 3 — Layered Architecture](https://oraclous.atlassian.net/wiki/spaces/OP/pages/65967) — Layer 4 (Application Gateway) ownership and exposed APIs
* [Section 7 — Portability Story](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753728) — MCP server, MCP client, embeddable widgets, adapter pattern

## ADRs implemented

* No new ADRs — R6 implements the Layer 4 commitments from [ADR-001](https://oraclous.atlassian.net/wiki/spaces/OP/pages/753752) and the portability commitments from [ADR-002](https://oraclous.atlassian.net/wiki/spaces/OP/pages/557058) already covered at the architectural level.

## Threats addressed

| Threat | Mitigation IDs implemented | Coverage |
| --- | --- | --- |
| T1 — Data exfiltration | T1-M4 (every external API call carries an authenticated principal; the gateway never bypasses ReBAC on the way through to the substrate) | Full T1 coverage at the external boundary |
| T5 — Notification spoofing | T5-M2 (webhook receivers verify source signatures; webhooks from unknown sources are rejected and logged) | Full T5 coverage |
| T7 — Audit-log gap | T7-M2 (every external API request produces a gateway-level provenance entry; the entry chains to the runtime-level entries for the same execution context) | Full T7 baseline at the external boundary |

## Governance impact

R6 makes external access governable. Before this release, public-facing surfaces are scattered across services with inconsistent rate limits, CORS rules, and integration key handling. After R6, every external request passes through the gateway and is subject to a single consistent enforcement layer. The Governance Taxonomy's `exposure_policy` binding becomes meaningful — declarations like "this harness is published with rate limit X, CORS scope Y, and integration key required" are now enforced by code.

## Risks

| Risk | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- |
| The chat API migration introduces customer-visible latency or breakage | High | Regression tests for chat APIs are a release gate. Canary deployment to a fraction of traffic. Rollback path documented. Customer-facing API contracts preserved. | qa-engineer + devops-implementer |
| The new MCP server has security regressions vs the retired bespoke MCP work | Medium | Section 7's MCP server design is explicit about lessons learned from the retired work. Threat-model review by security-architect before R6 closes. Selective ReBAC-gated surface from day one. | security-architect |
| Webhook signature verification has provider-specific quirks that lead to false rejections | Medium | Each declared webhook source type has its own signature verifier and its own test fixture replaying real provider payloads. False rejections during testing trigger verifier review before R6 closes. | backend-implementer |
| The MCP client integration imports a malicious tool from an untrusted external server | Medium | MCP server registration requires workspace admin approval. The first invocation of a newly imported tool is gated by an HITL approval. Output redaction patterns apply uniformly to imported and native tools. | security-architect |
| Embeddable widget surface introduces XSS via untrusted host pages | Medium | Widgets use the host's origin only for postMessage targeting; all DOM rendering uses safe APIs; CORS is strictly origin-scoped. Penetration testing pass before R6 closes. | security-architect + frontend-implementer |

## Dependencies

**Upstream:** R0–R5 (every prior release).

**Downstream:** R7 (compiler harness is exposed through the gateway). R8 (security hardening pass extends gateway-level mitigations).

## Sprint references

Jira epics to be created during Group E.

## Revision history

| Date | Change | Author | Reason |
| --- | --- | --- | --- |
| 27 May 2026 | Page created with the canonical release-page template | tech-lead (via Group D follow-up 3) | Establish R6 as the application gateway extraction release; matches Section 8 Phase 6 |
