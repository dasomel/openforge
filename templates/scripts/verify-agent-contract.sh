#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

fail() {
  echo "agent-contract: $*" >&2
  exit 1
}

require_file() {
  local path="$1"
  [[ -f "$ROOT/$path" ]] || fail "missing required file: $path"
}

require_text() {
  local path="$1"
  local text="$2"
  grep -Fq -- "$text" "$ROOT/$path" || fail "$path must contain: $text"
}

max_lines() {
  local path="$1"
  local limit="$2"
  local count
  count=$(wc -l < "$ROOT/$path" | tr -d ' ')
  (( count <= limit )) || fail "$path is $count lines; keep it <= $limit lines and move detail into linked docs/tooling"
}

require_file "AGENTS.md"
require_file "docs/agent-engineering.md"
require_file "templates/AGENTS.md"
require_file "templates/CODING_STANDARDS.md"

# Root contract: concise, repository-specific, and linked to the canonical standard.
max_lines "AGENTS.md" 80
require_text "AGENTS.md" "docs/agent-engineering.md"
require_text "AGENTS.md" "smallest coherent change"
require_text "AGENTS.md" "Do not claim completion"
require_text "AGENTS.md" "A) complete/verified"
require_text "AGENTS.md" "B) meaningful verified progress"
require_text "AGENTS.md" "C) stop with evidence"

# Reusable template: keep judgment/boundary/verification guidance in prompt context.
max_lines "templates/AGENTS.md" 100
for heading in "## Work contract" "## Bugs" "## Verification" "## Convergence"; do
  require_text "templates/AGENTS.md" "$heading"
done
require_text "templates/AGENTS.md" "formatter/linter rules own deterministic style"
require_text "templates/AGENTS.md" "reproduce -> failing regression test/evidence -> fix"

# Detailed coding guidance must remain outside the compact AGENTS contract.
require_text "templates/CODING_STANDARDS.md" "# CODING_STANDARDS.md"
require_text "templates/CODING_STANDARDS.md" "## Deterministic rules"

# Catch common context-bloat regressions: deterministic formatting rules belong in tooling.
if grep -Eiq '(^|[^[:alnum:]])(2|4)[ -]?spaces per indent|tabs? (must|should) be used for indentation|maximum line length (is|of) [0-9]+' "$ROOT/AGENTS.md" "$ROOT/templates/AGENTS.md"; then
  fail "deterministic formatting rule found in AGENTS contract; enforce it with formatter/linter configuration instead"
fi

echo "agent-contract: OK"
