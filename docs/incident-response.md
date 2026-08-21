# Security and Supply-Chain Incident Response Standard

A suspected compromised dependency, artifact, credential, workflow or maintainer account must be handled as a supply-chain incident until disproven.

## Response lifecycle

```text
Detect
→ Contain
→ Quarantine
→ Revoke/Rotate
→ Determine Blast Radius
→ Rebuild
→ Verify
→ Recover
→ Notify
→ Add Regression Control
```

## Minimum response actions

1. Freeze promotion of affected versions/artifacts.
2. Quarantine the dependency, artifact, workflow or credential.
3. Revoke or rotate exposed credentials, especially publishing and cloud identities.
4. Identify affected commits, builds, releases and downstream consumers.
5. Restore the last-known-good dependency/artifact set.
6. Rebuild from a clean, approved environment.
7. Verify artifact identity, provenance, SBOM and security results.
8. Record incident evidence and update detection/regression controls.

## Blast radius

Track:

- affected package/version
- source commits
- CI workflow runs
- generated artifacts
- published versions
- repositories consuming the artifact
- credentials potentially exposed
- environments potentially reached

## Emergency release

Emergency fixes may bypass routine cooling only when the exception includes reason, scope, risk, owner/reviewer where available, verification evidence and rollback plan.
