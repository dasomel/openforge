# ADR-0005: Require workflow-wide impact analysis for upgrades

- Status: Accepted
- Date: 2026-08-27
- Retrospective: captures existing change-management and compatibility standards

## Context

A dependency, runtime, or toolchain version can be individually compatible while still breaking packaging, CI, deployment, plugins, generated artifacts, platform support, or operational workflows.

## Decision

Do not adopt a new version solely because direct dependency compatibility appears valid. Analyze the end-to-end workflow affected by dependency, runtime, toolchain, platform, or build changes.

## Alternatives considered

- Always track latest releases.
- Upgrade when the direct dependency resolver succeeds.
- Freeze versions unless a security issue requires change.

## Rationale

Compatibility is a system property. OpenForge favors evidence-based upgrades over freshness for its own sake, while avoiding permanent stagnation.

## Consequences

- Upgrade reviews may require CI, packaging, runtime, plugin, deployment, and rollback evidence.
- Latest is not automatically best; old is not automatically safer.
- Upgrade decisions can be delayed when evidence is incomplete.

## Affected standards

- `docs/change-management.md`
- `docs/upgrade-compatibility.md`
- `docs/reproducible-build.md`
- `docs/ci-cd.md`
