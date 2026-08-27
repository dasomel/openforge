# Assessment Comparison

OpenForge can compare two previously generated assessment JSON files and show score changes, category deltas and per-rule improvements or regressions.

## Usage

```bash
openforge compare before.json after.json
```

JSON output:

```bash
openforge compare before.json after.json --format json
```

Write the comparison report to a file:

```bash
openforge compare before.json after.json \
  --format json \
  --output comparison.json
```

Fail CI when at least one existing rule regresses:

```bash
openforge compare baseline.json current.json --fail-on-regression
```

`--fail-on-regression` returns exit code `2` when a rule is classified as `REGRESSED`.

## Change classification

| Change | Meaning |
|---|---|
| `IMPROVED` | Score increased or `FAIL -> PASS` |
| `REGRESSED` | Score decreased or `PASS -> FAIL` |
| `ADDED` | Rule exists only in the newer report |
| `REMOVED` | Rule exists only in the older report |
| `UNCHANGED` | Status and score are unchanged |

Rules are matched by stable `rule_id` rather than display title.

## Schema and ruleset compatibility

Comparison remains possible when the two assessment files use different OpenForge assessment schemas or rulesets, but the report records compatibility warnings.

```text
WARN: assessment schema changed: openforge-assessment/v0.10 -> openforge-assessment/v0.11
WARN: ruleset changed: maturity-v0.1 -> maturity-v0.2
```

A schema/ruleset change can add, remove or redefine evidence semantics. Therefore `compatible=false` means score deltas should not be interpreted as pure platform change without reviewing the rule changes.

## Comparison JSON

The comparison report has its own versioned schema:

```text
openforge-comparison/v0.1
```

It includes:

- before/after assessment schema and ruleset
- compatibility flag and warnings
- overall score, grade and maturity-level delta
- category score deltas
- per-rule status/score deltas
- counts of improved, regressed, added, removed and unchanged rules

This output is deterministic and can be archived in CI or used as input to the optional AI result-analysis layer. AI does not classify or modify the underlying assessment results.
