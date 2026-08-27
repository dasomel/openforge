#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
NAME="${2:-$(basename "$(cd "$ROOT" && pwd)")}" 

exists() {
  [[ -e "$ROOT/$1" ]]
}

first_existing() {
  local item
  for item in "$@"; do
    if exists "$item"; then
      printf '%s' "$item"
      return 0
    fi
  done
  printf '%s' '-'
}

join_existing() {
  local out=()
  local item
  for item in "$@"; do
    exists "$item" && out+=("$item")
  done
  if ((${#out[@]} == 0)); then
    printf '%s' '-'
  else
    local IFS=','
    printf '%s' "${out[*]}"
  fi
}

instruction_files=$(join_existing AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md)
source_docs=$(join_existing DESIGN.md ARCHITECTURE.md CONTRIBUTING.md docs/architecture docs/design docs/decisions)
build_entry=$(first_existing Makefile Taskfile.yml Taskfile.yaml package.json pyproject.toml Cargo.toml go.mod)
ci_entry=$(first_existing .github/workflows .gitlab-ci.yml Jenkinsfile)

bug_repro="manual"
if exists tests || exists test || exists spec || exists e2e; then
  bug_repro="automatable"
fi

boundary_guidance="missing"
if exists DESIGN.md || exists ARCHITECTURE.md || exists docs/architecture || exists docs/design; then
  boundary_guidance="present"
fi

printf 'repository\tinstructions\tsource_docs\tbuild_entry\tci\tbug_repro\tboundary_guidance\n'
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$NAME" "$instruction_files" "$source_docs" "$build_entry" "$ci_entry" "$bug_repro" "$boundary_guidance"
