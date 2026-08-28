English | [한국어](README-ko.md)

# OpenForge

> **오픈소스 프로젝트 Blueprint & Engineering Standards**

OpenForge는 품질 높은 오픈소스 프로젝트를 만들고 발전시키고, 배포하고, 운영하고 유지하기 위한 재사용 가능한 Engineering Foundation입니다.

Repository structure, documentation, GitHub workflow, CI/CD, security, supply-chain governance, change impact analysis, upgrade/compatibility, developer environment security, AI-assisted engineering, container/IaC security, release, maintainer governance, resilience, localization, engineering tooling, **UI/UX 디자인 시스템**, reusable implementation templates, deployment baseline, 디자인 템플릿과 프로젝트 lifecycle을 공통 기준으로 관리합니다.

[소개](docs/about-ko.md) · [의사결정 기록 / ADR](docs/adr/README-ko.md) · [English README](README.md)

## 핵심 원칙

- English를 canonical project language로 사용하고 Korean을 first-class translation으로 제공합니다.
- 사용자 대상 Markdown은 `<name>.md`와 `<name>-ko.md` 규칙을 사용합니다.
- 프로젝트는 기본적으로 재현 가능하고, 문서화되고, 테스트 가능하며, 관측 가능하고, 접근 가능하며, 안전해야 합니다.
- GitHub Issue와 Pull Request를 주요 변경 관리 수단으로 사용합니다.
- Architecture 및 장기적인 Cross-project Decision은 ADR로 기록합니다.
- Accepted ADR은 History로 보존하고 실질적인 변경은 새로운 ADR로 Supersede합니다.
- Merge 전에 CI가 품질을 검증합니다.
- Security와 Supply Chain을 프로젝트 생명주기에 포함합니다.
- Dependency 호환성만으로 최신 버전을 즉시 채택하지 않습니다.
- Dependency/runtime/toolchain 변경은 workflow 전체 영향 분석을 수행합니다.
- AI agent와 repository-local instruction은 잠재적으로 untrusted execution input으로 취급합니다.
- 외부 plugin, skill, behavior specification, trace, eval baseline은 identity, integrity, provenance 및 behavioral policy 검증 전까지 untrusted input으로 취급합니다.
- 단독 maintainer OSS도 사람 수가 아니라 risk와 automated control을 기준으로 governance를 적용합니다.
- CI 장애가 security gate 우회를 유도하지 않도록 resilience/fallback을 설계합니다.
- Template은 출발점이며 모든 프로젝트에 그대로 적용되는 drop-in configuration이 아닙니다.
- UI의 의미와 Accessibility는 공통 표준을 따르되 Product Personality, Density, Platform Convention은 프로젝트 특성에 따라 의도적으로 달라질 수 있습니다.
- 의도적인 예외는 범위와 만료를 기록합니다.

## 의사결정 관리

OpenForge는 장기적인 공통 의사결정을 다음 계층으로 관리합니다.

```text
ADR → Standard → Template / CI / Policy → Adoption Record / Issue / PR
```

자세한 기준은 [의사결정 관리 표준](docs/decision-management-ko.md)과 [ADR Index](docs/adr/README-ko.md)를 참고합니다.

## 표준

- [Documentation Standard](docs/documentation-ko.md)
- [Repository Standard](docs/repository-ko.md)
- [GitHub Standard](docs/github-ko.md)
- [Development Standard](docs/development-ko.md)
- [Engineering Tooling Standard](docs/tooling-ko.md)
- [Engineering Tooling Matrix](docs/tooling-matrix-ko.md)
- [의사결정 관리 표준](docs/decision-management-ko.md) ([English](docs/decision-management.md))
- [Agent Engineering 표준](docs/agent-engineering-ko.md) ([English](docs/agent-engineering.md))
- [Agent Behavior 표준](docs/agent-behaviors-ko.md) ([English](docs/agent-behaviors.md))
- [Agent Evaluation 표준](docs/agent-evaluation-ko.md) ([English](docs/agent-evaluation.md))
- [Agent Engineering 적용 기록 — 2026-08](docs/agent-engineering-adoption-2026-08.md)
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

OpenForge는 [`templates/`](templates/) 아래에 구현 및 디자인 템플릿을 제공합니다. 주요 Project-level Template은 [`AGENTS.md`](templates/AGENTS.md), [`BEHAVIOR.md`](templates/BEHAVIOR.md), [`CODING_STANDARDS.md`](templates/CODING_STANDARDS.md), [`DESIGN.md`](templates/DESIGN.md), [`ADR.md`](templates/ADR.md), [`ADR-ko.md`](templates/ADR-ko.md)입니다.

```text
templates/
├── AGENTS.md
├── BEHAVIOR.md
├── CODING_STANDARDS.md
├── DESIGN.md
├── ADR.md
├── ADR-ko.md
├── agent-eval/      # structured trace / evaluation example
├── github/          # PR / CODEOWNERS
├── workflows/       # CI / release / SBOM / supply-chain
├── scripts/         # toolchain / validation / evaluation helper
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

## 컴플라이언스 평가 및 감사 도구

OpenForge는 공통 엔지니어링 표준 대비 각 OSS 저장소의 성숙도를 자동으로 진단하고, 재현 가능한 스코어카드, 이전 베이스라인과의 비교 분석, GitHub Issue 등록용 Gap 명세를 생성하는 이식 가능한 감사 엔진을 제공합니다.

```bash
# 전체 포트폴리오 컴플라이언스 감사 실행
python3 templates/scripts/audit-portfolio.py --config templates/portfolio.example.yml

# 특정 저장소 단독 감사 실행
python3 templates/scripts/audit-portfolio.py --repo /path/to/repo

# 이전 베이스라인과의 비교 (Delta 및 해결된 Gap 분석)
python3 templates/scripts/audit-portfolio.py --baseline docs/portfolio-audit-report.json

# 대표 Agent Trace 평가
python3 templates/scripts/evaluate-agent-trace.py templates/agent-eval/trace.example.json
```

Canonical auditor는 metric set `2026.09`를 사용합니다. 총 **36개 안정화된 compliance metric**을 제공하며, `.agents/behaviors/`를 채택한 저장소에는 opt-in `AGENT-004`를 적용합니다. `2026.08` baseline과의 비교는 가능한 경우 `additive-compatible`로 처리합니다. Trace/Eval Adoption은 아직 새 Portfolio Metric으로 승격하지 않고, 여러 Repository와 대표 Workflow에서 반복성이 입증된 이후에 검토합니다.

- [포트폴리오 스코어카드](docs/portfolio-scorecard-ko.md) — 14개 OSS 저장소의 표준 채택률 및 우선 개선 순위
- [참고 메트릭](docs/reference-metrics-ko.md) — 36개 표준 엔지니어링 및 성숙도 지표
- [Agent Behavior 표준](docs/agent-behaviors-ko.md) — 반복 행동과 구조 검증 Governance
- [Agent Evaluation 표준](docs/agent-evaluation-ko.md) — Trace Evidence, Deterministic Eval, Regression Comparison
- [Branch Protection 표준](docs/branch-protection-ko.md) — 기준 브랜치 보호 및 필수 CI 검사 요건
- [Gap Issues 카탈로그](docs/gap-issues/) — 영역별로 분리된 GitHub Issue 등록용 명세

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

기여는 [Contributing Guide](CONTRIBUTING-ko.md)를 따릅니다. 새로운 표준과 Template은 구체적인 Use Case, Reference Implementation 또는 반복 가능한 Engineering Benefit을 기반으로 추가합니다. 여러 OSS에 영향을 주는 장기적인 Policy 변경은 [ADR 기준](docs/decision-management-ko.md)을 함께 검토합니다.

## License

Apache License 2.0. [LICENSE](LICENSE)를 참고하세요.
