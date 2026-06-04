#!/usr/bin/env bash
# gated_merge.sh — the ONLY sanctioned merge path for OraclousAI repos (ORAA-250 / T1.2).
#
# Why this exists: the org is on GitHub free tier, where server-side branch protection and
# rulesets are unavailable for private repos. This script is the client-side enforcement of
# the Definition of Done at the merge point: it refuses to merge unless CI is green AND there
# is an approving review by a non-author AND the branch is up to date with base. The CTO (and
# any merger) MUST merge via this script instead of raw `gh pr merge`.
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

# Repos with no CI workflow skip the status-check gate (knowledge: pre-push hook covers quality).
NO_CI_REPOS=" knowledge "

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

# 2) Required CI checks must all be success (unless this repo has no CI).
if [[ "$NO_CI_REPOS" != *" $REPO_SHORT "* ]]; then
  mapfile -t BAD < <(gh api "/repos/$NWO/commits/$HEAD_SHA/check-runs" \
    --jq '.check_runs[] | select(.conclusion != "success" and .conclusion != "neutral" and .conclusion != "skipped") | "\(.name)=\(.status)/\(.conclusion)"' 2>/dev/null)
  TOTAL=$(gh api "/repos/$NWO/commits/$HEAD_SHA/check-runs" --jq '.total_count' 2>/dev/null)
  [ "${TOTAL:-0}" -gt 0 ] || refuse "no CI check-runs reported on $HEAD_SHA (CI did not run — is GitHub Actions billing OK?)"
  [ "${#BAD[@]}" -eq 0 ] || refuse "CI not green: ${BAD[*]}"
  echo "   ✓ CI green ($TOTAL checks)"
else
  echo "   ✓ no-CI repo ($REPO_SHORT): status-check gate skipped (pre-push hook covers quality)"
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
