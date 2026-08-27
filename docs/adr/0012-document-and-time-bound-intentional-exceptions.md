# ADR-0012: Document and time-bound intentional exceptions

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing OpenForge exception policy

## Context

A reusable standard cannot anticipate every repository, platform, offline environment, maintainer constraint, or transitional migration. Permanent silent exceptions, however, make a shared standard meaningless and accumulate invisible risk.

## Decision

Allow intentional deviations when justified, but record their scope, rationale, risk/impact, owner where applicable, and review or expiry condition. Exceptions should be revisited rather than becoming undocumented permanent defaults.

This applies beyond security where useful, including design-system deviations, compatibility constraints, CI fallbacks, and project-specific engineering rules.

## Alternatives considered

- No exceptions to standards.
- Allow repository-local deviations without documentation.
- Require a central approval process for every deviation.

## Rationale

Explicit exceptions preserve practical flexibility and create a path back to the standard. A blanket prohibition encourages hidden workarounds; unrestricted deviation destroys consistency.

## Consequences

- Standards remain defaults rather than absolute universal configurations.
- Maintainers gain visibility into accumulated divergence.
- Expired exceptions should trigger review, renewal with evidence, or removal.

## Affected standards

- `docs/security-exceptions.md`
- `docs/maintainer-governance.md`
- `docs/design-system.md`
- `docs/change-management.md`
- reusable templates
