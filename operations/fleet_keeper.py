#!/usr/bin/env python3
"""fleet-keeper — external intake/anti-stall enforcement for the OraclousAI board.

ORAA-250 (enforcement program: mechanisms, not rules). Runs on a short interval against the
GitHub Issues board (via the `gh` CLI) and keeps work moving so a human is not the load-balancer.

Why this exists
---------------
The board repeatedly dead-ended: ready work sat unassigned (no agent owns it -> nothing to pick),
and blocked issues stayed blocked after their blockers closed. A human had to hand-assign and
hand-label. This script mechanizes the two safe, idempotent corrections.

What it does
------------
KEY: the `backlog` label is the HOLDING state and does NOT queue work; the `ready` label is the
queued state that signals an agent to pick the issue up and start. Readying work = moving it to
`ready`. (This was the real dead-end: assigning while leaving the `backlog` label left work asleep.)

APPLIED (idempotent -> safe for a recurring job; once corrected they stop matching):
  1) AUTO-UNBLOCK  a `blocked` issue whose every blocker (tracked via `blocked-by:` references in
                   the issue body) is closed, that is NOT destructive and NOT `[needs-human]` ->
                   remove `blocked`, add `ready`. Fail-closed: any live blocker, or any prose
                   dependency we cannot verify, leaves it blocked + flagged.
  2) AUTO-ASSIGN   a ready, UNassigned issue (`backlog`, ACTIVE goal, NOT parked) -> assign the
                   role-matched agent AND set `ready`, so it self-starts and never strands ownerless.
  3) PROMOTE       an already-ASSIGNED ready issue stuck in `backlog` (ACTIVE goal, not parked)
                   -> `ready`, so it self-starts. (Assigning alone leaves it in backlog = asleep.)

DIGEST-ONLY (reported, never mutated):
  4) FLAG-STALL    an open in-review/in-progress issue idle > STALL_HOURS -> surfaced for CTO/human.

Guards (ORAA-4 §13.3 fail-closed): destructive titles (delete/migration/archival/...) and
`[needs-human]` issues are NEVER auto-unblocked; parked/deferred issues are NEVER auto-assigned.

Usage
-----
  python3 fleet_keeper.py            # DRY-RUN (default): prints the digest, mutates nothing
  python3 fleet_keeper.py --apply    # applies AUTO-UNBLOCK + AUTO-ASSIGN, prints the digest

Exit code is 0 on success; the digest goes to stdout (captured by cron/launchd logs).
"""
import json, re, subprocess, sys
from datetime import datetime, timezone

REPO = "OraclousAI/oraclous-backend"

# Only the highest-unfinished release + standing parallel tracks are workable, keyed by milestone.
ACTIVE_GOALS = {
    "R3 — Knowledge Graph Decomposition",
    "RF Phase A — Frontend Foundation",
    "Coordination / Platform",
}
STALL_HOURS = 4.0
DESTRUCTIVE = re.compile(r"\b(delete|remove|drop|migration|archival|archive|retire|salvage|irreversible|highest-risk)\b", re.I)
PARKED = re.compile(r"\[(platform/deferred|deferred|platform|gov|investigate)\]|investigate|relocate/quarantine", re.I)
PROSE_DEP = re.compile(r"\b(blocked by|hard-sequenced after|salvage before|depends on|after #\d+)\b", re.I)
BLOCKED_BY = re.compile(r"blocked-by:\s*#(\d+)", re.I)
APPLY = "--apply" in sys.argv


def gh(*args):
    """Run a `gh` CLI command and return stdout (JSON parsed when the output is JSON)."""
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout.strip()
    if not out:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def list_issues():
    """All open issues with the fields we need."""
    fields = "number,title,labels,assignees,milestone,updatedAt,body,state"
    return gh("issue", "list", "--repo", REPO, "--state", "open",
              "--limit", "500", "--json", fields) or []


def labels_of(i):
    return {label["name"] for label in i.get("labels", [])}


def milestone_of(i):
    m = i.get("milestone")
    return m.get("title") if m else None


def hours_since(ts):
    try:
        return (datetime.now(timezone.utc) - datetime.fromisoformat(ts.replace("Z", "+00:00"))).total_seconds() / 3600
    except Exception:
        return None


def role_for(title):
    t = (title or "").lower()
    if "[tests]" in t:
        return "test-author"
    if "[docs]" in t:
        return "docs-writer"
    if "[impl-infra]" in t or "[devops]" in t or "[infra" in t:
        return "devops-implementer"
    if any(k in t for k in ("[rf-", "frontend", "console", "shell-", "fe-")):
        return "frontend-implementer"
    if "[impl]" in t or any(k in t for k in ("kgs", "krs", "endpoint", "service", "backend")):
        return "backend-implementer"
    return None


def set_ready(number, add_assignee=None):
    """Move an issue to the ready/queued state: drop `blocked`/`backlog`, add `ready`."""
    args = ["issue", "edit", str(number), "--repo", REPO,
            "--remove-label", "blocked", "--remove-label", "backlog", "--add-label", "ready"]
    if add_assignee:
        args += ["--add-assignee", add_assignee]
    gh(*args)


def main():
    issues = list_issues()
    by_number = {i["number"]: i for i in issues}
    out = {"unblock": [], "assign": [], "promote": [], "stall": [], "skip": []}

    # 1) AUTO-UNBLOCK — read blockers from the issue body's `blocked-by: #N` references.
    for i in [x for x in issues if "blocked" in labels_of(x)]:
        num, title = i["number"], i.get("title") or ""
        if "[needs-human]" in title.lower() or DESTRUCTIVE.search(title):
            out["skip"].append((num, "blocked: human/destructive-gated (correct)"))
            continue
        body = i.get("body") or ""
        blockers = [int(n) for n in BLOCKED_BY.findall(body)]
        if not blockers:
            out["skip"].append((num, "no structural blockers found; verify"))
            continue
        # A blocker is clear if it is not present in the open-issue set (i.e. closed).
        live = [b for b in blockers if b in by_number]
        if not live:
            if PROSE_DEP.search(body):
                out["skip"].append((num, "structural blockers clear BUT prose-dep present -> fail-closed"))
            else:
                out["unblock"].append((num, title[:55]))
        else:
            out["skip"].append((num, f"live blockers: {live}"))

    # 2) AUTO-ASSIGN + 3) PROMOTE + 4) STALL
    for i in issues:
        num, title = i["number"], i.get("title") or ""
        labels = labels_of(i)
        gid = milestone_of(i)
        assignees = i.get("assignees", [])
        # backlog = holding (does NOT queue work); ready = queued -> picked up and started.
        # So readying work means moving it to `ready`: assign unassigned -> ready, or promote an
        # already-assigned backlog issue -> ready. Parked/deferred work is left in backlog.
        if "backlog" in labels and gid in ACTIVE_GOALS:
            if PARKED.search(title):
                out["skip"].append((num, "backlog parked/deferred -> left in backlog"))
            elif not assignees:
                role = role_for(title)
                out["assign"].append((num, role or "?", role or "NO-MATCH", title[:42]))
            else:
                who = assignees[0].get("login", "?")
                out["promote"].append((num, who, title[:46]))
        if {"in-review", "in-progress"} & labels:
            h = hours_since(i.get("updatedAt"))
            if h is not None and h > STALL_HOURS:
                state = "in-review" if "in-review" in labels else "in-progress"
                out["stall"].append((num, f"{state} idle {h:.1f}h"))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    print(f"=== fleet-keeper {'APPLY' if APPLY else 'DRY-RUN'} | {REPO} | {stamp} ===")

    print(f"-- AUTO-UNBLOCK -> ready ({len(out['unblock'])}) --")
    for num, t in out["unblock"]:
        print(f"   #{num}  {t}")
        if APPLY:
            set_ready(num)

    print(f"-- AUTO-ASSIGN -> ready ({len(out['assign'])}) --")
    for num, role, who, t in out["assign"]:
        print(f"   #{num}  role={role} -> {who}  {t}")
        if APPLY and who not in ("NO-MATCH", None):
            set_ready(num, add_assignee=who)

    print(f"-- PROMOTE backlog->ready (assigned, ready) ({len(out['promote'])}) --")
    for num, who, t in out["promote"]:
        print(f"   #{num}  agent={who}  {t}")
        if APPLY:
            set_ready(num)

    print(f"-- FLAG-STALL (digest-only; for CTO/human) ({len(out['stall'])}) --")
    for num, why in out["stall"]:
        print(f"   #{num}  {why}")

    print(f"-- SKIPPED (guarded/parked) ({len(out['skip'])}) --")
    for num, why in out["skip"]:
        print(f"   #{num}  {why}")

    print("=== done ===")


if __name__ == "__main__":
    main()
