# About OpenForge

> **Open Source Project Blueprint & Engineering Standards**

OpenForge is a reusable engineering foundation for creating, evolving, and maintaining high-quality open-source projects with a consistent engineering baseline.

English | [한국어](about-ko.md)

## What OpenForge Provides

- Repository and documentation standards
- English/Korean documentation conventions
- GitHub issue, pull request, and workflow standards
- CI/CD and security baselines
- Release and version-management practices
- Development tooling and language-specific standards
- Code intelligence and architecture-analysis guidance
- AI-assisted development guidance
- Internationalization and localization guidance
- OSS license and software supply-chain practices
- Reference implementation metrics for repository maturity
- Reusable project templates

## What OpenForge Is Not

OpenForge is not a framework and does not prescribe one programming language, cloud, runtime, or application architecture.

It provides a default engineering baseline. Projects may deviate when justified by their context; significant or intentional deviations should be documented through an ADR.

## Design Philosophy

OpenForge evolves from real OSS engineering experience. Standards are validated against active projects and improved when repeatable practices, incidents, reviews, or better engineering approaches are discovered.

```text
OpenForge
    ↓
OSS Project
    ↓
Implementation / Incident / Review
    ↓
Lessons / Metrics
    ↓
OpenForge Improvement
    ↺
```

## Reference Projects

The reference implementation set includes projects such as Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, and Beluga Manager.

These projects are references rather than dependencies. OpenForge captures repeatable engineering practices while preserving freedom in implementation choices.

See [Reference Implementation Metrics](reference-metrics.md) for the maturity scorecard.

## Language Policy

English is the canonical project language. Korean is maintained as a first-class translation using the `<name>-ko.md` convention.

See [Documentation Standard](documentation.md) for the full documentation policy.

## Lifecycle

OpenForge follows the same engineering discipline it recommends:

```text
Standard → Apply → Measure → Learn → Improve → Standardize
```
