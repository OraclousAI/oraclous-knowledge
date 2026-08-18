# ADR-052 — An App-Descriptor Layer Maps a Generated App's Shape onto a Team Run's Inputs

## Status

| | |
| --- | --- |
| Status | Proposed |
| Date | 2026-08-18 |
| Deciders | solution-architect (drafted), parhamdavari (ruled) |
| Driving evidence | [oraclous-backend#845](https://github.com/OraclousAI/oraclous-backend/issues/845) (Contract), first consumer [oraclous-backend#846](https://github.com/OraclousAI/oraclous-backend/issues/846) |
| Builds on | [ADR-002](adr-002-ohm-as-canonical-manifest-format.md) (OHM is the canonical run/harness manifest; this ADR does not amend it) |

## Context

The product direction is that a team run's output becomes a reusable **app** — something a user invokes repeatedly with its own input form and its own output view, distinct from the team run underneath it. The stated trajectory is that such apps get generated automatically, each with a different, unpredictable input/output shape. The **validation desk** (a Foray-style idea-validation flow) is the first one, built by hand; it will not be the last.

The gap: a team run only accepts `inputs` keys the team's OHM manifest already declares. `validate_input_keys` (`services/execution-engine-service/src/oraclous_execution_engine_service/services/team_run_service.py:204`) fail-closes on any other key — deliberately, per the #714 postmortem (run `538ab1fa`), where a silently dropped input key led a team member to invent its own guess instead. An app's own fields (the validation desk's `answers[]`, with each answer possibly flagged as a hypothesis to test rather than a premise to assume) have no declared place to land in that `inputs` dict.

Two ways to close that gap were on the table. Put the app's shape directly on the OHM manifest — which means every generated app grows its own manifest dialect, and OHM stops being purely "what capabilities, models, and governance this harness binds" (ADR-002). Or keep OHM as-is and put the app's shape in a layer that sits in front of the run and declares the mapping — which keeps the run manifest's contract stable no matter how many app shapes exist above it.

The same gap recurs for "an answer is a hypothesis, not a given" specifically: is that one app's private vocabulary, or something the platform understands generically for any run input, so that every future generated app doesn't reinvent it?

**An app is never one fixed shape — it can be born two different ways, and the descriptor must fit both.** The validation desk is born *with* its team: the user's first message already states the job ("evaluate my startup idea"), so the app's form and the team are designed together before that team ever runs once. A CodeRabbit-style app is born *from* a team that already exists and already ran, for whatever the user originally asked it to do; only afterward does the user ask to keep that exact setup and run it again through a form. In the first case the descriptor is authored up front, alongside the team. In the second, it has to be built after the fact, by inspecting what that specific team already reads in and already produces out. Either way the descriptor is one app's own field-to-run-input mapping, tied to one team — never a shape shared across apps; only its authoring moment differs.

## Decision

1. **A separate app-descriptor layer, not the OHM manifest, carries an app's input/output shape.** The descriptor declares the app's own fields and how each maps onto the underlying team run's declared `inputs` keys. `validate_input_keys` keeps checking against the run manifest's declared keys exactly as it does today — the descriptor is what produces a conforming `inputs` dict before that check runs, not a second manifest to teach the check about.

2. **"This input is a hypothesis to test, not a premise to assume" is a platform-level concept, not a per-app field.** Any run input can carry this flag generically, so a generated app's descriptor sets it declaratively instead of every app inventing and hand-wiring its own version. What the flag does downstream (how a team member is told to treat a flagged input) is a run/harness concern outside this ADR's scope — this ADR only decides that the flag itself is general, not that its runtime handling changes.

3. **The validation desk ships a one-off field now and migrates once the descriptor layer exists.** #845 blocked the validation desk's approve-starts-the-run step on this decision landing first; that cost is real and the desk does not need to carry it further. [#846](https://github.com/OraclousAI/oraclous-backend/issues/846) adds `answers[].hypothesis` as a field private to that one app, explicitly documented as temporary, with no change to `validate_input_keys`'s general contract. It migrates onto the descriptor layer once decisions 1 and 2 are implemented — tracked as a follow-up, not reopening this ADR.

4. **The descriptor is a single YAML file with a fixed, versioned top-level structure — the same discipline OHM (ADR-002) already applies to team manifests.** Every app descriptor has the same sections; only the content inside them is app-specific. This keeps authoring and validation tooling uniform across every app, however different their forms are from each other.

   ```yaml
   app_descriptor_version: "1.0"
   metadata:
     id: validation-desk
     name: "Validation Desk"
     description: "Evaluates whether a startup idea is worth pursuing."
   origin: authored          # "authored" (built with a new team) | "derived" (built from a team that already ran)
   target:
     team_id: <uuid>          # the team run this app wraps
   inputs:
     - key: idea
       label: "What is your idea?"
       type: string
       maps_to: task            # the run's declared inputs key this field becomes
     - key: answers
       label: "Follow-up answers"
       type: list
       maps_to: answers
       hypothesis_flaggable: true   # this field may carry decision 2's general flag
   outputs:
     - key: verdict
       label: "Verdict"
       from: result.verdict         # where in the run's output this is read from
   ```

   `origin` records which of the two authoring moments from the Context section produced this file. For `origin: derived`, a tool builds `target`, `inputs`, and `outputs` automatically by reading the target team's own manifest — its already-declared `inputs` keys and its output shape — and a human only supplies `metadata`. For `origin: authored`, a human writes `inputs` and `outputs` by hand, since no run exists yet to read them from.

## Consequences

### Positive

* The run manifest format (OHM, ADR-002) stays exactly what it is today: capabilities, models, prompts, governance, runtime. No app vocabulary leaks into it.
* One mapping mechanism serves every future generated app, so an app generator has one seam to target instead of inventing a shape per app.
* The hypothesis-vs-premise distinction becomes reusable platform vocabulary the first time it is needed generically, instead of being retrofitted later across N apps that each rolled their own.
* The validation desk is unblocked immediately (#846) without waiting on the descriptor layer's design and build.

### Negative

* Two things now describe an app end to end — the descriptor and the run manifest — instead of one. Whoever authors or generates an app must keep both consistent; the descriptor's resolution semantics still need to be designed (decision 4 fixes the shape, not the resolution point).
* #846 is deliberate debt: its field is known to be replaced. If the descriptor layer slips, that debt sits on the validation desk indefinitely — worth tracking, not blocking.

## Scope not decided here

Decision 4 fixes the descriptor's top-level YAML shape, but its storage location, versioning/deprecation rules beyond `app_descriptor_version`, the `derived`-origin auto-fill tool, and the resolution point (build time vs. run-create time) are follow-up design work, not settled by this ADR. Likewise the exact runtime behavior a hypothesis-flagged input triggers inside a team run is out of scope here.

## See also

* [oraclous-backend#845](https://github.com/OraclousAI/oraclous-backend/issues/845) — the Contract this ADR resolves
* [oraclous-backend#846](https://github.com/OraclousAI/oraclous-backend/issues/846) — the one-off field this ADR expects to migrate away
* [ADR-002](adr-002-ohm-as-canonical-manifest-format.md) — the run manifest format this ADR leaves unchanged
* `services/execution-engine-service/src/oraclous_execution_engine_service/services/team_run_service.py:204` — `validate_input_keys`, the fail-closed gate this ADR's mapping must satisfy
