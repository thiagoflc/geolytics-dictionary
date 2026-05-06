#!/usr/bin/env bash
# Publish wiki/*.md to the GitHub Wiki branch.
#
# GitHub Wiki lives in a separate git repo: <repo>.wiki.git.
# This script clones the wiki repo into a temp dir, copies wiki/*.md,
# commits and pushes.
#
# Prerequisites:
#   - Wiki must exist (create at least one page in https://github.com/thiagoflc/geolytics-dictionary/wiki).
#   - You must have push access to the wiki.
#   - `gh` CLI authenticated OR SSH key configured.
#
# Usage:
#   bash wiki/publish.sh                # publishes wiki/ → GitHub Wiki
#   bash wiki/publish.sh --dry-run      # shows diff without pushing

set -euo pipefail

REPO_OWNER="thiagoflc"
REPO_NAME="geolytics-dictionary"
WIKI_REMOTE="https://github.com/${REPO_OWNER}/${REPO_NAME}.wiki.git"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_SRC="${ROOT_DIR}/wiki"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

echo "→ Cloning ${WIKI_REMOTE} into ${TMP_DIR}"
git clone --depth=1 "${WIKI_REMOTE}" "${TMP_DIR}/wiki" 2>&1 \
  || { echo "❌ Failed to clone wiki. Has the Wiki been initialized?"; \
       echo "   Visit https://github.com/${REPO_OWNER}/${REPO_NAME}/wiki and create one page first."; \
       exit 1; }

echo "→ Copying wiki/*.md → wiki repo"
# Copy all .md files (and the publish.sh helper itself? No — exclude scripts and README)
find "${WIKI_SRC}" -maxdepth 1 -type f -name '*.md' -print0 \
  | while IFS= read -r -d '' f; do
      cp "$f" "${TMP_DIR}/wiki/$(basename "$f")"
    done

cd "${TMP_DIR}/wiki"

if ! git diff --quiet || [[ -n "$(git status --porcelain)" ]]; then
  echo "→ Changes detected:"
  git status --short
  echo
  git diff --stat | head -30 || true

  if $DRY_RUN; then
    echo "✅ --dry-run: not pushing."
    exit 0
  fi

  git add -A
  git -c user.name="GeoBrain Wiki Bot" \
      -c user.email="noreply@geobrain.local" \
      commit -m "docs(wiki): sync from main repository wiki/*.md"
  git push origin HEAD
  echo "✅ Wiki updated: https://github.com/${REPO_OWNER}/${REPO_NAME}/wiki"
else
  echo "✅ No changes to publish."
fi
