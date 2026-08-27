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

instruction_files=$(join_existing AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md .agent .codex .claude)
source_docs=$(join_existing DESIGN.md ARCHITECTURE.md CONTRIBUTING.md README.md docs/architecture docs/design docs/decisions docs)
build_entry=$(join_existing Makefile Taskfile.yml Taskfile.yaml package.json pyproject.toml Cargo.toml go.mod Vagrantfile)
ci_entry=$(first_existing .github/workflows .gitlab-ci.yml Jenkinsfile)
deterministic_tooling=$(join_existing .editorconfig .pre-commit-config.yaml .markdownlint.json .golangci.yml .shellcheckrc eslint.config.js eslint.config.mjs biome.json rustfmt.toml)

bug_repro="manual"
if exists tests || exists test || exists spec || exists e2e || exists __tests__; then
  bug_repro="automatable"
fi

boundary_guidance="missing"
if exists DESIGN.md || exists ARCHITECTURE.md || exists docs/architecture || exists docs/design; then
  boundary_guidance="present"
fi

context_bloat="ok"
for instruction in AGENTS.md CLAUDE.md GEMINI.md .github/copilot-instructions.md; do
  [[ -f "$ROOT/$instruction" ]] || continue
  bytes=$(wc -c < "$ROOT/$instruction" | tr -d ' ')
  if (( bytes > 12000 )); then
    context_bloat="review"
    break
  fi
done

printf 'repository\tinstructions\tsource_docs\tbuild_entry\tci\tdeterministic_tooling\tbug_repro\tboundary_guidance\tcontext_bloat\n'
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  "$NAME" "$instruction_files" "$source_docs" "$build_entry" "$ci_entry" "$deterministic_tooling" "$bug_repro" "$boundary_guidance" "$context_bloat"
