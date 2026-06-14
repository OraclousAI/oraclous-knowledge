---
title: "End-user personas (speculative — pending validation)"
owner: experience-architect
status: speculative-pending-validation
needs-signoff: tech-lead (Reza) / CTO
grounds-in: platform-architecture-v1.1 §1–2 (vision + conceptual model) + capability-surface-inventory.md
---

# End-user personas

> **Status: SPECULATIVE — pending validation.** These product personas do not exist in any prior doc; only
> *system roles* do (organisation / workspace / actor / member / agent). They are authored from the vision +
> the live capability surface and must be validated against real journeys before they are treated as
> canonical (skill §3.2 — tech-lead signs personas off). Only the **Tools** journey is signed so far, so the
> personas it touches are partially grounded; the **member** persona is the least validated and the
> weakest-served by live capability.

**Product persona ≠ system role.** A system role (operator/member/agent/admin) is a runtime actor-kind or a
ReBAC tuple — not a buyer/user with goals and pains. Each persona below states how it differs from the
like-named system role. The named apps (digital twin, customer support, code auditor, FTOps) are
*applications built on the platform*, not personas — they fold into the operator and application-builder
personas.

## 1. The operator / second-mind builder (primary buyer)
**Who:** a department/function lead (support, ops, eng, knowledge/data) at an org with scattered data and
ad-hoc AI. The economic buyer. ≠ the system "operator" (who states a goal to the compiler) — this is the
human who owns the outcome and budget.
**Goals:** stand up a governed "second mind" for their function without writing orchestration code or vendor
lock-in.
**Jobs:** create a workspace + ingest sources; author/compile an agent (prompt/model/tools/budget); configure
tools with credentials; run the agent and confirm it's right; keep cost visible; manage who can do what.
**Pains:** the Tools page is a browse-only catalogue (the register→instance→configure→validate→execute
lifecycle is gateway-exposed but FE-absent); Recipes is an inert viewer; connecting a provider still means
pasting keys (blocked on G1); binding the defining agent of a workspace is blocked on G2.
**Served by (inventory):** §5 workspaces (built); §4 author/run an agent (built); §1 instance lifecycle
(FE-absent — Tools journey inc 3–5); §2 recipes; §3 manual credentials (built). **Depends on G1, G2.**
**Success metric:** time-to-first-useful-agent-run — new workspace → configured/credentialed/validated tool →
successful first run, in one sitting, no code, no ticket.

## 2. The org admin / governance owner
**Who:** accountable for the org as the tenancy unit — security, compliance, access, supply-chain, cost.
Buys on data sovereignty + ISO/SOC2 + no lock-in. ≠ the workspace ReBAC "admin" tuple.
**Goals:** let teams adopt agents fast without loss of control — everything org-scoped, one governance model,
credentials never leaving the broker, a supply-chain gate on imported tools.
**Jobs:** manage org/members/roles/invites; vet+approve/reject MCP-imported tools (HITL); manage credentials
org-wide; watch cost; set deployment posture.
**Pains:** the approval gate is thin; credential management is partial; a provider connected at login isn't
usable as a tool credential without re-entry (G1); no UI for org-wide instance health; ReBAC cross-org
enforcement is scaffolded only (copy must not over-promise).
**Served by:** §6 orgs/members/billing (built); §1 MCP import + approve/reject (built) + instance health
(FE-absent); §3 credential CRUD. **Depends on G1.**
**Success metric:** adopt-without-loss-of-control — zero cross-org leaks + 100% imported tools through the
HITL gate before first use; provenance answers "who did what, on whose behalf, against what data".

## 3. The everyday member / task-board participant
**Who:** a non-technical workspace member working alongside agents on shared task boards (brand lead,
on-call SRE, legal reviewer, support rep). Never authors a harness. ≠ the "member" ReBAC tuple.
**Goals:** get routed work done with minimal friction — see what's assigned, act, hand off/escalate, approve
at HITL gates — inside governance, without learning internals.
**Jobs:** view/act on task-board tasks; claim/complete/hand-off/escalate; approve/reject at a HITL gate;
query a workspace (Explorer).
**Pains:** the platform makes humans first-class assignees, but the member-facing task-board is thin (durable
orchestration is "Jobs"/partial, harness assignments partial, no dedicated task-inbox surface). Risk of the
legacy chat-app IA making members feel they're chatting, not doing governed work.
**Served by:** §6 durable orchestration (partial); §4 assignments (partial); §5 search (built). **Largely
partial/absent — the weakest-served persona; a likely source of the next gap Contracts.**
**Success metric:** task-completion friction — find/act/hand-off/approve in a few clicks, no training; HITL
approvals completed not abandoned.

## 4. The application builder / publisher (developer-buyer)
**Who:** a developer/ISV/internal platform team building a product *on* Oraclous (digital twin, support,
auditor, FTOps). Composes harnesses + a thin surface, exposes via the gateway. Buys on portability (OHM/MCP).
**Goals:** build a sellable application as composed harnesses, publish via the gateway, keep it portable.
**Jobs:** register custom tools/capabilities (OHM descriptors); import MCP tools; author/compose harnesses;
evaluate retrieval quality; integrate via the gateway.
**Pains:** register-a-custom-tool + capability CRUD exist via gateway but are entirely FE-absent;
retrieval-quality eval has no surface; no UI for publishing/integration-keys/widgets (a likely gap cluster);
binding the harness(es) of a published app to a workspace is blocked on G2.
**Served by:** §1 register tool + capability CRUD (FE-absent) + MCP import (built); §4 compose/run harnesses
(built); §5 retrieval eval (FE-absent). **Depends on G2; publishing/keys/widgets a likely new gap cluster.**
**Success metric:** time-to-publish a first composed application without hand-rolling integration code +
portability proof (a harness round-trips through OHM to/from an external runtime).

## 5. The knowledge / data steward (recipe author-consumer)
**Who:** responsible for turning raw sources into the graph substrate via concern-driven recipes (ADR-022) —
data lead/analyst/SME. The human counterpart to the data-specialist agent.
**Goals:** get high-quality governed data into a workspace repeatably via recipes; verify a projection before
it writes; keep it org-scoped/auditable.
**Jobs:** browse/inspect the recipe library; start from a template; dry-run over a sample; save a draft; run a
recipe on a graph; later evaluate retrieval quality.
**Pains:** the sharpest FE-vs-backend gap — the whole recipe lifecycle is gateway-exposed but the Recipes page
is an inert JSON viewer; a naive CRUD form is the wrong model (needs author-preview-run); retrieval eval is
FE-absent.
**Served by:** §2 recipes browse/inspect (built/raw) + template/dry-run/save/run-on-graph (FE-absent); §5
ingest (built) + retrieval eval (FE-absent). **No backend gap — purely a frontend exposure gap.**
**Success metric:** confident-ingestion rate — template → dry-run-preview → saved recipe run against a graph,
having *seen* the projection before any write, zero raw-JSON editing.

---

## Platform success metrics (north-star + supporting — speculative)

**North star — Activated second minds:** count of workspaces that reached a working second-mind state = at
least one graph ingested via a recipe + at least one configured/credentialed/validated tool instance + at
least one successful agent run, all in the UI without code or a ticket. Spans all four human personas and
directly indicts the headline gaps (Tools lifecycle FE-absent, Recipes inert) until they close.

**Supporting:** (1) lifecycle-completability in-UI (% of the tool and recipe lifecycles reachable in the FE vs
API-only — the closure curve); (2) time-to-first-useful-agent-run; (3) governed-adoption integrity (zero
cross-org leaks + 100% MCP tools through the HITL gate); (4) human-actor task throughput (the weakest surface);
(5) portability proof rate; (6) provenance answerability.

**Gated on backend gaps (cannot be measured until they close):** OAuth-auto-connect adoption (% connected via
"Connect with…" vs manual paste) — **G1**; workspace-agent binding rate (% of workspaces with a bound defining
harness) — **G2**.

## Under-served-persona flag
The everyday-member task-board persona is the worst-served by live capability — the platform's signature
concept (humans as first-class task-board actors) is its thinnest live surface. A strong candidate for the
next gap Contracts and journey work after the currently-scheduled epics.
