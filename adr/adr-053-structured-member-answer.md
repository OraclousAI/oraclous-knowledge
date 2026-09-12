# ADR-053 — A Structured Member Answer Is Enforced Mechanically: a Per-Run Schema, a Member-Level Declaration, and a Platform-Minted Receipt

## Status

| | |
| --- | --- |
| Status | **Accepted** 2026-09-13 — the three decisions were RULED by the owner on 2026-09-12; the CTO accepted this record on 2026-09-13 (CLAUDE.md §8). Not yet built (unblocks [oraclous-backend#900](https://github.com/OraclousAI/oraclous-backend/issues/900), [#898](https://github.com/OraclousAI/oraclous-backend/issues/898)) |
| Date | 2026-09-12 (decisions ruled by the owner); accepted 2026-09-13 |
| Deciders | parhamdavari (ruled 2026-09-12); drafted by `backend-implementer` under a one-document authorship waiver ([oraclous-backend#1050](https://github.com/OraclousAI/oraclous-backend/issues/1050)); accepted by the CTO 2026-09-13 (CLAUDE.md §8 — not waived) |
| Driving evidence | [oraclous-backend#901](https://github.com/OraclousAI/oraclous-backend/issues/901) (the three questions, ruled) · [#1043](https://github.com/OraclousAI/oraclous-backend/issues/1043) (the live failure that forced them; run `d39fda19-cc7c-45ea-a0b7-ef49ca0ac944`) · [#1050](https://github.com/OraclousAI/oraclous-backend/issues/1050) (this handoff) |
| Builds on | [ADR-002](adr-002-ohm-as-canonical-manifest-format.md) (OHM is the canonical manifest format) — adds one field to `OHMCapability`; does not otherwise amend OHM v1.0/v1.1 |

## Context

A team member can declare which keys its answer must carry (`outputs_schema`, `requires_valid_json`, `outcome_critical` on `OHMMember`). Today it satisfies that contract by writing the keys into free text alongside everything else it says, and the platform peels JSON out of that text with a greedy `re.search(r"\{.*\}", output, re.DOTALL)` — first `{` in the reply to last `}`.

The compiler's own `reviewer` step proved this cannot hold. `REVIEWER_PROMPT` requires the model to emit the compiled team as one JSON object, then a separate `driving_signals` receipt object, immediately after it, as a second top-level object — both required, a reply carrying only one FAILS the step. The greedy peel spans both objects: it opens on the team's first `{` and closes on the receipt's last `}`, so `json.loads` raises on the concatenation, `_parse_member_object` swallows the exception and returns `{}`, and a perfectly well-formed team is discarded as if the member had produced nothing.

This was confirmed on live, verbatim text, not a hypothesis about weak models. Run `d39fda19-cc7c-45ea-a0b7-ef49ca0ac944`, model `openrouter/deepseek/deepseek-v4-flash` — a cheap model — obeyed both instructions exactly, produced two well-formed, correctly separated JSON objects, and was still failed by the peel. **The model did nothing wrong. The extraction contract was wrong.**

The owner's framing, and this ADR's motivating principle: **the shape a member returns must be mechanically controllable, and must not depend on how strong the model is, because users bring their own, often cheap, models.** A prompt-and-hope contract — "reply with the JSON object and nothing else" — fails that on its face; it degrades exactly when the model is weakest, which is exactly when the platform needs it most.

A tolerant reader (find the intended object wherever it sits, fix the contradictory instructions that produced two adjacent objects in the first place) ships separately as the immediate mitigation for #1043. It is not this ADR's subject. This ADR is the durable answer: a member's answer that must carry a fixed shape is not requested from the model in free text at all — it is either constrained by a schema the model's own tool-calling machinery enforces, or written by the platform itself from a call it already dispatched.

Three questions had to be ruled before #900 could build this. They were put to the owner on #901 and ruled there; this ADR records the rulings.

## Decision

### 1 — A per-run, per-organisation tool schema rides the manifest

`OHMCapability` gains one new, optional, typed field:

```python
resolved_schema: dict[str, Any] | None = None
```

It carries a JSON Schema for this capability's tool-call parameters, computed by the compiler per calling organisation at compile time, and — when present — it **overrides** the schema on the capability's stored registry descriptor for this run only. Absent, resolution behaves exactly as it does today, byte-identical. The tool catalogue is computed once, by the compiler, from the same seed-inventory-unioned-with-live-registry-filtered-by-substrate rule it already applies; this field is the only channel that rule's output takes into the runtime's tool specification.

**The name `parameters_schema` is refused.** `oraclous-frontend`'s `packages/api-client/src/tools.ts:35-37` already documents a `parameters_schema` key on the tool descriptor, written only by the MCP importer, and states in terms that it "is a different field with different semantics and is deliberately not merged into this one." A third field of that name, with a third meaning, walks straight into the collision the frontend already guards against.

**Chosen name: `resolved_schema`.** `manifest.py`'s own module docstring already uses "resolution" for this exact idea — turning a manifest-time reference into a concrete, run-specific value ("atomic reference resolution against the registry"). `resolved_schema` says precisely what the field is: the schema this capability *resolves to*, for this run, which may supersede the registry's static schema — not a second copy of an importer-owned, differently-scoped field that happens to also be JSON Schema. It shares no substring with `parameters_schema` and cannot be confused with it by a `grep` or by a reviewer skimming a diff.

**Rejected: `OHMCapability.config`.** `_materialise` copies `config` into the persisted registry instance row. Every compile would write a copy of the calling organisation's whole tool catalogue into the database — a new reserved-key rule to avoid that is more code than a typed field.

**Rejected: the harness runtime fetching the catalogue itself.** The compiler's catalogue is the seed inventory unioned with the live registry and filtered by substrate — a rule that would then have to be restated inside generic Layer 3 code, in a second place. `_slug.py`'s docstring is the standing record of what happens when two on-ramps hold their own copy of the same answer.

**Not a cross-repository shape today.** The frontend does not read `capabilities[]` off a member's sub-manifest at all: `packages/api-client/dist/teamDrafts.d.ts:19` and `teamRuns.d.ts:151` both type `subHarnesses` as an opaque `Readonly<Record<string, unknown>>`, never destructured. No `Contract` issue is required for this field. **It becomes one the moment a frontend surface reads it** — that is the trigger, not this ADR's acceptance.

### 2 — "A tool call is the member's answer" is declared on the member, not the run's settings bundle

`OHMMember` gains the declaration — a field such as `answer_from_tool: str | None`, naming the tool whose terminating call constitutes the member's answer — rather than the runtime policy envelope threaded into the loop at dispatch.

Every other per-member behaviour already lives on the member descriptor: its `tools`, its `max_tokens`/`max_tool_calls` caps, `on_exhaustion`, `requires_valid_json`, `outputs_schema`, `outcome_critical`. This joins them, for the same reason all of them are there: **a saved team must be self-describing.** Declared on the policy envelope instead, this behaviour would be invisible in the stored manifest — nothing in a saved team would show that one of its members answers this way. The threading cost (one more field walking member descriptor → runtime loop, the same path `outputs_schema`/`requires_valid_json`/`outcome_critical` already walked) is accepted as a known, already-paid cost, not a new one.

### 3 — The platform writes the proof of work, as a deliberate, bounded exception

Every member that holds a tool must prove it used one: it points at a real call in its own trace, or the compiler's grounding check fails it for claiming work it did not do (the check exists because a member once did exactly that — run `fe548aac`). If the member's answer *is* the designated tool call, it has nothing left to separately point at — the receipt and the answer are the same event.

**Ruled: when a member's loop terminates on the tool named by `answer_from_tool`, the PLATFORM writes the `driving_signals` receipt itself, from its own record of the dispatch it already made, carrying the real `tool_call_id`.** The ground: the platform's own record of a call it dispatched is strictly stronger evidence than a model's self-report of the same call. The model never writes this field, so it cannot forge it.

**This is a deliberate, bounded widening of what the platform may assert, and it must be read as exactly that — not as a quiet side effect of #900.** Three earlier rulings — [oraclous-backend#642](https://github.com/OraclousAI/oraclous-backend/issues/642), [#743](https://github.com/OraclousAI/oraclous-backend/issues/743), [#781](https://github.com/OraclousAI/oraclous-backend/issues/781) — each *narrowed* who may assert a receipt, because each concerned a claim the platform could not independently verify: a model asserting a receipt, an identifier, or a data-absence flag it may simply have invented. This decision runs in the opposite direction, and is safe only because the case is different in kind, not degree: **the platform dispatched the call itself and holds the id first-hand.** It is not taking the model's word for anything.

**The boundary is exact and does not generalise.** This exception applies only where all three hold: the loop is terminating on the tool named by that member's own `answer_from_tool`; the call is the one the platform itself dispatched; and the platform's own record of that dispatch shows it completed `ok`. It never applies to an ordinary tool call, and it never applies to anything a model supplied about itself. This is not a step toward the platform asserting other things on a member's behalf — it is a single, named, first-hand-evidence exception, and any future proposal to widen it further is a new decision, not an extension of this one.

Both alternatives were put to the owner and refused:

* **The model keeps writing its own receipt.** A weak model forgets it, the compile fails, and the member this mode exists to support — one running on a cheap model — is exactly the one it fails hardest. This makes compiles *less* reliable than today, not more.
* **Exempt such a member from the grounding requirement entirely.** Simple, but it opens a hole: a member could be deliberately given this mode specifically to bypass the check that exists because of `fe548aac`.

## Consequences

### Positive

* A member's structured answer is enforced by the platform's own tool-call machinery and its own dispatch record, not by how carefully a model follows a prose instruction. #1043's class of failure — a compliant model still failing shape validation — cannot recur for a member using this mode.
* A saved team is self-describing: `answer_from_tool` on the member, and `resolved_schema` on the capability it names, are both visible in the manifest, not reconstructed from runtime state.
* #900 and #898 are unblocked.
* The narrowing line of #642/#743/#781 is preserved as a line, not eroded by an unstated exception — this ADR draws the boundary explicitly, in the same document that widens it.

### Negative

* Widening what the platform may assert is a category of change that must be re-justified every time, not amortised — this ADR is not a precedent for a second, looser widening. Reviewers of any future proposal along these lines should require it to show the same first-hand-evidence property this one has, not merely cite this ADR.
* `resolved_schema` and the capability's stored registry schema are now two things that can disagree; nothing in this ADR specifies drift detection between them beyond "the per-run field wins when present."
* A member configured with `answer_from_tool` naming a tool it never calls (budget exhaustion, model refusal, wrong tool chosen) is not given a platform-minted receipt — that failure mode is unchanged from today's grounding check and is not softened by this decision.

## Scope not decided here

* The wire format and threading mechanics of `resolved_schema` from compiler output through to the tool-calling machinery the model actually sees (native tool-calling vs. a prompted schema) are #900's implementation, not this ADR.
* What happens when `answer_from_tool` is set but the member's loop ends without ever calling that tool is existing `on_exhaustion`/grounding behaviour; this ADR does not add a new terminal state for that case.
* The immediate #1043 mitigation (a tolerant reader across the six sites sharing the greedy-peel defect, and separating the contradictory `OUTPUT_CONTRACT_DIRECTIVE`/`GROUNDING_DIRECTIVE` instructions) ships ahead of this ADR's implementation and is not superseded by it — the two are complementary, not sequential alternatives.

## See also

* [oraclous-backend#901](https://github.com/OraclousAI/oraclous-backend/issues/901) — the three questions and both rounds of rulings this ADR records
* [oraclous-backend#1043](https://github.com/OraclousAI/oraclous-backend/issues/1043) — the live P0 that forced the rulings, including the verbatim reproduction on run `d39fda19-cc7c-45ea-a0b7-ef49ca0ac944`
* [oraclous-backend#1050](https://github.com/OraclousAI/oraclous-backend/issues/1050) — the authorship waiver for this document
* [oraclous-backend#900](https://github.com/OraclousAI/oraclous-backend/issues/900), [#898](https://github.com/OraclousAI/oraclous-backend/issues/898) — unblocked by this ADR
* [oraclous-backend#642](https://github.com/OraclousAI/oraclous-backend/issues/642), [#743](https://github.com/OraclousAI/oraclous-backend/issues/743), [#781](https://github.com/OraclousAI/oraclous-backend/issues/781) — the narrowing line decision 3 is a bounded, named exception to
* [ADR-002](adr-002-ohm-as-canonical-manifest-format.md) — the manifest format `resolved_schema` extends
