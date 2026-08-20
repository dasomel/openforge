# OpenForge

> **Open Source Project Blueprint & Engineering Standards**

OpenForge is a reusable engineering foundation for creating, evolving, and maintaining high-quality open-source projects.

It standardizes the parts of OSS development that should be consistent across projects: repository structure, documentation, GitHub workflows, CI/CD, security, releases, localization, development tooling, AI-assisted development, and project lifecycle practices.

[한국어 README](README-ko.md) · [About OpenForge](docs/about.md) · [한국어 소개](docs/about-ko.md)

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
- Localization is designed from the beginning rather than retrofitted later.
- Development tooling is standardized where it improves consistency and reproducibility.
- Actual project resources, identifiers, and API values are not translated.
- Intentional deviations from the baseline are documented through ADRs.

## Standards

- [Documentation Standard](docs/documentation.md)
- [Repository Standard](docs/repository.md)
- [GitHub Standard](docs/github.md)
- [Development Standard](docs/development.md)
- [Engineering Tooling Standard](docs/tooling.md)
- [Engineering Tooling Matrix](docs/tooling-matrix.md)
- [Security Standard](docs/security.md)
- [CI/CD Standard](docs/ci-cd.md)
- [Release Standard](docs/release.md)
- [Internationalization Standard](docs/i18n.md)
- [OSS Compliance Standard](docs/oss-compliance.md)
- [Reference Practices Audit](docs/reference-practices.md)
- [Reference Implementation Metrics](docs/reference-metrics.md)

## Engineering Tooling Examples

OpenForge provides defaults rather than one mandatory stack.

- **Go formatting:** `gofumpt` as the default formatter instead of direct `gofmt` usage
- **Go quality:** `go vet`, tests, and a static analyzer appropriate to the project
- **Code intelligence:** `codegraph`, `graphify`, or an equivalent tool when the repository benefits from dependency/call-graph analysis
- **AI-assisted development:** version-controlled project guidance such as `AGENTS.md`, `CLAUDE.md`, or equivalent instructions
- **Task automation:** Makefile or an equivalent reproducible task runner where appropriate

See the [Engineering Tooling Matrix](docs/tooling-matrix.md).

## Reference Metrics

OpenForge includes a practical maturity scorecard based on real implementation patterns from existing OSS projects.

Each applicable metric is scored:

- `2` — implemented and automated where practical
- `1` — partially or manually implemented
- `0` — missing
- `N/A` — not applicable

The scorecard covers documentation, architecture, GitHub, CI/CD, security, development tooling, release management, configuration, and localization.

See [Reference Implementation Metrics](docs/reference-metrics.md).

## Templates

Reusable GitHub and project templates are provided under [`templates/`](templates/).

A Go starter example is available under [`templates/go/`](templates/go/).

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
Implementation
  ↓
CI / Security / Testing
  ↓
Release
  ↓
Maintenance
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
