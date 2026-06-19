# Operations enforcement scripts (ORAA-250)

Two external enforcement **mechanisms** (not rules) live in `operations/`:

- `fleet_keeper.py` — intake & anti-stall automation for the GitHub Issues board (documented below).
- `gated_merge.sh` — the **only sanctioned merge path** for the repos. See "Merge gating" below.

## Merge gating — `gated_merge.sh`

> **Non-author review requires a second identity.** All agents act as one GitHub user, which cannot approve its own PRs. The CTO approves under a second identity whose token lives in `~/.config/oraclous/reviewer-gh-token` (chmod 600). Run `operations/setup-reviewer-identity.sh` to provision/verify it. Without it, the `main` ruleset's non-author-review rule deadlocks all merges.


The three repos are **public**, and each `main` has an **active GitHub ruleset** (empty `bypass_actors`)
enforcing CI-green + a non-author approving review + up-to-date base, server-side. `gated_merge.sh` is
the **defense-in-depth client companion** to that ruleset and the rebase-aware merge convenience: it
refuses to *attempt* a merge unless **CI is green** AND there is an **approving review by a non-author**
AND the **branch is up to date with base** (not behind/dirty), reporting the exact reason on refusal.

```sh
operations/gated_merge.sh <backend|frontend|knowledge> <pr#> [--squash|--merge|--rebase]
```

The CTO (and any merger) MUST merge via this script instead of raw `gh pr merge`. Knowledge has no
CI workflow, so its status-check gate is skipped (the pre-push hook covers quality there).

> The server-side rulesets are the primary gate (live as of 2026-06-04, ORAA-250); this script is the
> defense-in-depth / rebase-aware convenience path. If the repos ever return to private on the free
> tier, rulesets become unavailable and this script becomes the *only* gate again.

---

# Fleet-keeper — intake & anti-stall automation (ORAA-250)

`operations/fleet_keeper.py` is an **external enforcement mechanism** (not a rule) that keeps the
OraclousAI GitHub Issues board moving without a human acting as load-balancer. It drives the board
through the `gh` CLI on a short interval.

This file documents what it does, why, and how to run/schedule it. The script's own docstring is
the authoritative behaviour reference.

## The problem it fixes

The fleet repeatedly **dead-ended** and required manual intervention:

- **Ready work stranded ownerless.** An open issue with no assignee is invisible to every agent
  (agents pick up *assigned* work), so it sat until a human assigned it.
- **Stale blocks.** An issue stayed blocked after all its blockers closed, because nothing
  re-evaluated and unblocked it. Agents then picked it up and burned failing runs.

Both are state-correction problems. The keeper applies the two **idempotent** corrections every
cycle; once corrected, an issue stops matching, so the job is safe to run on a tight schedule.

## What it does

| Action | Mode | Rule |
|---|---|---|
| **AUTO-UNBLOCK** | applied | a blocked issue whose every blocking issue is closed, not destructive, not `needs-human`, no unverifiable prose dependency → remove the `blocked` label. **Fail-closed.** |
| **AUTO-ASSIGN** | applied | ready UNassigned issue (open, active milestone, not parked) → assign the role-matched agent **and add the `ready` label** (so it gets picked up). |
| **PROMOTE** | applied | already-ASSIGNED ready issue not yet marked ready (active milestone, not parked) → add the `ready` label. Assigning alone leaves it unqueued. |
| **FLAG-STALL** | digest-only | an in-review/in-progress issue idle > 4h → surfaced for the CTO/human. |

### Guards (ORAA-4 §13.3, fail-closed)

- **Never auto-unblocks** an issue whose title matches `delete|remove|drop|migration|archival|retire|salvage|irreversible|highest-risk`, or any `needs-human` issue — these require explicit human sign-off.
- **Never auto-unblocks** when structural blockers are clear but the description carries an
  unverifiable prose dependency (`blocked by`, `hard-sequenced after`, `salvage before`, …).
- **Never auto-assigns** a parked/deferred issue (`[deferred]`, `[platform]`, `[gov]`, `investigate`, …).

The named regression this guard exists for: **ORAA-78** (destructive R2 story) was once false-unblocked
because its prose dependency on ORAA-77 wasn't in a structured blocking-issue reference.

## Data-model notes (why the code looks the way it does)

- Blocking relations (the issues a given issue is blocked by, with each blocker's open/closed state)
  are read per issue via the `gh` CLI / GitHub API, so unblock logic fetches each blocked issue
  individually.
- **An unassigned issue is invisible to the fleet.** Assignment plus the `ready` label is what queues
  an issue for an agent to pick up; an open, unlabelled issue sits in the backlog. Readying = assigning
  and labelling `ready`. (This was the real dead-end.)

## Running it

```sh
python3 operations/fleet_keeper.py            # DRY-RUN (default) — prints digest, mutates nothing
python3 operations/fleet_keeper.py --apply    # applies UNBLOCK + ASSIGN, prints digest
```

Always read a dry-run before trusting a change to the goal set or guards.

## Scheduling

Two supported paths; pick one.

### A. launchd (survives everything; runs with no Claude session open) — preferred for production

```sh
cp operations/com.oraclous.fleet-keeper.plist ~/Library/LaunchAgents/
# edit the plist if the repo path differs from /Users/reza/workspace/OraclousAI/oraclous-knowledge
launchctl load  ~/Library/LaunchAgents/com.oraclous.fleet-keeper.plist   # arm (runs every 10 min)
launchctl unload ~/Library/LaunchAgents/com.oraclous.fleet-keeper.plist  # disarm
tail -f /tmp/fleet-keeper.log                                            # watch the digest
```

The plist runs `--apply` every 600s and appends each digest to `/tmp/fleet-keeper.log`.

### B. Claude-session cron (CronCreate)

A durable CronCreate job in the coordinator session runs the script every ~10 min while the REPL is
idle. Session-scoped and auto-expires after 7 days — fine for a supervised window, not for unattended
production. Use path A for anything long-lived.

## Maintenance

- **ACTIVE_GOALS** must track the current release. When a release closes and the next opens, update the
  goal-id set at the top of `fleet_keeper.py` (a dry-run will show issues being skipped if it's stale).
- **Role mapping** (`role_for`) keys off title tags (`[tests]`, `[docs]`, `[impl-infra]`, `[rf-*]`,
  `[impl]`). Keep it in sync with the labelling conventions in `engineering/pr-conventions.md`.
