---
title: "Journey — the Validation Desk: an idea in, an evidenced decision brief out"
owner: experience-architect
status: signed
signed-by: experience-architect
date: 2026-08-23
surface: apps/desk (`@oraclous/desk`) — the showcase application
grounds-in: >
  oraclous-frontend#208 (the epic) · the approved prototype artefact
  (`bed97d4b-e98c-49b3-8a8c-b962d1ba00ed`, the reference for layout, copy and the state model) ·
  the sign-in design ruling on oraclous-frontend#216 · the built desk
  (`apps/desk`, PRs #217/#219/#221/#222/#223/#225/#228/#230) and its per-issue specs under
  `oraclous-frontend/docs/specs/` · oraclous-backend#827 (the corpus decision, unresolved)
legacy-divergence: >
  There is no legacy precursor. The old frontend has no equivalent surface, so this is authored
  design rather than a lift, and the epic plus the prototype have been standing in for this spec
  since 2026-08-16. Component-level material is still lifted from the design system, never invented.
backend-gaps: >
  oraclous-backend#827 (corpus: open web versus a customer's own documents — unresolved, and the
  reason two pieces of intake are excluded) · #828 (the four mid-run emissions a run does not make,
  which is why the waiting screen is a feed rather than a progress bar) · #825 (the currency ceiling
  cannot fire, so no money figure may appear) · #822 (the calculator capability the economics screen
  reads) · #853 (a synthesising member that writes a readable decision brief).
---

# Journey — the Validation Desk

**What this application is.** A person describes an idea in one field. A team of agents researches it
for twenty to ninety minutes. The desk hands back a decision brief in which every claim carries what
supports it, and in which *"we could not establish this"* is a first-class answer rather than a gap.
It is the showcase application for the platform, so the argument it makes about evidence has to hold
on its own surfaces first: a screen that fabricates a state is a screen arguing against the product.

**Status of this document.** It is the design source for `apps/desk`. The prototype artefact remains
the visual reference for layout and wording; where the two disagree, this document wins, because a
prototype cannot be amended and this can. Section 3.3 is already one such amendment.

---

## 1. The user and the moment

**Primary persona — the founder or operator with a decision to make.** They are choosing between
four things: proceed, test one prerequisite first, refocus onto a different problem, or stop. They
have limited time, no research team, and a strong incentive to hear that the idea is good. That last
point shapes the whole application: a system that tells this person what they want to hear is worse
than no system, because it launders a guess into something that looks researched.

**Secondary persona — the person being shown the platform.** The desk is the showcase, so a visitor
watching over the primary user's shoulder is reading it as evidence of what the platform can do.
This is not a separate set of screens. It is the reason no screen may overstate: the one observer who
checks a claim and finds nothing behind it has learned the opposite of what the demonstration meant.

**The moment.** The user arrives with an idea they have already half-decided about, and about five
minutes of patience for being asked questions. They leave with a brief they will either act on
themselves or defend to somebody else — an investor, a board, a manager. Both uses demand the same
thing: every sentence must open to the material behind it, in one movement, without leaving the page.

**What they do afterwards.** They take the cheapest next action the brief names — a test with a
stated cost, a stated duration, and the thresholds that pass or fail it. The brief is not a report to
be filed. It is an argument for one next step, and everything above that step exists to say how much
the step can be trusted.

---

## 2. The three-phase state model

This is the spine of the application. Every screen reads from it, and nothing else tracks state.

| Phase | Who is working | What the user is told |
| --- | --- | --- |
| `intake` | The user | "Two steps from you, then we take over." |
| `running` | The platform | One sentence with what is happening, plus an evidence feed that fills. |
| `finished` | Nobody | What the run left behind, stated plainly — including when it left nothing. |

**The phase is derived from the run's own state on every poll, never tracked separately.** There is
no second copy to drift out of step with the engine. Three derivation rules carry real design intent
and must survive any refactor:

- **A paused run reads as `intake`.** The desk's team has exactly one human gate, the plan approval,
  and it sits before the run. A team that grows a second gate needs this reading revisited.
- **A state the client does not recognise reads as `running`.** The run exists and is not known to
  have ended, so waiting is the honest reading; declaring a brief that is not there is not.
- **A run being watched but not yet resolved reads as `running`,** not `intake`. Telling the user
  they still owe a step when a run already exists would be wrong.

**Phase and outcome are different facts and must not be merged.** The phase says who is working; in
`finished`, nobody is. The outcome says whether the work produced anything: only a run that succeeded
did. Failure, rejection and a spent budget all reach `finished` and none of them leaves a brief.

**The user's obligation ending and the run ending are separate moments, roughly twenty minutes
apart, and the interface shows them separately.** Leaving `intake` says the user is done. Reaching
`finished` says the run is done. This rule came out of prototype review and must not be undone.

---

## 3. Information architecture

### 3.1 Routes

| Route | Screen | Phase it belongs to |
| --- | --- | --- |
| `/sign-in` | Sign in — the only route outside the shell | none; there is no run yet |
| `/describe` | Step 1, the idea | `intake` |
| `/plan` | Step 2, the plan as a contract | `intake` |
| `/research` | The evidence feed | `running` |
| `/brief` | The decision brief | `finished` |
| `/brief/economics` | The economics of the idea | `finished` |

The run being watched travels in the query string (`?run=<id>`, with the workspace alongside it),
so every rail link carries the current query and a deep link survives a sign-in round trip. One
guard wraps the shell; the catch-all sits inside it, so an unrecognised path for a signed-out
visitor reaches the guard rather than being bounced first and rejected second.

### 3.2 The rail carries position; the strip carries the state sentence

An earlier revision of the prototype said the state in both places and read as clutter. The division
is the rule:

- **The rail** is a flat list of five rows — Describe, Approve plan, Research, Decision brief, and
  Economics nested under the brief — with one state mark per row and a single unlabelled divider
  after "Approve plan" separating the user's two steps from the platform's three. No group headings,
  no per-row subtitles, no banner.
- **The strip** is one element above the content carrying two lines: what is happening, and what the
  user should do about it. It is the only place the state is described in words, and it is a live
  region, so a screen reader hears a phase change without focus moving.

**A mark is a promise.** The vocabulary is a step number while the row waits for the user, a tick
when the row is done, a filled dot while research runs, an empty circle for not started, a cross for
a step the run never finished — and, on the brief row only, a mark for a document that was written
and could not be read (§6, rules 6 and 7). Six marks, and a row still being resolved keeps the one
the reader saw a moment ago rather than guessing ahead of the answer. The user's two rows tick as soon as a run exists — the run
existing is proof they did their part — and only the platform's rows depend on the outcome. A tick
on Decision brief promises a document, so a run that ended without one does not get it. Every mark
is decorative and is paired with the same meaning in words for a screen reader.

### 3.3 The rail's amendment: identity below a hairline

*(Ruled on oraclous-frontend#216, 2026-08-17. The prototype predates the session layer, so it had no
identity to place and its "no footer" rule had nothing to exclude.)*

**The rail carries position, and — below a hairline at its base — identity. It still never carries
run state.** The base row holds the signed-in address and a sign-out control styled as a text button,
not as a step: no mark, not a link in the step list, and after the five rows in document order so
the skip link still clears the whole rail in one stop.

The address is there, and not just a button, because the desk and the console hold **separate
sessions on purpose**. Signing in to one does not sign the user in to the other. The single place
that fact becomes concrete is seeing which account this application is holding, and it costs one line.

### 3.4 Sign-in wears the desk's material and none of its run language

The sign-in screen is a designed surface — it is the showcase's first frame — but it carries no rail,
no strip and no phase marks. Those describe a run, and before authentication there is no run;
showing five steps with state marks would state a run state that does not exist. The shell mounts
after the guard passes, never before it. Email and password only: account creation belongs to the
console, there is no signed-out password reset on the gateway, and a link to one would be a promise
the platform cannot keep.

---

## 4. The journeys

### J1 — Sign in

The user opens the desk, or follows a deep link into a run. A signed-out visitor is sent to
`/sign-in` with their destination preserved, and lands back on exactly that destination — including
the run identifier — after signing in.

A refresh must never flash the sign-in screen: the boot-time session restore gets its one chance
first. The restore beat is words alone, held back for 250ms so the usual sub-300ms restore never
paints a line only to remove it. On failure the message is announced where it is and focus does not
move; moving focus on error is disorienting.

**Never explains how the user got here.** See §6, rule 3.

### J2 — Describe the idea

One field. Nothing else: no optional fields collapsed underneath, no counter, and above all no
"1 of 3". A progress indicator is the single element that turns a first screen into a form to be
endured, and the whole of intake is meant to cost ninety seconds.

The designed shape of this screen has two more parts, and both are **held rather than faked**: the
idea read back to the user in their own frame with the inferred parts marked as inferred, and then
at most three questions, each showing its consequence inline as soon as an option is chosen. Both
need a service that reads the typed idea and answers; the platform has none yet. Anything on this
screen claiming to have understood the idea would be the client writing prose and attributing it to
a system that never read a word.

Two failure modes drive that design and are the reason it stays on the roadmap rather than being
dropped. Questions asked before the system knows anything produce generic answers and therefore a
generic plan. And a user who does not know an answer will invent one, which the run then researches
for half an hour as though it were ground truth — nothing downstream catches it, because the
citation check tests sources, not premises. **"I don't know" is therefore a first-class answer on
every question and visibly changes the plan**: anything answered that way enters the run as a
hypothesis with an experiment attached, never as a premise.

### J3 — Approve the plan

The plan is rendered as a contract, not a summary: each workstream with what it will go looking
for, read off the team's own document, and then the ceilings the run will be held to.

**This is the only approval that interrupts anything.** Every later human moment happens after the
brief exists, because a run that pauses mid-flight waits forever — the platform has no deadline, no
expiry and no notification.

Two rules bind this screen. **Tokens, never money**, while the currency ceiling cannot fire. And **a
figure the team's document does not carry is not shown** — not defaulted, not estimated, not
rendered as a zero. That is why there is no expected duration unless the team declares a wall-time
ceiling, and no source policy at all: the platform has no such field, and writing one would be the
client inventing the terms of a contract it is asking somebody to agree to.

### J4 — Wait, and watch the evidence arrive

The screen the user sees for twenty to ninety minutes, and the least conventional answer in the
application.

**A progress bar is not available and faking one is not acceptable.** The engine writes nothing
usable between start and settle: progress reads zero and then jumps to a hundred, the per-member
status map stays empty, and execution rows do not exist until a member finishes. There is no
server-sent-events plane and no websocket.

So **the waiting screen is an evidence ledger filling up, not a loading state.** Members write
artefacts into the workspace as they run, and polling those artefacts is the only thing on the
platform that moves during a run. It is also a better product than the progress bar would have been:
every row is real work the user can open and read while the run continues. Above the feed sit three
counters derived from the feed alone — sources captured, distinct systems, workstreams producing —
announced to a screen reader as they change.

**Design for leaving.** Twenty to ninety minutes is an errand, not a wait. The primary message is
that the user may close the tab, not that they should stay.

> **Unresolved contradiction — the email.** Two shipped surfaces tell the reader *"we will email you
> when the brief is ready"*: the status strip's running line and the waiting screen's lede. **The
> platform sends no such message.** There is no run-completion notification behind the gateway —
> which is the same fact §4 J3 and `oraclous-frontend#212` both rest on when they say a paused run
> waits forever. So the application's most repeated promise is the one thing on it that nothing can
> keep, and by rule 1 of §6 it should not be on the screen.
>
> This document does not resolve it, because the resolution is a product call and not a design one:
> either the platform gains a completion notification, or the copy changes to what leaving actually
> costs — that the run continues and the brief will be here on return. Tracked as
> `oraclous-frontend#233`. Until it is ruled, treat the copy as **known-wrong and quoted, not
> endorsed**: nothing new may be built on the assumption that the user is told anything.

**The poll cadence is a design decision, not a detail.** The gateway's per-address limiter has
already taken the console down at a fast beat with two tabs open. The status endpoint carries
nothing that moves inside a ninety-minute run, so it is polled slowly; the artefact feed is the only
thing worth watching, and is polled a little faster. The one exception is the plan gate, where the
user is waiting for the screen to acknowledge a decision they just made — the only moment on the
desk where latency is felt. A failed poll shows the last known state, never a blank.

**Explicitly forbidden here:** a percentage, an estimated finish time the platform cannot support,
live agent avatars, "the market analyst is thinking", and typing indicators. Nothing behind the
screen can support any of it, and faking it contradicts the product's own argument in the most
visible possible place.

### J4a — Mid-run questions *(designed, not built; see §10)*

A panel on the waiting screen where the run asks the user something only they can answer.

**The one rule: a mid-run question never blocks the run.** The run continues down the conservative
branch regardless. An answer in time improves the affected work; no answer ships that item as a
hypothesis with an experiment attached, which is what it should have been anyway. The question is an
upgrade, never a gate. Without that rule this is the design review already rejected: a paused run
waits forever, and the promise that the user may close the tab dies with it.

**Every question names what triggered it** — the specific source, at a specific time, that
contradicted a specific assumption. A question with no trigger is a form field, and form fields
belong in intake. At most three are open at once, only where the answer changes the decision, and
each card states what happens either way before the user chooses.

**Both outcomes must be visible in the brief.** An answered question appears as customer evidence
weighted above web sources, and the claim it supports moves off Hypothesis. An unanswered one
appears as a hypothesis whose drawer says plainly that we asked and heard nothing back, and that
this is the designed outcome rather than a failure. That contrast is the argument for the feature.

### J5 — Read the decision brief

The deliverable. Everything else exists to produce this screen.

Above the fold, in order: **the posture** — proceed, validate a prerequisite first, refocus, or hold;
**one sentence of rationale that names the biggest gap**, not a summary; **the cheapest next action**
as a single card with its test, cost, duration and pass/fail thresholds; and **what would change
this**, each hypothesis linked to its experiment. Then five section cards — demand, competition,
economics, risk, founder fit — at **six claims maximum per card**. A section needing more means the
synthesis did not synthesise.

**Per-section evidence strength is one written line, never a meter, a bar or a score.** "Twelve
sources, two primary. The pricing figures are the weakest part here." A number invites the user to
optimise it.

**"We could not establish X" is the integrity feature, and its placement is the whole point.** It is
a normal claim row, in section order, where the answer would have been — not an empty state, not
collapsed, not last, not greyed out. Its drawer shows what we looked at and what would settle it.
The wording carries more than the layout does: *"we could not establish"* reads as a person being
straight with you, where *"insufficient data"* reads as a defect. **Leading with our own limitation
in the top-of-page rationale is the entire differentiation in one sentence.**

**The claim drawer** is the drill path, and it is one drawer at three levels: claim, evidence list,
excerpt, with the excerpt expanding in place rather than on a new page. If auditing a claim costs
four clicks or a navigation, nobody will ever do it. In order it holds the claim and its labels; the
reasoning and the alternatives, when the claim is inferred; the formula and its inputs, when the
claim is computed; what we asked the user about it, including when no answer arrived; the evidence
with source, system, retrieval date and a verbatim excerpt; and then, **below a divider and at
identical visual weight, the counter-evidence and the limits.** That last section is the adversarial
posture made structural and is the part most likely to be quietly de-emphasised. It must not be.

It is a real modal: focus moves in on open and returns to the invoking claim on close, the tab order
is trapped while it is open, the closed drawer leaves the tab order entirely rather than merely
sliding out of view, and both Escape and the scrim close it.

### J6 — Open the economics

A separate screen, because prose that writes its own numbers reconciles wrongly and the failure is
public when it happens. Here prose explains and a versioned calculator computes.

**Every input is itself a labelled claim** carrying its own trust label and a link to its source, or
a note that the user supplied it at intake. This is the part that matters most: a reproducible
formula over an invented input is precision, not accuracy. If two of four inputs are hypotheses, the
page says so and the outputs carry a range rather than a single figure.

The formula is rendered legibly with its substituted values on the line below, not only its symbols.
Scenarios — low, base, high — use tabular figures and scroll within their own container rather than
pushing the page sideways. The page closes by stating what **all** scenarios assume: if every one
rests on a single unproven premise, that sentence says so, and says that the model would need
rebuilding rather than rescaling.

**The client never does the arithmetic.** The numbers come from the run's calculator capability.
With that capability absent, the page renders the inputs and states that the calculation is
unavailable. It never falls back to computing in the browser.

---

## 5. The trust-label system

Six labels. Every claim on the brief and every input on the economics screen carries exactly one.

| Label | Said as | What it means | On the page |
| --- | --- | --- | --- |
| `verified` | Verified | Supported by the sources listed below. | No chip. A dotted underline and a source count. |
| `derived` | Computed | Computed from the inputs below. The arithmetic is ours; the inputs are cited. | No chip. Monospace, signalling computed rather than written. |
| `inferred` | Inferred | This is our read, not a source's. | No chip. The drawer leads with the admission. |
| `hypothesis` | Hypothesis | Not established. It needs an experiment before anything rests on it. | **Chip.** Must link to an experiment. |
| `directional` | Directional | It points a direction and cannot support a decision on its own. | **Chip.** It is a warning against acting on it. |
| `unestablished` | Not established | We looked and could not settle it. Nothing below assumes an answer. | A normal claim row in section order (§4, J5). |

**Two chips on the page, not six.** A badge on every sentence reads as a compliance form; three of
the labels are the expected state and earn no chip at all. Only the two that change what the user
should do next are chipped. The user learns two affordances in about ten seconds, and the page reads
as judgement rather than paperwork.

**Inside the drawer, and in the economics label column, every label is named in full with its
meaning.** There the reader has explicitly asked what backs the sentence, and answering with a
treatment they must decode would withhold the one thing they came for.

**An unrecognised label reads as `inferred`, deliberately.** A typo must never dress a guess up as
evidence.

---

## 6. Honest-state rules

These are the application's own argument applied to its own surfaces. A violation is a defect at the
same severity as a broken screen.

1. **Never show a state the platform cannot substantiate.** No fabricated progress, no invented
   count, no estimated finish time, no confidence score.
2. **Never state something a second surface is about to contradict.** The status strip and the brief
   screen read the same query, because an earlier revision announced "your decision brief is ready"
   directly above a page saying none was written.
3. **A rejected session refresh and a first visit are indistinguishable to the desk, so neither gets
   an explanation.** A signed-out user sees the sign-in screen plainly. There is no "your session
   expired" message, ever, because naming one of two states we cannot tell apart is a fabrication.
4. **A figure the source document does not carry is not shown** — not defaulted, not estimated, not
   rendered as a zero.
5. **No currency figure anywhere** while the platform's spend ceiling cannot fire. Tokens only.
6. **Distinguish "nothing was written" from "something was written that we cannot read".** A run
   whose synthesis is one bracket wrong produced everything and needs one character fixed; telling
   that reader there is nothing is false in the expensive direction. The unreadable document is
   shown in full, unparsed and unrepaired.
7. **And do not overstate the correction either.** A page of instructions quoting the brief's schema
   reaches that state exactly as a real broken brief does. The desk knows two things — it could not
   read the document, and the document carries the marks of a brief — and says exactly those and
   stops. A lenient parser is a repairing parser under another name.
8. **A mark, a tick and a colour are all claims.** The finished treatment belongs to a run that
   delivered; a run that succeeded and left no brief keeps the neutral one.
9. **A failed poll shows the last known state, never a blank** — and once the desk has given up on a
   link it can never load, it says so rather than promising to keep trying.
10. **An absent capability degrades to a stated absence, never to a client-side substitute.**

---

## 7. Design constraints (the seven non-negotiables, as they bind this application)

Per the design-system brand book, restated for the desk. Anything not reachable from the tokens
below is a design-system pull request, not a feature pull request.

1. **Mint is live signal only — and this application reads that rule in two parts, deliberately.**
   Mint (`--accent`) never fills a button and never carries text: at 1.7:1 on paper it cannot, and
   any sentence set in it would fail §7.7 outright. Its one use here is the focus halo. **Live
   signal is therefore carried by `--success`, a green dark enough to hold contrast**, in exactly
   two places: the dot beside the waiting screen's heading while a run is live, and the left rule of
   a status strip whose run delivered. A run that succeeded and left no brief keeps the neutral rule
   — the colour is a claim about the outcome too. This split is a divergence from the brand book's
   literal wording and is recorded here rather than left to be rediscovered per screen.
2. **No emoji.** The desk's marks are a small typographic set, each one decorative and each one
   paired with the same meaning in words for a screen reader.
3. **Banned words in all user-facing copy**, including "journey", "robust", "leverage",
   "seamlessly", "intuitive", "empower" and "ecosystem". Budget an editing pass on anything derived
   from research prose; the source material uses several of them heavily.
4. **Sentence case, second person, bare imperative. Numerals as digits.**
5. **Two surfaces only, paper and ink. No third surface, no gradients — and on this application, no
   shadow anywhere.** The desk is built from rules and surfaces; a shadow would import a foreign
   object into it.
6. **The `>|` lockup never appears alone, and on this application it does not appear at all** — it
   names itself in words instead. **Nothing blinks:** the console's stepped cursor is not used here,
   and the one animated element is the live dot, which fades between full and 35% opacity while a
   run is live. That dot is decorative, hidden from screen readers because the strip says the same
   thing in words, and stopped entirely under reduced motion. Every interactive state change
   transitions, because an instant change reads as broken.
7. **WCAG AA is the floor from the first increment.** Seven type steps, eight spacing steps, two
   radii, nothing off-scale. Every text colour at 4.5:1 or better against every ground it appears
   on, in both themes, and no colour defined only inside a theme block. Nothing below 12.5px except
   uppercase labels at 11px with tracking. Minimum 26px on every interactive target with 8px
   between adjacent ones. An ink focus ring with a contrasting halo on everything — a same-hue ring
   alone is too weak on these surfaces. A skip link past the rail, and the modal contract above on
   the drawer.

One consequence of these worth recording, because it has already forced a change: **an alert colour
on an alert background failed AA on this palette at 3.84:1, and the same colour on plain paper
failed at 4.49:1.** Both routes were closed, so the failure tone moved to a rule and the words are
carried by ink. AA is not negotiable, so when a specified treatment cannot meet it, the treatment
changes rather than the floor.

---

## 8. Deliberately excluded

Carried across from the epic, and excluded for reasons that hold on the frontend as well as the
backend. None of these is a backlog item awaiting capacity; each is a decision.

- **The PDF export.** The brief's value is the drill path from a claim to an excerpt, and that is
  the one thing a printed page cannot carry.
- **Agency and multi-client surfaces.** A different product with a different tenancy story.
- **Version and delta views** between runs.
- **Standing teams and schedules.** The desk runs one idea at a time, on demand.
- **Any settings screen.** There is nothing on this application a user configures.

---

## 9. Deliberately open

**The corpus decision (`oraclous-backend#827`) is unresolved:** open web evidence versus a
customer's own uploaded documents. Every increment of this application is corpus-independent, and
two designed pieces are held until the decision lands rather than guessed at:

- **The upload and corpus-review step in intake** — where it sits in the two steps, and what the
  user is shown about what was ingested.
- **How a source is labelled and chipped** once sources can come from two materially different
  places. The trust labels in §5 describe how well a claim is supported; they say nothing about
  where the supporting material came from, and that is the gap this decision opens.

Neither is designed here. When #827 is ruled, both come back to this document as an amendment.

---

## 10. Where each part stands (2026-08-23)

| Part | State |
| --- | --- |
| Shell, three-phase model, rail, strip | Built. |
| Session layer and sign-in | Built, including the rail's identity row. |
| Describe — the one field | Built. The restatement and the three questions are held on a gateway endpoint that does not exist (§4, J2). |
| Approve the plan | Built, without an expected duration or a source policy — neither is a field the platform carries (§4, J3). |
| Research — the evidence feed | Built. The plan-as-contract section is blocked: the gateway returns no run manifest on any read. |
| Mid-run questions | Designed here, not built. A later stage must be able to read input that arrived after dispatch, and today a run's input is fixed at dispatch. |
| Decision brief and the claim drawer | Built. A live demonstration needs a synthesising member that writes one (`oraclous-backend#853`). |
| Economics | Built, and it degrades honestly while the calculator capability is absent. |
| The "we will email you" promise | **Shipped and wrong.** Two surfaces say it; nothing sends it (§4, J4). `oraclous-frontend#233`. |

---

## Related references

- `oraclous-frontend#208` — the epic, and the increment list this document supersedes as the design
  source.
- `oraclous-frontend#216` — the sign-in design ruling, including the rail amendment in §3.3.
- `oraclous-frontend/docs/specs/` — the per-issue build specs for intake, the research screen, the
  brief, the drawer, the economics and the two brief-recognition corrections.
- [`team-of-agents-console.md`](team-of-agents-console.md) — the console's journey spec. The two
  applications share a design system and a session package, and deliberately not a session.
- [`../../frontend/index.md`](../../frontend/index.md) — frontend architecture and conventions.
