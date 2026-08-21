# CI/CD Resilience Standard

CI/CD is an operational dependency for OSS. A temporary platform, registry or network failure must not corrupt state or create unsafe release behavior.

## Requirements

- Make build/test/release jobs retry-safe and idempotent where practical.
- Preserve important artifacts/evidence when a workflow fails.
- Separate transient retry from semantic failure; do not retry destructive publish/deploy actions blindly.
- Provide a documented manual or offline fallback for release-critical projects where practical.
- Keep dependency/artifact mirrors or caches available for declared offline/air-gap modes.
- Ensure rerunning a workflow cannot publish duplicate or unintended artifacts.
- Maintain clear last-known-good release references.
- Record outage-induced exceptions and convert recurring failures into regression checks.

## Release continuity

A CI outage must not force maintainers to bypass security gates blindly. Prefer:

```text
CI unavailable
→ preserve source/release candidate
→ use approved fallback validation
→ explicit exception when required
→ publish only after required evidence is restored
```
