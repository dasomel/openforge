# ADR-0006: Integrate security and supply-chain controls into the lifecycle

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing CI/release/supply-chain direction

## Context

Security checks performed only at the end of development miss compromised dependencies, CI permissions, build provenance, artifact identity, secret exposure, and release-process weaknesses earlier in the lifecycle.

## Decision

Build security and supply-chain controls into development, CI, build, packaging, release, and incident/maintenance workflows rather than treating security as a final release checklist.

## Alternatives considered

- Run vulnerability scanning only before release.
- Rely on hosting-platform defaults.
- Treat supply-chain security as optional for small OSS projects.

## Rationale

Controls are more useful when they protect the point where risk is introduced. Lifecycle integration also produces evidence that can be reused during release and incident response.

## Consequences

- CI permissions, dependencies, SBOM/provenance, artifact identity, release verification, and secrets become first-class engineering concerns.
- Automation is preferred where it reduces repetitive maintainer burden.
- Security exceptions must be explicit rather than silently disabling gates.

## Affected standards

- `docs/supply-chain.md`
- `docs/ci-security.md`
- `docs/release-security.md`
- `docs/package-identity.md`
- `docs/secrets-identity.md`
- `docs/vulnerability-management.md`
