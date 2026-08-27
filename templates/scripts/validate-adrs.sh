#!/usr/bin/env bash
set -euo pipefail

adr_dir="docs/adr"

required=(
  "$adr_dir/README.md"
  "$adr_dir/README-ko.md"
  "docs/decision-management.md"
  "docs/decision-management-ko.md"
  "templates/ADR.md"
  "templates/ADR-ko.md"
)

for file in "${required[@]}"; do
  test -f "$file" || { echo "Missing ADR contract file: $file"; exit 1; }
done

shopt -s nullglob
english_adrs=("$adr_dir"/[0-9][0-9][0-9][0-9]-*.md)
count=0

for file in "${english_adrs[@]}"; do
  [[ "$file" == *-ko.md ]] && continue
  base="${file%.md}"
  ko="${base}-ko.md"
  test -f "$ko" || { echo "Missing Korean ADR pair: $ko"; exit 1; }

  grep -q -- '- Status:' "$file" || { echo "ADR missing Status: $file"; exit 1; }
  grep -q -- '- Date:' "$file" || { echo "ADR missing Date: $file"; exit 1; }

  name="$(basename "$file")"
  ko_name="$(basename "$ko")"
  grep -Fq "$name" "$adr_dir/README.md" || { echo "English ADR missing from index: $name"; exit 1; }
  grep -Fq "$ko_name" "$adr_dir/README-ko.md" || { echo "Korean ADR missing from index: $ko_name"; exit 1; }

  count=$((count + 1))
done

for ko in "$adr_dir"/[0-9][0-9][0-9][0-9]-*-ko.md; do
  en="${ko%-ko.md}.md"
  test -f "$en" || { echo "Korean ADR has no English canonical pair: $ko"; exit 1; }
done

if (( count == 0 )); then
  echo "No ADR files found in $adr_dir"
  exit 1
fi

echo "ADR validation passed: $count English/Korean pairs indexed."
