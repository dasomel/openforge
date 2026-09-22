# Assessment profiles

OpenForge supports built-in applicability profiles so common project types can be assessed without maintaining a policy file for every repository.

## Built-in profiles

- `production` — all applicable repository, execution, platform, and runtime rules remain in scope.
- `kubernetes-platform` — includes repository engineering, execution, Kubernetes packaging, and runtime rules.
- `repository` — includes repository engineering, execution, and Kubernetes packaging rules, but excludes runtime rules.
- `oss-library` — includes documentation, governance, security, CI/CD, release, and execution rules; Kubernetes platform/runtime rules are not applicable by default.

Example:

```bash
openforge assess . --profile kubernetes-platform --runtime
openforge assess . --profile oss-library --run-execution
```

The legacy invocation remains supported:

```bash
openforge . --profile repository
```

## Combining a profile with an explicit policy

A built-in profile can be combined with `--policy`:

```bash
openforge assess . \
  --profile kubernetes-platform \
  --policy .openforge/policy.json \
  --runtime
```

The built-in profile is used as the base. Explicit policy fields override the preset when they are non-empty:

- a non-default `profile.name` replaces the preset name;
- non-empty `include_rules` replaces the preset inclusion scope;
- non-empty `exclude_rules` replaces the preset exclusion scope;
- waivers are added to the resolved policy.

The resolved policy still flows through the same deterministic applicability, waiver expiry, scoring, and policy fingerprint logic as a normal policy file.

## Why profiles affect applicability rather than score weights

Profiles do not silently change rule weights. They only decide whether a rule is applicable to the assessment target. Applicable PASS/FAIL rules keep their original weights; `NOT_APPLICABLE`, `WAIVED`, and `SKIP` findings remain outside the score denominator according to the normal scoring rules.

This keeps scores explainable and makes comparisons meaningful when the same profile and policy fingerprint are used across assessments.
