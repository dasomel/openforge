# OSS Reference Practices Audit

This document records practices observed in active `dasomel` OSS repositories and converts reusable patterns into OpenForge standards.

## English

OpenForge was reviewed against active repositories including Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, and Beluga.

### Reusable practices observed

| Practice | Reference repositories | OpenForge treatment |
|---|---|---|
| English/Korean documentation pairs | Narwhal, Narwhal Portal, nfs-quota-agent, KubeMetal, ldapium | Standardize on `<name>.md` + `<name>-ko.md` for owned user-facing docs |
| Version authority | Narwhal `VERSIONS.md` | Prefer one authoritative version/compatibility inventory |
| Changelog pair | Narwhal, nfs-quota-agent, KubeMetal, ldapium | `CHANGELOG.md` + `CHANGELOG-ko.md` |
| ADR / design records | Narwhal Portal, KubeMetal | Important architectural decisions become versioned ADRs |
| Incident / lessons log | Narwhal, KubeMetal | Operational failures become reusable engineering knowledge |
| AI repository instructions | Narwhal, Narwhal Portal, KubeMetal, nfs-quota-agent | Version `AGENTS.md`, `CLAUDE.md`, or equivalent when AI-assisted development is used |
| Release guide | ldapium, KubeMetal | Release procedures become explicit and reproducible |
| Security policy | ldapium and other platform repositories | `SECURITY.md` plus private reporting guidance |
| Legal / third-party attribution | ldapium, kube-ready-box | License, NOTICE and third-party obligations are documented |
| Environment example | ldapium | `.env.example` or equivalent safe configuration examples |
| Make-based developer UX | KubeMetal, ldapium, Narwhal | Prefer a small, discoverable command surface where appropriate |
| Version checks | ldapium | Automate version consistency checks when multiple manifests/configs carry versions |
| Supply-chain checks | ldapium scorecard workflow, image/release workflows | Add provenance, SBOM, vulnerability and workflow-hardening checks where applicable |
| Dependency freshness / cooling | Portfolio security review | `docs/supply-chain.md`: latest-compatible is insufficient; 14-day default cooling, emergency exception and progressive adoption |
| Change impact / workflow contract | Recent Bun CI incident and cross-workflow review | `docs/change-management.md`: Class C/D changes require workflow-wide impact analysis and runtime/toolchain verification |
| Build-time trust boundary | Rust supply-chain incident analysis | Treat install hooks, build scripts, proc-macros, plugins and code generators as executable supply-chain inputs |
| CI/CD security boundary | 2026 GitHub Actions cache/fork/OIDC threat model | `docs/ci-security.md`: runner, trigger, cache, permission, egress and artifact trust boundaries |
| Package identity | 2026 typosquat/evil-twin package and extension cases | `docs/package-identity.md`: publisher/namespace verification, ownership-change review and quarantine |
| Developer environment security | IDE/extension and repository-configuration incidents | `docs/developer-environment-security.md`: extension, devcontainer, Git hook and workspace-config trust controls |
| AI-assisted engineering security | 2026 coding-agent and prompt-injection incidents | `docs/ai-engineering-security.md`: agent permissions, untrusted context, tool execution and release boundary |
| Reproducible build | Release engineering practice | `docs/reproducible-build.md`: source/dependency/toolchain/builder/artifact identity linkage |
| Container/Kubernetes/IaC security | Narwhal, Beluga, KubeMetal, kube-ready-box | `docs/container-iac-security.md`: image/chart/provider/plugin integrity and privileged configuration review |
| Machine identity/security | CI and publishing threat model | `docs/secrets-identity.md`: short-lived identity, OIDC, least privilege and credential separation |
| Vulnerability lifecycle | Active OSS maintenance | `docs/vulnerability-management.md`: triage, remediation, verification, exceptions and monitoring |
| Supply-chain incident response | Recent package compromise patterns | `docs/incident-response.md`: quarantine, credential rotation, blast radius, clean rebuild and regression control |
| Release security | Package registry publishing incidents | `docs/release-security.md`: artifact freeze, publish isolation, approval and post-publish verification |
| Maintainer governance | Small OSS operating model | `docs/maintainer-governance.md`: single-maintainer support with risk-based review and automation |

## Change-management rule

A dependency/runtime/toolchain migration changes the build contract even when the application interface remains compatible. Before merge, search every workflow that can invoke the affected build, test, package or release command.

The historical Bun migration failure is the reference example: a build command changed to invoke Bun, but an independent Pages deployment workflow did not install Bun. The durable OpenForge rule is therefore **workflow-wide impact analysis**, not a one-off fix.

## Supply-chain rule

OpenForge is the reference standard for the portfolio. Repository-specific supply-chain policies should reference `docs/supply-chain.md` rather than inventing incompatible freshness, pinning, provenance or rollback rules.

## Governance rule

OpenForge supports single-maintainer repositories. Two-person review is a risk-reduction recommendation for high-impact changes, not a universal staffing requirement. When independent review is unavailable, strong automated controls, explicit impact analysis and retrospective review compensate where practical.

## Documentation naming exception

The `-ko.md` rule applies to project-owned, user-facing documentation. It does not require rewriting third-party or vendored documentation, generated documentation, or upstream artifacts whose filename is part of the upstream distribution contract.

## Recommended evidence loop

```text
Failure / Change
      ↓
Issue / ADR / Incident record
      ↓
Change impact analysis
      ↓
Implementation
      ↓
Regression test or CI check
      ↓
Security / supply-chain evidence
      ↓
Release note / Changelog
      ↓
Reusable documentation
```

This loop is particularly valuable for infrastructure and platform projects where integration defects can recur after upgrades.

## Korean

OpenForge는 실제 개발 중인 여러 OSS를 기준으로 공통 engineering practice를 표준화합니다. 공급망, 변경 영향 분석, CI/CD 보안, AI-assisted engineering, developer environment, release, maintainer governance까지 공통 정책으로 승격했습니다.

프로젝트별 특수성은 ADR 또는 project-specific guidance로 분리하고, 공통 정책은 각 표준 문서를 참조합니다.
