# ADR-0003: Use risk-based security and governance for OSS

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing OpenForge security/governance direction

## Context

Many OpenForge reference projects are maintained by small teams or a single maintainer. Enterprise controls copied literally from large organizations can make OSS maintenance impractical, while removing controls because the maintainer count is small creates avoidable risk.

## Decision

Scale security and governance controls by risk, trust boundary, release impact, privilege, and automation opportunity rather than by maintainer count alone.

Prefer automated controls where practical and use documented exceptions where a full control is disproportionate.

## Alternatives considered

- Apply enterprise governance unchanged to every repository.
- Relax security controls for single-maintainer projects.
- Leave security/governance entirely project-specific.

## Rationale

Risk-based controls preserve practical maintainability without making project size a proxy for security requirements.

## Consequences

- High-impact release, identity, secret, supply-chain, and permission changes can require stronger controls even in a small OSS.
- Low-risk process overhead should be minimized.
- Exceptions need rationale and review/expiry rather than becoming silent permanent defaults.

## Affected standards

- `docs/security.md`
- `docs/maintainer-governance.md`
- `docs/security-exceptions.md`
- `docs/supply-chain.md`
