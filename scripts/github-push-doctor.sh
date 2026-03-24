#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "[FAIL] gh CLI not found. Install: sudo apt-get install -y gh"
  exit 1
fi

REPO_SLUG="${1:-}"
if [[ -z "$REPO_SLUG" ]]; then
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    REPO_SLUG="$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)"
  fi
fi

if [[ -z "$REPO_SLUG" ]]; then
  echo "Usage: $0 <owner/repo>"
  echo "Example: $0 Kigmon/Hazy"
  exit 1
fi

echo "== GitHub auth =="
gh auth status -h github.com || true

echo
echo "== Repo info =="
gh repo view "$REPO_SLUG" --json nameWithOwner,viewerPermission,isPrivate,isArchived,defaultBranchRef

echo
echo "== Branch protection check (default branch) =="
DEFAULT_BRANCH="$(gh repo view "$REPO_SLUG" --json defaultBranchRef -q .defaultBranchRef.name)"
if gh api "repos/$REPO_SLUG/branches/$DEFAULT_BRANCH/protection" >/dev/null 2>&1; then
  echo "[INFO] Branch protection is enabled on $DEFAULT_BRANCH"
else
  echo "[INFO] Branch protection API not enabled or no protection configured for $DEFAULT_BRANCH"
fi

echo
echo "== Rulesets API probe =="
RULESET_ERR="$(gh api "repos/$REPO_SLUG/rulesets" 2>&1 >/dev/null || true)"
if [[ -z "$RULESET_ERR" ]]; then
  echo "[INFO] Rulesets API is accessible"
else
  echo "[WARN] Rulesets API error:"
  echo "$RULESET_ERR"
  if echo "$RULESET_ERR" | grep -q "Upgrade to GitHub Pro or make this repository public"; then
    echo
    echo "[ACTION] This repo/account cannot query rulesets on private repo under current plan."
    echo "         Make repo public temporarily or upgrade plan, then retry push/publish."
  fi
fi

echo
echo "== Next-step quick actions =="
echo "1) If main push is blocked, push a branch then open PR:"
echo "   git push -u origin HEAD:fix/publish"
echo "2) Publish artifacts via Actions after code lands."
