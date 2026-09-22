#!/usr/bin/env bash
set -euo pipefail

root="${1:-.agents/behaviors}"

if [[ ! -d "$root" ]]; then
  echo "Behavior directory not found: $root" >&2
  exit 1
fi

status=0
count=0

while IFS= read -r -d '' file; do
  count=$((count + 1))
  dir="$(basename "$(dirname "$file")")"

  if [[ "$(sed -n '1p' "$file")" != "---" ]]; then
    echo "$file: missing opening YAML frontmatter delimiter" >&2
    status=1
    continue
  fi

  closing="$(awk 'NR > 1 && $0 == "---" { print NR; exit }' "$file")"
  if [[ -z "$closing" ]]; then
    echo "$file: missing closing YAML frontmatter delimiter" >&2
    status=1
    continue
  fi

  frontmatter="$(sed -n "2,$((closing - 1))p" "$file")"
  name="$(printf '%s\n' "$frontmatter" | sed -n 's/^name:[[:space:]]*//p' | head -n1)"
  description="$(printf '%s\n' "$frontmatter" | sed -n 's/^description:[[:space:]]*//p' | head -n1)"

  if [[ -z "$name" ]]; then
    echo "$file: missing frontmatter field 'name'" >&2
    status=1
  elif [[ "$name" != "$dir" ]]; then
    echo "$file: name '$name' must match directory '$dir'" >&2
    status=1
  fi

  if [[ -z "$description" ]]; then
    echo "$file: missing frontmatter field 'description'" >&2
    status=1
  fi

done < <(find "$root" -mindepth 2 -maxdepth 2 -type f -name BEHAVIOR.md -print0 | sort -z)

if [[ "$count" -eq 0 ]]; then
  echo "No BEHAVIOR.md files found under $root" >&2
  exit 1
fi

if [[ "$status" -ne 0 ]]; then
  exit "$status"
fi

echo "Validated $count behavior specification(s) under $root"
