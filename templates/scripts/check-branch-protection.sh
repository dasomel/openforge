#!/usr/bin/env bash
set -euo pipefail

repo="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")}"
branch="${2:-main}"

if [[ -z "$repo" ]]; then
  echo "Usage: $0 <owner/repo> [branch]" >&2
  exit 1
fi

echo "Checking branch protection for $repo @ $branch..."

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI is required." >&2
  exit 1
fi

response=$(gh api "repos/$repo/branches/$branch" 2>/dev/null || true)

if [[ -z "$response" ]]; then
  echo "Error: Could not fetch branch info for $repo ($branch)." >&2
  exit 1
fi

protected=$(echo "$response" | grep -o '"protected":[^,}]*' | head -n 1 | cut -d: -f2 | tr -d ' "')

if [[ "$protected" == "true" ]]; then
  echo "✅ Branch '$branch' is PROTECTED."
  gh api "repos/$repo/branches/$branch/protection" 2>/dev/null || true
else
  echo "⚠️  Branch '$branch' is UNPROTECTED (protected: false)."
  echo "Consider applying baseline branch protection per docs/branch-protection.md."
fi
