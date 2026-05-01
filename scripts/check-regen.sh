#!/usr/bin/env bash
# check-regen.sh
# Verifies that running the data generation script produces no structural
# changes to tracked files. Timestamp-only diffs in the "generated" field
# are ignored because generate.js always stamps new Date().toISOString().
# Any other diff (added/removed keys, changed values) causes a non-zero exit.
#
# Usage:
#   bash scripts/check-regen.sh
#
# The script is also invoked by the node-tests CI job to ensure that
# data/full.json and api/v1/ are always up-to-date with generate.js.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

echo "Running: node scripts/generate.js"
node scripts/generate.js

echo "Checking for uncommitted diffs in data/full.json and api/v1/ ..."

# Capture diff lines that are not timestamp changes.
# Lines starting with +/- (but not +++ or ---) are actual changes.
# Lines containing only a "generated" timestamp update are ignored.
STRUCTURAL_DIFF=$(
  git diff data/full.json api/v1/ \
    | grep '^[+-]' \
    | grep -v '^---' \
    | grep -v '^+++' \
    | grep -v '"generated":' \
    || true
)

if [ -n "$STRUCTURAL_DIFF" ]; then
    echo ""
    echo "FAIL: regenerated data differs structurally from committed files."
    echo "Run 'node scripts/generate.js' locally and commit the result."
    echo ""
    echo "Structural diff:"
    echo "$STRUCTURAL_DIFF"
    exit 1
else
    echo "OK: no structural changes detected (timestamp diffs are expected and ignored)."
    exit 0
fi
