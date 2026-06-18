#!/usr/bin/env bash
# gated_merge.sh — the ONLY sanctioned merge path for OraclousAI repos (ORAA-250 / T1.2).
#
# Why this exists: the repos are public with active `main` rulesets enforcing this server-side;
# this script is the rebase-aware client companion + the mandated merge command. It refuses to
# merge unless the required (gate-able) CI checks are green AND there is an approving review by a
# non-author AND the branch is up to date with base. The CTO (and any merger) MUST merge via this
# script instead of raw `gh pr merge`.
#
# Usage:  operations/gated_merge.sh <repo-short> <pr-number> [--squash|--merge|--rebase]
#   repo-short ∈ {backend, frontend, knowledge}   (maps to OraclousAI/oraclous-<repo-short>)
#   default merge method: --squash
#
# Exit 0 = merged. Non-zero = refused (with the reason). Nothing is merged on any failure.
set -uo pipefail

REPO_SHORT="${1:?usage: gated_merge.sh <backend|frontend|knowledge> <pr#> [--squash|--merge|--rebase]}"
PR="${2:?pr number required}"
METHOD="${3:---squash}"
NWO="OraclousAI/oraclous-${REPO_SHORT}"

# REQUIRED, gate-able status checks per repo — these MUST mirror the `main` ruleset's
# required_status_checks. They are the ALWAYS-GREEN contexts only: under ADR-010 two-PR TDD
# the `unit`/`integration` checks are RED-by-design until the `[impl]` lands, so they are
# deliberately NOT listed here (gating on them would freeze the board). Keep in sync with the
# ruleset (set-required-checks below in operations/) and ORAA-4 §20.
required_checks_for() {
  case "$1" in
    backend)  printf '%s\n' "lint" ;;
    frontend) printf '%s\n' \
        "Lint / Type-check / Format" \
        "Gate 1: api-client-boundary" \
        "Gate 2: no-token-in-storage" \
        "Gate 3: axe-core AA" \
        "Gate 4: bundle-budget" \
        "Gate 5: no-dangerouslySetInnerHTML / set:html" ;;  # quality job + 5 ORAA-216 invariant gates (all on main, green)
    knowledge) ;;  # no CI workflow — pre-push hook + review cover it
  esac
}

refuse() { echo "❌ gated_merge REFUSED ($NWO #$PR): $1" >&2; exit 1; }

echo "== gated_merge: $NWO #$PR =="

# 1) PR must be OPEN and mergeable (not DIRTY/BEHIND).
read -r STATE MERGEABLE MERGE_STATE AUTHOR HEAD_SHA < <(
  gh api "/repos/$NWO/pulls/$PR" \
    --jq '[.state, (.mergeable|tostring), .mergeable_state, .user.login, .head.sha] | @tsv' 2>/dev/null) \
  || refuse "cannot read PR"
[ "$STATE" = "open" ] || refuse "PR is not open (state=$STATE)"
case "$MERGE_STATE" in
  dirty)  refuse "merge conflicts (mergeable_state=dirty) — rebase the branch onto base first" ;;
  behind) refuse "branch is BEHIND base (mergeable_state=behind) — rebase before merging" ;;
  blocked|unknown) echo "   note: mergeable_state=$MERGE_STATE — continuing to explicit gates below" ;;
esac

# 2) Each REQUIRED (gate-able) check for this repo must be success. We check only the
#    always-green contexts, NOT the TDD-red unit/integration jobs (see required_checks_for).
#    Written for bash 3.2 (macOS default) — no mapfile/arrays.
REQ_CHECKS="$(required_checks_for "$REPO_SHORT")"
if [ -z "$REQ_CHECKS" ]; then
  echo "   ✓ no required CI contexts for $REPO_SHORT (pre-push hook + review cover it)"
else
  RUNS_JSON=$(gh api "/repos/$NWO/commits/$HEAD_SHA/check-runs" --paginate 2>/dev/null)
  while IFS= read -r ctx; do
    [ -n "$ctx" ] || continue
    concl=$(printf '%s' "$RUNS_JSON" | python3 -c "
import sys,json
ctx=sys.argv[1]; runs=json.load(sys.stdin).get('check_runs',[])
m=[r for r in runs if r.get('name')==ctx]
print(m[-1]['conclusion'] if m else 'MISSING')" "$ctx")
    [ "$concl" = "success" ] || refuse "required check '$ctx' is '$concl' (must be success)"
    echo "   ✓ required check green: $ctx"
  done <<EOF
$REQ_CHECKS
EOF
fi

# 3) At least one APPROVING review by a non-author.
APPROVED_BY_OTHER=$(gh api "/repos/$NWO/pulls/$PR/reviews" \
  --jq "[.[] | select(.state==\"APPROVED\") | .user.login] | map(select(. != \"$AUTHOR\")) | unique | length" 2>/dev/null)
[ "${APPROVED_BY_OTHER:-0}" -ge 1 ] || refuse "no approving review by a non-author (author=$AUTHOR)"
echo "   ✓ approved by a non-author"

# All gates passed — merge.
echo "== all gates passed — merging ($METHOD) =="
gh pr merge "$PR" --repo "$NWO" "$METHOD" --delete-branch || refuse "gh pr merge failed"
echo "✅ merged $NWO #$PR"
