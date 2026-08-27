#!/usr/bin/env bash
set -euo pipefail

# OpenForge Branch Protection Planner & Enforcement Tool
# Queries active check-runs on the target branch, compares against standard baseline,
# and safely plans or applies branch protection rules.

repo="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")}"
branch="${2:-main}"
apply=false

for arg in "$@"; do
  if [[ "$arg" == "--apply" ]]; then
    apply=true
  fi
done

if [[ -z "$repo" ]]; then
  echo "Usage: $0 <owner/repo> [branch] [--apply]" >&2
  exit 1
fi

echo "======================================================================"
echo "OpenForge Branch Protection Planner"
echo "Repository : $repo"
echo "Branch     : $branch"
echo "Mode       : $(if [ "$apply" = true ]; then echo "APPLY (live mutation)"; else echo "PLAN (dry-run)"; fi)"
echo "======================================================================"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) is required." >&2
  exit 1
fi

echo "Fetching recent commits and check-runs from GitHub..."

# Fetch latest commit SHA on target branch
commit_sha=$(gh api "repos/$repo/commits/$branch" --jq '.sha' 2>/dev/null || echo "")
if [[ -z "$commit_sha" ]]; then
  echo "Error: Could not fetch latest commit on branch '$branch' for $repo." >&2
  exit 1
fi

echo "Latest Commit: $commit_sha"

# Fetch check runs for the latest commit
check_runs_json=$(gh api "repos/$repo/commits/$commit_sha/check-runs" 2>/dev/null || echo "{\"check_runs\":[]}")
detected_checks=$(echo "$check_runs_json" | gh api --input - --jq '.check_runs[].name' 2>/dev/null | sort -u || true)

# Standard requested checks for OpenForge Tier 1 repositories
standard_requested=(
  "repository-check"
  "adr-validation"
  "supply-chain"
  "compliance-test"
  "markdown"
)

echo ""
echo "Detected CI Check Contexts on '$branch':"
if [[ -z "$detected_checks" ]]; then
  echo "  (No check-runs detected yet on latest commit)"
else
  while IFS= read -r check; do
    echo "  ✓ $check"
  done <<< "$detected_checks"
fi

echo ""
echo "Standard Requested Checks Evaluation:"
ready_contexts=()
missing_contexts=()

for req in "${standard_requested[@]}"; do
  if echo "$detected_checks" | grep -qx "$req"; then
    echo "  ✓ $req (Active)"
    ready_contexts+=("$req")
  else
    echo "  ? $req (Missing or not yet run on latest commit)"
    missing_contexts+=("$req")
  fi
done

# If only legacy single-job repository-check is present, adjust plan
if [[ ${#ready_contexts[@]} -eq 0 ]] && echo "$detected_checks" | grep -q "repository-check"; then
  ready_contexts=("repository-check" "markdown")
fi

echo ""
echo "======================================================================"
if [[ ${#ready_contexts[@]} -ge 1 ]]; then
  plan_status="READY"
  echo "Plan Status: READY"
  echo "Contexts to be enforced (${#ready_contexts[@]}): ${ready_contexts[*]}"
else
  plan_status="BLOCKED"
  echo "Plan Status: BLOCKED (No matching standard checks observed on latest commit)"
fi
echo "======================================================================"

if [[ "$apply" == true ]]; then
  if [[ "$plan_status" != "READY" ]]; then
    echo "Cannot apply branch protection while plan status is BLOCKED." >&2
    exit 1
  fi

  echo "Applying branch protection to $repo @ $branch..."

  # Build JSON payload
  contexts_json=$(printf '%s\n' "${ready_contexts[@]}" | jq -R . | jq -s .)
  payload=$(jq -n --argjson ctx "$contexts_json" '{
    required_status_checks: {
      strict: true,
      contexts: $ctx
    },
    enforce_admins: false,
    required_pull_request_reviews: null,
    restrictions: null
  }')

  gh api -X PUT "repos/$repo/branches/$branch/protection" --input - <<< "$payload"
  echo "✅ Branch protection applied successfully."
else
  echo ""
  echo "Dry-run plan complete. To apply these settings to GitHub, run:"
  echo "  $0 $repo $branch --apply"
fi
