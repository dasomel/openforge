# Upgrade and Compatibility Engineering Standard

Upgrades are engineering changes, not version substitutions. Compatibility is necessary but is not sufficient evidence for adoption.

## Requirements

- Maintain a supported version/compatibility matrix where relevant.
- Classify upgrades as patch, minor, major, runtime/toolchain, security or migration changes.
- Apply dependency cooling/review policy to routine upgrades.
- Record previous and target version, dependency graph changes and known breaking changes.
- Identify affected build, test, package, deployment and release workflows before merge.
- Run clean-build, regression and compatibility validation appropriate to the change.
- Preserve a last-known-good version and deterministic rollback path for release-critical upgrades.
- For major/runtime/toolchain changes, use canary or staged adoption where practical.
- Document deprecations and migration actions.
- Do not allow compatibility tests to override integrity, provenance or security failures.

## Runtime/toolchain migration

A migration such as npm → pnpm or Node → Bun MUST inspect all workflows, scripts, developer documentation, containers and release paths that depend on the previous toolchain.

## Evidence

Upgrade evidence SHOULD include:

```text
previous version
→ target version
→ dependency diff
→ compatibility matrix
→ build/test result
→ security result
→ artifact digest
→ rollback reference
```
