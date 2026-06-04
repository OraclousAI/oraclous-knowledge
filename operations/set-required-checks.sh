#!/usr/bin/env bash
# set-required-checks.sh — finalize the merge gate by adding required_status_checks to the
# `main-protection` rulesets (ORAA-250). Run this AFTER the CI-split PR (#133) merges, so the
# `lint` job exists on backend `main`. Idempotent (re-PUTs the full ruleset each time).
#
# Gate-able contexts are the ALWAYS-GREEN ones only — backend `lint`, frontend lint + gate jobs.
# The TDD-red `unit`/`integration` jobs are deliberately excluded (ADR-010). Mirrors
# required_checks_for() in gated_merge.sh and ORAA-4 §20.
#
# Usage: operations/set-required-checks.sh
set -uo pipefail
ORG=OraclousAI

pr_rule='{"type":"pull_request","parameters":{"required_approving_review_count":1,"dismiss_stale_reviews_on_push":true,"require_code_owner_review":false,"require_last_push_approval":false,"required_review_thread_resolution":false,"allowed_merge_methods":["merge","squash","rebase"]}}'

checks_rule() {  # $1 = JSON array of {"context":...}
  printf '{"type":"required_status_checks","parameters":{"strict_required_status_checks_policy":true,"do_not_enforce_on_create":false,"required_status_checks":%s}}' "$1"
}

ruleset_body() {  # $1 = optional trailing checks-rule (with leading comma)
cat <<JSON
{
  "name": "main-protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "bypass_actors": [],
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    ${pr_rule}${1:-}
  ]
}
JSON
}

declare -A CHECKS
CHECKS[backend]='[{"context":"lint"}]'
CHECKS[frontend]='[{"context":"Lint / Type-check / Format"},{"context":"Gate 1: api-client-boundary"},{"context":"Gate 2: no-token-in-storage"},{"context":"Gate 3: axe-core AA"},{"context":"Gate 4: bundle-budget"},{"context":"Gate 5: no-dangerouslySetInnerHTML"}]'
CHECKS[knowledge]=''   # no CI workflow

for r in backend frontend knowledge; do
  rid=$(gh api "/repos/$ORG/oraclous-$r/rulesets" --jq '.[] | select(.name=="main-protection") | .id' 2>/dev/null)
  [ -n "$rid" ] || { echo "❌ oraclous-$r: no main-protection ruleset"; continue; }
  if [ -n "${CHECKS[$r]}" ]; then
    body=$(ruleset_body ",$(checks_rule "${CHECKS[$r]}")")
  else
    body=$(ruleset_body "")
  fi
  echo "--- oraclous-$r (ruleset $rid) ---"
  printf '%s' "$body" | gh api -X PUT "/repos/$ORG/oraclous-$r/rulesets/$rid" --input - \
    --jq '{enforcement, rules: [.rules[].type]}' 2>&1 | head -3
done
echo "✅ required checks set. Verify a [tests] PR can still merge (its lint is green; unit/integration red-by-design are not gated)."
