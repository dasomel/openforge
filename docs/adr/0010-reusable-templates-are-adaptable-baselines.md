# ADR-0010: Treat reusable templates as adaptable baselines

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing OpenForge template policy

## Context

OpenForge provides reusable workflows, policies, Kubernetes resources, GitOps patterns, design templates, and engineering documents. Versions, permissions, domains, identity, threat models, platforms, and operational requirements differ across projects.

## Decision

Templates are conservative implementation starting points, not universal drop-in configuration. Projects must adapt versions, permissions, paths, commands, domains, images, identities, platform conventions, and ecosystem-specific controls to their context.

## Alternatives considered

- Guarantee templates as universal drop-in configuration.
- Provide documentation only and no reusable implementation.
- Fork a separate template set per reference project.

## Rationale

Reusable implementation accelerates project bootstrap, but pretending context-specific infrastructure is universally correct creates unsafe defaults and hidden coupling.

## Consequences

- Template consumers remain responsible for project-specific review.
- OpenForge should document assumptions and placeholders clearly.
- Reference projects inform templates but do not become rigid dependencies.

## Affected areas

- `templates/`
- repository standard
- security and deployment templates
- design-system adoption template
