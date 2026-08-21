# Security Standard

Security is a default project requirement, not a release-only activity.

## Rules

- Never commit passwords, tokens, API keys, private keys or production secrets.
- Use secret managers or GitHub Actions secrets for sensitive values.
- Apply least privilege to applications, Kubernetes resources and CI credentials.
- Validate external input and fail safely.
- Keep dependencies and base images current through the supply-chain policy, not through blind latest-version adoption.
- Run security and dependency scans in CI when practical.
- Publish a security policy and vulnerability-reporting process.
- Record security-impacting architecture decisions.

## Supply chain

OpenForge uses `docs/supply-chain.md` as the portfolio reference standard.

Required controls include:

- immutable dependency/artifact identity where supported
- lockfiles and checksum/integrity verification
- dependency release-age/cooling policy
- direct/transitive dependency diff review
- build-time dependency and script trust-boundary review
- restricted build/test egress for high-risk jobs
- SBOM covering relevant runtime and build-time inputs
- provenance/attestation where supported
- image vulnerability scanning
- signed releases where practical
- quarantine and last-known-good rollback capability
- offline/air-gapped verification where applicable

"Latest compatible" is not a sufficient security decision.

## Change impact

Dependency, runtime, package-manager, build-tool, CI action and release-tool changes are Class C or D changes under `docs/change-management.md` and require workflow-wide impact analysis.

A change is incomplete if source code is updated but an independent CI/CD/release workflow still depends on the previous runtime or build contract.

## Incident handling

Security issues should be reported privately until remediation or mitigation is available.
Do not put sensitive operational details in public issues.

When a security incident or integration failure reveals a repeatable weakness, add a deterministic CI/regression check and update the relevant standard documentation.