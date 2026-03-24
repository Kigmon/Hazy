#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/publish-main-and-build.sh https://github.com/<owner>/Hazy.git
#
# If origin already exists, URL arg is optional.

REPO_URL="${1:-}"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Commit/stash changes first."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  if [[ -z "$REPO_URL" ]]; then
    echo "No origin remote found. Provide repo URL as first arg."
    exit 1
  fi
  git remote add origin "$REPO_URL"
fi

echo "Switching local branch to main with current content..."
git checkout -B main

echo "Pushing main to origin..."
git push -u origin main

echo "Attempting to trigger GitHub Actions .deb build workflow..."
if command -v gh >/dev/null 2>&1; then
  gh workflow run build-deb.yml || true
  echo "If workflow trigger succeeded, download artifact from:"
  echo "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions"
else
  echo "gh CLI not found. Open GitHub Actions and run 'Build Debian Package' manually."
fi

echo "Done. Repo is published on main."
