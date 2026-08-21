English | [한국어](README-ko.md)

# OpenForge

> **오픈소스 프로젝트 Blueprint & Engineering Standards**

OpenForge는 품질 높은 오픈소스 프로젝트를 만들고 발전시키고, 배포하고, 운영하고 유지하기 위한 재사용 가능한 Engineering Foundation입니다.

Repository structure, documentation, GitHub workflow, CI/CD, security, supply-chain governance, change impact analysis, upgrade/compatibility, developer environment security, AI-assisted engineering, container/IaC security, release, maintainer governance, resilience, localization, engineering tooling, reusable implementation templates, deployment baseline, 디자인 템플릿과 프로젝트 lifecycle을 공통 기준으로 관리합니다.

[소개](docs/about-ko.md) · [English README](README.md)

## 핵심 원칙

- English를 canonical project language로 사용하고 Korean을 first-class translation으로 제공합니다.
- 사용자 대상 Markdown은 `<name>.md`와 `<name>-ko.md` 규칙을 사용합니다.
- 프로젝트는 기본적으로 재현 가능하고, 문서화되고, 테스트 가능하며, 관측 가능하고, 접근 가능하며, 안전해야 합니다.
- GitHub Issue와 Pull Request를 주요 변경 관리 수단으로 사용합니다.
- Architecture Decision은 ADR로 기록합니다.
- Merge 전에 CI가 품질을 검증합니다.
- Security와 Supply Chain을 프로젝트 생명주기에 포함합니다.
- Dependency 호환성만으로 최신 버전을 즉시 채택하지 않습니다.
- Dependency/runtime/toolchain 변경은 workflow 전체 영향 분석을 수행합니다.
- AI agent와 repository-local instruction은 잠재적으로 untrusted execution input으로 취급합니다.
- 단독 maintainer OSS도 사람 수가 아니라 risk와 automated control을 기준으로 governance를 적용합니다.
- CI 장애가 security gate 우회를 유도하지 않도록 resilience/fallback을 설계합니다.
- Template은 출발점이며 모든 프로젝트에 그대로 적용되는 drop-in configuration이 아닙니다.
- 의도적인 예외는 범위와 만료를 기록합니다.

## 표준

- [Documentation Standard](docs/documentation-ko.md)
- [Repository Standard](docs/repository-ko.md)
- [GitHub Standard](docs/github-ko.md)
- [Development Standard](docs/development-ko.md)
- [Engineering Tooling Standard](docs/tooling-ko.md)
- [Engineering Tooling Matrix](docs/tooling-matrix-ko.md)
- [Security Standard](docs/security-ko.md)
- [Supply Chain Security Standard](docs/supply-chain-ko.md)
- [Package and Artifact Identity](docs/package-identity-ko.md)
- [CI/CD Security Standard](docs/ci-security-ko.md)
- [CI/CD Resilience Standard](docs/ci-resilience-ko.md)
- [Change Management and Impact Analysis](docs/change-management-ko.md)
- [Upgrade and Compatibility Engineering](docs/upgrade-compatibility-ko.md)
- [Reproducible Build](docs/reproducible-build-ko.md)
- [Developer Environment Security](docs/developer-environment-security.md)
- [AI-Assisted Engineering Security](docs/ai-engineering-security-ko.md)
- [Container, Kubernetes and IaC Security](docs/container-iac-security-ko.md)
- [Secrets and Machine Identity](docs/secrets-identity-ko.md)
- [Vulnerability Management](docs/vulnerability-management-ko.md)
- [Security and Supply-Chain Incident Response](docs/incident-response-ko.md)
- [Release Security](docs/release-security-ko.md)
- [Security Exceptions and Waivers](docs/security-exceptions-ko.md)
- [Maintainer Governance](docs/maintainer-governance-ko.md)
- [CI/CD Standard](docs/ci-cd-ko.md)
- [Release Standard](docs/release-ko.md)
- [Internationalization Standard](docs/i18n-ko.md)
- [OSS Compliance Standard](docs/oss-compliance-ko.md)
- [Reference Practices Audit](docs/reference-practices-ko.md)
- [Reference Implementation Metrics](docs/reference-metrics-ko.md)

## 재사용 가능한 템플릿

OpenForge는 [`templates/`](templates/) 아래에 구현 및 디자인 템플릿을 제공합니다.

```text
templates/
├── github/          # PR / CODEOWNERS
├── workflows/       # CI / release / SBOM
├── scripts/         # toolchain / validation
├── policy/          # dependency / engineering policy
├── container/       # Docker baseline
├── kubernetes/      # Deployment / Service / Ingress / NetworkPolicy / PDB / Kustomize
├── gitops/          # Argo CD / GitOps
├── identity/        # OIDC / SSO
├── observability/   # health / metrics / traces / logs
├── backup/          # backup / restore
├── offline/         # air-gap bundle
└── design/          # README / landing / architecture / status / design tokens
```

각 템플릿은 대상 프로젝트의 runtime, permission, platform, deployment model, identity, image, domain, threat model에 맞게 조정해야 합니다.

## Reference Metrics

OpenForge의 maturity scorecard는 documentation, architecture, GitHub, CI/CD, security, supply-chain, change management, upgrade/compatibility, developer environment, AI-assisted engineering, release, resilience, configuration, localization 등을 평가합니다.

- `2` — 구현되어 있고 가능한 경우 자동화됨
- `1` — 부분적 또는 수동으로 구현됨
- `0` — 미구현
- `N/A` — 해당 없음

자세한 내용은 [Reference Implementation Metrics](docs/reference-metrics-ko.md)를 참고합니다.

## 프로젝트 생명주기

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

## 참고 프로젝트

OpenForge는 Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, Beluga Manager 등의 실제 OSS 개발 사례에서 반복 가능한 Engineering Practice를 추출합니다.

## Contributing

기여는 [Contributing Guide](CONTRIBUTING-ko.md)를 따릅니다. 새로운 표준과 템플릿은 구체적인 사용 사례, 참고 구현 또는 반복 가능한 Engineering Benefit을 근거로 제안해야 합니다.

## License

Apache License 2.0. See [LICENSE](LICENSE).
