English | [한국어](README-ko.md)

# OpenForge

> **오픈소스 프로젝트 Blueprint & Engineering Standards**

OpenForge는 품질 높은 오픈소스 프로젝트를 만들고 발전시키고 유지하기 위한 재사용 가능한 Engineering Foundation입니다.

[소개](docs/about-ko.md) · [English README](README.md)

## 왜 OpenForge인가?

새로운 OSS 프로젝트를 시작할 때마다 동일한 Engineering Foundation을 처음부터 다시 만들 필요가 없도록 합니다. OpenForge는 실제 운영 중인 프로젝트에서 검증된 패턴을 기반으로 실용적인 기본 기준을 제공합니다.

OpenForge는 **Repository Blueprint, Engineering Standard, 재사용 가능한 Project Template**으로 적용할 수 있도록 설계되었습니다.

## 핵심 원칙

- English를 canonical project language로 사용하고 Korean을 first-class translation으로 제공합니다.
- 사용자 대상 Markdown은 `<name>.md`와 `<name>-ko.md` 규칙을 사용합니다.
- 프로젝트는 기본적으로 재현 가능하고, 문서화되고, 테스트 가능하며, 관측 가능하고, 안전해야 합니다.
- GitHub Issue와 Pull Request를 주요 변경 관리 수단으로 사용합니다.
- 아키텍처 결정은 ADR로 기록합니다.
- Merge 전에 CI가 품질을 검증합니다.
- Security와 Supply Chain 관리를 프로젝트 생명주기에 포함합니다.
- Localization은 나중에 추가하지 않고 처음부터 설계합니다.
- 일관성과 재현성을 높이는 개발 도구는 표준화합니다.
- 실제 프로젝트 리소스 이름, identifier, API 값 등은 번역하지 않습니다.
- 기본 기준에서 의도적으로 벗어나는 경우 ADR로 기록합니다.

## 표준

- [Documentation Standard](docs/documentation-ko.md)
- [Repository Standard](docs/repository-ko.md)
- [GitHub Standard](docs/github-ko.md)
- [Development Standard](docs/development-ko.md)
- [Engineering Tooling Standard](docs/tooling-ko.md)
- [Engineering Tooling Matrix](docs/tooling-matrix-ko.md)
- [Security Standard](docs/security-ko.md)
- [CI/CD Standard](docs/ci-cd-ko.md)
- [Release Standard](docs/release-ko.md)
- [Internationalization Standard](docs/i18n-ko.md)
- [OSS Compliance Standard](docs/oss-compliance-ko.md)
- [Reference Practices Audit](docs/reference-practices-ko.md)
- [Reference Implementation Metrics](docs/reference-metrics-ko.md)

## 개발 도구 예시

OpenForge는 하나의 기술 스택을 강제하기보다 프로젝트에 적합한 기본값을 제공합니다.

- **Go Formatter:** 직접 `gofmt`를 사용하는 대신 기본 formatter로 `gofumpt` 사용
- **Go Quality:** `go vet`, 테스트, 프로젝트에 적합한 static analyzer
- **Code Intelligence:** dependency/call graph 분석이 필요한 경우 `codegraph`, `graphify` 또는 동등 도구
- **AI-assisted development:** `AGENTS.md`, `CLAUDE.md` 등 version-controlled project guidance
- **Task automation:** 필요한 경우 Makefile 또는 동등한 재현 가능한 task runner

자세한 내용은 [Engineering Tooling Matrix](docs/tooling-matrix-ko.md)를 참고합니다.

## Reference Metrics

OpenForge에는 기존 OSS 프로젝트의 실제 구현 사례를 기반으로 한 프로젝트 maturity scorecard가 포함되어 있습니다.

각 적용 항목은 다음과 같이 평가합니다.

- `2` — 구현되어 있고 가능한 경우 자동화됨
- `1` — 부분적 또는 수동으로 구현됨
- `0` — 미구현
- `N/A` — 해당 없음

문서, 아키텍처, GitHub, CI/CD, 보안, 개발 도구, 릴리스, 설정, 다국어 등 주요 영역을 평가합니다.

자세한 내용은 [Reference Implementation Metrics](docs/reference-metrics-ko.md)를 참고합니다.

## Templates

재사용 가능한 GitHub 및 프로젝트 템플릿은 [`templates/`](templates/) 아래에서 제공합니다.

Go starter 예제는 [`templates/go/`](templates/go/)에서 확인할 수 있습니다.

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

## 참고 프로젝트

OpenForge는 다음과 같은 실제 OSS 개발 사례를 참고하여 발전합니다.

- Narwhal
- Narwhal Portal
- nfs-quota-agent
- kube-ready-box
- KubeMetal
- ldapium
- Beluga Manager

이 프로젝트들은 엄격한 의존 대상이 아니라 참고 구현입니다. 목표는 반복해서 적용할 수 있는 Engineering Practice를 표준화하면서 각 프로젝트의 구현 선택권은 유지하는 것입니다.

## Contributing

기여는 [Contributing Guide](CONTRIBUTING-ko.md)를 따릅니다. 새로운 표준은 구체적인 사용 사례, 참고 구현 또는 반복 가능한 Engineering Benefit을 근거로 제안해야 합니다.

## License

Apache License 2.0. See [LICENSE](LICENSE).
