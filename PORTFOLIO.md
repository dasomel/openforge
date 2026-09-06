# OpenForge OSS Portfolio

![OpenForge OSS Portfolio](docs/assets/openforge-portfolio.svg)

OpenForge manages the shared engineering state, standards adoption, dependencies, development impact and evidence-backed progress of the OSS portfolio.

## Views

- [Development Dashboard](docs/portfolio-dashboard.md)
- [Ecosystem Architecture](docs/portfolio-architecture.md)
- [Dependency & Impact Intelligence](docs/portfolio-impact.md)
- [Portfolio Governance / Status PR Workflow](docs/portfolio-governance.md)

## Canonical data

- [`portfolio/projects.json`](portfolio/projects.json)
- [`portfolio/relationships.json`](portfolio/relationships.json)
- [`portfolio/milestones.json`](portfolio/milestones.json)
- [`portfolio/status.schema.json`](portfolio/status.schema.json)

## Operating rule

```text
Downstream OSS implementation
        ↓
repository-specific verification
        ↓
status publication payload
        ↓
OpenForge pull request
        ↓
OpenForge CI / impact review
        ↓
merge = official portfolio state
        ↓
dashboard / graph / infographic
```

OpenForge never treats an upstream or downstream code merge alone as proof that a cross-project capability is complete. The owning repository must publish the evidence-backed status transition.
