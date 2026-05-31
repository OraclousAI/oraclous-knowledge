# Jira board and workflow mapping

**Document status:** Active · **Owned by:** product-planner with tech-lead sign-off

## The eight columns

| Column | WIP limit | Owning agent |
| --- | --- | --- |
| BACKLOG | — | product-planner (or unowned) |
| READY | — | test-author (BE); frontend-implementer (FE) |
| TESTS AUTHORING | 3 | test-author |
| TESTS REVIEWS | 3 | be-test-reviewer |
| IMPLEMENTATION | 5 | backend-implementer / frontend-implementer |
| CODE REVIEW | 5 | code-reviewer + qa-engineer (BE); human tech-lead (FE) |
| DONE | — | — |
| BLOCKED | — | `human` |

## BLOCKED means "human, you are the unblock"

BLOCKED is reserved for tickets that cannot proceed **without human action**. A ticket enters BLOCKED only via the `escalate_to_human` operation (all four steps together). A ticket waiting on a dependency does NOT go to BLOCKED — it stays in its column and links the blocker via a "is blocked by" link.

## The frontend asymmetry (deliberate, temporary)

FE work currently has no test-authoring, test-review, or code-review agent. FE tickets move READY → IMPLEMENTATION → CODE REVIEW (human) → DONE. Re-evaluate at RF Phase B.

## Agent Owner field and issue type IDs

- `Agent Owner` = `customfield_10074`, 13 options
- `needs-human` = `customfield_10075`, option id `10032`
- `human` option id = `10031`
- `Contract` type id = `10049`, `ADR` = `10016`, `Spike` = `10015`
