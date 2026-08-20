# Security Standard

Security is a default project requirement, not a release-only activity.

## Rules

- Never commit passwords, tokens, API keys, private keys or production secrets.
- Use secret managers or GitHub Actions secrets for sensitive values.
- Apply least privilege to applications, Kubernetes resources and CI credentials.
- Validate external input and fail safely.
- Keep dependencies and base images updated.
- Run security and dependency scans in CI when practical.
- Publish a security policy and vulnerability-reporting process.
- Record security-impacting architecture decisions.

## Supply chain

Recommended controls:

- dependency pinning or lockfiles
- SBOM generation
- provenance/attestation where supported
- image vulnerability scanning
- signed releases when practical

## Incident handling

Security issues should be reported privately until remediation or mitigation is available.
Do not put sensitive operational details in public issues.
