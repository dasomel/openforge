#!/usr/bin/env bash
set -euo pipefail

fail=0

check_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    echo "Missing supply-chain contract: $file" >&2
    fail=1
  fi
}

check_file "docs/supply-chain.md"
check_file "docs/change-management.md"
check_file "docs/plugin-supply-chain.md"
check_file "templates/policy/dependency-policy.yml"
check_file "templates/policy/plugin-intake-policy.yml"
check_file "templates/offline/trusted-plugin-catalog.yml"
check_file "templates/workflows/supply-chain.yml"

if [[ -f templates/workflows/supply-chain.yml ]]; then
  grep -q 'actions/checkout@<APPROVED_IMMUTABLE_REVISION>' templates/workflows/supply-chain.yml || {
    echo "Supply-chain workflow must use an immutable checkout placeholder." >&2
    fail=1
  }
fi

if [[ -f templates/policy/plugin-intake-policy.yml ]]; then
  grep -q 'ownership_is_not_trust: true' templates/policy/plugin-intake-policy.yml || fail=1
  grep -q 'require_immutable_revision: true' templates/policy/plugin-intake-policy.yml || fail=1
  grep -q 'fail_closed_on_missing_entry: true' templates/policy/plugin-intake-policy.yml || fail=1
fi

if (( fail != 0 )); then
  exit 1
fi

echo "OpenForge supply-chain contracts are present and structurally valid."
