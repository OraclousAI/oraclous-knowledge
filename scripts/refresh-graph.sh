#!/bin/sh
# scripts/refresh-graph.sh — manual knowledge-graph refresh (ORAA-4 §16 / ORAA-210)
#
# Runs `graphify update` on the KB, stages graphify-out/, and prints the next
# step. Use this when you need to refresh the graph outside a normal KB commit:
#
#   - Release-seam retrospective (ORAA-4 §14): run before or after the retro
#     to ensure the graph reflects the full sprint's merged docs.
#   - After bulk imports or cross-repo doc syncs that bypass normal commits.
#   - Manual hygiene check after a long stretch without a KB change.
#
# The pre-commit hook (`.githooks/pre-commit`) already runs this automatically
# whenever a KB content section is staged. This script is the escape hatch for
# cases where the hook didn't run or the graph is known to be stale.
#
# Usage:
#   sh scripts/refresh-graph.sh           # refresh + stage
#   sh scripts/refresh-graph.sh --check   # report staleness only (no update)

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

if ! command -v graphify >/dev/null 2>&1; then
	echo "Error: graphify is not installed or not in PATH." >&2
	echo "Install it with: pip install graphify" >&2
	exit 1
fi

if [ "${1:-}" = "--check" ]; then
	echo "graphify --check not supported natively; comparing manifest mtime..."
	if [ -f graphify-out/manifest.json ]; then
		newest_md=$(find adr architecture compliance contracts engineering flows frontend meta operations releases services-reference -name "*.md" -newer graphify-out/manifest.json 2>/dev/null | head -1)
		if [ -n "$newest_md" ]; then
			echo "⚠  Knowledge graph may be stale: $newest_md is newer than graphify-out/manifest.json"
			exit 1
		else
			echo "✅ Knowledge graph appears current."
			exit 0
		fi
	else
		echo "⚠  graphify-out/manifest.json not found; graph has never been built."
		exit 1
	fi
fi

echo "Refreshing knowledge graph..."
graphify update "$REPO_ROOT"

echo ""
echo "Staging graphify-out/ changes..."
git add graphify-out/

STAGED=$(git diff --cached --name-only graphify-out/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$STAGED" -gt 0 ]; then
	echo ""
	echo "✅ $STAGED graphify-out/ file(s) staged."
	echo "   Commit with: git commit -m '[ORAA-xx] [agent:docs-writer] chore: refresh knowledge graph'"
else
	echo ""
	echo "✅ graphify-out/ is already current — nothing to stage."
fi
