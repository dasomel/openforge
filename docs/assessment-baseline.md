# Assessment baselines

OpenForge can persist an assessment as a reviewable baseline and compare future assessments against it.

## Create a baseline

```bash
openforge . --runtime --policy openforge-policy.json --format json --output current.json
openforge-baseline create current.json
```

The default output is `.openforge/baseline.json`. A custom path may be supplied as the third argument.

The baseline preserves the original assessment JSON and adds `_baseline` metadata containing:

- baseline schema
- creation timestamp
- assessment schema
- ruleset
- overall score
- policy profile and fingerprint, when present

Because the original assessment fields remain unchanged, the file can still be consumed by normal OpenForge comparison tooling.

## Check against a baseline

```bash
openforge . --runtime --policy openforge-policy.json --format json --output current.json
openforge-baseline check .openforge/baseline.json current.json
```

Exit codes:

- `0`: no rule regression detected
- `2`: one or more rule regressions detected
- `3`: `--require-compatible` was requested and schema, ruleset, or policy identity changed
- `1`: command/input error

For strict CI usage:

```bash
openforge-baseline check \
  .openforge/baseline.json \
  current.json \
  --require-compatible
```

## Compatibility

A baseline is considered directly comparable when the following identities remain the same:

1. assessment schema
2. ruleset
3. policy profile/fingerprint

A changed policy can legitimately alter the denominator and therefore the score. Strict CI should use `--require-compatible` so policy/ruleset changes are reviewed separately from engineering regressions.

## Repository practice

Commit `.openforge/baseline.json` when it represents an intentionally reviewed reference state. Update it through an explicit review after a ruleset or policy migration rather than silently replacing it on every CI run.

The initial implementation is exposed as the `openforge-baseline` companion binary. It is built from the same Rust package and is intended to be folded under a future clap subcommand hierarchy as `openforge baseline` without changing the baseline file format.
