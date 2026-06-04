#!/usr/bin/env python3
"""fleet-keeper — external intake/anti-stall enforcement for the OraclousAI PaperClip fleet.

ORAA-250 (enforcement program: mechanisms, not rules). Runs on a short interval against the
local PaperClip API and keeps the board moving so a human is not the load-balancer.

Why this exists
---------------
The fleet repeatedly dead-ended: ready work sat unassigned (no agent owns it -> heartbeat has
nothing to pick), and blocked issues stayed blocked after their blockers closed. A human had to
hand-assign and hand-trigger. This script mechanizes the two safe, idempotent corrections.

What it does (verified against the real PaperClip data model, 2026-06-04)
------------------------------------------------------------------------
APPLIED (idempotent -> safe for a recurring job; once corrected they stop matching):
  1) AUTO-UNBLOCK  a `blocked` issue whose every `blockedBy[]` (read from the SINGLE-issue GET;
                   the list endpoint omits it) is done/cancelled, that is NOT destructive and
                   NOT `[needs-human]` -> set status `backlog`. Fail-closed: any live blocker,
                   or any prose dependency we cannot verify, leaves it blocked + flagged.
  2) AUTO-ASSIGN   a ready issue (`backlog`, in an ACTIVE goal, NOT parked/deferred) with no
                   assignee -> the role-matched agent, so work never strands ownerless. Once
                   assigned, the agent's own heartbeat picks it up.

  3) WAKE          an IDLE agent that has assigned ready work sitting (issue `backlog`/`in_progress`,
                   no active run, idle > WAKE_MIN) -> trigger `paperclipai heartbeat run --agent-id
                   <id> --source assignment`. This is the missing first-wake: assigning an issue
                   does NOT schedule a run (issues have no monitorNextCheckAt), so without this the
                   board dead-ends with the human hand-triggering. Deduped per agent; idle agents
                   only (never double-triggers a running one); the WAKE_MIN gate bounds re-tries.

DIGEST-ONLY (reported, never mutated):
  4) FLAG-STALL    in_review/in_progress idle > STALL_HOURS -> surfaced for the CTO/human.

Guards (ORAA-4 §13.3 fail-closed): destructive titles (delete/migration/archival/...) and
`[needs-human]` issues are NEVER auto-unblocked; parked/deferred issues are NEVER auto-assigned.

Usage
-----
  python3 fleet_keeper.py            # DRY-RUN (default): prints the digest, mutates nothing
  python3 fleet_keeper.py --apply    # applies AUTO-UNBLOCK + AUTO-ASSIGN, prints the digest

Exit code is 0 on success; the digest goes to stdout (captured by cron/launchd logs).
"""
import glob, json, os, re, subprocess, sys, urllib.request
from datetime import datetime, timezone

API = "http://127.0.0.1:3100/api"
COMPANY_ID = "19cdd0be-92a9-4599-a591-d578da8ab2c5"   # OraclousAI (prefix ORAA)

# Only the highest-unfinished release + standing parallel tracks are workable.
ACTIVE_GOALS = {
    "0e34e971-52ee-4003-96aa-5aef472f577f",  # R3 — Knowledge Graph Decomposition
    "6a4b4608-04db-47ea-bf48-d0ffabee5bbc",  # RF Phase A — Frontend Foundation
    "09a7702a-315d-4120-a7ad-18a8a00de373",  # Coordination / Platform
}
STALL_HOURS = 4.0
WAKE_MIN = 30.0
DESTRUCTIVE = re.compile(r"\b(delete|remove|drop|migration|archival|archive|retire|salvage|irreversible|highest-risk)\b", re.I)
PARKED = re.compile(r"\[(platform/deferred|deferred|platform|gov|investigate)\]|investigate|relocate/quarantine", re.I)
PROSE_DEP = re.compile(r"\b(blocked by|hard-sequenced after|salvage before|depends on|after ORAA-\d+)\b", re.I)
APPLY = "--apply" in sys.argv


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def listy(x):
    return x if isinstance(x, list) else x.get("data", [])


def paperclip_bin():
    """Resolve the installed paperclipai entrypoint (npx cache path has a rotating hash)."""
    cands = sorted(glob.glob(os.path.expanduser("~/.npm/_npx/*/node_modules/paperclipai/dist/index.js")),
                   key=lambda p: os.path.getmtime(p), reverse=True)
    return cands[0] if cands else None


def trigger_heartbeat(agent_id):
    """Fire one agent heartbeat (source=assignment) to start its assigned work, fire-and-forget.
    The spawned run is decoupled from this CLI streamer, so a short --timeout-ms is fine."""
    binp = paperclip_bin()
    if not binp:
        return "paperclipai bin not found"
    try:
        subprocess.Popen(
            ["node", binp, "heartbeat", "run", "--agent-id", agent_id,
             "--source", "assignment", "--trigger", "system", "--timeout-ms", "2000"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return "triggered"
    except Exception as e:
        return f"trigger-failed: {e}"


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


def main():
    issues = listy(api("GET", f"/companies/{COMPANY_ID}/issues"))
    agents = listy(api("GET", f"/companies/{COMPANY_ID}/agent-configurations"))
    by_ident = {i.get("identifier"): i for i in issues}
    name_to_agent = {a.get("name"): a for a in agents}
    be_agents = [a for a in agents if (a.get("name") or "").startswith("backend-implementer")]
    running = {a["id"] for a in agents if a.get("status") == "running"}
    agent_status = {a["id"]: a.get("status") for a in agents}
    agent_name = {a["id"]: a.get("name") for a in agents}
    out = {"unblock": [], "assign": [], "wake": [], "stall": [], "skip": []}

    # 1) AUTO-UNBLOCK — requires the single-issue blockedBy[]
    for i in [x for x in issues if x.get("status") == "blocked"]:
        ident, title = i.get("identifier"), i.get("title") or ""
        if "[needs-human]" in title.lower() or DESTRUCTIVE.search(title):
            out["skip"].append((ident, "blocked: human/destructive-gated (correct)"))
            continue
        try:
            full = api("GET", f"/issues/{i['id']}")
            full = full.get("data", full) if isinstance(full, dict) else full
        except Exception as e:
            out["skip"].append((ident, f"fetch-fail {e}"))
            continue
        blockers = full.get("blockedBy") or []
        desc = full.get("description") or ""
        if blockers and all(b.get("status") in ("done", "cancelled") for b in blockers):
            if PROSE_DEP.search(desc):
                out["skip"].append((ident, "structural blockers clear BUT prose-dep present -> fail-closed"))
            else:
                out["unblock"].append((ident, title[:55]))
        else:
            live = [b.get("identifier") for b in blockers if b.get("status") not in ("done", "cancelled")]
            out["skip"].append((ident, f"live blockers: {live or '(none structural; verify)'}"))

    # 2) AUTO-ASSIGN + 3) WAKE + 4) STALL
    for i in issues:
        st, gid, title = i.get("status"), i.get("goalId"), i.get("title") or ""
        assignee = i.get("assigneeAgentId")
        if st == "backlog" and not assignee and gid in ACTIVE_GOALS:
            if PARKED.search(title):
                out["skip"].append((i["identifier"], "backlog parked/deferred -> not auto-assigned"))
                continue
            role = role_for(title)
            tgt = None
            if role == "backend-implementer" and be_agents:
                tgt = ([a for a in be_agents if a["id"] not in running] or be_agents)[0]
            elif role and role in name_to_agent:
                tgt = name_to_agent[role]
            out["assign"].append((i["identifier"], role or "?", (tgt or {}).get("name", "NO-MATCH"), title[:42]))
        if st in ("backlog", "in_progress") and assignee and not i.get("activeRun") and not PARKED.search(title):
            h = hours_since(i.get("lastActivityAt") or i.get("updatedAt"))
            if h is not None and h * 60 > WAKE_MIN and gid in ACTIVE_GOALS:
                out["wake"].append((i["identifier"], st, assignee, f"idle {h:.1f}h, assigned, no active run"))
        if st in ("in_review", "in_progress"):
            h = hours_since(i.get("lastActivityAt") or i.get("updatedAt"))
            if h is not None and h > STALL_HOURS:
                out["stall"].append((i["identifier"], f"{st} idle {h:.1f}h"))

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    print(f"=== fleet-keeper {'APPLY' if APPLY else 'DRY-RUN'} | {COMPANY_ID[:8]} | {stamp} ===")

    print(f"-- AUTO-UNBLOCK -> backlog ({len(out['unblock'])}) --")
    for ident, t in out["unblock"]:
        print(f"   {ident}  {t}")
        if APPLY:
            api("PATCH", f"/issues/{by_ident[ident]['id']}", {"status": "backlog"})

    print(f"-- AUTO-ASSIGN ({len(out['assign'])}) --")
    for ident, role, who, t in out["assign"]:
        print(f"   {ident}  role={role} -> {who}  {t}")
        if APPLY and who not in ("NO-MATCH", None):
            api("PATCH", f"/issues/{by_ident[ident]['id']}",
                {"assigneeAgentId": name_to_agent[who]["id"], "status": "backlog"})

    print(f"-- WAKE (trigger heartbeat run for idle assigned agents) ({len(out['wake'])}) --")
    woken = set()
    for ident, st, aid, why in out["wake"]:
        nm = agent_name.get(aid, (aid or "?")[:8])
        idle = agent_status.get(aid) == "idle"
        tag = "[idle -> trigger]" if idle else f"[agent {agent_status.get(aid)}; skip]"
        print(f"   {ident}  {st}  agent={nm}  {why}  {tag}")
        if APPLY and idle and aid not in woken:
            woken.add(aid)
            print(f"      -> heartbeat run {nm}: {trigger_heartbeat(aid)}")

    print(f"-- FLAG-STALL (digest-only; for CTO/human) ({len(out['stall'])}) --")
    for ident, why in out["stall"]:
        print(f"   {ident}  {why}")

    print(f"-- SKIPPED (guarded/parked) ({len(out['skip'])}) --")
    for ident, why in out["skip"]:
        print(f"   {ident}  {why}")

    print("=== done ===")


if __name__ == "__main__":
    main()
