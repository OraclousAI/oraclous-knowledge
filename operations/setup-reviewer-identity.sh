#!/usr/bin/env bash
# setup-reviewer-identity.sh — verify the second GitHub identity used to satisfy the
# "non-author approving review" ruleset (ORAA-250). The agents all act as one GitHub
# user (`Jahankohan`), which cannot approve its own PRs; the CTO approves under a second
# identity whose token lives in ~/.config/oraclous/reviewer-gh-token (chmod 600).
#
# This script does NOT create or print the token. It validates that the token file exists,
# resolves to a DIFFERENT GitHub login than the agents' identity, and can see the repos.
#
# One-time setup (you do this):
#   1. Create a GitHub PAT for a SECOND identity (your `fardinvahdat` org account, or a
#      dedicated machine-user invited to the OraclousAI org). Scopes: classic `repo`
#      (+ `workflow`), or fine-grained with Contents:RW + Pull requests:RW on the 3 repos.
#   2. mkdir -p ~/.config/oraclous && umask 077
#      printf '%s' '<TOKEN>' > ~/.config/oraclous/reviewer-gh-token
#      chmod 600 ~/.config/oraclous/reviewer-gh-token
#   3. Run this script to verify.
set -uo pipefail
TOKEN_FILE="${HOME}/.config/oraclous/reviewer-gh-token"
AGENT_IDENTITY="Jahankohan"   # the single identity all agents currently use

fail() { echo "❌ $1" >&2; exit 1; }

[ -f "$TOKEN_FILE" ] || fail "missing $TOKEN_FILE — create the reviewer PAT and save it there (see header)."
perms=$(stat -f '%Lp' "$TOKEN_FILE" 2>/dev/null || stat -c '%a' "$TOKEN_FILE" 2>/dev/null)
[ "$perms" = "600" ] || echo "⚠️  $TOKEN_FILE is mode $perms — recommend 600."

TOKEN="$(cat "$TOKEN_FILE")"
[ -n "$TOKEN" ] || fail "$TOKEN_FILE is empty."

LOGIN=$(GH_TOKEN="$TOKEN" gh api /user --jq '.login' 2>/dev/null) || fail "token is invalid (gh /user failed)."
echo "reviewer token resolves to GitHub login: $LOGIN"
[ "$LOGIN" != "$AGENT_IDENTITY" ] || fail "reviewer identity ($LOGIN) is the SAME as the agents' identity ($AGENT_IDENTITY) — a PR cannot be approved by its own author. Use a different account."

echo "checking repo visibility + PR-review capability:"
for r in oraclous-backend oraclous-frontend oraclous-knowledge; do
  perm=$(GH_TOKEN="$TOKEN" gh api "/repos/OraclousAI/$r" --jq '.permissions.push' 2>/dev/null)
  [ "$perm" = "true" ] && echo "   ✓ $r: write access" || echo "   ⚠️  $r: no write access (reviews may still post, but cannot merge)"
done

echo "✅ reviewer identity '$LOGIN' is provisioned and distinct from the agents' '$AGENT_IDENTITY'."
echo "   The CTO will approve PRs with:  GH_TOKEN=\$(cat $TOKEN_FILE) gh pr review <pr#> --repo OraclousAI/<repo> --approve"
