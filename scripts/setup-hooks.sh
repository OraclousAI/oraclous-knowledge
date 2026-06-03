#!/bin/sh
# Point git at the repo's tracked hooks directory.
#
# core.hooksPath is LOCAL config (not committed), so each clone must run this
# once to activate the .githooks/pre-commit hook that keeps index.md and
# llms.txt current.
#
# Usage:
#   sh scripts/setup-hooks.sh

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
git config core.hooksPath .githooks
chmod +x "$REPO_ROOT/.githooks/pre-commit" 2>/dev/null || true

echo "core.hooksPath set to .githooks — KB index pre-commit hook is active."
