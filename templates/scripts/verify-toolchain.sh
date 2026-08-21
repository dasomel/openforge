#!/usr/bin/env bash
set -euo pipefail

required_tools=("git")

for tool in "${required_tools[@]}"; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Required tool not found: $tool" >&2
    exit 1
  fi
done

printf 'git: '; git --version

# Add ecosystem-specific checks, for example:
# node --version
# pnpm --version
# bun --version
# go version
# rustc --version
# java -version
# terraform version
