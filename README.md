English | [한국어](README-ko.md)

# OpenForge

> **Open Source Project Blueprint & Engineering Standards**

OpenForge is a reusable engineering foundation for creating, evolving, deploying, and maintaining high-quality open-source projects.

It standardizes the parts of OSS development that should be consistent across projects: repository structure, documentation, GitHub workflows, CI/CD, security, supply-chain governance, change impact analysis, upgrade/compatibility, developer environment security, AI-assisted engineering, container/IaC security, releases, maintainer governance, resilience, localization, engineering tooling, reusable implementation templates, deployment baselines, design templates, and project lifecycle practices.

[About](docs/about.md)

## Core Principles

- English is the canonical project language; Korean is a first-class translation.
- Projects should be reproducible, documented, testable, observable, accessible, and secure by default.
- GitHub Issues and Pull Requests are the primary change-management mechanism.
- Architecture decisions are recorded as ADRs.
- CI validates quality before changes are merged.
- Security and supply-chain controls are built into the lifecycle.
- Dependency compatibility alone does not justify immediate adoption of the newest release.
- Dependency/runtime/toolchain changes require workflow-wide impact analysis.
- AI agents and repository-local instructions are treated as potentially untrusted execution inputs.
- Security controls are risk-based so single-maintainer OSS projects remain practical.
- CI outages must not force maintainers to bypass security gates blindly.
- Templates provide implementation starting points, not universal drop-in configuration.

## Templates

OpenForge now separates templates into reusable implementation layers:

```text
templates/
├── github/          # PR / CODEOWNERS patterns
├── workflows/       # CI / release / SBOM workflows
├── scripts/         # toolchain and validation helpers
├── policy/          # dependency and engineering policies
├── container/       # Docker image baseline
├── kubernetes/      # deployment / service / ingress / network / PDB / Kustomize
├── gitops/          # Argo CD / GitOps deployment patterns
├── identity/        # OIDC / SSO integration contract
├── observability/   # health / metrics / traces / logs contract
├── backup/          # backup and restore runbook
├── offline/         # air-gap bundle manifest
└── design/          # README / landing page / diagrams / status / design tokens
```

Each template is intentionally generic and must be adapted to the target project's runtime, permissions, platform, and threat model.

## Standards

See the complete standards catalog under `docs/`.

## Project Lifecycle

```text
Idea → Definition → Repository Bootstrap → Standards + Templates
→ Implementation → Impact / Supply Chain Review → CI / Security / Testing
→ Release / Publish Verification → Operations → Incident Learning → OpenForge Improvement
```

## Reference Projects

OpenForge captures repeatable practices from active OSS projects including Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, and Beluga Manager.

## License

Apache License 2.0.
