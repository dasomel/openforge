# About OpenForge

> Open Source Project Blueprint & Engineering Standards

OpenForge is the reference engineering standard for creating, evolving, and maintaining open-source projects with a consistent foundation.

## What OpenForge Provides

- Repository and documentation standards
- English/Korean documentation conventions
- GitHub issue, pull request, and workflow standards
- CI/CD and security baselines
- Release and version-management practices
- Development tooling and language-specific standards
- Code intelligence and architecture-analysis guidance
- AI-assisted development instructions
- Internationalization and localization guidance
- OSS license and supply-chain practices
- Reference implementation metrics for repository maturity
- Reusable project templates

## What OpenForge Is Not

OpenForge is not a framework and does not prescribe one programming language, cloud, runtime, or application architecture.

It provides a default engineering baseline. Projects can deviate when justified by their context; intentional deviations should be documented through an ADR.

## Design Philosophy

OpenForge evolves from real project experience. Standards are validated against active OSS repositories and improved when repeatable practices, incidents, or better engineering approaches are discovered.

```text
OpenForge
    ↓
OSS Project
    ↓
Implementation / Incident / Review
    ↓
Lessons & Metrics
    ↓
OpenForge Improvement
    ↺
```

## Reference Projects

The reference metrics are informed by projects including Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, and Beluga Manager.

See [Reference Implementation Metrics](reference-metrics.md) for the maturity scorecard.
