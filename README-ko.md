English | [한국어](README-ko.md)

# OpenForge

> **오픈소스 프로젝트 Blueprint & Engineering Standards**

OpenForge는 품질 높은 오픈소스 프로젝트를 만들고 발전시키고, 배포하고, 운영하고 유지하기 위한 재사용 가능한 Engineering Foundation입니다.

Repository structure, documentation, GitHub workflow, CI/CD, security, supply-chain governance, change impact analysis, upgrade/compatibility, developer environment security, AI-assisted engineering, container/IaC security, release, maintainer governance, resilience, localization, engineering tooling, **UI/UX 디자인 시스템**, reusable implementation templates, deployment baseline, 디자인 템플릿과 프로젝트 lifecycle을 공통 기준으로 관리합니다.

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
- 외부 plugin과 skill은 immutable identity, integrity 및 실행 행위 정책 검증을 통과하기 전까지 untrusted executable input으로 취급합니다.
- 단독 maintainer OSS도 사람 수가 아니라 risk와 automated control을 기준으로 governance를 적용합니다.
- CI 장애가 security gate 우회를 유도하지 않도록 resilience/fallback을 설계합니다.
- Template은 출발점이며 모든 프로젝트에 그대로 적용되는 drop-in configuration이 아닙니다.
- UI의 의미와 Accessibility는 공통 표준을 따르되 Product Personality, Density, Platform Convention은 프로젝트 특성에 따라 의도적으로 달라질 수 있습니다.
- 의도적인 예외는 범위와 만료를 기록합니다.

## 실행 가능한 성숙도 진단

OpenForge는 표준을 문서로만 남기지 않고 deterministic evidence로 진단하는 독립 Rust CLI도 제공합니다.

```bash
openforge assess . --format json
openforge assess . --run-execution --format json
openforge assess . --runtime --kube-context my-cluster --format json
openforge compare baseline.json current.json --fail-on-regression
```

진단 계층은 의도적으로 분리합니다.

- **L1 Repository** — 문서, 거버넌스, 보안, CI/CD, 릴리스, 플랫폼, Web Asset의 source evidence
- **L2 Execution** — 지원 ecosystem에 대한 trusted built-in build/test/lint probe
- **L3 Runtime** — Kubernetes의 availability, policy coverage, RBAC/security, storage/CSI, certificate, backup/restore, observability, GitOps를 read-only로 진단
- **Web runtime evidence** — immutable cache policy(`WEB-008`)와 실제 cache-hit evidence(`WEB-009`)를 명시적 opt-in 방식으로 확인
- **Optional AI analysis** — AI는 완료된 결과를 해석할 수 있지만 점수, PASS/FAIL, evidence를 변경하지 않음

Profile, applicability, 기간이 있는 waiver, baseline, compare/regression gate를 지원하므로 프로젝트 특성이 다른 경우에도 동일한 규칙을 억지로 적용하지 않습니다.

자세한 내용은 [Maturity Assessment](docs/maturity-assessment-ko.md), [Assessment Profiles](docs/assessment-profiles.md), [Assessment Comparison](docs/assessment-comparison.md), [Web Asset / Image Delivery](docs/web-asset-image-delivery.md), [Runtime Web Cache Verification](docs/web-cache-runtime-verification.md), [Runtime Cache Effectiveness](docs/web-cache-effectiveness.md)를 참고하세요.

## 표준

- [Documentation Standard](docs/documentation-ko.md)
- [Repository Standard](docs/repository-ko.md)
- [GitHub Standard](docs/github-ko.md)
- [Development Standard](docs/development-ko.md)
- [Engineering Tooling Standard](docs/tooling-ko.md)
- [Engineering Tooling Matrix](docs/tooling-matrix-ko.md)
- [OSS 디자인 시스템 표준](docs/design-system-ko.md) ([English](docs/design-system.md))
- [OpenForge OSS Design System — Figma](https://www.figma.com/design/Y1JpRSOwctAKSwPjDNbe1g)
- [Security Standard](docs/security-ko.md)
- [Supply Chain Security Standard](docs/supply-chain-ko.md)
- [Plugin Supply-Chain Intake Standard](docs/plugin-supply-chain-ko.md)
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

OpenForge는 [`templates/`](templates/) 아래에 구현 및 디자인 템플릿을 제공합니다. 프로젝트별 Archetype, Token Mapping, Product Personality, Workflow, Accessibility, 예외를 기록하기 위한 [`templates/DESIGN.md`](templates/DESIGN.md)를 제공합니다.

```text
templates/
├── DESIGN.md        # 프로젝트 디자인 시스템 계약
├── github/          # PR / CODEOWNERS
├── workflows/       # CI / release / SBOM / supply-chain
├── scripts/         # toolchain / validation / supply-chain checks
├── policy/          # dependency / plugin-intake / engineering policy
├── container/       # Docker baseline
├── kubernetes/      # Deployment / Service / Ingress / NetworkPolicy / PDB / Kustomize
├── gitops/          # Argo CD / GitOps
├── identity/        # OIDC / SSO
├── observability/   # health / metrics / traces / logs
├── backup/          # backup / restore
├── offline/         # air-gap bundle / trusted plugin catalog
└── design/          # README / landing / architecture / status / design token
```

Template은 보수적인 출발점입니다. Target repository와 threat model에 맞게 version, permission, path, command, domain, image, identity, ecosystem-specific control을 조정해야 합니다.

## Reference Project

OpenForge의 디자인 시스템 표준은 현재 개발 중인 프로젝트의 서로 다른 UI 성격을 참고합니다.

- Narwhal / Narwhal Portal — Platform Portal
- Beluga Manager — Data Control Plane
- ClusterDeck — Desktop Operator
- KubeMetal — Desktop ML Infrastructure
- ldapium — Admin Console
- nfs-quota-agent — Operations Dashboard
- eGovFrame Launcher — Developer Tool

이 프로젝트들은 rigid dependency가 아니라 반복 가능한 Engineering 및 Design Practice를 추출하기 위한 Reference입니다.

## Contributing

기여는 [Contributing Guide](CONTRIBUTING-ko.md)를 따릅니다. 새로운 표준과 Template은 구체적인 Use Case, Reference Implementation 또는 반복 가능한 Engineering Benefit을 기반으로 추가합니다.

## License

Apache License 2.0. [LICENSE](LICENSE)를 참고하세요.
