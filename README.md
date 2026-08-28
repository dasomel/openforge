English | [한국어](README-ko.md)

# OpenForge

> **Open Source Project Blueprint & Engineering Standards**

OpenForge is a reusable engineering foundation for creating, evolving, deploying, and maintaining high-quality open-source projects.

It standardizes the parts of OSS development that should be consistent across projects: repository structure, documentation, GitHub workflows, CI/CD, security, supply-chain governance, change impact analysis, upgrade/compatibility, developer environment security, AI-assisted engineering, container/IaC security, releases, maintainer governance, resilience, localization, engineering tooling, **UI/UX design systems**, reusable implementation templates, deployment baselines, design templates, and project lifecycle practices.

[About](docs/about.md) · [Decision History / ADRs](docs/adr/README.md)

## Why OpenForge?

Starting an OSS project should not mean rebuilding the same engineering foundation every time. OpenForge provides a practical baseline based on patterns already proven across active projects.

OpenForge is designed to be applied as a **repository blueprint, engineering standard, reusable project template, and implementation catalog**.

## Core Principles

- English is the canonical project language; Korean is a first-class translation.
- User-facing Markdown follows `<name>.md` and `<name>-ko.md`.
- Projects should be reproducible, documented, testable, observable, accessible, and secure by default.
- GitHub Issues and Pull Requests are the primary change-management mechanism.
- Architecture and durable cross-project decisions are recorded as ADRs.
- Accepted ADRs preserve history; material changes supersede them instead of rewriting rationale.
- CI validates quality before changes are merged.
- Security and supply-chain controls are built into the lifecycle.
- Dependency compatibility alone does not justify immediate adoption of the newest release.
- Dependency/runtime/toolchain changes require workflow-wide impact analysis.
- AI agents and repository-local instructions are treated as potentially untrusted execution inputs.
- External plugins, skills, behavior specifications, traces, and eval baselines are treated as untrusted inputs until identity, integrity, provenance, and behavioral policy checks pass.
- Security controls are risk-based so single-maintainer OSS projects remain practical.
- CI outages must not force maintainers to bypass security gates blindly.
- Reusable templates provide implementation starting points but are not universal drop-in configuration.
- UI semantics and accessibility are shared while project personality, density, and platform conventions may vary intentionally.
- Intentional deviations from the baseline are time-bounded and documented.

## Decision History

OpenForge separates durable rationale from normative standards and rollout history:

```text
ADR -> Standard -> Template / CI / Policy -> Adoption record / Issue / PR
```

See the [ADR index](docs/adr/README.md). The initial retrospective ADR set captures major common decisions already reflected across OpenForge standards, including language policy, risk-based governance, AI/plugin trust, upgrade impact analysis, lifecycle security, design-system boundaries, agent-engineering context management, evidence-first verification, reusable-template policy, CI resilience, and exception governance.

## Standards

- [Documentation Standard](docs/documentation.md)
- [Repository Standard](docs/repository.md)
- [GitHub Standard](docs/github.md)
- [Development Standard](docs/development.md)
- [Engineering Tooling Standard](docs/tooling.md)
- [Engineering Tooling Matrix](docs/tooling-matrix.md)
- [Agent Engineering Standard](docs/agent-engineering.md) ([한국어](docs/agent-engineering-ko.md))
- [Agent Behavior Standard](docs/agent-behaviors.md) ([한국어](docs/agent-behaviors-ko.md))
- [Agent Evaluation Standard](docs/agent-evaluation.md) ([한국어](docs/agent-evaluation-ko.md))
- [Agent Engineering Adoption — 2026-08](docs/agent-engineering-adoption-2026-08.md)
- [OSS Design System Standard](docs/design-system.md) ([한국어](docs/design-system-ko.md))
- [OpenForge OSS Design System — Figma](https://www.figma.com/design/Y1JpRSOwctAKSwPjDNbe1g)
- [Security Standard](docs/security.md)
- [Supply Chain Security Standard](docs/supply-chain.md)
- [Plugin Supply-Chain Intake Standard](docs/plugin-supply-chain.md)
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

OpenForge provides reusable implementation and design templates under [`templates/`](templates/). Important project-level templates include [AGENTS.md](templates/AGENTS.md), [BEHAVIOR.md](templates/BEHAVIOR.md), [CODING_STANDARDS.md](templates/CODING_STANDARDS.md), [DESIGN.md](templates/DESIGN.md), and [ADR.md](templates/ADR.md).

```text
templates/
├── AGENTS.md        # concise agent execution contract
├── BEHAVIOR.md      # reusable recurring-agent behavior specification
├── CODING_STANDARDS.md
├── DESIGN.md        # project design-system contract
├── ADR.md           # durable decision record
├── agent-eval/      # structured trace/evaluation examples
├── github/          # PR / CODEOWNERS patterns
├── workflows/       # CI / release / SBOM workflows
├── scripts/         # toolchain / validation / evaluation helpers
├── policy/          # dependency / plugin-intake / engineering policies
├── container/       # Docker image baseline
├── kubernetes/      # Deployment / Service / Ingress / NetworkPolicy / PDB / Kustomize
├── gitops/          # Argo CD / GitOps deployment patterns
├── identity/        # OIDC / SSO integration contract
├── observability/   # health / metrics / traces / logs contract
├── backup/          # backup and restore runbook
├── offline/         # air-gap bundle and trusted plugin catalog manifests
└── design/          # README / landing / architecture / status / design tokens
```

Templates are intentionally conservative. Adapt versions, permissions, paths, commands, domains, images, identities, and ecosystem-specific controls to the target repository and threat model.

## Reference Metrics

OpenForge includes a practical maturity scorecard covering documentation, architecture, GitHub, CI/CD, security, supply-chain governance, change management, upgrade/compatibility, developer environment, AI-assisted engineering, release management, resilience, configuration, localization, design-system adoption, and agent behavior governance.

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
Standards + Template Adoption
  ↓
Implementation
  ↓
Change Impact / Supply Chain Review
  ↓
CI / Security / Testing
  ↓
Release / Publish Verification
  ↓
Operations / Backup / Observability
  ↓
Maintenance / Incident Learning
  ↓
Lessons / Metrics
  ↓
OpenForge Improvement
```

## Compliance Assessment

OpenForge provides a portable compliance audit engine to assess OSS repositories against shared engineering standards, generating reproducible scorecards, delta comparisons, and actionable GitHub gap issues.

```bash
# Run portfolio-wide compliance audit
python3 templates/scripts/audit-portfolio.py --config templates/portfolio.example.yml

# Audit a single local repository
python3 templates/scripts/audit-portfolio.py --repo /path/to/repo

# Compare against historical baseline
python3 templates/scripts/audit-portfolio.py --baseline docs/portfolio-audit-report.json

# Evaluate a representative agent trace
python3 templates/scripts/evaluate-agent-trace.py templates/agent-eval/trace.example.json
```

The canonical auditor publishes metric set `2026.09`. It contains **36 stable compliance metrics**, including opt-in `AGENT-004` for repositories that adopt `.agents/behaviors/`. Comparisons against `2026.08` are reported as additive-compatible when appropriate. Trace/eval adoption is deliberately not a new portfolio metric yet; it must first demonstrate repeatability across multiple repositories and representative workflows.

- [Portfolio Scorecard](docs/portfolio-scorecard.md) — 14-repository adoption scorecard and remediation ranking
- [Reference Metrics](docs/reference-metrics.md) — 36 standard engineering and maturity metrics
- [Agent Behavior Standard](docs/agent-behaviors.md) — recurring agent conduct and structural validation governance
- [Agent Evaluation Standard](docs/agent-evaluation.md) — trace evidence, deterministic behavior eval, and regression comparison
- [Branch Protection Standard](docs/branch-protection.md) — canonical branch gates and status check requirements
- [Gap Issues Catalog](docs/gap-issues/) — structured GitHub issue drafts grouped by area

## Reference Projects

OpenForge is informed by active OSS development practices, including:

- Narwhal / Narwhal Portal
- ClusterDeck
- nfs-quota-agent
- kube-ready-box
- KubeMetal
- ldapium
- Beluga Manager
- eGovFrame Launcher

These projects are references, not rigid dependencies. The goal is to capture repeatable engineering and design practices while keeping projects free to choose their own implementation details.

## Contributing

Contributions should follow the repository's [Contributing Guide](CONTRIBUTING.md). New standards and templates should be supported by a concrete use case, reference implementation, or repeatable engineering benefit. Durable cross-project policy changes should include an ADR when they meet the criteria in the [ADR index](docs/adr/README.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
