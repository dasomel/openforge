English | [한국어](README-ko.md)

# OpenForge

> **Open Source Project Blueprint & Engineering Standards**

OpenForge is a reusable engineering foundation for creating, evolving, and maintaining high-quality open-source projects.

It standardizes the parts of OSS development that should be consistent across projects: repository structure, documentation, GitHub workflows, CI/CD, security, supply-chain governance, change impact analysis, upgrade/compatibility, developer environment security, AI-assisted engineering, container/IaC security, releases, maintainer governance, resilience, localization, development tooling, reusable implementation templates, and project lifecycle practices.

[About](docs/about.md)

## Why OpenForge?

Starting an OSS project should not mean rebuilding the same engineering foundation every time. OpenForge provides a practical baseline based on patterns already proven across active projects.

OpenForge is designed to be applied as a **repository blueprint, engineering standard, and reusable project template**.

## Core Principles

- English is the canonical project language; Korean is a first-class translation.
- User-facing Markdown follows `<name>.md` and `<name>-ko.md`.
- Projects should be reproducible, documented, testable, observable, and secure by default.
- GitHub Issues and Pull Requests are the primary change-management mechanism.
- Architecture decisions are recorded as ADRs.
- CI validates quality before changes are merged.
- Security and supply-chain controls are built into the lifecycle.
- Dependency compatibility alone does not justify immediate adoption of the newest release.
- Dependency/runtime/toolchain changes require workflow-wide impact analysis.
- AI agents and repository-local instructions are treated as potentially untrusted execution inputs.
- Security controls are risk-based so single-maintainer OSS projects remain practical.
- CI outages must not force maintainers to bypass security gates blindly.
- Reusable templates provide implementation starting points but are not universal drop-in configuration.
- Intentional deviations from the baseline are time-bounded and documented.

## Standards

- [Documentation Standard](docs/documentation.md)
- [Repository Standard](docs/repository.md)
- [GitHub Standard](docs/github.md)
- [Development Standard](docs/development.md)
- [Engineering Tooling Standard](docs/tooling.md)
- [Engineering Tooling Matrix](docs/tooling-matrix.md)
- [Security Standard](docs/security.md)
- [Supply Chain Security Standard](docs/supply-chain.md)
- [Package and Artifact Identity](docs/package-identity.md)
- [CI/CD Security Standard](docs/ci-security.md)
- [CI/CD Resilience Standard](docs/ci-resilience.md)
- [Change Management and Impact Analysis](docs/change-management.md)
- [Upgrade and Compatibility Engineering](docs/upgrade-compatibility.md)
- [Reproducible Build](docs/reproducible-build.md)
- [Developer Environment Security](docs/developer-environment-security.md)
- [AI-Assisted Engineering Security](docs/ai-engineering-security.md)
- [Container, Kubernetes and IaC Security](docs/container-iac-security.md)
- [Secrets and Machine Identity](docs/secrets-identity.md)
- [Vulnerability Management](docs/vulnerability-management.md)
- [Security and Supply-Chain Incident Response](docs/incident-response.md)
- [Release Security](docs/release-security.md)
- [Security Exceptions and Waivers](docs/security-exceptions.md)
- [Maintainer Governance](docs/maintainer-governance.md)
- [CI/CD Standard](docs/ci-cd.md)
- [Release Standard](docs/release.md)
- [Internationalization Standard](docs/i18n.md)
- [OSS Compliance Standard](docs/oss-compliance.md)
- [Reference Practices Audit](docs/reference-practices.md)
- [Reference Implementation Metrics](docs/reference-metrics.md)

## Templates

Reusable implementation starting points are provided under [`templates/`](templates/):

- GitHub PR and security-sensitive path samples
- CI and release-security workflow baselines
- Toolchain verification script
- Dependency governance policy example

Templates are intentionally conservative. Adapt permissions, versions, paths, commands and ecosystem-specific controls to the target repository and threat model.

## Reference Metrics

OpenForge includes a practical maturity scorecard covering documentation, architecture, GitHub, CI/CD, security, supply-chain governance, change management, upgrade/compatibility, developer environment, AI-assisted engineering, release management, resilience, configuration, and localization.

Each applicable metric is scored:

- `2` — implemented and automated where practical
- `1` — partially or manually implemented
- `0` — missing
- `N/A` — not applicable

See [Reference Implementation Metrics](docs/reference-metrics.md).

## Project Lifecycle

```text
Idea
  ↓
Project Definition
  ↓
Repository Bootstrap
  ↓
Documentation + Architecture
  ↓
Template Adoption
  ↓
Implementation
  ↓
Change Impact / Supply Chain Review
  ↓
CI / Security / Testing
  ↓
Release / Publish Verification
  ↓
Maintenance / Incident Learning
  ↓
Lessons / Metrics
  ↓
OpenForge Improvement
```

## Reference Projects

OpenForge is informed by active OSS development practices, including:

- Narwhal
- Narwhal Portal
- nfs-quota-agent
- kube-ready-box
- KubeMetal
- ldapium
- Beluga Manager

These projects are references, not rigid dependencies. The goal is to capture repeatable engineering practices while keeping projects free to choose their own implementation details.

## Contributing

Contributions should follow the repository's [Contributing Guide](CONTRIBUTING.md). New standards should be supported by a concrete use case, reference implementation, or repeatable engineering benefit.

## License

Apache License 2.0. See [LICENSE](LICENSE).
