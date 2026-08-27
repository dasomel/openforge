# ADR-0011: CI resilience must not encourage blind security bypass

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing CI resilience direction

## Context

External scanners, registries, runners, package services, and CI integrations can fail independently of the code under review. A hard dependency on one service can block maintenance, but simply bypassing security gates during outages converts availability pressure into security risk.

## Decision

Design CI resilience and fallback paths so an external outage does not require maintainers to blindly disable security or quality controls. Distinguish code failure, policy failure, and infrastructure/service failure, and use explicit fallback/evidence where appropriate.

## Alternatives considered

- Fail closed with no recovery path for every external service failure.
- Allow maintainers to bypass gates manually whenever CI is unavailable.
- Make security checks informational only.

## Rationale

Availability and security are both engineering requirements. Resilience should preserve as much assurance as possible while making degraded states explicit.

## Consequences

- CI should expose why a gate failed.
- Fallbacks may use alternate checks, cached evidence, reruns, or documented exception paths depending on risk.
- High-risk releases may still need to wait when equivalent assurance cannot be obtained.

## Affected standards

- `docs/ci-resilience.md`
- `docs/ci-security.md`
- `docs/security-exceptions.md`
- release standards
