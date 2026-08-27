# ADR-0007: Standardize UI semantics without erasing product identity

- Status: Accepted
- Date: 2026-08-27
- Related implementation: `docs/design-system.md`

## Context

The OSS portfolio includes platform portals, desktop operators, data control planes, administration consoles, operations dashboards, and developer tools. A single visual theme would ignore different operating contexts, but fully independent design systems would duplicate accessibility, state, token, and interaction decisions.

## Decision

Standardize semantic colors, state meanings, accessibility, focus, core interaction intent, foundational tokens, and reusable patterns. Allow controlled project-specific differences in accent, density, navigation composition, data visualization, and platform-native conventions.

Projects declare an archetype and intentional deviations in `DESIGN.md`.

## Alternatives considered

- Force one visual design across every OSS.
- Keep every repository completely independent.
- Share only a color palette.

## Rationale

Consistency is most valuable where meaning and usability cross project boundaries. Product identity and operating density are context-dependent and should not be homogenized.

## Consequences

- Shared semantics can map to different framework implementations.
- Design reviews focus on intent/accessibility before pixel identity.
- Project deviations remain possible but become explicit and traceable.

## Affected standards and assets

- `docs/design-system.md`
- `docs/design-system-ko.md`
- `templates/DESIGN.md`
- OpenForge OSS Design System Figma source
